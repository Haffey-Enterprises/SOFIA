# Module: agent_loop.runner
# Purpose: The pass loop. Per pass it fetches the ledger fresh, takes an
#          immutable prior-pass snapshot (contract §2), runs the scheduled
#          reviewers against that snapshot and gathers their emissions, then
#          admits them through the admission gate in a fixed deterministic order
#          (§3) — no admission interleaves with any review. It then runs the
#          arbiter on open/unclassified findings, snapshots the pass record at
#          routing time, and routes; on CONTINUE the author stub acts. Dry mode
#          throughout: resolutions and escalations are proposed and logged.
# Scope:   Orchestration only. Judgment about "done" is in gates.route (no LLM).
#          The only LLM judgment (the arbiter) is injected as a port; reviewers
#          are injected via a Plan. Author, arbiter position, gates, router, the
#          schema enums, and mode are untouched by the real-hats contract (§8).

from __future__ import annotations

import copy
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Callable

from agent_loop.admission import admit
from agent_loop.arbiter import Arbiter
from agent_loop.gates import RouterExit, open_cbm, route
from agent_loop.ledger import Ledger, LedgerHeader, LedgerStore, PassRecord
from agent_loop.log import ActionLog
from agent_loop.reviewers import (
    DocumentFetcher,
    DocumentSet,
    Plan,
    Substrate,
    SubstrateFetcher,
    default_document_fetcher,
    default_substrate_fetcher,
    stub_plan,
)
from agent_loop.scenarios import Scenario
from agent_loop.stubs import author_pass


class RunHalted(RuntimeError):
    """Base for the runner's fail-loud halts (never a real CONVERGED/HALT exit)."""


class LoopBoundExceeded(RunHalted):
    """Raised when a run exceeds max_passes.

    A safety backstop, not a spec exit: a loop that routes CONTINUE forever
    would otherwise spin. It fails loudly so it can never be mistaken for a real
    CONVERGED/HALT exit.
    """


class InstrumentCompromisedError(RunHalted):
    """Raised when a scheduled reviewer is effectively absent this pass.

    A pass in which any scheduled reviewer produced >=1 parse-dropped emission
    and 0 admitted findings is instrument-compromised (mechanical-gates.md §3,
    amended 2026-07-02 after run-003's false CONVERGED): CONVERGED must never be
    reachable through a fully-dropped reviewer. Fail-loud before routing. Partial
    drops and legitimately empty emissions (zero findings, zero drops) do not
    trip the guard.
    """


@dataclass
class RunResult:
    """The outcome of a run.

    Attributes:
        exit: The router exit that ended the run.
        passes_run: How many passes executed.
        ledger: The final ledger state.
        log: The structured action log (drops, parse-drops, coherence skips,
            classifications, proposed resolutions/escalations — the dry-mode
            evidence base).
    """

    exit: RouterExit
    passes_run: int
    ledger: Ledger
    log: ActionLog


def _default_clock() -> str:
    """Wall-clock ISO-8601 timestamp. Does not affect any gate outcome."""
    return datetime.now(timezone.utc).isoformat()


def _gather_then_admit(
    ledger: Ledger,
    snapshot_state: Ledger,
    plan: Plan,
    pass_number: int,
    records: DocumentSet,
    substrate: Substrate,
    log: ActionLog,
) -> tuple[list[str], list[str]]:
    """Run all scheduled reviewers against the snapshot, then admit in order.

    Implements contract §3 (gather-then-admit) over §2's amended snapshot
    semantics (ratified 2026-07-02): the plan and every reviewer receive the
    same snapshot *state* but each as its **own** frozen deep copy — never the
    shared base object, never another consumer's copy, never the `ledger`
    instance admission mutates. Isolation is therefore structural: a reviewer
    that mutates its own copy cannot leak to any later reviewer, to the plan, or
    to the admitted ledger (§9h).

    Every reviewer runs to completion before any admission; admission then
    proceeds in fixed rank order (LAA, SA, EA, coherence) with each reviewer's
    emission order preserved. No admission interleaves with any review.

    Also tracks, per reviewer, its parse-drops this pass (via the log delta) and
    whether any of its findings reached the ledger, so the instrument-compromised
    guard (mechanical-gates §3) can fire.

    Returns:
        (agents_run labels in admission order, compromised-reviewer labels).
    """
    # The plan's scheduling view is its own isolated copy of the state.
    scheduled = plan(pass_number, copy.deepcopy(snapshot_state), log)

    # Gather — no admission yet. Each reviewer gets its OWN frozen copy of the
    # snapshot AND of records/substrate, made at the same point (run-prep §4):
    # DocumentSet/Substrate are frozen dataclasses with mutable dict fields, so
    # sharing them left the same one-level-down cross-anchoring seam the §2
    # amendment closed for the snapshot.
    gathered = []
    for scheduled_reviewer in scheduled:
        reviewer_snapshot = copy.deepcopy(snapshot_state)
        reviewer_records = copy.deepcopy(records)
        reviewer_substrate = copy.deepcopy(substrate)
        drops_before = len(log.of_kind("parse_dropped"))
        findings = scheduled_reviewer.run(
            pass_number, reviewer_snapshot, reviewer_records, reviewer_substrate, log
        )
        parse_drops = len(log.of_kind("parse_dropped")) - drops_before
        gathered.append((scheduled_reviewer.identity, findings, parse_drops))

    # Admit in fixed deterministic order (stable sort preserves schedule order
    # on ties); emission order within a reviewer is preserved.
    gathered.sort(key=lambda triple: triple[0].admission_rank)
    agents_run: list[str] = []
    reached_ledger = {identity.label: 0 for identity, _, _ in gathered}
    for identity, findings, _ in gathered:
        agents_run.append(identity.label)
        for finding in findings:
            result = admit(ledger, finding, pass_number, log)
            if not result.dropped:  # admitted, reopened, or matched an open id
                reached_ledger[identity.label] += 1

    # Instrument-compromised guard: a reviewer that parse-dropped at least once
    # and put nothing on the ledger is effectively absent. Partial drops and
    # legitimately empty emissions (zero drops) never trip it.
    compromised = [
        identity.label
        for identity, _, parse_drops in gathered
        if parse_drops >= 1 and reached_ledger[identity.label] == 0
    ]
    return agents_run, compromised


def run_loop(
    header: LedgerHeader,
    plan: Plan,
    arbiter: Arbiter,
    store: LedgerStore,
    *,
    fix_changes: dict[str, str] | None = None,
    authorities: object = None,
    design_intent: object = None,
    fetch_documents: DocumentFetcher = default_document_fetcher,
    fetch_substrate: SubstrateFetcher = default_substrate_fetcher,
    label: str = "review loop",
    max_passes: int = 50,
    clock: Callable[[], str] = _default_clock,
    log: ActionLog | None = None,
) -> RunResult:
    """Drive the design-review loop to its router exit.

    The single runner for both the canned stub path and the real-hat path — the
    difference is the injected `plan`. Each pass: fetch fresh, freeze a
    prior-pass snapshot (§2), assemble fresh inputs (§5), gather-then-admit (§3),
    classify open findings (arbiter), snapshot the pass record at routing time,
    and route; CONTINUE runs the author.

    Args:
        header: The ledger header/parameters.
        plan: The pass plan selecting which reviewers run (and logging skips).
        arbiter: The arbiter port (the only LLM judgment).
        store: The file-backed ledger store (fresh-fetched each pass).
        fix_changes: Author fix→doc-change map (stub path); empty by default.
        authorities: Substrate passed to the arbiter (unchanged position, §8).
        design_intent: Design intent passed to the arbiter (§8).
        fetch_documents: Fresh document-set fetch (§5); placeholder by default.
        fetch_substrate: Fresh substrate fetch (§5); empty by default.
        label: Name used in the loop-bound error message.
        max_passes: Loud safety bound against a non-terminating loop.
        clock: Injectable timestamp source.
        log: Optional pre-built action log. None uses a fresh in-memory log
            (the skeleton default). The real run injects a log wired to the
            live JSONL sink (run-prep §7) and shared with the LLM emitters/
            arbiter so their `llm_call` provenance lands on the same stream.

    Returns:
        The RunResult with the final exit, pass count, ledger, and action log.

    Raises:
        LoopBoundExceeded: If the loop does not terminate within max_passes.
    """
    log = log if log is not None else ActionLog()
    store.save(Ledger(header=header))
    effective_fix_changes = fix_changes or {}

    pass_number = 0
    while True:
        pass_number += 1
        if pass_number > max_passes:
            raise LoopBoundExceeded(
                f"{label} did not terminate within {max_passes} passes"
            )

        # Fresh fetch — no agent inherits another's context.
        ledger = store.load()

        # §2: the frozen prior-pass snapshot state, taken before any current-pass
        # admission. This base is never handed to a consumer — _gather_then_admit
        # hands the plan and each reviewer its own deep copy of it (amended
        # 2026-07-02), so admission's mutations to `ledger` are never visible
        # through any consumer's snapshot, and no consumer shares an object.
        snapshot_state = copy.deepcopy(ledger)

        # §5: the runner is the fetch point — reviewers do not fetch for
        # themselves. Assembled fresh per pass from the header's document set.
        records = fetch_documents(list(header.set))
        substrate = fetch_substrate(list(header.set))

        # §3: gather all emissions, then admit in fixed order.
        agents_run, compromised = _gather_then_admit(
            ledger, snapshot_state, plan, pass_number, records, substrate, log
        )

        # Instrument-compromised guard (mechanical-gates §3): before any
        # arbiter/routing, fail loud if a scheduled reviewer parse-dropped and
        # admitted nothing — CONVERGED must never be reachable through a
        # fully-dropped reviewer. run_aborted is emitted by the run-path wrapper
        # (run_real) as the exception propagates.
        if compromised:
            store.save(ledger)
            raise InstrumentCompromisedError(
                f"{label} pass {pass_number}: reviewer(s) {compromised} produced "
                "parse-dropped emissions and admitted no findings — instrument "
                "compromised, refusing to route (would risk a false CONVERGED)"
            )

        # Arbiter — the only LLM judgment — classifies open/unclassified findings
        # of a defect severity only. POSITIVE findings (survived-attack credits)
        # are never classified (a decision-bearing POSITIVE is incoherent): they
        # stay open/unclassified, are never sent to the arbiter, and so can never
        # reach a decision-bearing halt payload (README §arbiter, amended
        # 2026-07-02).
        classified_any = False
        for finding in ledger.findings:
            if (
                finding.status == "open"
                and finding.classification == "unclassified"
                and finding.severity != "POSITIVE"
            ):
                result = arbiter.classify(finding, authorities, design_intent)
                finding.classification = result.classification
                finding.authority_locus = result.authority_locus
                classified_any = True
                log.emit(
                    "classified",
                    finding_id=finding.id,
                    classification=result.classification,
                    confidence=result.confidence,
                )
        if classified_any:
            agents_run.append("arbiter")

        # Snapshot at routing time (post-admission, post-arbiter, pre-author):
        # the identical value the router reads — one value, no drift.
        cbm = open_cbm(ledger)
        ledger.passes.append(
            PassRecord(
                pass_number=pass_number,
                open_cbm_count=cbm,
                agents_run=agents_run,
                timestamp=clock(),
            )
        )
        store.save(ledger)

        # Route (pure, mechanical).
        exit_ = route(ledger)

        if exit_.kind == "CONVERGED":
            log.emit("converged", pass_number=pass_number, open_cbm=cbm)
            return RunResult(exit_, pass_number, ledger, log)

        if exit_.kind == "HALT_DECISION":
            log.emit(
                "halt",
                reason=exit_.reason,
                pass_number=pass_number,
                payload=[f.id for f in exit_.payload],
            )
            # Dry mode: one proposed escalation per finding, unbundled. Bundling
            # multiple decisions into one escalation is prohibited.
            for finding in exit_.payload:
                log.emit(
                    "proposed_escalation",
                    finding_id=finding.id,
                    reason=exit_.reason,
                    ticket="RBT in t-bone-haff-sofia — proposed, not opened",
                )
            return RunResult(exit_, pass_number, ledger, log)

        # CONTINUE → back to the author.
        log.emit("continue", pass_number=pass_number, open_cbm=cbm)
        author_pass(ledger, pass_number, effective_fix_changes, log)
        store.save(ledger)


def run_scenario(
    scenario: Scenario,
    store: LedgerStore,
    max_passes: int = 50,
    clock: Callable[[], str] = _default_clock,
) -> RunResult:
    """Drive one canned dummy scenario to its router exit (the stub path).

    A thin wrapper over `run_loop` with a stub plan (antagonist + coherence
    every pass — §6). Behaviour is unchanged from the skeleton; the four dummy
    scenarios remain the regression harness (§9g).

    Args:
        scenario: The planted scenario (header, reviewer stubs, arbiter port,
            fix-change map).
        store: The file-backed ledger store.
        max_passes: Loud safety bound.
        clock: Injectable timestamp source.

    Returns:
        The RunResult.
    """
    return run_loop(
        header=scenario.header,
        plan=stub_plan(scenario.antagonist, scenario.coherence),
        arbiter=scenario.arbiter,
        store=store,
        fix_changes=scenario.fix_changes,
        authorities=scenario.authorities,
        design_intent=scenario.design_intent,
        label=scenario.id,
        max_passes=max_passes,
        clock=clock,
    )
