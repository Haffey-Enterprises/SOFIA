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
