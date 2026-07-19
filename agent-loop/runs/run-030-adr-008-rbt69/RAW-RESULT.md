# run-030-adr-008-rbt69 — Raw Result (computed from action-log post-abort)

**Manifest is deliberately unfinalized** — the run aborted, and `run_real` leaves the
manifest unfinalized on the abort path (run-prep §7). Every number below is computed from
`action-log.jsonl` (the `llm_call` provenance events) after the fact, not read from a
finalized manifest. This file is a hand-back convenience for the claude.ai cold-audit leg;
it fabricates nothing. Folder left uncommitted for the operator's git transaction.

## Outcome

- **Exit: ABORTED — `LlmTransportError` at pass 5, external API usage-limit.** The
  antagonist-EA pass-5 call returned HTTP 400 `invalid_request_error`: "You have reached
  your specified API usage limits. You will regain access on 2026-08-01 at 00:00 UTC." The
  §6 emitter policy gave it one 30 s-backoff retry (`llm_retry`, transport); the retry hit
  the same 400 and the run aborted loudly (`run_aborted`). This is an **account-level
  spend/usage cap, not a run defect** — categorically different from run-029's
  `InstrumentCompromisedError` (a §3e parse-drop storm). It is unrelated to the RBT-70
  variable, the target, the substrate, or the loop machinery.
- **Passes: 4 complete + partial pass 5.** Pass-5 hats LAA and SA ran clean; EA
  transport-failed (retry → same 400 → abort). No pass-5 coherence, no pass-5 router
  disposition.
- HEAD at launch: `0370254` (PR #37, RBT-70 merged). Model `claude-opus-4-8`, dry,
  max_passes 6. Single-variable gate verified before launch (target sha `24461d3f` =
  run-029 pin; substrate byte-identical to run-029; arbiter+author prompts byte-identical;
  only the 4 gen-11 reviewer prompts + `real_hats.py` changed).

## Criterion 0 — the RBT-70 single-variable proof: **MET (via path (a))**

- **`parse_dropped: 0` across the entire run.** Zero reviewer parse-drops on any pass,
  including pass-2, pass-3, and pass-4 coherence — the exact locus that stormed in run-029.
- **`reviewer_output_preamble_stripped: 0`** — the array-salvage seam **never needed to
  fire**. The gen-11 forcing function ("your entire response is the raw findings array,
  first character `[` … no preamble") suppressed the reconciliation narration at the root,
  so every coherence emission was clean `[`-first JSON. This is path (a) of criterion 0
  (clean JSON), the stronger of the two acceptable outcomes.
- Every hat call across all passes carried `stop_reason: end_turn` with a parseable array.
- **Answering the kick-off's explicit hand-back question:** no `reviewer_output_preamble_stripped`
  fired anywhere (0 occurrences). Note a *different* seam did fire — see below.

## Per-site token totals (through the abort)

| site | input | cache_read | 1h_create | 5m_create | calls |
|---|---|---|---|---|---|
| antagonist-LAA | 228,102 | 603,604 | 150,901 | 0 | 5 |
| antagonist-SA | 228,102 | 603,684 | 150,921 | 0 | 5 |
| antagonist-EA | 147,952 | 452,583 | 150,861 | 0 | 4 |
| coherence | 147,952 | 452,703 | 150,901 | 0 | 4 |
| arbiter | 44,637 | 10,613,790 | 149,490 | 0 | 72 |
| author | 2,069,228 | 552,501 | 176,907 | 0 | 68 |

(EA/coherence show 4 calls — pass-5 EA failed both attempts before an `llm_call` logged;
LAA/SA ran their pass-5 call before the EA failure.)

## Criterion 1 — 1h TTL applied: **CONFIRMED**

All six actors' cache-creation landed in the `ephemeral_1h` bucket; `ephemeral_5m` = 0
across the board (including the author, 176,907 in the 1h bucket). Unambiguous structural
proof the 1-hour TTL was applied.

## Criterion 2 — cross-pass caching pays: **CONFIRMED LIVE**

Per-pass hat `cache_read` (run-028 read ≈0 on **every** pass):

| site | p1 | p2 | p3 | p4 | p5 |
|---|---|---|---|---|---|
| antagonist-LAA | 0 | 150,901 | 150,901 | 150,901 | 150,901 |
| antagonist-SA | 0 | 150,921 | 150,921 | 150,921 | 150,921 |
| antagonist-EA | 0 | 150,861 | 150,861 | 150,861 | — |
| coherence | 0 | 150,901 | 150,901 | 150,901 | — |

Every pass-2+ hat read its full ~150k substrate from cache; the 1-hour window survived
each inter-pass gap through pass 5. The core RBT-69-piece-2 win, demonstrated across four
inter-pass boundaries (run-029 showed it across one).

## Criterion 3 — identity de-inflation: **mechanical evidence strong**

- **`dedup_open: 12`** — 12 re-emissions collapsed onto an already-open id instead of
  minting a fresh one (the piece-1 de-inflation mechanism, at admission).
- **`claim_divergence: 12`** *(10 unique finding_ids; the guard re-fires each pass a
  reworded variant re-arrives)* — materially-reworded-same findings captured as
  `claim_variants` on the existing record, nothing hidden or discarded.
- These are the mechanical identity-key collapse the criterion is judged on (not raw
  `open_cbm` deltas, which are confounded by the reorder variable per the pre-registration
  Attribution rule). Full reworded-vs-genuinely-distinct triage is the cold-audit leg.

## Criterion 4 — honest disposition: **NOT REACHED**

Aborted at pass 5 on the external cap before any pass-5 router disposition. The last router
event was pass-4 `continue`. Not a mislabel (the failure mode criterion 4 guards) — no
disposition was produced. Piece 3 remains proven by unit test S2; its live exercise is
deferred to a run that completes.

## open_cbm trajectory (router events)

- pass 1: **19** · pass 2: **16** · pass 3: **28** · pass 4: **37** (through the last
  completed pass). Non-monotonic (dip then climb); under the volume-swamp guideline (<50)
  at every recorded pass. Raw deltas vs run-028 (18→24→41→55) are **not** the criterion-3
  measure (reorder-confounded).

## Other observed events (for the cold audit)

- **`author_output_preamble_stripped: 12`** — the AUTHOR's preamble-tolerant parser
  (gen-10 / RBT-67, a *different* seam from the reviewer array-salvage) salvaged 12 author
  preambles-before-JSON. The author write path narrated before its JSON envelope 12 times;
  each was salvaged and logged, none aborted. (Distinct from the reviewer seam, which never
  fired.)
- **`llm_retry: 3`** — 2× author content ("malformed author output", invalid vocabulary
  value; one logged retry each, escalate-not-abort policy) + 1× antagonist-EA transport
  (the fatal usage-cap 400).
- **Author disposition split:** 20 `author_edit`, 46 `author_refused`, 68 author calls,
  2.07M input tokens. High refuse rate → decision-bearing accumulation (each refuse
  escalates a resolvable to decision-bearing, status open), consistent with the open_cbm
  climb.
- **`admitted: 96`, `classified: 72`** across the 4.x passes.

## Single-variable gate (confirmed held)

Inputs hash-matched run-029 before launch: target ADR-008 sha `24461d3f` (= run-029's
recorded pre-run pin, sourced from the pristine sandbox source, NOT run-029's author-mutated
committed copy); 14 substrate files byte-identical to run-029; arbiter (`3b786d5d`) and
author (`4e435d2c`) prompts byte-identical to run-029. The only variables were the four
gen-11 reviewer prompts (LAA `76ce2c8b`, SA `12361c62`, EA `68fe9c98`, coherence `836986a8`)
and `real_hats.py` (the RBT-70 array-salvage seam) — the intended RBT-70 delta. Manifest
`calibration.generation` still reads `10` (RBT-70 did not bump it; recoverable from the four
gen-11 `prompt_sha256`) — filed as a develop fast-follow, deliberately not bumped on the
proving run.

## Bottom line for the cold audit

run-030 **proved what run-029 could not** — criterion 0 (the RBT-70 fix) is met, via the
strongest path (clean JSON, salvage seam never needed), plus criteria 1, 2, and strong
criterion-3 mechanical evidence. Only criterion 4's live exercise is outstanding, deferred
by an **external API usage cap** (resets 2026-08-01), not by any instrument or code defect.
A completing run against the same target after the cap resets would exercise criterion 4;
the disposition machinery is otherwise proven by unit test S2.
