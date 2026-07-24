# Claude Code run prompt — run-032 (DDR-003 first real engagement)

You are launching the design-review-loop's **first real engagement**: a bounded live review of **DDR-003 — Feedback Loop Governance, PROPOSED v0.1.0** (RBT-14). This is production use with audit watches, not a fixture experiment. Fresh-read `run-supervision.protocol.md` (including §2 spend-discipline gates and the §5 watches), `run-prep.contract.md`, and the DDR-003 deliberation record before anything else — do not run from memory or from this prompt's paraphrases.

**Preconditions (Tad's git transaction, already merged to the working branch before you start):** the pre-registration commit containing (a) `docs/ddr/DDR-003-feedback-loop-governance.md` (PROPOSED v0.1.0), (b) `agent-loop/deliberation/ddr-003-feedback-loop-governance/record.md` (the ratified Phase-2 deliberation record), and (c) this prompt. Committed-before-launch criteria + prompt are the lawful pre-registration carrier (protocol §2). Record the pre-run HEAD SHA in the manifest. If any of the three is uncommitted, stop and report — do not launch.

## §2 spend-discipline checklist (answer in the pre-registration, explicitly)

1. **Units before dollars** — the loop's mechanics are unit-proven (S-/T-suites; S-SAT-1…6, R-1/R-2) and the instrument phase closed at run-031. This run answers only what no suite or captured fixture can: (a) **fresh-document behavior** — finding volume, quality, and hat balance on a never-reviewed record; (b) **a real decision docket** — whether escalations are genuinely underdetermined decisions rather than re-litigations of ratified intent (the deliberation record is in substrate; reviewers and arbiter can resolve against it); (c) **a first live natural CONVERGED**, now mechanically reachable — hoped for, never forced.
2. **Bound to the minimum passes** — `max_passes = 4`. A fresh document needs two full review-fix-review cycles plus a confirming pass to reach a natural CONVERGED; 4 is the minimum that can observe that outcome, and the bound forces a cheap honest disposition if it halts instead. Not a high ceiling.
3. **Match the target to the question** — DDR-003 is the question: the loop's remaining unknowns are only answerable by real work, and this record is the real work. It is governance-dense but freshly authored and self-reviewed against the same substrate the loop will hold it to — a plausible convergence candidate, unlike the decision-dense stale fixtures.
4. **Mine captured fixtures first** — done: run-030/031 taught everything the captured folders could (phantom taxonomy, satisfied-close behavior, oscillation). No captured run contains a fresh real document; this question spends or goes unanswered.

**Cost envelope (estimate, not measurement):** substrate is roughly 2× run-031's (full canon set), with per-actor 1-hour prompt caching live; at 3–4 passes expect roughly **$30–50**. Acknowledge before pass 1; abort on cost runaway per protocol §3e.

## Run prep (run-prep.contract.md governs; this run's recipe)

- `run_id: run-032-ddr-003-rbt14`.
- **Documents:** header set = `["DDR-003"]`; snapshot `docs/ddr/DDR-003-feedback-loop-governance.md` from the clean working tree at the pre-run HEAD (gate 2: `docs/` clean; gate 8: hash-verified at launch). Single-document set — the coherence hat reviews doc-vs-substrate.
- **Substrate (NEW recipe for this target — do not reuse any prior run's frozen substrate; assemble fresh, hash-pinned per §3):**
  - `authorities/`: `ADR-001-reasoning-architecture.md` · `ADR-002-graph-system-of-record.md` · `ADR-008-ground-truth-mutation-governance.md` · `DDR-001-data-architecture.md` · `DDR-002-graph-schema.md` · `DDR-004-inherited-confidence-derivation.md` · `SDD-001-knowledge-service.md` (all from `docs/` at the pre-run HEAD) · `ddr-template.md` + `author-decision-record` SKILL.md (from the bedrock checkout).
  - `design-intent/`: `agent-loop/deliberation/ddr-003-feedback-loop-governance/record.md` (the ratified rulings — authoritative design intent for this review) · `agent-loop/triage/triage-001-distilled-set/record.md` (charter: Appendices A/C) · `sofia-vision.md` (as in prior runs).
  - Manifest records origin + SHA-256 per file (§3); empty substrate is a prep failure.
- **Prompts:** gen-12, all six, hashes recorded fresh; `calibration.generation: 12`. No prompt changes for this run — zero intended instrument variables vs run-031; anything observed is document-driven, which is the point.
- **Author: sandbox-apply dry mode per `run-supervision.protocol.md` §9, unchanged.** Edits land in `runs/run-032-ddr-003-rbt14/documents/` and nowhere else; no canonical write, no ticket write, no network write. The trust ramp holds — run-031's 1 reopen / 9 edits is not "boring," so canonical write-trust is not advanced this run.
- Model, parameters, transport: as run-031 (Opus, max_tokens 8192) unless the protocol says otherwise.

## During the run

Supervise per protocol §3 + the author streams (§9f/g). Do not intervene in-loop. Abort only on the protocol's own triggers (parse-drop storm, volume swamp — note the fresh-document guideline of >~50 admitted pass-1 findings, cost runaway, mechanical misbehavior, anchor-fail storm).

## Capture and report (report-and-STOP; no audit authoring, no commit)

Deliver raw results only — the cold audit is authored on claude.ai against protocol §5 (including the edit-region-overlap watch, the RELIT-class recurrence watch, and the interpretive-satisfied-close-at-medium-confidence watch; those are audit acts, not yours):

- Run folder complete: `action-log.jsonl`, `ledger.json`, `emissions/`, `manifest.json` (finalized), per-pass documents state, `substrate/`.
- A RAW-RESULT summary: per-pass counts of `author_edit` / `author_satisfied` / `author_satisfied_evidence_fail` / `author_refused`; the `classified` split with confidence distribution; `open_cbm` trajectory; open decision-bearing at halt or the CONVERGED stamp; the router disposition; per-hat finding volumes; total cost from the `llm_call` stream with the cache-read/creation split.
- Do NOT score success, do NOT group the docket, do NOT touch RBT-14 or any ticket, do NOT commit. The audit, the docket coalescing, the convergence ruling, and all git transactions are upstream of you.

STOP after the report.
