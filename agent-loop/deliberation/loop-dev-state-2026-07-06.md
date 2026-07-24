# Loop dev state — 2026-07-06 (carrier)

Supersedes: loop-dev-state-2026-07-05.md
Session: ticketing + calibration-event authoring (post-RBT-15-audit-close).
No runs executed; no corpus amendments; four Linear tickets created.

## Session outcomes

1. **RBT-51 created** — loop instrument. Gen-4 (severity/cap discipline, all
   four reviewer prompts, in-place SEVERITY DISCIPLINE replacement) and gen-5
   (arbiter LOCUS ATTRIBUTION line, appended after OUTPUT DISCIPLINE) texts
   RATIFIED VERBATIM (Tad, 2026-07-06) and carried in the ticket — the ticket
   is the event record for both. Runner snapshot-or-pin scope ratified
   (4 points: immutable-at-launch; manifest records reviewed content;
   live-read REMOVED, not gated; fail-loud on mismatch). Not a gen-numbered
   event — no prompt bytes.
2. **RBT-52 created** — T1 prep tool. **Durable home of the five-act
   enumeration** (Code's 010/011 prep-report §5 friction log, verbatim with
   provenance line) — previously chat-context-only; this carrier line is the
   pointer. Scope: prep_run entry point, --from-run, pinned provenance
   sub-schema, prep-gate lessons 1–3 as assertions, RBT-50 tool-home
   convention. **Snapshot-at-prep RATIFIED as T1 scope** (Tad, 2026-07-06):
   prep snapshots the reviewed document set into the run folder; the runner
   consumes it (RBT-51 Item 3 satisfied from below). §2 per-pass-freshness
   reading: entry provenance immutable, intra-run evolution reads the run's
   own document home (live-mode leg is n=0 design reasoning). Node-20 /
   actions-checkout@v4 ride-along landed here.
3. **RBT-53 created (High)** — D1 inherited-confidence decision record.
   Design session NOT held; ticket carries the election + five-question set
   as opening substrate. Doctype gate rules at authoring. v0.3.0 routes
   §3.4.3 authority to this record BY NAME; draw acceptance does not gate on
   it (disposition Item 7).
4. **RBT-54 created** — DDR-002 additive amendment batch (#25 scoping clause
   + ProvenanceSummary structuring). Design session NOT held. Carries the
   BUILD-gate rule (amendment before BUILD leg, or #25's 1a/1b bucket ruled
   first). Touch 2's honest floor carried: no valid finding forced it —
   economy. **Open discrepancy flagged in-ticket:** RBT-46 shows In Progress
   while RBT-15's charter cites DDR-002 v1.2.0 as binding — version chain
   verified as the RBT-54 authoring session's first act.

## Fixed facts (carried + updated)

- Audits committed at `38c7074`; prior session closed at remote develop
  `2f884a6`. Cumulative validity-precision ledger: **157/170**.
- Prompt files: develop-tip bytes sha256-verified IDENTICAL to run-011 pins,
  2026-07-06 (all five: LAA 1e2c2972…, SA 55a9059b…, EA b5c5b3bf…,
  coherence b3d7f85f…, arbiter 756b5025…). Hashes re-pin at next run prep;
  next manifest records generation 5, citing RBT-51's two event records.
- Substrate: files resolve as `<category>/<logical_id>.md`; manifest hashes
  validator-method (text, `read_text().encode()`); assembly copies, never
  moves, with post-assembly canonical-source assertion (lessons 1–3, now
  also RBT-52 acceptance criteria).
- RBT-15 HELD OPEN: criterion 2 MET; criterion 1 pending v0.3.0 + one
  verification draw + ACCEPTED ruling.

## Successor queue (ordered)

1. **Code handoff prompts for RBT-51 + RBT-52** — authored and ratified on
   this surface; one session, RBT-51 gen-events + the designed pair
   (RBT-52 snapshot ↔ RBT-51 runner consumption) implemented together.
2. **SDD-001 v0.3.0 amendment authoring** — disposition Item 2: §3.4.3
   fail-closed interim (typed rejection for confidence-less, timestamp-less
   citations), authority routed by name to RBT-53's record, values as
   config-surfaced interim defaults per §4.6; Item 5: §3.5.4 D2 pointer
   stands as written.
3. **Verification draw** — after RBT-51/52 land; prep via the new tool
   (its first live exercise); two-draw standard; zero-recurrence baselines
   (severity/cap → 0; locus inflation → 0, gating T3) get their first
   post-corrective read.
4. **RBT-15 criterion-1 close-out** upon ACCEPTED.
   RBT-53 / RBT-54 design sessions: queue-free ordering; RBT-54's BUILD-gate
   is the only hard constraint.

## Watches & ride-alongs

- Gen-6 (reviewer-side caching): own ticket AFTER gen-4/5 land — not a bus.
- T4 watch streams: stand as carried; no new instances until next run.
- Layering-invariant ADR (services-as-tools / agency-as-caller): surfaced,
  NOT ratified, NOT ticketed; rhyme-not-merger with RBT-53 ruled.
- Filesystem MCP: verified live this session (get_file_info round-trip);
  silent-timeout recovery protocol stands.

## Addendum — 2026-07-08 (post-implementation close)

RBT-51 + RBT-52 landed. PR #15, true merge `d73cb23` to develop
(2026-07-08) — commit structure preserved as designed: A `846d102`
(gen-4/gen-5), B `8a44dd0` (RBT-52 prep tool), C `b2b5f18` (RBT-51 Item 3
runner change, atomic with the run-prep contract amendment). Build fixup
`908cebc` (latent pyproject flat-layout defect, surfaced by the new CI
gate's first run) rode as a fourth commit before merge.

**Mid-implementation finding, ruled same-day (2026-07-06):** RBT-51 Item 3
conflicted with ratified `run-prep.contract.md` §2 (working-tree source
clause) and §7 (manifest document_set shape). Eight-touch amendment
(§§1,2,7,8,10) ratified and landed in Commit C — design and code moved
atomically. Contract now reads correctly against the implemented runner.

**Prompt hashes, verified at develop tip (generation-5 re-pin candidates
for next run prep manifest):**
  antagonist-LAA.prompt.md     b964d2f9f0e7cdaf1159d56ce22724b8d61a88c108231789ff1a56e2fe9b7ef1
  antagonist-SA.prompt.md      e77ffbc743b86391ed1b1231c8bc6c1d4ddddfc5cb02089f07db2c6ba9bf3859
  antagonist-EA.prompt.md      d440b7c2b19d7f6f69a42247413c124577d039eb5524bd9593e57fde428b53b0
  coherence-sweep.prompt.md    3a0ca3a14024a1c4b9b17f395c0c2510450df183adc663cfb04e53f310382299
  arbiter-classifier.prompt.md e852036bd37b01a4db1f8116cfddac739577203843a262f30ae0aa06dc786043

**Zero-recurrence baselines ARMED:** severity/cap class → 0 (gen-4);
locus inflation → 0 (gen-5, gating T3). First post-corrective read is the
SDD-001 v0.3.0 verification draw.

**RBT-51 latitude:** none — implemented per ratified scope.
**RBT-52 latitude, ruled (Tad, 2026-07-08):** (1) home split —
`agent_loop/prep.py` engine + thin `scripts/prep_run.py` CLI — ACCEPTED.
(2) N-draw manifest reading — one prepared folder per run-id, provenance
differing only in run_id — ACCEPTED WITH PROBE: **the v0.3.0 draw's prep
session must explicitly confirm two run folders emit correctly before
launch** — carried here so the probe isn't lost between now and then.

Both tickets → Done. Successor queue position 1 (Code handoff for
RBT-51/52) is CLOSED. Queue advances to position 2: SDD-001 v0.3.0
amendment authoring.

## Addendum — 2026-07-09 (verification-draw cycle close)

The RBT-15 review loop is CLOSED. Successor-queue positions 2, 3, and 4
(v0.3.0 authoring · verification draw · criterion-1 close-out) all closed
this date. **SDD-001 → ACCEPTED v1.0.0** — the corpus's first ACCEPTED
service SDD — merged to develop at `b4c3755` (PR #17, true merge; document +
run-012 artifacts + cold audit in one unit, PR #10/#14 pattern). RBT-15 and
RBT-55 both Done.

**Probe + draw.** The RBT-52 N-draw probe PASSED (two folders, provenance
identical modulo run_id); run-013 (prepared-never-launched sibling) deleted
before commit per ratified disposition — the committed artifact set carries
one launched run. Run-012: gen-5 prompts (all five hashes == the re-pin
values above), dry, HALT_DECISION @ pass 1. Cold audit by the designated
successor session, rulings ratified per item — carrier:
`agent-loop/runs/run-012-sdd-001/audit.md`. Validity 7/10; **cumulative
ledger 157/170 → 164/180.** D1 dissolved by the election-routing; Item-2
resolvables closed; D2 stands. Two audit-side finds routed to the
derivation record's question set (Δt anchor explicitness; per-class branch
totality — `DeploymentEnvironment` carries no `observed_at`).

**Armed baselines, first read.** Gen-4 severity/cap: **HOLDS** (0
instances; non-vacuous for LAA/SA, vacuous for coherence — decisive test is
the next coherence emission at cap). Gen-5 locus: **FIRES** (0→1, the
run's one resolvable locus; skill-gloss entailment its cited sections don't
carry) — **T3 promotion stays gated**; gen-5 behavioral effect not
demonstrated at n=1.

**Attribution (ruled three-way).** EA/coherence hat_null decomposed:
defect-side silence = the amendment working (their reproducible 010/011
content was entirely D1/D2, exactly the dissolved loci) — SUSTAINED; gen-4
over-correction — NOT SUSTAINED (LAA/SA hit floors exactly on identical
bytes); the empty-emission mechanics = the pre-existing run-correlated
pathology, **n=3** (first-draw empties 0/4 → 3/4 → 3/4), new datum:
re-draw non-recovery (3/3 → 1/3) — T4 watch, no corrective.

**Arbiter stream — the run's instrument headline.** 1/5 DB genuine, 4
misses on one mechanism: DB classifications carry no authority_locus, so
the de-facto validity screen never runs — the structural asymmetry the
run-011 audit §5 predicted, now load-bearing (the amendment moved the
defect surface onto document-internal-apparatus terrain). Exhibit: the
same defect classified DB (via LAA's framing) and resolvable (via SA's) —
resolving-authority frame instability; all six calls high-confidence.
**Named candidate at threshold strength, awaiting election: a DB-side
locus/validity screen (instrument design question, own deliberation).**
No corrective fired this cycle.

**Validator ride-along (PR #17 third commit, `e44a40d`).** First contact
between the RBT-50 docs-structure validator and the RBT-55 `documents/`
snapshot population: doctype-placement fired on the frozen SDD snapshot.
Root-cause fix ridden per 908cebc precedent — frozen-snapshot exemption
widened to both populations (`substrate/` + `documents/`), predicate
renamed, filename hygiene preserved on snapshots, tightness
fixture-verified (a misplaced SDD elsewhere in a run dir still fires).
**Watch/ride-along candidate:** the validator has no test harness, so the
exemption's tightness property is unpinned against future edits — rides
with the next validator-touching ticket (parked alongside the Node.js CI
warning).

**Operating-model learnings, 2026-07-09 (both sessions).**

- **Route A hybrid ratified:** the design surface may implement via
  context-quarantined subagent with pre-push review + per-transaction
  approval; the write path to GitHub is bundle-handoff (the claude.ai
  GitHub connector is READ-ONLY by design — org grants cannot change it;
  the write-capable Claude Code GitHub App is a future direct route via
  repo-bound code.claude.com environments).
- **Bridge envelope:** file transfer + ref-only git transport safe;
  index/worktree git ops strand locks (mount forbids unlink); the prep
  tool is bridge-safe (create-only, no network, no LLM). New this leg:
  read-only verification (`--no-optional-locks`) and tracked-file
  overwrites via the bridge's guarded write path both exercised clean.
- **Ticket numbers never in run artifacts or LLM-consumed files** (ruled;
  enforced in RBT-55; develop prompt files swept clean). Tickets,
  carriers, and audits are the provenance homes.
- **Handoffs embed constraints in artifacts, not prose:** base-pinned
  compare URLs; the no-merge gate written into the PR body itself; PR
  shape validated on the design surface before merge (base, head SHA,
  commit count, file count — held twice this cycle, catching nothing and
  costing minutes: the gate earns its keep on the day it catches).

**Queue state.** RBT-53 / RBT-54 design sessions: queue-free ordering,
RBT-54's BUILD-gate the only hard constraint; RBT-53's opening substrate
now carries the run-012 question-set additions. **Gen-6 ticketing is
eligible** (gen-4/5 landed) — not yet ticketed. T3 promotion remains
gated on gen-5 zero-recurrence (reset by this run's instance).
