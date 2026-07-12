# Union Disposition Record — DDR-004 v0.1.0 (runs 014 ∪ 015)

| Field | Value |
|---|---|
| **Session** | RBT-53 cold-audit session, 2026-07-11 (claude.ai surface; COLD successor — authoring surface recused) |
| **Basis** | Run-014 + run-015 audits (companion pair, this folder + run-014's), 44/44 findings ruled, rulings + union analyses (U1–U6) ratified per item |
| **Rulings** | Seven disposition items (D1–D7), each ratified individually by Tad, 2026-07-11 |
| **Status** | RATIFIED — execution sequenced below; nothing in this record self-executes. NO-MERGE until DDR-004 ACCEPTED (per the ticket's standing gate) |

## D1 — Check-D revision items (the pre-registered hold, formally flagged; RATIFIED)

The six flagged lines (mechanically reproduced against the frozen snapshot: Rationale line 1 ·
Pre-Acceptance 4 · Reconciliation 1; identifier instances R6 ×1, RBT-53 ×3, RBT-54 ×3) relocate to
Cross-References / reduce to subject-name-only — **plus** the reviewer-flagged identifiers outside the
validator's regex (run-009/010/011/012, "union disposition Item 1"). Clears check D before push. The one
severity variance (9bddf949's MATERIAL vs four COSMETIC lanes) is recorded here and dissolves with the fix.

## D2 — Substantive revision edits (ratified rulings → document actions; authoring surface drafts; RATIFIED)

- **a.** §3 "Reconstructible" conditioned on Pre-Acceptance Condition 2 (F-A).
- **b.** §4 carrier tense — "is carried in the schema" / "fails registration" aligned to Condition 1's
  forthcoming-amendment routing (F-B; one edit resolves five findings).
- **c.** §4 discriminator sentence — authority class sets the base; staleness-mode sets only the decay
  term (F-C; 855242d2 rider).
- **d.** Reconciliation qualification — "no content change *for this record's acceptance*; the §3.4.3
  interim description refreshes with the RBT-54 Touch 3 landing" + the paired refresh rider written onto
  RBT-54 Touch 3 (F-D; 6f5aaa1a).
- **e.** Reconciliation double-listing split — fail-closed rejection *behavior* confirmed unchanged; its
  *primary-control role and single-case enumeration* superseded (61f87db6).
- **f.** References/Cross-References header widened to §2.2–2.5 + §2.6 (0b94cfae).

## D3 — Decision rider: decouple the DeploymentEnvironment flat base (RATIFIED)

da6eccd6 exposed that DDR-004 as authored couples DeploymentEnvironment's flat base to the same `base`
tunable §6 calibrates exclusively from aging-fact evidence — a re-tune would silently move a non-aging
class the calibration never measured. **Ruled: decouple** — DeploymentEnvironment's flat base becomes
its own contested tunable, initialized 0.9 (equal to the Environment aging base), its calibration basis
named or explicitly deferred. Touches §2/§4/§6 in the revision + the matching tweak to RBT-54 Touch 3's
§2.2 annotation (currently "the Environment base"). Item 6's 0.9 value and Item 3's invariant split
stand untouched. Riding here: 945a8fb0's rider — RBT-54 Touch 3 specifies the basis-4 rejection *type*
(and whether a conformance note joins the amendment).

## D4 — Already-ruled bucket: re-evaluation declined, no reopen (RATIFIED)

The F-A fork (Item 8 + the Touch-3 addendum stand — seven findings *confirm* the ratified verify-intent
gate) · F-D's routing satisfaction (the RBT-53 anchor-capture stands) · Item 6's 0.9 election (declined
at draw-A #8) · Items 3 and 7's boundary rulings (the union's two large credit clusters). The review's
weight on the eight ratified positions is confirmation, not contradiction.

## D5 — No-action bucket: the five OVERs (RATIFIED)

551d512f · b479937f · 8c502c3c · a975e568 · 8a01ef39 — no document defect exists; all draw-local;
species named in the union table (audit §3).

## D6 — Acceptance-posture input (RATIFIED)

9e710b13 routes to the acceptance act: the record's shape — sound design, two DDR-002 amendment
prerequisites tracked on RBT-54 Touch 3, standing non-blocking constants condition — is the template's
ACCEPTED-WITH-CONDITIONS case. The status ruling itself is made at close, not here.

## D7 — Instrument dispositions (consolidating ratified U3–U6; RATIFIED)

T4 EA-streak watch continues (n=3 EA-only first-emission empties; re-draw recovery 5/8), no corrective;
recipe-level note: single-draw DDR reviews cannot currently rely on the EA lane — the two-draw union is
the operative mitigation · gen-4's coherence-at-cap watch **closes** (decisive case tested, 0 instances,
non-vacuous all hats) · gen-5 baseline holds at cumulative 1 with the a80870ab borderline recorded as
non-firing; **T3 stays gated** (first clean read post-reset) · the DB-side-locus/validity-screen
candidate gains this run's data (10/13 genuine; miss-class calls all on design-intent-resolvable
ground), remains unelected pending its own deliberation · the 13 dry-mode proposed escalations → **no
tickets opened** (content fully absorbed into D1–D6) · the execution report's "llm_retry (recovered)"
wording corrected in the audits (the retries are the EA below-floor re-draws; draw A's did not recover).

## Execution sequence (consolidated)

1. **DDR-004 revision → the authoring surface** (recused from this audit): D1 sweep + D2a–f + D3's
   §2/§4/§6 decouple edits; check D cleared before push; v0.1.0 → v0.2.0 PROPOSED.
2. **RBT-54 Touch 3 riders** (adjacent-ticket write — authorized only on explicit ratification at the
   capture step): §3.4.3 interim-description refresh (D2d) · §2.2 annotation tweak + decoupled-tunable
   note (D3) · basis-4 rejection-type specification (D3/945a8fb0).
3. **One-unit landing:** run-014 + run-015 artifacts + both audits + this record + revised DDR-004 in a
   single base-pinned PR to develop (PR-shape check at landing: base, head SHA, file count; the
   docs-structure frozen-snapshot exemption covers `substrate/` + `documents/` — verify at landing);
   `prep/rbt-53-ddr-004-integration` @ `f377f625` retained until the artifacts land.
4. **Status ruling at acceptance** (D6 input): PROPOSED → ACCEPTED-WITH-CONDITIONS on the RBT-54 DDR-002
   prerequisites, ruled at the capture step.
5. **SDD-001 pointer resolution at acceptance:** §3.4.3 + §9 subject-name sites resolve to "DDR-004";
   §9 scope-enumeration refresh rides the same change-log-carried edit.
6. **RBT-53 three-layer capture** (comment + description prefix + workflow state) on the decided-upon
   ticket; adjacent tickets read-only except as authorized in step 2.

## Close addendum — R1–R6 ruled per item (Tad, 2026-07-12)

- **R1 (status):** ACCEPTED-WITH-CONDITIONS, conditions = the RBT-54 Touch 3 prerequisites; single
  landing at **1.0.0**, merge = the acceptance act (NO-MERGE gate satisfied by the same event).
  **Condition discharge is pinned:** when RBT-54 Touch 3 lands, DDR-004's status change
  (A-W-C → ACCEPTED) rides that landing — captured on RBT-54 (2026-07-12 comment, item 4).
- **R2 (revision):** handoff prompt issued to the authoring surface; scope = D1 sweep + D2a–f + D3;
  check D cleared before push.
- **R3 (adjacent write):** authorized and executed — RBT-54 Touch 3 addendum #2 (four riders,
  2026-07-12 comment).
- **R4 (closure):** RBT-53 stays In Progress; the follow-on session that applies the fixes and
  re-reviews closes it. Three-layer capture executed 2026-07-12 (comment + description banner +
  state-unchanged ruling).
- **R5 (landing):** ratified as sequenced in step 3 above.
- **R6 (SDD-001 pointers):** same landing PR, **separate commit** for the SDD-001 pointer-resolution +
  §9 scope-refresh edit.
