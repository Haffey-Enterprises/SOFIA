# run-032 — RAW-RESULT (report-and-STOP; unscored)

Raw capture only. No success scoring, no docket grouping, no ticket/commit — those
are the claude.ai cold audit's job (protocol §5) and Tad's git.

| Field | Value |
|---|---|
| **Run** | run-032-ddr-003-rbt14 |
| **Target** | DDR-003 — Feedback Loop Governance, PROPOSED v0.1.0 |
| **Pre-run HEAD** | e3d2bcd1343a004dfd7393e72d7d7ea45252e1a6 |
| **Calibration** | gen-12, all six prompts (zero intended instrument variables vs run-031) |
| **Router disposition** | **HALT_DECISION:oscillation** at pass 3 (natural halt; not the max_passes=4 bound) |
| **Passes run** | 3 |
| **Wall clock** | 984 s (16.4 min) |
| **Operational health** | 0 llm_retry · 0 parse_dropped · 0 anchor_fail · 4 author_output_preamble_stripped (benign salvage) |

## Per-pass

| Pass | Admitted (MAT/COS/POS) | classified (res/dec) | edit | satisfied | sat_evidence_fail | refused | unresolved | reopened | terminal · open_cbm |
|---|---|---|---|---|---|---|---|---|---|
| 1 | 28 (15/5/8) | 20 (14/6) | 0 | 0 | 0 | 0 | 0 | 0 | continue · 15 |
| 2 | 31 (18/9/4) | 27 (18/9) | 2 | 2 | 1 | 9 | 0 | 0 | continue · 29 |
| 3 | 18 (11/3/4) | 16 (13/3) | 3 | 3 | 0 | 10 | 2 | 2 | **halt:oscillation** |

**open_cbm trajectory:** 15 → 29 → halt (diverging, not converging).

## Classified split (all passes, from action-log)

- classification: **45 resolvable / 18 decision-bearing** (63 classification events across passes)
- confidence: **52 high / 11 medium / 0 low**

## Author dispositions (cumulative)

- author_edit: 5
- author_satisfied: 5
- author_satisfied_evidence_fail: 1
- author_refused: 19
- author_unresolved: 2  (both cause=`target` — cross-doc findings naming DDR-004/SDD-001 and DDR-001, not in the single-doc set)
- reopened: 2  (recurrence_count 1 each — the edit-then-reopen trust signal, §9g)
- author_output_preamble_stripped: 4  (gen-11 salvage seam)

## Halt-state ledger (unique findings, deduped)

- **77 unique findings** — severity: 44 MATERIAL / 17 COSMETIC / 16 POSITIVE
- status: 69 open / 8 closed
- classification (ledger-final): 40 decision-bearing / 21 resolvable / 16 unclassified (= POSITIVE, not arbiter-routed)
- **open decision-bearing at halt: 40**  (raw count — docket NOT grouped; coalescing is the audit's job per §5 / RBT-71 Piece B)

### Oscillation-halt payload (the 2 findings that tripped the gate)
- `796e0e3670293968` — src=antagonist-SA, MATERIAL, classified resolvable, recur=1, raised pass 2; locus "§8 conformance item 1 — DDR-001 conformance check 4 … mechanized"; target [DDR-003]
- `1450d89da4d67735` — src=coherence, COSMETIC, classified resolvable, recur=1, raised pass 2; locus "Cross-References — DDR-002 invariant list vs body"; target [DDR-003]

Both surfaced as dry-mode `proposed_escalation` (proposed, not opened).

## Per-hat finding volumes (ledger, by source)

| Hat | Total | MAT | COS | POS |
|---|---|---|---|---|
| antagonist-LAA | 21 | 14 | 5 | 2 |
| antagonist-SA | 23 | 12 | 5 | 6 |
| coherence | 22 | 11 | 5 | 6 |
| antagonist-EA | 11 | 7 | 2 | 2 |

## Cost (from llm_call stream; manifest per_site_tokens)

| Site | calls | input | output | cache_creation | cache_read | cc_1h_bucket |
|---|---|---|---|---|---|---|
| antagonist-LAA | 3 | 97,080 | 10,044 | 160,969 | 321,938 | 160,969 |
| antagonist-SA | 3 | 97,080 | 10,129 | 160,989 | 321,978 | 160,989 |
| antagonist-EA | 3 | 97,080 | 9,479 | 160,929 | 321,858 | 160,929 |
| coherence | 3 | 97,080 | 12,404 | 160,969 | 321,938 | 160,969 |
| arbiter | 63 | 37,567 | 10,698 | 159,405 | 9,883,110 | 159,405 |
| author | 30 | 991,622 | 7,826 | 81,206 | 388,289 | 81,206 |
| **TOTAL** | **105** | **1,417,509** | **60,580** | **884,467** | **11,559,111** | **884,467** |

- **All cache_creation landed in the 1-hour bucket** (884,467 cc = 884,467 cc_1h) — RBT-69 §7a caching lever confirmed live; hats showed `cache_read > 0` on passes 2+ (C3 acceptance satisfied vs run-028's ≈0).
- **Estimated cost: ~$23.23** at Opus 4.8 rates (input $5 / output $25 / 1h-cache-write $10 / cache-read $0.50 per MTok) — under the pre-registered $30–50 envelope. Breakdown: input $7.09 · output $1.51 · cache-write(1h) $8.84 · cache-read $5.78.

## Run folder (complete)

`ledger.json` · `action-log.jsonl` · `manifest.json` (finalized) · `substrate/` · `documents/` (per-pass end state) · `emissions/` (105) · `PRE-REGISTRATION.md` · this file.
