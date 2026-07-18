# run-029-adr-008-rbt69 — Pre-Registration

Registered **before launch** (instrument-empiricism): the acceptance criteria and the
baseline are fixed before any run-029 data exists, so a miss reads as mechanism, not a
post-hoc shrug. This is the supervised dry run that proves RBT-69's three merged
optimizations (PR #36, `6ea865c`) in the wild.

## Target & isolation

- **Target:** ADR-008 (`ground-truth-mutation-governance`), snapshotted fresh from the
  pristine sandbox canonical source — sha `24461d3f`, byte-identical to run-028's
  pre-run target.
- **Substrate:** copied verbatim from run-028's frozen snapshot (14 files). Substrate is
  never author-mutated, so this is byte-identical.
- **Prompt layer identical (verified before launch).** All six `prompt_sha256` match
  run-028's manifest exactly (calibration **gen-10** both): antagonist-LAA `0db740e8…`,
  -SA `1da965d9…`, -EA `439ecae2…`, coherence `5a6656b0…`, arbiter `3b786d5d…`, author
  `4e435d2c…`. RBT-69 touched no prompt file, so "the RBT-69 code is the only variable"
  holds literally at the prompt layer, not just target/substrate.
- **Model:** `claude-opus-4-8`; dry mode; `max_tokens` 8192.

## Known variables & attribution split (registered before launch)

The RBT-69 code carries **two** model-visible changes, not one, and the attribution is
pinned here so the audit cannot rationalize a delta after the fact:

1. **Identity-key change (piece 1)** — mechanical, at admission: `derive_id` now keys on
   `(sorted(target), normalize_locus(locus), altitude)`, claim removed. Its effect is a
   ledger-observable collapse of distinct ids at one `(target, locus, altitude)`.
2. **Substrate-leading reorder (piece 2, caching)** — the hat/author `## User` block now
   leads with the frozen substrate (`SUBSTRATE → DOCUMENT SET → LEDGER SNAPSHOT →
   recency`). **Order is content for an LLM — no cosmetic exemption.** Ratified and
   expected, but it means raw finding-count / `open_cbm` deltas vs run-028 could partly
   reflect reorder-induced behavioral drift, not only the identity fix.

**Attribution rule for criterion 3 (de-inflation).** Criterion 3 is judged on the
**mechanical identity-key collapse** — fewer distinct ids at the same
`(target, locus, altitude)`, observable at admission in the ledger — **not** on raw
finding-count / `open_cbm` deltas vs run-028. Any emission-level drift (a hat surfacing
materially different findings under the reordered prompt) routes to its **own audit
stream**, separate from the identity-collapse measurement.

## Baseline — run-028-adr-008 (from its manifest + ledger)

- Exit: `HALT_DECISION:oscillation` (plateau driver), **4 passes**, 108 findings.
- `open_cbm` trajectory: **18 → 24 → 41 → 55** (monotonic climb, zero recurrences).
- Per-site tokens (`1h`/`5m` split absent — run-028 predates the RBT-69 field):
  - antagonist-LAA: input 918,344 · cache_read 2,564 · calls 5
  - antagonist-SA: input 742,203 · cache_read 0 · calls 4
  - antagonist-EA: input 742,203 · cache_read 0 · calls 4
  - coherence: input 527,061 · cache_read 0 · calls 3
  - arbiter: input 48,540 · cache_read 11,361,240 · calls 78
  - author: input 2,123,606 · cache_read 110,084 · calls 59

## Pre-registered acceptance criteria

1. **Caching applied (C3, TTL proof).** Every actor's cache-creation tokens land in
   `ephemeral_1h_input_tokens`, ~nil in `ephemeral_5m` — the structural proof the 1-hour
   TTL took. Confirmable even single-pass (the arbiter writes the 1h bucket within a pass).
2. **Caching pays across passes (C3, cross-pass win).** IF ≥2 passes: hat/author
   `cache_read > 0` on passes 2+ (run-028 ≈0), total input materially below the run-028
   profile. If it halts in 1 pass, this specific reuse isn't exercised — not a failure
   (see note).
3. **Identity de-inflation (piece 1).** Judged on the **mechanical identity-key collapse**
   (see Attribution rule above): fewer distinct ids at one `(target, locus, altitude)`,
   observable at admission in the ledger — **not** raw finding-count / `open_cbm` deltas vs
   run-028 (those are confounded by the substrate-reorder variable). `claim_divergence` is
   a superset by design — volume expected, triaged in the cold audit, not an alarm.
4. **Honest disposition (piece 3).** Whatever exit is reached is the honest one for the
   ledger state: non-recurrence plateau → `non-convergence` (never `oscillation`); genuine
   reopen → `oscillation`; resolvables-exhausted-with-open-decisions → `decision-bearing`;
   clean ledger → `CONVERGED`. Failure = a *mislabeled* disposition, not any particular exit.

   **Note on the replay specifically:** the identity fix may prevent the plateau entirely
   (inflation was the plateau driver), so run-029 may now halt `decision-bearing` in 1–2
   passes instead of grinding to a plateau. That is the *strongest* evidence pieces 1+3
   work — not a missing `non-convergence` (which is already proven by unit test S2).

## Abort triggers (operational health only — §3e)

Parse-drop storm · volume swamp (>~50 admitted in pass 1) · cost runaway · mechanical
misbehavior (a pass repeating, ledger not advancing). Transport failure aborts itself.
Stance leakage / SA↔coherence overlap / arbiter confidence / POSITIVE volume are
**evidence, never abort triggers** — scored cold post-run.
