# run-030-adr-008-rbt69 — Pre-Registration

Registered **before launch** (instrument-empiricism): the acceptance criteria and the
baseline are fixed before any run-030 data exists, so a miss reads as mechanism, not a
post-hoc shrug. run-030 is the clean retry of run-029 — the first RBT-69 proving run,
which aborted at pass 2 (coherence preamble → `InstrumentCompromisedError`). RBT-70 fixed
that; run-030 proves the fix and completes the RBT-69 proving that run-029 could not.

## Single-variable discipline (the governing constraint)

run-030 changes **exactly one variable** from run-029: the RBT-70 work — the four
**gen-11** reviewer prompts (`[`-first output-discipline / silent-re-verification rule)
plus `real_hats.py`'s `_extract_json_array` array-salvage seam. Everything else is
byte-identical to run-029, verified before launch:

- **Target (ADR-008):** sha `24461d3f` — the pristine pre-run document, sourced from the
  untouched sandbox canonical source, **byte-identical to run-029's recorded pre-run pin**.
  (run-029's *committed* `documents/` copy is the post-run author-mutated end-state, sha
  `19897547`, deliberately not used — the dry-mode author writes edits into `documents/`
  across passes, run-supervision §9.)
- **Substrate (14 files):** copied verbatim from run-029's frozen `substrate/`,
  hash-verified byte-identical; each file re-hashes to its own `substrate/manifest.json`
  pin (gate 4). Never author-mutated.
- **Non-reviewer prompts:** arbiter `3b786d5d…` and author `4e435d2c…` — **byte-identical
  to run-029** (verified). RBT-70 touched neither.
- **RBT-69 code:** unchanged — the only `agent_loop/*.py` file that differs between
  run-029's HEAD (`6ea865c`) and run-030's HEAD (`0370254`) is `real_hats.py` (the RBT-70
  seam), confirmed by `git diff --name-only`.
- **Model:** `claude-opus-4-8`; dry mode; `max_tokens` 8192.

**Expected instrument delta (the one intended variable).** run-030's manifest will record
NEW `prompt_sha256` for the four reviewer prompts (gen-11: LAA `76ce2c8b…`, SA `12361c62…`,
EA `68fe9c98…`, coherence `836986a8…`) and exercises the changed `real_hats.py`. Any input
hash differing from run-029's *other than these* would be a second variable — the prep
gate for that (target + substrate + arbiter/author prompt hashes = run-029's) passed.

**Known metadata note (not a variable).** `run_real.py`'s `CALIBRATION.generation`
constant still reads `10`; RBT-70 bumped the reviewer prompts to gen-11 but did not bump
the constant. run-030's manifest will therefore stamp `generation: 10` alongside gen-11
prompt hashes. This is provenance metadata, not a model input — flagged for the RBT-70
follow-up / cold audit, not fixed here (fixing code would itself be a second variable).

## Baseline — run-028-adr-008 (from its manifest + ledger)

- Exit: `HALT_DECISION:oscillation` (plateau driver), **4 passes**, 108 findings.
- `open_cbm` trajectory: **18 → 24 → 41 → 55** (monotonic climb, zero recurrences).
- Per-site tokens (run-028 predates the RBT-69 1h/5m split field):
  - antagonist-LAA: input 918,344 · cache_read 2,564 · calls 5
  - antagonist-SA: input 742,203 · cache_read 0 · calls 4
  - antagonist-EA: input 742,203 · cache_read 0 · calls 4
  - coherence: input 527,061 · cache_read 0 · calls 3
  - arbiter: input 48,540 · cache_read 11,361,240 · calls 78
  - author: input 2,123,606 · cache_read 110,084 · calls 59

Direct predecessor = run-029 (aborted pass 2, coherence preamble). run-029 pass-1
`open_cbm` = 21; pass-2 hats read full substrate from cache before the coherence drop
(1h-TTL confirmed live).

## Pre-registered acceptance criteria

**0. The abort does not recur (the RBT-70 single-variable proof).** Pass-2 coherence —
which stormed in run-029 — now either (a) emits clean `[`-first JSON (gen-11 forcing
function suppressed the reconciliation narration at the root), or (b) narrates a preamble
that the seam salvages, logging `reviewer_output_preamble_stripped`, findings admitted, no
parse-drop. Either is a pass. A pass-2 `InstrumentCompromisedError` is the failure — and
since RBT-70 is the only changed variable, an abort here falsifies the RBT-70 fix
specifically.

**1. Caching applied (C3, TTL proof).** Every actor's cache-creation tokens land in
`ephemeral_1h_input_tokens`, ~nil in `ephemeral_5m` — the structural proof the 1-hour TTL
took. Confirmable even single-pass (the arbiter writes the 1h bucket within a pass).

**2. Caching pays across passes (C3, cross-pass win).** IF ≥2 passes: hat/author
`cache_read > 0` on passes 2+ (run-028 ≈0), total input materially below the run-028
profile. If it halts in 1 pass, this specific reuse isn't exercised — not a failure; it
rests on the unit suite.

**3. Identity de-inflation (piece 1).** Judged on the **mechanical identity-key collapse**:
fewer distinct ids at one `(target, locus, altitude)`, observable at admission in the
ledger — **not** raw finding-count / `open_cbm` deltas vs run-028 (confounded by the
substrate-reorder variable). Watch the `claim_divergence` stream: a superset by design —
volume expected, triaged in the cold audit, not an alarm.

**4. Honest disposition (piece 3).** Whatever exit is reached is the honest one for the
ledger state: non-recurrence plateau → `non-convergence` (never `oscillation`); genuine
reopen → `oscillation`; resolvables-exhausted-with-open-decisions → `decision-bearing`;
clean ledger → `CONVERGED`. Failure = a *mislabeled* disposition, not any particular exit.

   **Note on the replay specifically:** the identity fix may prevent the plateau entirely
   (inflation was the plateau driver), so run-030 may now halt `decision-bearing` in 1–2
   passes instead of grinding to a plateau. That is the *strongest* evidence pieces 1+3
   work — not a missing `non-convergence` (already proven by unit test S2).

## Abort triggers (operational health only — §3e)

Parse-drop storm · volume swamp (>~50 admitted in pass 1) · cost runaway · mechanical
misbehavior (a pass repeating, ledger not advancing). Transport failure aborts itself.
Special watch: pass-2 coherence (the run-029 abort locus) — expect clean `[`-first JSON or
a logged `reviewer_output_preamble_stripped` salvage, not a drop. Stance leakage /
SA↔coherence overlap / arbiter confidence / POSITIVE volume are **evidence, never abort
triggers** — scored cold post-run.

## Config

- run-id `run-030-adr-008-rbt69`; doc-id `ADR-008`; dry mode; `claude-opus-4-8`;
  `max_tokens` 8192; `max_passes` **6** (matching run-029; attended bound); no coherence
  addendum (none exists — matches run-029).
- HEAD at launch: `0370254` (PR #37, RBT-70 merged). Prep gates 1-5,8 green; 6/7 pending
  until the key is sourced at launch.
