# Claude Code run prompt — run-033 (DDR-003 confirming review of v0.2.0)

You are launching the **operator-authorized confirming review** of **DDR-003 v0.2.0** (RBT-14): run-032's docket has been ruled (all nine decisions, ratified per item 2026-07-19), the rulings are realized in v0.2.0, and the rulings document is in this run's substrate. Fresh-read `run-supervision.protocol.md`, `run-prep.contract.md`, the DDR-003 deliberation record, and `agent-loop/deliberation/ddr-003-feedback-loop-governance/run-032-docket-rulings.md` before anything else.

**Preconditions (Tad's git transaction, committed before launch):** (a) `docs/ddr/DDR-003-feedback-loop-governance.md` at v0.2.0; (b) `agent-loop/deliberation/ddr-003-feedback-loop-governance/run-032-docket-rulings.md`; (c) the finalized run-032 folder including `audit.md`; (d) this prompt. Record the pre-run HEAD in the manifest; committed criteria + prompt = the pre-registration carrier. If any is uncommitted, stop and report.

## §2 spend-discipline checklist (answer in the pre-registration, explicitly)

1. **Units before dollars** — this run answers the one question no suite or captured run can: **does the loop reach a clean verdict on a document whose escalated decisions have been ruled and whose rulings are in substrate** — the first-live-CONVERGED question run-032 could not reach, now under its designed conditions (operator rulings available to the arbiter as authority). Secondary: does the run-032 finding population resolve against the rulings rather than re-escalate (the docket-rulings file's resolvable-against-ruling contract, live).
2. **Bound to the minimum passes** — `max_passes = 3`: pass 1 reviews the amended record, pass 2 lets the author work any residue with a re-review, pass 3 confirms. The expected outcomes are CONVERGED or a small honest docket; either is a disposition.
3. **Match the target to the question** — v0.2.0 is the question: a converge-believed record with its decision surface ruled. This is the loop's designed operating point, never yet observed.
4. **Mine captured fixtures first** — run-032's folder answered everything it could (the docket, the audit, the instrument findings). Whether the *ruled* state converges is not in any captured run.

**Cost envelope — corrected arithmetic (run-032 instrument finding; this is binding):** compute and report cost from **all four usage line items** — uncached input, output, cache-write (1h premium), cache-read — at the model's list prices. Run-032's true cost was ≈$69.7 at 3 passes on this substrate shape (the ≈$23 live figure omitted cache economics). Expect **≈$50–75** for this run; acknowledge before pass 1, and the §3e cost-runaway watch tracks the four-line-item total, not the uncached subset.

## Run prep (run-prep.contract.md governs)

- `run_id: run-033-ddr-003-rbt14-v020`.
- **Documents:** header set `["DDR-003"]`; snapshot `docs/ddr/DDR-003-feedback-loop-governance.md` (v0.2.0) from the clean tree at the pre-run HEAD; gates 1–8 as always.
- **Substrate (fresh assembly, hash-pinned; run-032's recipe + one addition):**
  - `authorities/`: unchanged recipe — ADR-001 · ADR-002 · ADR-008 · DDR-001 · DDR-002 · DDR-004 · SDD-001 (from `docs/` at the pre-run HEAD) · `ddr-template.md` + `author-decision-record` SKILL.md (bedrock checkout).
  - `design-intent/`: the DDR-003 deliberation record · **`run-032-docket-rulings.md` (NEW — the ratified rulings; reviewers and arbiter read these as authoritative design intent)** · the triage-001 record · `sofia-vision.md`.
- **Prompts:** gen-12, all six, hashes recorded; `calibration.generation: 12`. Zero instrument variables vs run-032 — the only intended variables are the document (v0.2.0) and the substrate addition (the rulings), which is the experiment.
- **Author: sandbox-apply dry mode per protocol §9, unchanged.** Trust ramp not advanced.
- Model, parameters, transport: as run-032.

## During the run

Supervise per protocol §3/§9; no in-loop intervention; abort only on the protocol's own triggers, with the cost watch on the corrected four-line-item total.

## Capture and report (report-and-STOP; no audit authoring, no commit)

Run folder complete (all standard artifacts) + a RAW-RESULT summary: per-pass counts of author actions and classifications with confidence split; `open_cbm` trajectory; **the router disposition — if CONVERGED, say so plainly; it would be the loop's first**; open decision-bearing at halt (raw, ungrouped); per-hat volumes; cost as the four line items and their total. Do not score, group, write tickets, or commit — the cold audit and the convergence ruling are authored on claude.ai; all git transactions are Tad's.

STOP after the report.
