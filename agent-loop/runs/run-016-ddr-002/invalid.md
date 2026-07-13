# run-016-ddr-002 — INVALID AS REVIEW (all-hats-null false-CONVERGED)

**Ruling:** R-A, 2026-07-13. This fired draw is **invalid as a review** and carries
no findings, verdict, or convergence signal. It is preserved as **pathology
evidence** — the empirical basis for the all-hats-null fail-loud guard (RBT-54 R-C).

## What happened

The draw was fired against the landing-state substrate (bedrock 1.3.0, DDR-002
v1.3.0, DDR-004 v1.1.0, SDD-001 v1.2.0). Every one of the four hats went
**variance-to-zero**:

| Hat | initial draw | re-draw | outcome |
|---|---|---|---|
| antagonist-LAA | `[]` | `[]` | `hat_null` |
| antagonist-SA | `[]` | `[]` | `hat_null` |
| antagonist-EA | `[]` | `[]` | `hat_null` |
| coherence | `[]` | `[]` | `hat_null` |

Event tally: 8 `llm_call`, 4 `llm_retry` (one re-draw per hat), 4 `hat_null`,
1 `converged`. Ledger findings: **0**. Router exit: **CONVERGED**, pass 1,
`open_cbm = 0`.

With no all-hats-null guard in force at fire time, the router read zero open
counted findings and declared **CONVERGED** — a **false convergence** produced by
a wholly null instrument, not by a clean review. A legitimate empty result is
structurally impossible under the 2-POSITIVE floor; an all-hats-null draw is
therefore instrument-compromised by construction.

## Disposition

- **Invalid as review.** No finding, count, or "CONVERGED" from this draw is
  admissible. No remedy is inferred from it here.
- **Preserved as evidence.** The fired outputs (`ledger.json`, `manifest.json`,
  `action-log.jsonl`, `emissions/`) stand as the empirical basis for the RBT-54
  R-C all-hats-null guard, which fails such a draw loud instead of false-converging.
- **The valid draw will be run-017.** run-016 is retained only as this pathology
  record; it is never re-interpreted as a review.

Diagnosis of *why* every hat emitted `[]` is tracked separately (the SA arms
probe under `probes/`); no remedy lands before those probe results are ruled.

## Diagnosis (ruled R-D1, 2026-07-13)

**Root cause — narrated-completion deference, conjunctive form.** A reviewer hat
emits the sanctioned-empty `[]` **iff at least one copy of a completed-review /
adjudication / ratification narrative is present anywhere in context** — a
document Change Log row, the deliberation record, or a peer-document Change Log.
The narrative reads as *"this has already been reviewed and ratified"*, and the
hat defers to it instead of reviewing. It is **conjunctive**: removing one copy
does not wake the hat; **every** copy must be gone.

**Evidence — 17/17 samples consistent** (single-copy SA probe, gen-5, model
`claude-opus-4-8`):

| Sample | Context change from full run-016 | Narrative copies left | Findings | POS | out-tok | assembled-prompt sha256 |
|---|---|---|---|---|---|---|
| fired draw (4 hats × 2 = 8) | none (full input) | ≥1 | **0** (all `[]`) | 0 | 4 | — |
| B | authorities − DDR-002 | ≥1 (doc + record) | 0 | 0 | 4 | `4a05ebe8…` |
| C | document Status → PROPOSED | ≥1 (doc + record) | 0 | 0 | 4 | `83235c1c…` |
| D | design-intent − record | ≥1 (doc Change Log) | 0 | 0 | 4 | `c252cd03…` |
| E | auth − {DDR-002,SDD-001,DDR-004} + record out | ≥1 (doc Change Log) | 0 | 0 | 4 | `0e29a593…` |
| F | E-trim + record restored | *(HELD — not fired: D-silent AND E-silent)* | — | — | — | — |
| G | SKILL authority → 1.0.0 bytes | ≥1 (doc + record) | 0 | 0 | 4 | `63ef4cbb…` |
| H | document − 3 v1.3.0 Change Log rows | ≥1 (record retained) | 0 | 0 | 4 | `55e667bc…` |
| I | document → DDR-002 v1.2.0 | ≥1 (v1.2.0 Change Log + record) | 0 | 0 | 4 | `b57d04a3…` |
| **J** | **E-trim + H-strip (record out AND doc rows out)** | **0** | **6** | **2** | **2353** | `2e327b4c…` |
| **K** | run-015 SA call reconstructed byte-for-byte, re-fired | **0** (healthy baseline; no completion narrative) | **6** | **2** | **2958** | `c55b348826…` |

**J woke on the first zero-narrative context** (6 findings) — the only arm with
*every* copy removed. **K, the byte-for-byte run-015 re-fire, woke at healthy
baseline** — the model and serving path are exonerated; a live gen-5 SA hat
produces findings when no completion narrative is present. H (doc rows out, record
kept) and D (record out, doc rows kept) both stayed silent — the conjunction.

**Falsified along the way** (each held ≥1 narrative copy and stayed silent, so
each is *not* the cause): status metadata (C), target-as-authority self-reference
(B), context length (E is ~½ length, still silent), the SKILL 1.0.0→1.3.0 text
(G), single-copy narrative removal (D, H), and transport/params (no stop
sequences, no prefill sent; the model self-terminated — confirmed at ruling).

**Remedy — gen-7** (below): a reviewer-prompt calibration rule that recodes
narrated process as *data under review*, never a verdict that discharges the
review. **The documents are byte-unchanged** — the Change Logs were doing their
honest job (faithfully narrating what happened); the defect was in how the hat
*read* them. Acceptance gate: probe Arm L (full run-016 input, gen-7 SA prompt)
must wake.
