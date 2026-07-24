# run-033 — RAW-RESULT (report-and-STOP; unscored)

Raw capture only. No success scoring, no docket grouping, no ticket/commit — the cold
audit and the convergence ruling are authored on claude.ai (protocol §5); git is Tad's.

| Field | Value |
|---|---|
| **Run** | run-033-ddr-003-rbt14-v020 |
| **Target** | DDR-003 — Feedback Loop Governance, PROPOSED v0.2.0 |
| **Pre-run HEAD** | ca410614a30919e39c25807550ccbb5e5499de73 |
| **Calibration** | gen-12, all six prompts (zero intended instrument variables vs run-032; only the document (v0.2.0) and the substrate addition (run-032-docket-rulings) changed) |
| **Router disposition** | **run_aborted — `LoopBoundExceeded`** ("did not terminate within 3 passes"). **NOT CONVERGED, NOT oscillation-halt.** Manifest left **unfinalized** by design (§7 abort path). |
| **Passes run** | 3 (bound reached; router asked to continue at pass 3) |
| **Wall clock** | ~17.4 min (Σ llm_call latency; manifest wall_clock not written) |
| **Operational health** | 0 llm_retry · 0 parse_dropped · 0 reopened · 1 author_output_preamble_stripped (benign) |

## Primary question — answered

**The first-live-CONVERGED did not occur.** DDR-003 v0.2.0, with its ruled decision
surface and the rulings in substrate, did **not** converge within the 3-pass bound.
`open_cbm` rose monotonically **17 → 27 → 39** with **no oscillation** (reopen count 0
throughout — the gate that halted run-032 never engaged). Reviewers surfaced counted
findings faster than the author resolved them; the loud loop-bound backstop caught it.
Raw evidence only — whether the standing open decision-bearing set is genuine-new vs
re-escalation-against-ruling is the cold audit's call (§5), not scored here.

## Per-pass

| Pass | Admitted (M/C/P) | classified (res/dec) | edit | satisfied | sat_evidence_fail | refused | unresolved | reopened | open_cbm |
|---|---|---|---|---|---|---|---|---|---|
| 1 | 29 (17/4/8) | 21 (16/5) | 0 | 0 | 0 | 0 | 0 | 0 | 17 |
| 2 | 30 (18/5/7) | 23 (11/12) | 2 | 8 | 0 | 5 | 1 | 0 | 27 |
| 3 | 21 (13/5/3) | 18 (8/10) | 1 | 0 | 1 | 8 | 1 | 0 | 39 → **bound** |
| (author residue, post-pass-3 fix cycle) | — | — | 0 | 1 | 0 | 7 | 0 | 0 | — |

**open_cbm trajectory:** 17 → 27 → 39 → LoopBoundExceeded (diverging; no plateau, no oscillation).

## Classified split (all passes)

- classification: **35 resolvable / 27 decision-bearing** (62 classification events)
- confidence: **55 high / 7 medium / 0 low** (arbiter conservative-bias intact)

## Author dispositions (cumulative)

- author_edit: 3
- author_satisfied: 9  (vs run-032's 5 — more findings closed by evidence-anchored satisfaction with the rulings in substrate)
- author_satisfied_evidence_fail: 1
- author_refused: 20
- author_unresolved: 2  (both cause=`target` — cross-doc findings naming DDR-002, not in the single-doc set)
- reopened: 0  (no edit-then-reopen churn this run)
- author_output_preamble_stripped: 1

## Ledger at abort (unique findings, deduped)

- **80 unique findings** — severity: 48 MATERIAL / 14 COSMETIC / 18 POSITIVE
- status: 68 open / 12 closed
- **open decision-bearing at abort: 50**  (raw, ungrouped; docket coalescing is the audit's job. No `proposed_escalation` fired — escalations attach to a HALT_DECISION, not to a loop-bound abort, so these stand open in the ledger unescalated.)

## Per-hat finding volumes (ledger, by source)

| Hat | Total | MAT | COS | POS |
|---|---|---|---|---|
| coherence | 23 | 14 | 4 | 5 |
| antagonist-LAA | 21 | 11 | 6 | 4 |
| antagonist-SA | 21 | 13 | 3 | 5 |
| antagonist-EA | 15 | 10 | 1 | 4 |

## Cost — four line items (ratified convention; derived from llm_call stream, manifest unfinalized)

| Site | calls | input | output | cache_creation | cache_read | cc_1h_bucket |
|---|---|---|---|---|---|---|
| antagonist-LAA | 3 | 107,512 | 11,294 | 160,001 | 328,744 | 160,001 |
| antagonist-SA | 3 | 107,512 | 12,069 | 160,001 | 328,804 | 160,001 |
| antagonist-EA | 3 | 107,512 | 9,667 | 160,001 | 328,624 | 160,001 |
| coherence | 3 | 107,512 | 13,001 | 160,001 | 328,744 | 160,001 |
| arbiter | 62 | 41,373 | 10,182 | 160,015 | 9,843,747 | 160,015 |
| author | 33 | 940,424 | 8,429 | 57,229 | 500,248 | 57,229 |
| **TOTAL** | **107** | **1,411,845** | **64,642** | **857,248** | **11,658,911** | **857,248** |

- All cache_creation landed in the **1-hour bucket** (857,248 = cc_1h) — RBT-69 §7a caching lever live; hats read from cache on passes 2+.
- **Four-line-item total @ `claude-opus-4-8` list prices ($5 / $25 / $10 / $0.50 per MTok): $23.08**
  — input $7.06 · output $1.62 · cache-write(1h) $8.57 · cache-read $5.83.
- **Same tokens @ legacy Opus rates ($15 / $75 / $30 / $1.50): $69.23** — this is the figure the run-033 prompt (≈$50–75) and the docket ("run-032 ≈$69.7") assume. **The convention (all four line items) is honored either way; the 3× gap is purely the per-token rate.** `claude-opus-4-8` lists at $5/$25 (claude-api skill, authoritative, cached 2026-06-24), so the true four-line-item total is **$23.08**, not ~$69. Flagged for the cold audit to reconcile the cost-architecture workstream's baseline.

## Run folder

`ledger.json` · `action-log.jsonl` (319 events) · `manifest.json` (**unfinalized** — abort path) · `substrate/` (9 authorities + 4 design-intent incl. run-032-docket-rulings) · `documents/` · `emissions/` (107) · `PRE-REGISTRATION.md` · this file. No `audit.md` (cold audit is upstream).
