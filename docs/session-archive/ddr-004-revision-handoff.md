SOFIA — DDR-004 REVISION: apply the ratified disposition of the run-014/015 two-draw cold audit.
You are the AUTHORING surface for DDR-004 (you authored v0.1.0 and its deliberation record). The
review and the COLD audit are COMPLETE; every ruling and disposition is RATIFIED per item (Tad,
2026-07-11/12). Your job is faithful drafting of the ratified edits — do NOT re-litigate rulings,
do NOT reopen ratified positions; surface any drafting conflict as a question, never deviate silently.
Per-item ratification for anything not covered below. Two-surface: you draft; Code mechanizes the
validator run; git transactions are Tad's.
═══ FRESH-FETCH FIRST (pointers, not substitutes; branch prep/rbt-53-ddr-004-integration @ f377f625) ═══
1. agent-loop/runs/run-015-ddr-004/disposition.md — D1–D7 + the R1–R6 close addendum. THE BINDING SPEC.
2. run-014-ddr-004/audit.md (primary) + run-015-ddr-004/audit.md (companion + union) — ruling context;
   every edit below traces to a ratified verdict there.
3. docs/ddr/DDR-004-inherited-confidence-derivation.md v0.1.0 (sha256 bc69dc6b…, verify before editing).
4. Canon at need: DDR-002 v1.2.0 §1/§2.2/§2.6/§4/§5/§7 · SDD-001 v1.0.0 §3.4.3/§9 ·
   author-decision-record skill + ddr-template · the DDR-004 deliberation record.
5. Linear: RBT-53 (2026-07-12 comment + banner = the close rulings) · RBT-54 (2026-07-12 Touch 3
   addendum #2 = the four riders your edits must stay consistent with).
═══ THE EDITS (all ratified; disposition item in parentheses) ═══
1. (D1) Identifier sweep of the normative body — the six check-D lines (R6 ×1, RBT-53 ×3, RBT-54 ×3 in
   Rationale / Pre-Acceptance / Reconciliation) AND the beyond-regex items the reviewers flagged
   (run-009 / runs 010/011 / run-012, "union disposition Item 1") → relocate to Cross-References or
   reduce to subject-name-only. GATE: `bash scripts/validate-docs-structure.sh` (diff mode) must pass
   check D on the revised file before push.
2. (D2a) §3 "Reconstructible" restated as conditioned on Pre-Acceptance Condition 2 (the property is
   fork-independent by the "either way" clause; the phrasing, not the ruling, changes).
3. (D2b) §4 carrier tense — "The declared basis is carried in the schema" / "fails registration" →
   conditional phrasing aligned to Condition 1's forthcoming-amendment routing. One edit; it resolves
   the whole ratified F-B family (88caf2eb · 01369e21 · 480db100 · a80870ab · df2dc420).
4. (D2c) §4 discriminator sentence at the DeploymentEnvironment disposition: authority class sets the
   base; staleness-mode sets only the decay term (canon ordering, DDR-002 §4).
5. (D2d) Reconciliation qualification: "no content change FOR THIS RECORD'S ACCEPTANCE; the §3.4.3
   interim description refreshes with the RBT-54 Touch 3 landing." (The refresh rider is already on
   RBT-54 — keep the two texts consistent.)
6. (D2e) Reconciliation double-listing split: the fail-closed CONFIDENCE_UNDERIVABLE rejection
   BEHAVIOR is confirmed unchanged; its PRIMARY-CONTROL ROLE and single-case enumeration are
   superseded. Two entries, no item listed on both sides.
7. (D2f) References header + Cross-References: DDR-002 citation widened to §2.2–2.5 + §2.6.
8. (D3) DECOUPLE: DeploymentEnvironment's flat base becomes its OWN contested tunable, initialized
   0.9 (equal to the Environment aging base) — no longer the shared `base`. Touches §2 (constant
   treatment), §4 (per-class disposition), §6 (calibration scope: name its calibration basis or defer
   it explicitly). Consistent with RBT-54 addendum #2 item 2.
9. (R6) SDD-001 pointer edit — SEPARATE COMMIT in the landing PR: §3.4.3 body + §9 "the forthcoming
   inherited-confidence-derivation decision record" → "DDR-004"; §9 scope-enumeration refresh
   (non-exhaustive vs DDR-004's six components); change-log-carried; no other SDD content change.
═══ VERSION / STATUS (R1, ratified) ═══
Single landing at 1.0.0 ACCEPTED-WITH-CONDITIONS (conditions = RBT-54 Touch 3: declared-basis
carriers + Evidence.observed_at semantic; the constants standing condition stays non-blocking as
authored). Change Log rows carry the review-driven revision + the acceptance, citing both run audits
as carriers. Merge = the acceptance act (the standing NO-MERGE-until-ACCEPTED gate is satisfied by
the same event). Status-discharge note: A-W-C → ACCEPTED rides the RBT-54 Touch 3 landing, not this one.
═══ LANDING (R5) ═══
One base-pinned PR to develop: revised DDR-004 + the SDD-001 pointer commit (separate) + run-014/015
artifacts incl. both audits + disposition.md. At landing verify: PR shape (base, head SHA, commit and
file counts) · the docs-structure frozen-snapshot exemption stays green on substrate/ + documents/ ·
git-level confirm that develop (9236625) is the branch's merge-base (closes the audit's one named
integrity residual). Keep prep/rbt-53-ddr-004-integration @ f377f625 until landed.
═══ CLOSE ═══
RBT-53 closes with this follow-on session (Tad's R4 ruling). NOT THIS SESSION: RBT-54 Touch 3
amendment authoring (its own session); reopening any D4-bucket position.
