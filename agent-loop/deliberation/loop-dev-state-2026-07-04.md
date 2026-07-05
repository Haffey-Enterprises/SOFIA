# Agent-Loop Development State — 2026-07-04

> Carrier artifact for the reviewer-edit-loop development workstream. Written at
> the close of the triage-001/run-008/run-009 session (claude.ai surface).
> Kickoff prompts point here; this file is extended or superseded per session.
> Companion carriers: `agent-loop/triage/triage-001-distilled-set/record.md`
> (conventions, Appendix D) and `agent-loop/runs/run-00*/audit.md` (per-run audits).
>
> **Currency pass 2026-07-04 (post-audit session):** run-009 audit + run-008
> fold-in audit are RATIFIED and committed (PR #10, main @ dcb5e21); SDD-001
> v0.2.0 authored from the review union; RBT-49 opened (prompt caching +
> empty-emission re-draw). Threads below marked CLOSED→pointer where those
> products supersede; the EA-empty framing in T4 is corrected (the original
> hat-altitude reading did not survive the evidence).

## Where the loop stands

| Run | Set | Outcome |
|---|---|---|
| 001–003 | corpus (4 docs) | Aborted — auth / parameter / parse-storm; each hardened a transport guard |
| 004, 005, 007 | corpus | HALT_DECISION @ pass 1; ratified audits; cumulative precision 88/92 |
| 006 | corpus | Aborted mid-gather (credit exhaustion); kept as intra-generation variance sample |
| 008 | SDD-001 (first single-doc set) | Aborted ×2 @ ArbiterParseError — arbiter omitted required `confidence` field 4/4 attempts on one finding (fence was a red herring; parser already strips). Kept as evidence record |
| 009 | SDD-001 (substrate carried from 008) | **HALT_DECISION @ pass 1 — the loop works on SDDs.** 16 findings (7 M / 2 C / 6 POSITIVE, caps held), 9 resolvable w/ authority loci, 1 genuine decision-bearing (zero-evidence conclusions — routed to SDD-001 v0.2.0 deliberation, NOT loop work) |

**Audit status (2026-07-04):** run-009 audit and run-008 fold-in audit both
RATIFIED per item and committed — `runs/run-009-sdd-001/audit.md` +
`runs/run-008-sdd-001/audit.md`. Cumulative validity precision **121/128**.
The arbiter's resolvable/decision-bearing split held up against human rulings
(the T3 evidence question, first installment — answered yes); one new arbiter
defect species recorded as a watch item: **locus-entailment inflation**
(24b85a37 — real sources, fabricated entailment; run-009 audit §4). SDD-001
v0.2.0 was authored from the ratified run-008 ∪ run-009 union and merged
(PR #10); its review run is queued behind RBT-49.

**Hardening #4 (post-008, via Code):** the content retry now names the parse
defect instead of blind-resending. Validated empirically in run-009: 11 arbiter
calls / 10 classifications — one corrective retry fired and succeeded.

**Fixed facts a session must not re-learn the hard way:** one-folder-one-run
(gate 1 fail-loud on existing `ledger.json`; there is NO resume); substrate files
resolve as `<category>/<logical_id>.md`; the validator hashes text
(`read_text().encode()`), not bytes; prompts are hash-pinned per run manifest and
**calibration is fenced at gen 2** — any prompt change is a ratified gen-3
calibration event, never a prep tweak; dry mode only (the author applies
nothing; live mode does not exist yet); model `claude-opus-4-8`, max_tokens 8192,
`ANTHROPIC_API_KEY` in the launching shell.

## Development threads, in recommended priority order

### T1 — Prep tooling (warrant EARNED; design → RBT ticket → Code) — STILL OPEN, now the priority thread
Run-009 answered the experiment: the loop earns its keep on SDDs, and ~8 SDD
reviews are queued behind SDD-001 (RBT-19–26). Generalize the one-off
`prep_run008.py` (see run-008 folder history; its fix script encodes the two
prep-gate lessons) into a standing tool: parameterize run-id + doc-ids +
substrate recipe; recipe for SDD runs = corpus docs as frozen authorities +
sdd-template + author-decision-record SKILL + deliberation record + vision block
+ charter notes as design-intent. Open design points: tool home (package module
vs `scripts/`), recipe-per-doc-type declaration, whether the tool also emits the
launch line. Design on claude.ai, ticket to Reboot, Code implements.
**Note:** RBT-49 covers the runner-side items (caching, re-draw) — the prep
tool itself still has NO ticket; RBT-50 (validator restore) will land a
`scripts/`-or-CI convention that bears on the tool-home design point.
**Prep-gate lesson #3 (2026-07-04):** substrate assembly COPIES, never moves —
canonical paths are sources, not staging. The run-008 prep relocated the
canonical deliberation record into substrate (empty source dir left behind;
restored + byte-verified 2026-07-04). The generalized tool must copy-and-verify,
and its prep-gate check should assert every substrate source still exists at
its canonical path after assembly.

### T2 — Arbiter cost (prompt caching) — CLOSED → **RBT-49** (High, 2026-07-04)
Superseded by the ticket, which carries the ratified spec and fuller sizing
(run-009: 1,297,750 in; arbiter 11×~82k = 69%): [static prefix][per-finding
tail] + `cache_control`; batch classification ruled an explicit non-goal
(per-finding retry isolation, validated run-009 audit §5a). Also in RBT-49,
ruled: reviewer empty-emission re-draw — below-POSITIVE-floor emission triggers
one re-draw; second empty → `hat_null` + continue (reviewer nulls degrade
recall, recoverable via union; arbiter nulls corrupt the ledger, correctly
fatal). Sequencing intent: RBT-49 lands before the SDD-001 v0.2.0 review run.

### T3 — The EDIT half: dry→live promotion path (gated on audit evidence)
The loop is review-only. Live mode (author applies resolvable fixes per
authority locus; `doc_changes` recorded; coherence re-runs on doc change — the
scheduling rule already exists) is designed-but-unwired, and the arbiter
prompt's own dry-mode note sets the promotion gate: watch the low/medium-
confidence decision-bearing stream across dry runs; "do not promote to live
until that stream is boring." **First evidence installment landed (2026-07-04):**
the ratified audits validate the resolvable stream (121/128; zero
false-resolvables; the one decision-bearing trigger was correct) — but n=1 at
SDD scale, and the locus-entailment-inflation watch item (run-009 audit §4) is
exactly the defect class that becomes load-bearing in live mode (a
`proposed_resolution` executing from an inflated locus). Gate holds: more dry
runs before machinery. Do not design live mode ahead of that evidence —
empirical warrant before machinery.

### T4 — Gen-3 calibration backlog (watch-only; rule when evidence accumulates)
- **Uncertainty-corner hypothesis (OPEN — sole carrier is this file):** the
  arbiter prompt forbids low-confidence `resolvable` and gives no legal output
  for "resolvable but unsure"; run-008's 4/4 field-omission on one finding fits
  the corner. Offender never re-emitted in 009, and the corrective retry
  recovered the one 009 instance in a single attempt (audit §5a). If corrective
  retries start failing on this pattern, the gen-3 prompt ruling comes back to
  the design surface with the evidence.
- **Severity-discipline nit — CLOSED as recorded → run-009 audit §5c:** fe2b5642
  ruled HELD-MIS-SEV (content true, severity wrong — second instance of the
  8ed91773 class). Cap-pressure hypothesis on record at n=1: the POSITIVE *cap*
  may smuggle surplus held-checks out as COSMETIC — the mirror of run-005's
  floor-pressure finding. No prompt change (no-prompt-chasing holds at n=2);
  a third instance triggers one corrective: severity discipline restated *with
  the cap interaction named*.
- **Empty emissions — FRAMING CORRECTED → run-009 audit §5b; re-draw ruled into
  RBT-49:** the original reading here ("hat productivity varies by document
  altitude") did not survive the evidence. Three empties across the SDD runs —
  008p1 **LAA**, 008p2 **SA**, 009 **EA** — each on bytes where the *same hat*
  produced substantive findings in a sibling draw. This is **variance-to-zero**:
  a draw-level degenerate completion, hat-independent and input-independent, ~3
  of 11 SDD-scale hat-draws. Detectable mechanically: the ratified 2-POSITIVE
  floor makes a compliant `[]` structurally impossible — malformed-by-
  calibration, not a null result. Ruled (RBT-49 item 2): one re-draw; second
  empty → `hat_null` + continue. The roster question proper stays held — the
  remaining live watch streams: per-hat productivity by doc type, stance
  leakage, cross-hat migration (5 instances logged through run-008 fold-in §1),
  SA↔coherence seam, arbiter confidence stream, POSITIVE cross-run stability
  (credits reproduce across draws; defects don't — fold-in §4).

### T4b — Operating-mode evidence (NEW 2026-07-04; feeds the queued deliberation)
Two structural results from the audit session, recorded here as the loop-side
pointer (full treatment: run-009 audit §2, run-008 fold-in §3):
- **Union-over-runs is not marginal at SDD scale — it is the whole result.**
  Same-bytes runs 008/009 produced near-zero defect overlap, each holding
  strong finds the other missed; a whole altitude (EA) absent from one run's
  single-draw view. The high-recall mode is union-of-k runs; RBT-49's caching
  is what makes k affordable.
- **Repeat passes ≠ fresh runs.** Run-008's dry-mode pass 2 (no doc change,
  ledger-in-context) yielded ZERO new true defects: EA re-emitted its own set,
  SA zeroed, LAA reached (both new MATERIALs ruled OVER). Fresh *runs* find
  disjoint defects; repeat *passes* find none. The plateau/pass logic and the
  union question should be ruled together.

### T5 — Housekeeping (cheap, ride-along)
README's Run section is skeleton-era (no `run_real`) — doc-vs-repo drift, one
paragraph. Prep-recipe docs should note coherence axis-2 (cross-document) is
vacuous on single-doc sets — expected, audit-noted, not a defect.

## Dependencies and boundaries
- Run-009 audit + run-008 fold-in: **LANDED and ratified** (main @ dcb5e21) —
  the T3/T4 evidence inputs above. Consume, do not re-derive.
- SDD-001 revision: **v0.2.0 AUTHORED and merged** (PR #10) — PROPOSED, pending
  its own review run (queued behind RBT-49). Corpus-side; not loop work.
- RBT-48 (conformance harness catch-up) is SOFIA-corpus-side; not this thread.
  RBT-50 (doc-validator restore, CI gate) is repo-infrastructure; bears on T1's
  tool-home question only.
- Two-surface split holds per thread: design/deliberation/ratification on
  claude.ai; implementation via Code prompts; git transactions are Tad's.
