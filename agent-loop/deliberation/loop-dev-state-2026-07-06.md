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
