# Claude Code implementation prompt — RBT-71 decision-surface fixes

You are the execution leg. The design is ratified and specced: `rbt-71-decision-surface.spec.md` (PROPOSED v0.1.0, six items ratified per item by Tad 2026-07-19). Implement it exactly; where the spec and this prompt diverge, the spec wins; where implementation reveals a genuine gap, report and STOP — do not design.

**Fresh-fetch guard.** Re-read from disk before touching anything: the spec; `agent_loop/author.py`; `design/author.prompt.md`; the four reviewer prompts; `design/ledger-schema.md`; `design/mechanical-gates.md` (you will NOT change it — verify that stays true); `run-supervision.protocol.md`; the `design-review-loop` SKILL (bedrock). Do not trust memory or this prompt's paraphrases. Verify each edit target's stated FROM state against the actual file before editing; on any mismatch, report and STOP.

**Do not commit. Git transactions are Tad's.** Working-tree changes + a change report are your deliverable.

## Changes

1. **`agent_loop/author.py` — the satisfied-close path.**
   - `AuthorSatisfied` frozen dataclass: `finding_id`, `evidence_present: str | None`, `evidence_absent: str | None`, `authority_satisfied`, `rationale`, `confidence`. Construction invariants: at least one evidence field non-null and non-empty; `confidence in ("high","medium")`; `authority_satisfied` non-empty. (Mirror `AuthorEdit`'s invariant style.)
   - Parse seam: accept `"action": "close_satisfied"` in `_parse_author_output`; extend `_diagnose_author_defect` and `_author_repair_suffix`'s contract restatement accordingly. Malformed → None → existing retry/escalate path, unchanged.
   - Apply seam: new `_apply_satisfied` — verify `evidence_present` occurs ≥ 1 time verbatim in the current target document text and/or `evidence_absent` occurs 0 times (both supplied → both must hold). On verify: `status="closed"`, `pass_closed`, `resolution_note = "satisfied: already conforms to <authority_satisfied>"`, emit `author_satisfied` (finding_id, evidence kind(s), authority_satisfied, confidence). On fail: emit `author_satisfied_evidence_fail` (finding_id, which check failed, match counts) and `_escalate` — never close. No doc write, no `DocChange`.
   - Storm accounting: a satisfied-close counts as productive (like an edit) for the anchor/parse storm guards' "nothing applied" conjunction — a pass of valid satisfied-closes is not a storm.
   - Touch nothing in `_escalate`, the router, or gates. `open_cbm` semantics must be provably unchanged (S-SAT-6).

2. **`design/author.prompt.md`** — add the third action schema (spec §1 verbatim), the quotable-evidence hard rule, and the bias extension (fabricated fix > fabricated satisfaction > needless refusal; torn between close and refuse → refuse). Keep the Output-discipline block's "exactly one of the two objects" language in sync ("one of the three").

3. **Reviewer prompts (×4)** — append Contract rule 9 exactly as spec §3 states, identically in all four files (the Contract block is byte-identical across them — verify it still is after the edit, e.g. by diffing the block). This is prompt **generation 12**; record the generation rationale where the calibration record lives (manifest `calibration` at next run-prep; note the known gen-stamp gap task).

4. **`design/ledger-schema.md`** — document the satisfied `resolution_note` variant and the two new action-log events. No schema field changes.

5. **`run-supervision.protocol.md`** — (a) §2: insert the spend-discipline block from `run-supervision-s2-amendment.md` verbatim, positioned before the cost-envelope item; (b) §5: add the cross-pass edit-region-overlap audit check (two edits whose anchor regions intersect in the document across passes, computed from captured emissions); (c) §5: add the docket-discipline surfacing line (decision set is presented grouped by distinct underlying decision; ratification per decision; groups splittable on operator demand).

6. **`design-review-loop` SKILL (bedrock repo)** — triage section: the docket-coalescing presentation shape per spec §2 (propose grouping into distinct underlying decisions; one ask per decision; member finding-ids listed; body-evidence per group; splittable).

## Tests (write these; they are the acceptance gate)

S-suite additions, named in the spec §6 — implement all: **S-SAT-1** (verifying `evidence_present` closes; absent from halt payload), **S-SAT-2** (non-occurring `evidence_present` → escalate, stays open), **S-SAT-3** (occurring `evidence_absent` → escalate), **S-SAT-4** (re-raise of a satisfied-closed identity → `recurrence_count` increments → `HALT_DECISION:oscillation`), **S-SAT-5** (low-confidence / evidence-less construction fails → escalate path, nothing applied), **S-SAT-6** (`open_cbm`/plateau arithmetic identical whether a finding closed by edit or by satisfied-close).

Replay fixtures from `runs/run-030-adr-008-rbt69/` (captured, $0): **R-1** — all 46 captured refusal emissions still parse to `AuthorRefusal` and escalate (backward compatibility). **R-2** — replay the run-030 ledger with the 19 phantom-class findings (ids per category in `runs/run-030-adr-008-rbt69/rbt-71-categorization.json` — every id whose category is not GENUINE) closed via fixture `close_satisfied` outcomes and assert the open decision-bearing set at the halt boundary is **33**, not 52.

Run the full existing suite; zero regressions.

## Report and STOP

Deliver: per-file diffs summary; test run output; explicit confirmation `mechanical-gates.md` is untouched and the reviewer Contract blocks are still byte-identical across the four prompts; any gap found (report, do not resolve). The live proving run (max_passes=3, ADR-008) is a separate, operator-authorized step — do not launch it.
