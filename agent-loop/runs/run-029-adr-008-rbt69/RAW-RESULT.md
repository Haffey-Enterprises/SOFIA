# run-029-adr-008-rbt69 — Raw Result (computed from action-log post-abort)

**Manifest is deliberately unfinalized** — the run aborted, and `run_real` leaves the
manifest unfinalized on the abort path (run-prep §7). Every number below is computed from
`action-log.jsonl` (the `llm_call` provenance events) after the fact, not read from a
finalized manifest. This file is a hand-back convenience for the claude.ai cold-audit leg;
it fabricates nothing. Folder left uncommitted for the operator's git transaction.

## Outcome

- **Exit: ABORTED — `InstrumentCompromisedError` at pass 2.** The coherence hat produced
  parse-dropped emissions on both its initial emission and its redraw retry, admitted no
  findings, and the runner refused to route (guard against a false CONVERGED). This is the
  §3e.1 parse-drop-storm class — the correct, honest operational-health abort.
- **Passes: 1 complete + partial pass 2** (pass-2 hats LAA/SA/EA/coherence ran; coherence
  dropped; no pass-2 ledger snapshot / router disposition).
- HEAD at launch: `6ea865c` (unchanged from prep). Model `claude-opus-4-8`, dry, max_passes 6.

## Per-site token totals (through the abort)

| site | input | cache_read | 1h_creation | 5m_creation | calls |
|---|---|---|---|---|---|
| antagonist-LAA | 39,939 | 150,705 | 150,705 | 0 | 2 |
| antagonist-SA | 39,939 | 150,725 | 150,725 | 0 | 2 |
| antagonist-EA | 39,939 | 150,665 | 150,665 | 0 | 2 |
| coherence | 71,106 | 301,410 | 150,705 | 0 | 3 |
| arbiter | 14,498 | 3,587,760 | 149,490 | 0 | 25 |
| author | 733,979 | 166,892 | 96,709 | 0 | 25 |

## Per-pass cache_read (the criterion-2 signal)

| site | pass 1 cache_read | pass 2 cache_read |
|---|---|---|
| antagonist-LAA | 0 | **150,705** |
| antagonist-SA | 0 | **150,725** |
| antagonist-EA | 0 | **150,665** |
| coherence | 0 | **301,410** (2 calls) |

Run-028 hats read ≈0 from cache on **every** pass. Here every pass-2 hat read its full
~150k substrate from cache — the 1-hour TTL survived the inter-pass gap, exactly the piece-2
mechanism.

## open_cbm trajectory

- pass 1: **21** (run-028 pass 1 = 18). Only pass 1 recorded; the abort truncated the
  pass-2 snapshot. Raw delta vs run-028 is **not** the criterion-3 measure (confounded by
  the substrate-reorder variable — see PRE-REGISTRATION Attribution rule).

## Criteria scorecard (pre-registered)

1. **C1 — 1h TTL applied: CONFIRMED.** All six actors' cache-creation landed in the 1h
   bucket, 5m = 0 across the board. Structural TTL proof, unambiguous.
2. **C2 — cross-pass caching pays: CONFIRMED LIVE.** Pass-2 hats read their full substrate
   from cache (LAA/SA/EA ~150k each; run-028 ≈0 on all passes). Exercised despite the abort
   because the pass-2 hats ran before coherence's drop. The core RBT-69-piece-2 win is
   demonstrated in the wild, not just on the unit suite.
3. **C3 — identity de-inflation: PARTIAL (mechanical evidence present).** The
   `claim_divergence` guard fired once, textbook: same `finding_id` `1b8c8b5c92484635`, the
   incoming claim a re-wording of the existing ("I attacked the Decision for scope creep …")
   — captured as a variant instead of minting a fresh id. 1 `dedup_open` (an id collapsed).
   Full `open_cbm` trajectory truncated by the abort — the de-inflation *mechanism* is
   observable; the multi-pass trajectory is not.
4. **C4 — honest disposition: NOT REACHED.** Aborted before any router disposition. Piece 3
   remains proven by unit test S2; not exercised on real input this run.

## Abort diagnosis (for triage / re-spec)

- **Defect:** coherence hat emitted a narration preamble *before* the JSON array on pass 2
  (`pass02-coherence-1.txt` starts "Reading the current state…"; the redraw
  `pass02-coherence-2.txt` starts "Now sweeping the current state…"). The reviewer parse
  seam is strict (no preamble tolerance) → both `parse_dropped: invalid JSON`. Pass 1's
  four hats all emitted clean `[`-first JSON.
- **Class:** same genre as run-027's author preamble-before-JSON, which **gen-10 fixed for
  the author parser only** (preamble-tolerant + parse-fail-escalates). That tolerance was
  never ported to the reviewer parse seam. RBT-69 touched no prompt/parser.
- **Leading hypothesis (n=1, held):** run-028 ran 4 full passes on byte-identical
  target/substrate/prompts with **no** coherence parse-drop storm. run-029 differs in
  exactly two ways: the identity-key change (admission-only — cannot alter emission text)
  and the **substrate-reorder** (emission-visible; order is content for an LLM). The reorder
  is therefore the leading suspect for inducing the pass-2 preamble. Opus is
  non-deterministic, so a one-off cannot be excluded — but this is precisely the
  reorder-induced behavioral drift the pre-registration flagged as a second variable, here
  manifesting as an operational failure rather than finding-count drift. Belongs in the cold
  audit's own stream.
- **Re-spec candidates (claude.ai leg, not decided here):** (a) port the gen-10
  preamble-tolerant + parse-fail-doesn't-abort discipline to the reviewer parse seam so one
  narrated preamble degrades to a drop-and-continue rather than an instrument-compromised
  abort; and/or (b) tighten the reviewer prompts' output discipline (JSON-array-first, no
  preamble) the way gen-10 tightened the author; and (c) investigate the reorder→preamble
  link directly (re-run with reorder isolated).
