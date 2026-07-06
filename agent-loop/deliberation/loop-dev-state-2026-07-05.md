# Agent-Loop Development State — 2026-07-05

> Carrier artifact for the reviewer-edit-loop development workstream. Written at
> the close of the RBT-15 cold-audit session (claude.ai surface), 2026-07-05.
> **Supersedes `loop-dev-state-2026-07-04.md`** (retained as history; its two
> currency passes are consolidated here). Kickoff prompts point here.
> Companion carriers: `agent-loop/triage/triage-001-distilled-set/record.md`
> (conventions, Appendix D) and `agent-loop/runs/run-0*/audit.md` (per-run audits)
> + `runs/run-011-sdd-001/disposition.md` (the SDD-001 v0.2.0 union disposition).

## Where the loop stands

| Run | Set | Outcome |
|---|---|---|
| 001–003 | corpus (4 docs) | Aborted — auth / parameter / parse-storm; each hardened a transport guard |
| 004, 005, 007 | corpus | HALT_DECISION @ pass 1; ratified audits; cumulative precision 88/92 |
| 006 | corpus | Aborted mid-gather (credit exhaustion); intra-generation variance sample |
| 008 | SDD-001 (first single-doc set) | Aborted ×2 @ ArbiterParseError; kept as evidence record |
| 009 | SDD-001 (substrate from 008) | HALT_DECISION @ pass 1 — the loop works on SDDs. 121/128 post-audit |
| 010 | SDD-001 v0.2.0 (draw 1 of 2) | **HALT_DECISION @ pass 1.** 19 findings (7M/4C/8POS); 0 empties (armed null held). Audit RATIFIED 2026-07-05 |
| 011 | SDD-001 v0.2.0 (draw 2, same bytes `fe6c8ee1`, corpus tip `9b960e52`) | **HALT_DECISION @ pass 1.** 23 findings (11M/4C/8POS); 3 empties, all single-re-draw recovered, 0 `hat_null`. Audit + union RATIFIED 2026-07-05 |

**Audit status (2026-07-05):** run-010 audit, run-011 fold-in audit (union table),
and the seven-item union disposition record all RATIFIED per item; committed on
`develop` at **`38c7074`** (validator PASS, 94 files scanned; the
`disposition.md` new-species question resolved benignly — check F gates only
`audit.md`/`record.md` by name, so the file lands as an ungated agent-loop
working note; no ruling needed). Cumulative validity precision **157/170**.
Union validity 36/42 (6 TRUE · 12 TRUE- · 2 HELD-MIS-SEV · 16 POS-TRUE · 6
OVER). Arbiter classification 16/17 DB genuine (one isolated miss), 9/9
resolvable. **Disposition headline: the §3.4.3 inherited-confidence
derivation is ELECTED for its own decision record** (D1, ten members, four
hats); D2 (#25) → DDR-002 additive amendment with a BUILD sequencing rule.
RBT-15 acceptance check ruled: criterion 2 (1b flip commitment) MET in §7.2;
criterion 1 (Three-hat → ACCEPTED) not yet met — **RBT-15 held open** through
v0.3.0 (disposition Item 2) → one verification draw (Item 7) → ACCEPTED.
Progress block posted to the ticket 2026-07-05.

**Fixed facts a session must not re-learn the hard way:** one-folder-one-run
(gate 1 fail-loud on existing `ledger.json`; NO resume); substrate files resolve
as `<category>/<logical_id>.md`; the validator hashes text, not bytes; prompts
are hash-pinned per run manifest and **calibration is fenced at gen 3** with
THREE ratified events queued, strictly scoped, hashes re-pinning at next run
prep: **gen-4** — severity discipline restated with the cap interaction named,
all four reviewer prompts (a held check is a POSITIVE-class emission; at cap,
drop it, never re-label as defect); **gen-5** — arbiter locus-attribution line
(each authority_locus element attributed to the document that actually carries
it, within its stated scope); **gen-6** — reviewer-side prompt caching (shared
substrate prefix + hat tail; renumbered from its provisional label). Gen-N is
not a bus — each event separately scoped and recorded. Any prompt change remains
a ratified calibration event, never a prep tweak. Dry mode only; model
`claude-opus-4-8`, max_tokens 8192, `ANTHROPIC_API_KEY` in the launching shell.
PRs target `develop`; doc-structure gate live (checks A–F); `disposition.md`
ruled in as an ungated run-folder working note by the validator's own taxonomy
(2026-07-05 — see audit-status block above).

## Development threads

### T1 — Prep tooling (DESIGN-READY; ticket next) — the priority thread
Design matured to ready this session: **five scriptable acts, `--from-run`
carry-forward, provenance sub-schema, document-snapshot-at-prep question** (the
last interacts with the runner snapshot-or-pin fix below — design them
together). Tool-home convention in hand from RBT-50 (fresh-authored scripts in
`scripts/`, self-contained rationale, single-ticket provenance, CI-wired with
free local path). Recipe for SDD runs unchanged (corpus docs as frozen
authorities + sdd-template + author-decision-record SKILL + deliberation record
+ vision block + charter notes). Prep-gate lessons 1–3 stand — notably #3:
substrate assembly COPIES, never moves; the tool asserts every canonical source
survives assembly. "Ticket after RBT-15" resolved to: **ticket now** (RBT-15
holds open through v0.3.0; waiting on ticket-close would starve the queue).

### T2 — Arbiter cost (prompt caching) — CLOSED → DELIVERED (Rc result recorded)
RBT-49's caching rode the two-draw sequence per Rc. **Honest delta vs estimate:
arbiter cache cut ~79–82% delivered against ~85–90% priced**; whole-sequence
economics ~54% — **roughly two draws for one uncached run's spend**, which is
what made the k=2 union affordable. Cache mechanics confirmed in the action
logs (010: 10/11 arbiter calls read 81,376 cached tokens; 011: 14/15).
Follow-on is gen-6 (reviewer-side caching): re-draws proved to CLUSTER (T4),
so making them near-free is now pointed, not speculative.

### T3 — Dry→live promotion path (gate HOLDS; second installment landed)
Second evidence installment: 157/170 cumulative; 16/17 DB genuine; zero
corrective retries across both draws (the uncertainty corner never re-emitted).
BUT: locus-entailment inflation reached n=3 and fired gen-5 — and this is
exactly the defect class that becomes load-bearing in live mode (a
`proposed_resolution` executing from an inflated locus). Gate logic
strengthened accordingly: **live-mode promotion does not revisit until gen-5
demonstrates zero locus-inflation recurrence across post-corrective runs.**
Also recorded for the live-mode design when it comes: the resolvable
authority_locus functioned as a de-facto validity screen five times across the
union; DB classifications carry no locus, so that screen is structurally absent
where the union's one classification miss occurred (4b3e626e). Observation
only; no corrective.

### T4 — Calibration watch streams (major update; two correctives fired)
- **Uncertainty corner (OPEN, quiet):** zero instances, zero corrective
  retries across 010/011. Standing.
- **Severity-discipline / cap-pressure — corrective FIRED (gen-4):** instance
  #3 (f4a5ba9d, run-010) met the pre-ruled trigger; 86a16eac (run-011) is a
  pre-corrective instance #4 strengthening the mechanism (all post-calibration
  instances: coherence, at its 2-POSITIVE cap — **hat-correlated**).
  Post-gen-4 baseline: the class goes to ZERO; the first post-gen-4 instance
  is the corrective's real test, not the pre-corrective tail.
- **Locus-entailment inflation — corrective FIRED (gen-5):** n=3 (24b85a37 →
  6c1aff22 → 13e08962), consistent mechanism, all non-load-bearing in dry
  mode. Post-gen-5 baseline: zero recurrence, gating T3 as above.
- **Variance-to-zero (empties) — clustering scored, n=2 armed runs, held
  loosely:** draw 1 = 0/4; draw 2 = 3/4, all single-re-draw recoveries, zero
  `hat_null`; EA (run-009's empty hat) was draw 2's only clean hat. Empties
  are **run-correlated**, not per-hat-independent — a run-level latent factor.
  Contrast pair now named: cap-pressure hat-correlated; empties run-correlated.
  The RBT-49 re-draw mechanic carried the entire recovery load (3/3).
- **POSITIVE cross-run stability — ANSWERED (union §3):** convergence
  reproduces — as credit clusters (authorship boundary: 4 credits per draw)
  and as decision-bearing families (D1, D2) — while one-off findings, valid
  and invalid alike, are draw-local. Three defect/credit inversion pairs all
  resolved credit-side; one genuinely two-sided locus (#25) read correctly
  from both sides.
- **Reviewer-side species named:** "never surfaced" false positives (real
  loci, entailment contradicted by the record's own surfacing apparatus) —
  LAA, exactly one per draw (4dfe13af, 13e08962). Watch-only.
- **EA roster — RESOLVED:** surface-driven variance, not hat dysfunction;
  the all-POSITIVE streak broke on D1's gravity with two valid MATERIALs.

### T4b — Operating mode — ANSWERED; folds into T4 on next supersession
The 010/011 union confirms 008/009: union-over-runs is the result, now with
the refinement that reproduction-across-draws separates document signal from
draw noise on BOTH the defect and credit sides. Ruled consequence (disposition
Item 7): the v0.3.0 verification is ONE draw — k=2 was for baseline-setting;
bounded-delta verification doesn't need it.

### T5 — Housekeeping (cheap, ride-along)
- GitHub is deprecating Node 20 for `actions/checkout@v4` — one-line workflow
  bump, ride the next CI-touching ticket.
- README Run section still skeleton-era; prep-recipe docs should note
  coherence axis-2 is vacuous on single-doc sets. Standing.

## Successor queue (from the ratified disposition, execution order)
1. **Loop-instrument micro-ticket** — gen-4 + gen-5 + runner snapshot-or-pin
   (root-cause fix: live-read at launch made the develop freeze load-bearing
   by hand) — lands BEFORE the v0.3.0 verification draw.
2. **T1 prep-tool ticket** — design-ready; snapshot-at-prep question designed
   jointly with the runner fix.
3. **D1 decision-record ticket** (disposition Item 1) and **DDR-002
   amendment-batch ticket** (Items 3+4) — order free between them; Item 3's
   sequencing rule binds only relative to BUILD.
4. **SDD-001 v0.3.0** (Item 2) — RBT-15 scope; authored against Item-1 routing.
5. **v0.3.0 single verification draw** (Item 7) — gen-6 ideally lands first.

## Dependencies and boundaries
- Run-010/011 audits + disposition: RATIFIED; committed on `develop` at
  `38c7074` (validator PASS, 94 files).
- SDD-001 v0.2.0 remains the corpus-side document of record until v0.3.0 lands.
- RBT-48 before the BUILD-leg flip (ticket-ruled); #25 amendment before BUILD
  or its 1a/1b bucket ruled first (disposition Item 3) — sibling rules, no conflict.
- Two-surface split holds: design/ratification on claude.ai; Code implements;
  git transactions are Tad's.
