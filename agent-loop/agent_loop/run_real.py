# Module: agent_loop.run_real
# Purpose: Run assembly and prep validation for the supervised first dry run
#          (run-prep.contract.md §8). Owns the six fail-loud prep gates (all
#          before any LLM call), a gates-only validation entry point (used at
#          prep with no LLM call), the full assembly (ledger home, real fetchers,
#          four API-backed reviewers, real arbiter, real plan), the run manifest,
#          and the live-log sink. Dry mode throughout; fix_changes empty;
#          max_passes 10 (attended).
# Scope:   Orchestration + gates. The real Anthropic transport is constructed
#          only on the launch path (build_real_transport); every function here is
#          driven by an injected transport so no test makes a real API call.

from __future__ import annotations

import json
import os
import subprocess
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Callable, Mapping

from agent_loop.fetchers import (
    DocumentResolutionError,
    DocumentSnapshotError,
    RepoDocumentFetcher,
    RunSubstrateFetcher,
    SubstrateError,
    sha256_text,
    validate_substrate_manifest,
    verify_document_snapshot,
)
from agent_loop.emissions import EmissionCapture
from agent_loop.ledger import DEFAULT_COUNTED_SEVERITIES, LedgerHeader, LedgerStore
from agent_loop.log import ActionLog, JsonlFileSink
from agent_loop.manifest import (
    finalize_manifest,
    per_site_token_totals,
    write_prep_manifest,
)
from agent_loop.real_hats import build_real_reviewer, load_system_prompt, real_hat_plan
from agent_loop.reviewers import (
    IDENTITY_COHERENCE,
    IDENTITY_EA,
    IDENTITY_LAA,
    IDENTITY_SA,
    ReviewerIdentity,
)
from agent_loop.runner import RunResult, run_loop
from agent_loop.transport import ApiArbiter, Transport, build_api_emitter

# The four reviewer prompts, keyed by the identity whose findings they stamp.
REVIEWER_PROMPTS: dict[ReviewerIdentity, str] = {
    IDENTITY_LAA: "antagonist-LAA.prompt.md",
    IDENTITY_SA: "antagonist-SA.prompt.md",
    IDENTITY_EA: "antagonist-EA.prompt.md",
    IDENTITY_COHERENCE: "coherence-sweep.prompt.md",
}
ARBITER_PROMPT = "arbiter-classifier.prompt.md"
# The five prompt files whose hashes the manifest records and gate 5 checks.
ALL_PROMPT_FILES: tuple[str, ...] = tuple(REVIEWER_PROMPTS.values()) + (ARBITER_PROMPT,)

# Run-one configuration (model/params live in config, never hardcoded in the
# transport module — run-prep §6). No sampling parameters: temperature/top_p/
# top_k are deprecated on Opus 4.7+ and 400 on non-default values (amended
# 2026-07-02); the request payload carries max_tokens only.
RUN_ONE_MODEL = "claude-opus-4-8"
RUN_ONE_MAX_TOKENS = 8192
RUN_ONE_MAX_PASSES = 10

# Prompt-set calibration generation recorded in the manifest alongside the
# re-pinned prompt hashes. Two ratified calibration events since gen-3's
# semantics-preserving arbiter reorder: gen-4 restated the severity/cap
# discipline in-place in all four reviewer prompts (a held check is
# POSITIVE-class, never re-labeled a defect to fit the volume cap); gen-5
# appended the arbiter locus-attribution line (no locus extended beyond its
# document's stated scope; an underivable locus classifies decision-bearing).
# The rationale cites by meaning: operational artifacts never carry ticket
# numbers — ticket linkage lives in tickets, carriers, and audits.
CALIBRATION = {
    "generation": 5,
    "rationale": (
        "gen-4: severity/cap discipline restated in-place in all four reviewer "
        "prompts — a held check is POSITIVE-class, never re-labeled a defect to "
        "fit the volume cap; gen-5: arbiter locus-attribution line appended — "
        "no locus extended beyond its document's stated scope, underivable "
        "locus classifies decision-bearing"
    ),
}


# --- gate reporting ----------------------------------------------------------


@dataclass(frozen=True)
class GateResult:
    """The outcome of one prep gate.

    `pending` marks a gate that could not be evaluated yet (no key for gate 6/7,
    or no probe configured in gates-only mode) — distinct from an outright
    failure, though both leave the report not-ok (a run cannot launch until every
    gate passes).
    """

    number: int
    name: str
    passed: bool
    detail: str
    pending: bool = False


@dataclass
class GateReport:
    """The collected prep-gate results."""

    results: list[GateResult] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        """True iff every gate passed."""
        return all(result.passed for result in self.results)

    def failures(self) -> list[GateResult]:
        """The gates that did not pass (including pending), in order."""
        return [result for result in self.results if not result.passed]


class PrepGateError(RuntimeError):
    """A prep gate failed; the run aborts before any LLM call."""

    def __init__(self, report: GateReport) -> None:
        """Carry the failing report for the caller to inspect/log."""
        self.report = report
        failed = "; ".join(f"gate {r.number} ({r.name}): {r.detail}" for r in report.failures())
        super().__init__(f"prep gates failed — {failed}")


# --- git helpers (subprocess by default; injectable for tests) ---------------


def _default_git_docs_status(sofia_root: Path) -> str:
    """Return `git status --porcelain docs` output for the repo (docs subtree)."""
    completed = subprocess.run(
        ["git", "-C", str(sofia_root), "status", "--porcelain", "docs"],
        capture_output=True,
        text=True,
        check=False,
    )
    return completed.stdout


def _default_git_head(sofia_root: Path) -> str:
    """Return `git rev-parse HEAD` for the repo."""
    completed = subprocess.run(
        ["git", "-C", str(sofia_root), "rev-parse", "HEAD"],
        capture_output=True,
        text=True,
        check=False,
    )
    return completed.stdout.strip()


# --- the six prep gates ------------------------------------------------------


def run_prep_gates(
    run_id: str,
    doc_ids: list[str],
    *,
    sofia_root: str | Path,
    runs_root: str | Path,
    prompt_dir: str | Path,
    create_missing_dir: bool = False,
    git_status: Callable[[Path], str] = _default_git_docs_status,
    env: Mapping[str, str] | None = None,
    probe: Callable[[], None] | None = None,
) -> GateReport:
    """Run the eight prep gates (run-prep §8), collecting every result.

    Makes no reviewer or arbiter call. Gate 7's one-token probe is the only
    prep-time API contact, and only when a `probe` is supplied AND gates 1-6 all
    pass; gates-only validation passes no probe, so gate 7 reports pending. With
    `create_missing_dir=False` (the gates-only default) there are no side effects;
    the full run passes `create_missing_dir=True` so gate 1 creates the prepared
    folder.

    Gate 1 (run-prep §8, ratified): `ledger.json` is the discriminator — refuse a
    used run (ledger present; a used run-id is immutable evidence, retries take a
    new run-id per run-supervision.protocol.md §4), pass a prepared folder
    (substrate present, no ledger), and create the folder if absent.

    Gate 6/7: `ANTHROPIC_API_KEY` presence is the fast fail ahead of the probe;
    without a key both report pending. Gate 7 sends one minimal message
    (`max_tokens: 1`) through the run's emitter configuration — converting
    transport-class misconfiguration (bad key, bad parameter shape) into a prep
    failure at the cost of one token.
    """
    resolved_env = env if env is not None else os.environ
    sofia_root = Path(sofia_root)
    run_dir = Path(runs_root) / run_id
    documents_root = run_dir / "documents"
    prompt_dir = Path(prompt_dir)
    results: list[GateResult] = []

    # Gate 1 — run folder not already executed; create the prepared folder.
    ledger_path = run_dir / "ledger.json"
    if ledger_path.exists():
        results.append(
            GateResult(1, "run-folder", False, f"run already executed: {ledger_path} exists")
        )
    else:
        if create_missing_dir:
            run_dir.mkdir(parents=True, exist_ok=True)
        results.append(GateResult(1, "run-folder", True, f"{run_dir} ready (not yet run)"))

    # Gate 2 — docs tree clean (the HEAD stamp is meaningless over a dirty tree).
    status = git_status(sofia_root)
    clean = status.strip() == ""
    results.append(
        GateResult(2, "docs-clean", clean, "clean" if clean else f"dirty docs tree: {status!r}")
    )

    # Gate 3 — every doc-id resolves to exactly one file WITHIN THE SNAPSHOT
    # (amended §2 / RBT-51 Item 3): resolution is the prep tool's act; the runner
    # resolves against `documents/`, never the working tree.
    fetcher = RepoDocumentFetcher(documents_root)
    unresolved: list[str] = []
    for doc_id in doc_ids:
        try:
            fetcher.resolve(doc_id)
        except DocumentResolutionError as exc:
            unresolved.append(str(exc))
    results.append(
        GateResult(3, "docs-resolve", not unresolved, "all resolved" if not unresolved else "; ".join(unresolved))
    )

    # Gate 4 — substrate populated and its manifest validates.
    substrate_root = run_dir / "substrate"
    try:
        validate_substrate_manifest(substrate_root)
        RunSubstrateFetcher(substrate_root)(doc_ids)
        results.append(GateResult(4, "substrate", True, "substrate valid"))
    except SubstrateError as exc:
        results.append(GateResult(4, "substrate", False, str(exc)))

    # Gate 5 — all five prompt files exist and yield a non-empty ## System.
    prompt_problems: list[str] = []
    for name in ALL_PROMPT_FILES:
        try:
            system_text = load_system_prompt(prompt_dir / name)
            if not system_text.strip():
                prompt_problems.append(f"{name}: empty ## System")
        except (FileNotFoundError, ValueError) as exc:
            prompt_problems.append(f"{name}: {exc}")
    results.append(
        GateResult(5, "prompts", not prompt_problems, "all present" if not prompt_problems else "; ".join(prompt_problems))
    )

    # Gate 6 — ANTHROPIC_API_KEY present in the environment (fast fail).
    has_key = bool(resolved_env.get("ANTHROPIC_API_KEY"))
    results.append(
        GateResult(
            6,
            "api-key",
            has_key,
            "present" if has_key else "ANTHROPIC_API_KEY not set",
            pending=not has_key,
        )
    )

    # Gate 7 — one-token probe through the run's emitter configuration. Only when
    # gates 1-6 all pass and a probe is supplied; else pending (gates-only, or an
    # earlier gate already fails fast — never spend a token on a doomed prep).
    gates_1_6_pass = all(result.passed for result in results)
    if not gates_1_6_pass:
        results.append(
            GateResult(7, "probe", False, "pending — gates 1-6 not all passing", pending=True)
        )
    elif probe is None:
        results.append(
            GateResult(7, "probe", False, "pending — no probe configured (gates-only)", pending=True)
        )
    else:
        try:
            probe()
            results.append(GateResult(7, "probe", True, "one-token probe succeeded"))
        except Exception as exc:  # noqa: BLE001 — any probe failure is a prep failure
            results.append(GateResult(7, "probe", False, f"probe failed: {exc}"))

    # Gate 8 — the frozen document snapshot verifies against its provenance
    # record (amended §8 gate 8 / RBT-51 Item 3): `documents/` is present,
    # non-empty, and every file's SHA-256 matches the prep-written manifest.
    # Absence or any mismatch aborts before the first reviewer call; the runner
    # never falls back to the working tree. Gate 2 keeps its prep-time role: the
    # snapshot was taken from a clean docs tree, so the HEAD SHA stamp is
    # meaningful for the snapshotted bytes.
    try:
        verify_document_snapshot(run_dir)
        results.append(GateResult(8, "doc-snapshot", True, "snapshot verified"))
    except DocumentSnapshotError as exc:
        results.append(GateResult(8, "doc-snapshot", False, str(exc)))

    return GateReport(results=results)


def validate_prep(
    run_id: str,
    doc_ids: list[str],
    *,
    sofia_root: str | Path,
    runs_root: str | Path,
    prompt_dir: str | Path,
    git_status: Callable[[Path], str] = _default_git_docs_status,
    env: Mapping[str, str] | None = None,
) -> GateReport:
    """Gates-only prep validation (run-prep §8) — no LLM call, no side effects.

    The Phase-3 entry point: validates an already-prepared run folder without
    creating anything or invoking any emitter.
    """
    return run_prep_gates(
        run_id,
        doc_ids,
        sofia_root=sofia_root,
        runs_root=runs_root,
        prompt_dir=prompt_dir,
        create_missing_dir=False,
        git_status=git_status,
        env=env,
    )


# --- full run assembly -------------------------------------------------------


def run_real(
    run_id: str,
    doc_ids: list[str],
    *,
    sofia_root: str | Path,
    runs_root: str | Path,
    prompt_dir: str | Path,
    transport: Transport,
    model: str = RUN_ONE_MODEL,
    max_tokens: int = RUN_ONE_MAX_TOKENS,
    max_passes: int = RUN_ONE_MAX_PASSES,
    git_status: Callable[[Path], str] = _default_git_docs_status,
    head_sha: str | None = None,
    created: str | None = None,
    now: Callable[[], float] = time.monotonic,
    sleeper: Callable[[float], None] = time.sleep,
    backoff_seconds: float = 30.0,
    env: Mapping[str, str] | None = None,
    coherence_addendum: str | None = None,
) -> RunResult:
    """Assemble and run the supervised dry run against an injected transport.

    Runs the prep gates fail-loud (gate 7's one-token probe is the only prep-time
    API contact, before any reviewer or arbiter call), then assembles the ledger
    home, real fetchers, four per-call-site API reviewers, the real arbiter, and
    the real plan; writes the prep manifest; streams the action log to
    `action-log.jsonl`; runs the loop (dry, fix_changes empty); and finalizes the
    manifest. On any run-path abort a `run_aborted` event is logged (and streamed)
    before the exception propagates, and the manifest is left unfinalized.

    Raises:
        PrepGateError: If any prep gate fails (no reviewer/arbiter call is made).
    """
    # Gate 7 probe: one minimal (max_tokens=1) call through the run's transport.
    def _probe() -> None:
        transport("probe", "probe", model, 1)

    report = run_prep_gates(
        run_id,
        doc_ids,
        sofia_root=sofia_root,
        runs_root=runs_root,
        prompt_dir=prompt_dir,
        create_missing_dir=True,
        git_status=git_status,
        env=env,
        probe=_probe,
    )
    if not report.ok:
        raise PrepGateError(report)

    sofia_root = Path(sofia_root)
    prompt_dir = Path(prompt_dir)
    run_dir = Path(runs_root) / run_id
    documents_root = run_dir / "documents"
    substrate_root = run_dir / "substrate"

    store = LedgerStore(run_dir / "ledger.json")
    # §2 as amended: the fetcher reads the run's frozen document snapshot each
    # pass — never the working tree (live-read removed, not gated).
    doc_fetcher = RepoDocumentFetcher(documents_root)
    substrate_fetcher = RunSubstrateFetcher(substrate_root)
    substrate = substrate_fetcher(doc_ids)  # arbiter's authorities/design-intent

    sink = JsonlFileSink(run_dir / "action-log.jsonl")
    log = ActionLog(sink=sink)
    capture = EmissionCapture(run_dir / "emissions")

    reviewers = {}
    for identity, prompt_name in REVIEWER_PROMPTS.items():
        emitter = build_api_emitter(
            site_label=identity.label,
            model=model,
            max_tokens=max_tokens,
            log=log,
            transport=transport,
            now=now,
            sleeper=sleeper,
            backoff_seconds=backoff_seconds,
            capture=capture,
        )
        reviewers[identity] = build_real_reviewer(
            identity, prompt_dir / prompt_name, emitter, capture, redraw=True,
            brief_addendum=(coherence_addendum if identity == IDENTITY_COHERENCE else None),
        )
    plan = real_hat_plan(
        reviewers[IDENTITY_LAA],
        reviewers[IDENTITY_SA],
        reviewers[IDENTITY_EA],
        reviewers[IDENTITY_COHERENCE],
    )
    arbiter = ApiArbiter(
        prompt_path=prompt_dir / ARBITER_PROMPT,
        transport=transport,
        log=log,
        model=model,
        max_tokens=max_tokens,
        now=now,
        sleeper=sleeper,
        backoff_seconds=backoff_seconds,
        capture=capture,
    )

    header = LedgerHeader(
        set=list(doc_ids),
        counted_severities=list(DEFAULT_COUNTED_SEVERITIES),
        plateau_N=3,
        mode="dry",
    )

    # §7/T6 as amended: the manifest records the frozen snapshot provenance —
    # doc-id → run-folder-relative snapshot path + content SHA-256 (what was
    # actually reviewed) — read from the prep-written provenance record, alongside
    # the top-level HEAD SHA.
    snapshot_provenance = json.loads(
        (documents_root / "manifest.json").read_text(encoding="utf-8")
    )
    resolved_docs = {
        entry["doc_id"]: {"snapshot_path": entry["snapshot_path"], "sha256": entry["sha256"]}
        for entry in snapshot_provenance["files"]
    }
    prompt_hashes = {
        name: sha256_text((prompt_dir / name).read_text(encoding="utf-8"))
        for name in ALL_PROMPT_FILES
    }
    manifest_path = run_dir / "manifest.json"
    write_prep_manifest(
        manifest_path,
        run_id=run_id,
        created=created if created is not None else datetime.now(timezone.utc).isoformat(),
        document_set=resolved_docs,
        head_sha=head_sha if head_sha is not None else _default_git_head(sofia_root),
        prompt_hashes=prompt_hashes,
        substrate_manifest_ref="substrate/manifest.json",
        model=model,
        parameters={"max_tokens": max_tokens},
        calibration=CALIBRATION,
    )

    wall_start = now()
    try:
        result = run_loop(
            header=header,
            plan=plan,
            arbiter=arbiter,
            store=store,
            fix_changes={},
            authorities=substrate.authorities,
            design_intent=substrate.design_intent,
            fetch_documents=doc_fetcher,
            fetch_substrate=substrate_fetcher,
            label=run_id,
            max_passes=max_passes,
            log=log,
        )
    except Exception as exc:
        # §7: mark the terminal abort on the live stream before it propagates,
        # so the tail distinguishes an aborted run from one sitting in backoff.
        # The manifest is deliberately left unfinalized.
        log.emit("run_aborted", reason=str(exc), error_type=type(exc).__name__)
        raise
    finally:
        sink.close()

    exit_str = result.exit.kind + (f":{result.exit.reason}" if result.exit.reason else "")
    finalize_manifest(
        manifest_path,
        router_exit=exit_str,
        passes_run=result.passes_run,
        per_site_tokens=per_site_token_totals(log),
        wall_clock_seconds=now() - wall_start,
    )
    return result


def main() -> None:  # pragma: no cover
    """CLI launch path (attended run). Constructs the real Anthropic transport."""
    import argparse

    from agent_loop.transport import build_real_transport

    parser = argparse.ArgumentParser(description="Run the supervised design-review dry run.")
    parser.add_argument("run_id")
    parser.add_argument("doc_ids", nargs="+", help="e.g. ADR-001 ADR-002 DDR-001 DDR-002")
    parser.add_argument("--sofia-root", default=str(Path(__file__).resolve().parents[2]))
    parser.add_argument(
        "--coherence-addendum-file", default=None,
        help="file whose text is appended to the coherence hat's brief (RBT-54 R-C seam list)",
    )
    args = parser.parse_args()

    agent_loop_root = Path(args.sofia_root) / "agent-loop"
    coherence_addendum = (
        Path(args.coherence_addendum_file).read_text(encoding="utf-8")
        if args.coherence_addendum_file
        else None
    )
    result = run_real(
        args.run_id,
        args.doc_ids,
        sofia_root=args.sofia_root,
        runs_root=agent_loop_root / "runs",
        prompt_dir=agent_loop_root / "design",
        transport=build_real_transport(),
        coherence_addendum=coherence_addendum,
    )
    print(f"{args.run_id}: {result.exit.kind} in {result.passes_run} pass(es)")


if __name__ == "__main__":  # pragma: no cover
    main()
