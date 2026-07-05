# Run-008 Fold-In Audit — SDD-001 Review (Aborted Companion Draw)

| Field | Value |
|---|---|
| **Run** | run-008-sdd-001 — ABORTED at pass-2 arbiter (`ArbiterParseError`, no fabricated classification; `finalized: false`) |
| **Audited** | 2026-07-04, fold-in format (companion to the run-009 audit; not a full re-derivation of stream-level checks); **rulings ratified by Tad, per item (F1–F7), 2026-07-04** |
| **Auditor** | Authored on claude.ai; substrate verified against the pinned corpus — run-008's `substrate/manifest.json` is **sha-identical to run-009's, all nine files** (same bytes; all verifications transfer) |
| **Corpus** | SDD-001 v0.1.0 PROPOSED; authorities ADR-001 v1.1.0 · ADR-002 v1.1.0 · DDR-001 v1.3.0 · DDR-002 v1.2.0 at repo HEAD f279b1e; run HEAD e1bed19 |
| **Scope** | The full admitted set: pass-1 (15: 7M, 2C, 6P — ledgered) + pass-2 (8: 5M, 1C, 2P — emission-only; the abort preceded their ledger write). The abort mechanics themselves are audited in the run-009 audit §5a; the pass-1/pass-2 empty emissions (LAA, SA) in §5b. |
| **Purpose** | Rule the admitted findings so the SDD-001 v0.2.0 revision draws from the ratified **run-008 ∪ run-009 union** (run-009 audit §2: ≈zero defect overlap on identical bytes). |

## 1. Dedup map (rulings keyed to clusters, not emissions)

| Cluster | Members | Keeper | Note |
|---|---|---|---|
| D3-008 — 1b required-flip | 5f7c1196 (p1), 9e8ad389 (p2) | p2 (sharper) | EA pass-2 re-emission of its own pass-1 find |
| D4-008 — DDR-003 predicate timing | 41298a93 (p1), eba07f8 (p2) | p1 | EA re-emission; **eba07f8 is the abort finding** — it dies here as a dup of its own sibling; the abort cost the run nothing substantive |
| D5-008 — KG-entry cross-origin timing | 89daf7f1 (p1), 5275077 (p2) | p1 | EA re-emission |
| D6-008 — pin-resolution mapping | dea78865 (p1, SA, M), f7e4db33 (p2, LAA, C) | SA M | **Cross-hat migration datum #5** (SA→LAA, severity decayed) |
| Cross-run — disclosed-TODO species | da1f9990 ↔ run-009's 8c4f855e (ratified R4) | — | R4 precedent governs |
| Cross-run — POSITIVE stability | b27046↔0f85a6b2; e83e5c5d/06205e779/ec892345↔f0f72c9d/b7d57a70 | — | see §4 |

## 2. Per-finding rulings — RATIFIED (Tad, per item, 2026-07-04)

### Walked items

| id(s) | sev | validity | ruling |
|---|---|---|---|
| **31cf1fc8** (coherence p1) | M | **TRUE** | **F1 — ratified: ROUTE.** §3.5.3 supplies ProvenanceSummary internal structure (keyed-by-`evidence_id` entries + a per-entry source-node reference — a third content element) that DDR-002 §4 defines with exactly two properties and **expressly names the internal structuring a gap**, closable only by additive DDR-002 amendment on a real instance. Same family as run-009's 24b85a37; strongest run-008 keeper. **Disposition:** v0.2.0 constructs per the ratified two-property contract; the keyed structure (incl. source-node reference) is recorded as **named proposed content for a future additive DDR-002 amendment**. Empirical floor: n=0 promotions; no instance pressure to close early. |
| **49b7f966** (SA p1) | M | **TRUE** | **F2 — ratified: ROUTE (option i).** The SDD's at-materialization `RETRACTS` timing stands (grounded in DDR-002 §5's own retraction gloss; a proposal-time edge would be inert and muddy #21) — but the standing pre-decision window makes #25's biconditional literally unsatisfiable as ratified, and the SDD's "harness catch-up" coordination note would scope a check's *implementation* away from its ratified *text*. **Disposition:** v0.2.0 replaces the note with a named routing — the #25 scoping clause (biconditional scoped to executed/terminal proposals) is **proposed additive DDR-002 amendment content**, joining F1 in the same batch. The harness implements from ratified text only. |
| **5f7c1196 + 9e8ad389** (EA p1+p2, deduped) | M | **TRUE-** | **F3 — ratified, MATERIAL, with the bounding-clause fix.** The moving-set posture is correct and charter-grounded ("plus the triage additions" ≈ as-it-stands; a frozen list would rot mid-RBT-48) — but §7.2's "as it stands at build time" is textually **unbounded**: nothing says where new 1b contracts may come from. **Fix:** one clause — the flip obligation covers the 1b set **as derived from DDR-002 §7's ratified invariant set (including ratified additive amendments) at build time**. Movement stays; it moves only within a ratified boundary. |
| **e848295** (coherence p1) | M | **OVER** | **F4 — ratified.** Mechanism misreads the layering (the 4ed4046d/R1 class): schemas fix shapes, SDDs assign contract details within upstream authorship grants — and the grant exists (DDR-001 marks `Evidence` ASA-authored; `weight` is reasoning content riding a Species-1 ASA write). Caller-supplies-weight is a declared SDD-level contract decision, not a smuggled authorship split. The sentence's only true defect ("fixed derivation, executed not authored") **is be9b148e**, found independently and more precisely by run-009 SA, ratified TRUE, fix riding the R6 docket ruling. Residue after subtracting be9b148e: zero. |
| **586bfe0c** (LAA p2) | M | **OVER** | **F5 — ratified.** Category confusion: the execute/author dichotomy is a *write-authorship* claim (ADR-002 §2.6); hosting predicate evaluation in-process is an *architecture* choice — and executing semantics single-sourced elsewhere (§4.2 prohibits a gateway-local fork) is the definition of executing-not-authoring. The disclosure demand targets the wrong surface: the commitment is declared exactly where record discipline puts it (§2.1 line item, §4.2 full treatment, §2.2 routing). Unlike ratified 38ed4fc0, this absolute survives the body intact. The finding concedes its own case mid-claim ("which is within claim"). |
| **114ba295** (LAA p2) | M | **OVER** | **F6 — ratified.** "Provisional by declared design" ≠ "not decided": nine operations fully specified, binding conventions fixed, plus a decided **evolution rule** (additive only, consuming-SDD-driven) with the empirical floor stated in the same sentence ("ahead of any synthesis run") and the corpus's own precedent named (DDR-002's provisional index set). Jurisdictional test across the family: undeclared (24b85a37 → TRUE-), reserved-upstream (31cf1fc8 → TRUE), granted-and-exercised (e848295 → OVER), **declared-warranted-precedented (this → OVER)**. No residual sliver. |

### Block items (F7, ratified as stated)

| id(s) | sev | validity | ruling |
|---|---|---|---|
| **dea78865 + f7e4db33** (SA p1 M + LAA p2 C echo, deduped) | M | **TRUE** | §3.4.3 asserts pin resolution executed and §7.1 cites it as satisfying DDR-001 check 5, but the input-to-pin mapping is undeclared (business-key citation → which retained version? already-superseded target → what behavior?). DDR-002 §4/§5/§6 fix the pin's shape, not the resolution rule. **v0.2.0 authoring inclination (not ruled):** no resolution at capture — the request carries the explicit version reference the retrieval envelope already supplied (evidence pins what the reasoner actually read); superseded versions legal by design. Keeper: SA MATERIAL. |
| **da1f9990** (SA p1) | C | **TRUE-, no action** | Disclosed routed-not-invented cross-reference to the unauthored cost-estimation SDD; R4 precedent (8c4f855e) governs. Third instance of the disclosed-TODO-re-reported species for the calibration file. |
| **41298a93 + eba07f8** (EA p1+p2, deduped) | M | **TRUE-** | Timing exposure real but bounded in the safe direction: fail-closed (§4.4) makes the worst reachable state over-*exclusion*, never over-admission. The soft spot is the *argument*: "not blocking by construction" leans circularly on DDR-003-gates-the-loop when DDR-003 is the unauthored thing (the ratified fact is the EA gate's existence per DDR-001 Decision.5; the criteria are DDR-003's). **Fix:** v0.2.0 re-grounds the not-blocking claim on fail-closed as the load-bearing control, the gate's ratified existence secondary. |
| **89daf7f1 + 5275077** (EA p1+p2, deduped) | M | **TRUE-, no design change** | The block-and-surface interim precedes the KG-entry-governance ADR but is the *only* #22-conforming interim (silent admission violates a ratified safety-critical check), fully disclosed, escalation path named, nothing structural persists (a rejection branch, trivially unwound). Optional rider: cite DDR-002's safe-interim language ("surface-to-EA as a scope-conflict, never silent auto-composition") in §3.5 as the posture's explicit warrant. |
| **dd5fe59c** (coherence p1) | C | **TRUE** | §3.3.8 traversal notation reads two parallel inbound edges (`MATERIALIZES_PROVENANCE_OF`, `DECIDED_ON` — both →CandidatePromotion per DDR-002 §5) as sequential. Reachability unaffected; wording fix. |
| **POSITIVEs ×8** — p1: e83e5c5d, 0c8b53d6, 06205e779, 98aa3134, b27046, 8b9543e; p2: ad4819f7, ec892345 | P | **TRUE (all)** | All verified against substrate as genuine holds. Cross-run/cross-pass stability note → §4. |

## 3. Pass-2 behavior under dry mode (no doc change; pass-1 ledger in context)

First observed data on what a second antagonist pass does when nothing changed: **EA re-emits** (3/3 of its pass-2 MATERIALs restate pass-1 finds, sharpened — consistent with EA's big-target stability from run-007 §2); **SA zeroes** (empty emission — the §5b variance-to-zero mode); **LAA reaches** (2 genuinely new MATERIALs, both ruled OVER — summary/framing-layer attacks after the fresh-surface supply thinned, plausibly anchored on the 38ed4fc0 class; plus 1 cross-hat echo at decayed severity). Net new true defect yield of pass 2: **zero** (the one TRUE contribution, f7e4db33, is a dup). Implication held, not concluded: in dry mode without doc changes, a second same-run pass is near-pure cost — the plateau/pass logic and the union-over-runs question should be considered together (a fresh *run* found disjoint defects; a second *pass* found none). → queued operating-mode deliberation.

## 4. Cross-run POSITIVE stability (roster file)

The write-authorship/Species-2 credits reproduced across both runs and both passes (b27046↔0f85a6b2; e83e5c5d/06205e779/ec892345↔f0f72c9d/b7d57a70). POSITIVEs are markedly more stable than defects — consistent with credits targeting the largest declared surfaces, the same size-stability relation run-007 observed on EA. Recorded; no roster conclusion.

## 5. Dispositions out of this fold-in

- **Consolidated SDD-001 v0.2.0 work order (run-008 ∪ run-009, all rulings ratified):**
  1. Confidence-function family per the **R6 docket ruling (option c)**: rollup + zero-evidence posture routed to the solutioning-agent SDD; §7.1 ADR-001 §6.2 row scoped honestly; §8 gains the non-gating evidence-less-conclusion disclosure surface; Evidence inheritance derivation table declared here as an SDD determination (authoring inclination); be9b148e/01feb783 citations re-scoped accordingly.
  2. `PRODUCED`-edge authorship declared in §3.4.5, phrased to cover the `CONTAINS` sibling (R2).
  3. §1 sole-read-boundary absolute scoped to ground-truth reads, audit ops named as the disclosed exception (R3).
  4. §7.1/§3.5.3 #15 row split: monotonicity precondition by-construction; #15 itself CI/harness with the gateway's at-materialization verification named (R7/7272d2b5).
  5. ProvenanceSummary constructed per DDR-002's two-property contract; keyed structure re-homed as named amendment content (F1).
  6. #25 coordination note replaced with the named DDR-002-amendment routing (F2).
  7. §7.2 1b-flip bounding clause: the set as derived from DDR-002 §7's ratified invariant set incl. ratified additive amendments (F3).
  8. capture-evidence input-to-pin mapping declared (F7a; inclination: explicit version reference required, no capture-time resolution).
  9. §4.2/§3.5 not-blocking argument re-grounded on fail-closed (F7c).
  10. Optional riders: §3.2 invocation-authority clarifying clause (R1); §3.5 safe-interim warrant citation (F7d); record-level own-determinations note (79063465); §3.3.8 arrow-notation wording (F7e).
- **Two-item DDR-002 additive-amendment batch (proposed, named, not opened):** (i) ProvenanceSummary internal structuring — the keyed-by-`evidence_id` structure incl. per-entry source-node reference (F1); (ii) #25 scoping clause — biconditional scoped to executed/terminal proposals (F2). Both follow the Named-Gaps/additive discipline; timing rides the empirical-warrant rule and Tad's call.
- **No corpus triage items** — every ruling lands in the SDD's own revision cycle or the named amendment batch.
- **Findings-about-instrument:** pass-2 dry-mode behavior (§3) + cross-hat migration datum #5 (§1) + cross-run POSITIVE stability (§4) → queued operating-mode deliberation / roster file. Disclosed-TODO species at n=3 (da1f9990, 8c4f855e, f7e4db33-adjacent) — watch, no prompt change.
- **Precision (run-008 set):** 21 rulings (13 clusters + 8 POSITIVEs) — 18 TRUE or TRUE-with-caveat, 3 OVER, 0 FALSE-POS, 0 fabrications. **Cumulative across audited runs: 121/128.**
- **Commit:** this fold-in audit joins the run-008 folder (abort record, `finalized: false` preserved as-is) and travels with the run-009 audit; git transaction is Tad's.
