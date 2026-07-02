# Module: agent_loop.runner
# Purpose: The pass loop — build step 5's driver. Each pass it fetches the
#          ledger fresh, runs the reviewer stubs through the admission gate,
#          runs the arbiter on open/unclassified findings, snapshots the pass
#          record at routing time, and routes. On CONTINUE the author stub acts;
#          on CONVERGED/HALT the run returns. Dry mode throughout: resolutions
#          and escalations are proposed and logged, never applied/opened.
# Scope:   Orchestration only. All judgment about "done" is in gates.route (no
#          LLM). The only LLM judgment (the arbiter) is injected as a port.

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Callable

from agent_loop.admission import admit
from agent_loop.gates import RouterExit, open_cbm, route
from agent_loop.ledger import Ledger, LedgerStore, PassRecord
from agent_loop.log import ActionLog
from agent_loop.scenarios import Scenario
from agent_loop.stubs import author_pass


class LoopBoundExceeded(RuntimeError):
    """Raised when a run exceeds max_passes.

    A safety backstop, not a spec exit: a scenario that routes CONTINUE forever
    would otherwise spin. It fails loudly so it can never be mistaken for a real
    CONVERGED/HALT exit.
    """


@dataclass
class RunResult:
    """The outcome of a scenario run.

    Attributes:
        exit: The router exit that ended the run.
        passes_run: How many passes executed.
        ledger: The final ledger state.
        log: The structured action log (drops, classifications, proposed
            resolutions/escalations — the dry-mode evidence base).
    """

    exit: RouterExit
    passes_run: int
    ledger: Ledger
    log: ActionLog


def _default_clock() -> str:
    """Wall-clock ISO-8601 timestamp. Does not affect any gate outcome."""
    return datetime.now(timezone.utc).isoformat()


def run_scenario(
    scenario: Scenario,
    store: LedgerStore,
    max_passes: int = 50,
    clock: Callable[[], str] = _default_clock,
) -> RunResult:
    """Drive one dummy scenario to its router exit.

    Args:
        scenario: The planted scenario (header, reviewer stubs, arbiter port,
            fix-change map).
        store: The file-backed ledger store (fresh-fetched each pass).
        max_passes: Loud safety bound against a non-terminating loop.
        clock: Injectable timestamp source.

    Returns:
        The RunResult with the final exit, pass count, ledger, and action log.

    Raises:
        LoopBoundExceeded: If the loop does not terminate within max_passes.
    """
    log = ActionLog()
    store.save(Ledger(header=scenario.header))

    pass_number = 0
    while True:
        pass_number += 1
        if pass_number > max_passes:
            raise LoopBoundExceeded(
                f"scenario {scenario.id!r} did not terminate within "
                f"{max_passes} passes"
            )

        # Fresh fetch — no agent inherits another's context.
        ledger = store.load()
        agents_run: list[str] = []

        # Reviewers (canned). Both run every pass; the coherence stub reads the
        # doc-change state the author recorded in the prior pass. The canned
        # stubs do not read current-pass findings, so there is no cross-anchoring
        # to guard here. When the REAL hats are wired, each must judge against
        # the prior-pass ledger snapshot (fetched fresh, not this mutating
        # in-pass reference) — the no-cross-anchoring property is architectural.
        for name, reviewer in (
            ("antagonist-stub", scenario.antagonist),
            ("coherence-stub", scenario.coherence),
        ):
            agents_run.append(name)
            for emitted in reviewer(pass_number, ledger):
                admit(ledger, emitted, pass_number, log)

        # Arbiter — the only LLM judgment — classifies open/unclassified findings.
        classified_any = False
        for finding in ledger.findings:
            if finding.status == "open" and finding.classification == "unclassified":
                result = scenario.arbiter.classify(
                    finding, scenario.authorities, scenario.design_intent
                )
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
        author_pass(ledger, pass_number, scenario.fix_changes, log)
        store.save(ledger)
