# Run-018 Audit — DDR-002 v1.3.0 Verification Draw (gen-8, draw 1)

| Field | Value |
|---|---|
| **Run** | run-018-ddr-002 — operator-elected verification draw over the revised text (run-012 pattern; companion to run-017) |
| **Document** | DDR-002 v1.3.0 staged, post run-017/cold-read folds — content sha256 `9bb0f9b3d9c9b08e44d5ca5a8fa807d67869f15fa18e285c963750232848e6a3` (pre-P18 state; P18 folds below supersede) |
| **Instrument** | gen-8 (unchanged from run-017); landing-state substrate re-manifested at the revised tree (manifest head `cda9e816`); coherence addendum; all-hats-null guard armed; `stop_reason` captured |
| **Draw health** | 4/4 hats substantive first draw (2,706–3,743 output tokens, all `end_turn`); 0 re-draws; 0 `hat_null`; arbiter 18/18 classified (11 decision-bearing / 7 resolvable), 0 retries |
| **Audit** | Cold audit, 2026-07-13 session (claude.ai surface); every claim verified against the pinned staged bytes (DDR-002 `9bb0f9b3`, SDD-001 `a6a9ddaa`, DDR-004 substrate `fbab79ce`); rulings ratified per item by Tad (P18-1) |
| **Verification question** | Did the run-017 P-closures and cold-read CR-closures hold, and did the revisions introduce defects? |

## §1 Scope & method

26 findings (14 MATERIAL / 4 COSMETIC / 8 POSITIVE); 18 classified. Verdict vocabulary per the
run-009/010/011/017 audits: TRUE / TRUE- / OVER / FALSE-POS / HELD-MIS-SEV. Verification substrate:
the staged landing set + ADR-001/ADR-002/DDR-001/DDR-004 (hash-matched to the run manifest) +
the run-018 ledger.

## §2 Per-finding rulings

| # | id | hat | sev | cls | verdict | basis (one line) |
|---|---|---|---|---|---|---|
| 1 | 385488aa | LAA | M | DB | **OVER** | economy-exception family (w/ 11, 15): twice-ratified, P-6 floor carried in-row; the Rationale's discipline is conditional ("and locking it would over-specify") — the form-fixing/zero-constants warrant occupies that residual space |
| 2 | b0d05717 | LAA | M | DB | **OVER** | Decision block claims testable components, not exhaustive enumeration; named items ride Decision.5/.7/.9 umbrellas; T-07 precedent available if it hurts |
| 3 | 5338c9d4 | LAA | M | res | **TRUE-** | family F-A (w/ 12, 21): exemplar cannot demonstrate #26's equality as authored — the P-5 gloss disclosed the elision but hid one operand. **→ P18-2 fold** |
| 4 | e3ba8126 | LAA | C | DB | **FALSE-POS** | "RBT-54 threads §7 current-state prose" is false against the pinned bytes — §7 carries zero ticket IDs (CR-6 landed); residue = the named F-ii seam |
| 5 | 9f471e17 | LAA | P | — | **TRUE** | Touch-1 three-scenario lifecycle re-verified at every call-site (reproduces the Item-B walkthrough) |
| 6 | 969f600d | LAA | P | — | **TRUE** | citable-universe boundary + citation-scoped clause verified verbatim |
| 7 | 616f18e8 | SA | M | DB | **OVER** | two-carrier split explicit (§2 preamble + Decision.11); #26 quantifies over the only machine-registered carrier; core-plane declarations are document/constants-fixed with no graph-state subject |
| 8 | 7e1eeb75 | SA | M | DB | **OVER** | Governance `flat_base` is DDR-004 §4's verbatim disposition, faithfully carried (drift-proofing). Residue: DDR-004's honest-floor sentence omits Governance citation-reachability → next-touch note, joins A-3 (**P18-5**) |
| 9 | 9a71c6dc | SA | M | DB | **FALSE-POS** | claimed audit loss doesn't obtain: `RejectedAlternative` durable, `WOULD_HAVE_USED` targets retained version nodes (never-delete), survival guarantee scoped to Evidence expiry — the empty span hides nothing. Adjacent auditor observation → **P18-6 fold** |
| 10 | 8aad4b5d | SA | M | DB | **TRUE-** | real detection asymmetry: #15 detects promotion-side flips standing; nothing detects the retraction-side flip (#21 traces to *an*, not the *governing*, approving decision; SDD verifies governing verdict only at materialization). **→ P18-3 gap-naming fold** |
| 11 | ecadca35 | SA | M | res | **OVER** | family w/ 1, 15 — arbiter locus is the ratifying deliberation record |
| 12 | 2716a247 | SA | C | res | **TRUE-** | family F-A → P18-2 fold |
| 13 | 66e9ad69 | SA | P | — | **TRUE** | monotonicity/tie-exclusion verified verbatim (§2.4, #15) |
| 14 | d529a90d | SA | P | — | **TRUE** | rollup ceiling verified verbatim (§4, #24) |
| 15 | 5f25f5c0 | EA | M | DB | **OVER** | family w/ 1, 11 — posture twice-ratified (Item 4 + C1), floor carried |
| 16 | 6e53e304 | EA | M | res | **OVER** | cross-conditioned discharge is RBT-53 close ruling R1's design; atomic at merge (run-017 #14/#16 lineage) |
| 17 | b7bf345c | EA | M | DB | **OVER** | exemplar/capability split is the ruled v1.2.0 T-08 disposition (run-017 #2 lineage) |
| 18 | 28ba7634 | EA | C | res | **OVER** | dependency-density posture is the disclosed reversibility-scoped discipline; arbiter locus functions as rebuttal |
| 19 | 3c887183 | EA | P | — | **TRUE** | basis-kind-only + fail-closed + additive re-instatement verified |
| 20 | 816d66ac | EA | P | — | **TRUE** | §7 authority split verified verbatim |
| 21 | 1c10d155 | coh | M | res | **TRUE-** | family F-A → P18-2 fold |
| 22 | 7ddc4487 | coh | M | DB | **OVER** | the Touch-3 row itself discloses the DDR-004 §4 absence (A-3, named next-touch obligation); DDR-004 substrate bytes confirm exactly the disclosed state (run-017 #4/#21 lineage) |
| 23 | a9a90cb7 | coh | M | DB | **FALSE-POS** | "not visibly scoped away from GateDecision" is false: the precedence prose lives inside the PromotionDecision bullet in candidate language; the supertype bullet carries no precedence rule; SDD §3.6.3 agrees. CR-4's gap clause and §2.4 coexist |
| 24 | 1cdfb294 | coh | C | res | **OVER** | "closed at v1.3.0" sits in a *Cross-References* bullet — the marker-level status surface by v1.2.0's ratified convention (T-15/T-18); A-8 governs contract prose, which §4 is clean of |
| 25 | 8f9a5e0b | coh | P | — | **TRUE** | Δt endpoint assignment verified verbatim at all three loci (DDR-002 §4 / DDR-004 §3 / SDD §3.4.3) |
| 26 | ce96ac26 | coh | P | — | **TRUE** | seam-1 joint-satisfiability verified incl. SDD §3.5.4's conformance note — the acceptance-item walkthrough reproduced a second time, on the revised text |

## §3 Scorecard & observations

| Metric | Value |
|---|---|
| Findings ruled | 26/26 |
| Validity | 12/26 — 4 TRUE- · 8 POSITIVE-TRUE · **11 OVER** · **3 FALSE-POS** |
| Arbiter | 18/18 classified; loci clean (several functioned as de-facto rebuttals — #11, #16, #18, #24) |
| Families | F-A (#3+#12+#21, exemplar gloss vs #26, three-hat) — resolves with one gloss line (P18-2); F1+F11+F15 (economy warrant, three-hat) — ruled, OVER. No family-grade defect; E2′ escalation did not trigger |
| Closure verification | **All run-017 P-closures and cold-read CR-closures held.** CR-6 relocation byte-verified landed; P-2/P-3/P-4/CR-4 survived direct re-attack. One revision-introduced presentational wrinkle (the P-5 gloss family), one line to close |
| New-defect yield | 1 latent gap-naming find (#10: retraction-side detection asymmetry) + 1 auditor-adjacent clarity fold (`WOULD_HAVE_USED` rebind annotation) |

**Instrument observations (calibration ledger):** (1) the OVER skew (11) is the known gen-8 cost
profile — de-deferenced reviewers re-attacking ratified-and-disclosed decisions; absorbed correctly
by the arbiter/disposition layer. (2) **FALSE-POS is a new verdict class for this instrument** (first
appearance; run-017 had zero): three findings asserted factual predicates refuted by the reviewed
bytes themselves (§7 ticket-ID state, §2.4 scope placement, retention semantics). Wrong-reading,
not fabrication — recorded for the calibration ledger.

**Escalation ruling (P18-7):** no third draw. The verification draw did its job — closures held; the
folds are cold-read-class (no decision content). Fold, re-pin, land.
