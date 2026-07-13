# Run-017 Audit — DDR-002 v1.3.0 Review (gen-8, draw 1)

| Field | Value |
|---|---|
| **Run** | run-017-ddr-002 — first four-hat draw over the amended DDR-002 (landing-state substrate) |
| **Document** | DDR-002 v1.3.0 staged — content sha256 `1816317c…` (pre-revision state; revisions below supersede) |
| **Instrument** | gen-8 (empty-emission floor prompt-side + recency review directive + rule 8; run-016's pathology remediated — see `run-016-ddr-002/invalid.md`); E2′ seam list via coherence addendum; all-hats-null guard armed; `stop_reason` captured |
| **Draw health** | 4/4 hats substantive first draw (2,239–3,388 output tokens, all `end_turn`); 0 re-draws; 0 `hat_null`; POSITIVE caps held 2/2/2/2; arbiter 16/16 classified (8 decision-bearing / 8 resolvable), 0 retries |
| **Audit** | Cold audit, 2026-07-13 session (claude.ai surface); every finding's claimed entailment verified against staged bytes; every arbiter `authority_locus` checked; rulings ratified per item by Tad (P-1) |
| **Companion** | run-018 (verification draw over the revised text — operator-elected, run-012 pattern) |

## §1 Scope & method

24 findings (10 MATERIAL / 6 COSMETIC / 8 POSITIVE); 16 classified. Verdict vocabulary per the
run-009/010/011 audits: TRUE / TRUE- / OVER / FALSE-POS / HELD-MIS-SEV. Verification substrate:
the staged landing set + ADR-001/ADR-002/DDR-001 (staged from the branch tree, hash-matched to
the run manifest) + the run-017 ledger.

## §2 Per-finding rulings

| # | id | hat | sev | cls | verdict | basis (one line) |
|---|---|---|---|---|---|---|
| 1 | a7445003 | LAA | M | DB | **OVER** | cited skill text (over-documentation) doesn't entail the defect; substance carried by #15 at the correct citation |
| 2 | ea4bd37a | LAA | M | res | **OVER** | deliberate two-justification split (ruled v1.2.0 text) — exemplar warrant "stands as authored" |
| 3 | e9271a9d | LAA | M | res | **TRUE-** | declaration-scope vs derivation-semantics boundary genuinely blurry; the clause is a ratified schema-side scoping (deliberation D3); no change |
| 4 | b0e37dbe | LAA | C | DB | **OVER** | claims "undeclared dependency" — the cited Change Log row itself declares it (A-3, alignment obligation named) |
| 5 | 1969b328 | LAA | P | — | **TRUE** | Decision-block ↔ body ownership mapping verified |
| 6 | f2247900 | LAA | P | — | **TRUE** | Touch-1 re-scope carries no smuggled retraction of #21 — verified |
| 7 | 05ce312a | SA | M | DB | **TRUE** | real unnamed case: post-materialization re-decision of an executed retraction (the #15-flip analogue) — named only for promotions. **→ P-3 revision** |
| 8 | 040bdb6d | SA | M | DB | **OVER** | zero-evidence rollup case explicitly deferred to the SDD in the same §4 sentence — disclosed routing, not silence |
| 9 | b5b4683f | SA | M | DB | **TRUE** | verified vs §3 edge grammar: #10's Condition half (a v1.2.0 extension) requires `GOVERNED_BY`/`MANDATES` structure never defined for `Condition` — latent defect, #21/#25 genus. **→ P-2 revision** |
| 10 | ee1a2a2a | SA | C | res | **TRUE-** | exemplar literal omits `property_schema`, which #26 keys on. **→ P-5 revision** |
| 11 | 0a1622fb | SA | C | DB | **TRUE** | the F-i ticket-ID inventory item arriving as pre-ratified. **→ CR-6 (cold-read gate)** |
| 12 | 3af76a2d | SA | P | — | **TRUE** | #15 well-definedness under strict monotonicity — verified (run-010 credit lineage) |
| 13 | 47abca26 | SA | P | — | **TRUE** | provenance-survival span closure — verified incl. the two Evidence-reaching paths |
| 14 | a9fba72d | EA | M | res | **OVER** | discharge coupling is reciprocal and atomic in the landing set (DDR-004 v1.1.0 records it); the named risk doesn't obtain |
| 15 | d9cf31fb | EA | M | DB | **TRUE-** | Rationale's empirical-warrant line exists verbatim; Touch 2 closed ahead of an instance — real tension, twice-ratified as an economy exception (Item 4 + C1), floor carried. **→ P-6 revision (ruled-exception clause)** |
| 16 | e64b168f | EA | M | res | **OVER** | the A-W-C→ACCEPTED ride was RBT-53 close ruling R1's explicit design; landing-state coherent |
| 17 | 09ca64e5 | EA | C | res | **TRUE-** | the A-14 References-convention question resurfacing where A-14 scheduled it. **→ F17 ruling at gate: upstream-only stands** |
| 18 | bf67e807 | EA | P | — | **TRUE** | exposure-window timing posture — verified |
| 19 | 47c7c67b | EA | P | — | **TRUE** | routing discipline vs forthcoming siblings — verified |
| 20 | 35b9a7fc | coh | M | DB | **TRUE** | #26 keys on `property_schema`'s label set with nothing binding `confidence_basis`'s key set to it — well-formedness gap. **→ P-4 revision (key-set equality)** |
| 21 | 43fa2c0f | coh | C | res | **TRUE-** | accurate observation of the A-3 delta; disclosed in-row; alignment obligation stands |
| 22 | 2b91586c | coh | C | res | **OVER** | the row enumerates *additions* (two); the other two arrays pre-date at v1.1.0 — the arbiter's own locus (C1) refutes the claim |
| 23 | 82cec953 | coh | P | — | **TRUE** | seam 2 (basis annotations ↔ DDR-004 §4) verified no-drift, all six dispositions verbatim |
| 24 | 0bd2b0e1 | coh | P | — | **TRUE** | seam 1 (#25 ↔ #21 ↔ SDD-001 §3.5.4) — the Item-B acceptance walkthrough independently reproduced, rejected-retraction case included |

## §3 Scorecard & observations

| Metric | Value |
|---|---|
| Findings ruled | 24/24 |
| Validity | 17/24 — 4 TRUE · 5 TRUE- · 8 POSITIVE-TRUE · **7 OVER** |
| Arbiter | 16/16 classified; loci clean (two functioned as de-facto rebuttals — #17, #22: the locus-as-validity-screen pattern, DB-side this time) |
| Families | F1+F15 (Touch-2 warrant, cross-hat) — resolves to a ratified ruling with one TRUE- survivor; F4+F21 (`PlaneDefinition`) — expected-by-ruling pair. No family-grade defect survives |
| New-defect yield | 2 latent pre-batch defects found (#9: #10's Condition half; #7 as a gap-naming): the review paying for itself beyond the batch |

**Instrument observation (gen-8 cost profile):** the 7 OVERs skew to a new class — de-deferenced
reviewers re-attacking ratified-and-disclosed decisions (findings 4, 14, 16). This is the accepted
cost of the run-016 remedy: gen-8 trades deference for ruled-decision re-surfacing, absorbed
correctly by the arbiter/disposition layer. Recorded for the calibration ledger.

**Escalation ruling:** operator elected a verification draw over the revised text (run-018, the
run-012 pattern) — not the E2′ family-grade escalation, which did not trigger.
