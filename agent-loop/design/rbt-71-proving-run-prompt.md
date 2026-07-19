# Claude Code proving-run prompt — run-031 (RBT-71 de-pollution proof)

You are launching the bounded live proving run for the RBT-71 fixes. Preconditions: the RBT-71 implementation is committed (both repos) and the full suite is green. Fresh-read `run-supervision.protocol.md` (including the new §2 spend-discipline gates and §5 checks), `run-prep.contract.md`, and `rbt-71-decision-surface.spec.md` §6 before anything else — do not run from memory or from this prompt's paraphrases.

## §2 spend-discipline checklist (answer in the pre-registration, explicitly)

1. **Units before dollars** — the mechanics are already unit-proven (S-SAT-1…6, R-1/R-2). This run answers only the genuinely emergent questions: does the live author use `close_satisfied` correctly (right cases, verifying evidence) rather than over- or under-using it; does the gen-12 rule change what reviewers ground their claims in; does the halt-time decision surface land ≈ born + genuinely-underdetermined.
2. **Bound to the minimum passes** — `max_passes = 3`. Run-030 showed the phantom mechanism fully expressed by pass 2–3; three passes suffice to observe satisfied-close behavior across a re-review cycle, and the bound forces a cheap disposition.
3. **Match the target to the question** — target ADR-008, deliberately: the de-pollution claim is about the document that polluted. Decision-density is the point here, not a cost accident.
4. **Mine captured fixtures first** — done; this entire ticket's analysis ran off run-030 at $0. The live run is the last step, not the first.

## Run prep (run-prep.contract.md governs; highlights)

- `run_id: run-031-adr-008-rbt71`.
- Target: fresh snapshot from the pristine sandbox canonical source (`agent-loop/sandbox/adr-008/...`) — hash-verify byte-identical to pin `24461d3f` (same pristine input as run-029/030, for comparability). Record provenance in the documents manifest.
- Substrate: copied verbatim from run-030's frozen `substrate/`, hash-verified per file.
- Manifest: record all six prompt hashes fresh; `calibration.generation: 12` with the gen-12 rationale (rule 9); note the changed variables honestly — **two intended variables vs run-030**: the author change (prompt + `close_satisfied` path) and the gen-12 reviewer rule. The audit attributes by stream (refusal/closure stream vs finding stream).
- Model, parameters, transport: as run-030 (Opus, max_tokens 8192), unless the run-supervision protocol says otherwise. Expected cost at 3 passes: roughly $18–20; abort semantics unchanged.

## During the run

Supervise per `run-supervision.protocol.md`. Do not intervene in-loop; abort conditions are the protocol's own (storms, instrument compromise, transport).

## Capture and report (report-and-STOP; no audit authoring, no commit)

Deliver the raw results only — the cold audit is authored on claude.ai, not by you:

- Run folder complete: action-log, ledger, emissions, manifests, per-pass documents state.
- A RAW-RESULT summary: per-pass counts of `author_edit` / `author_satisfied` / `author_satisfied_evidence_fail` / `author_refused`; the `classified` split; `open_cbm` trajectory; open decision-bearing at halt; the router disposition; total cost from the llm_call stream.
- Do NOT score success — that scoring (refusal-stream split, halt surface ≈ born + genuine, hand-validated satisfied-close sample against reconstructed states) is the claude.ai audit's job against the spec §6 criteria.

STOP after the report. The audit, the spec's ACCEPTED promotion, and all git transactions are upstream of you.
