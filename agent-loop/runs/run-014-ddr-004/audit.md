# Run-014 Audit — DDR-004 v0.1.0 Review (Draw A of 2)

| Field | Value |
|---|---|
| **Run** | run-014-ddr-004 (draw A of the RBT-53 two-draw sequence — the corpus's first DDR review) |
| **Document** | DDR-004 v0.1.0 PROPOSED — snapshot sha256 `bc69dc6b…` **recomputed against the reviewed bytes** (== both draw manifests == the canonical `docs/ddr/` copy at the corpus tip); reviewed AS-AUTHORED, deliberately carrying the six held check-D lines |
| **Corpus tip** | `f377f625` (prep/rbt-53-ddr-004-integration; develop `9236625` an ancestor). Substrate = the ratified RBT-57 9-item DDR recipe; all 18 frozen files (9 × 2 draws) sha256-recomputed == the substrate manifests; cross-draw byte-identical; **zero SDD-cycle artifact leakage** (byte-verified); frozen canon byte-equal to the working-tree canonical docs |
| **Mode** | dry · HALT_DECISION:decision-bearing @ pass 1 · 199.3s · **EA hat_null** (two `[]` emissions, 4 output tokens each; the run's one `llm_retry` is the EA below-floor reviewer re-draw, which did **not** recover — the execution report's "transient llm_retry (recovered)" is corrected here) · LAA/SA/coherence clean first emissions · 0 parse drops · 0 aborts |
| **Prompts** | generation 5; all five hashes == the gen-5 re-pin — **four-source agreement** (both draw manifests · run-012 manifest · the 2026-07-06 carrier addendum · recomputed from the working-tree prompt bytes) |
| **Audit** | COLD audit, 2026-07-11 successor session (the authoring surface authored DDR-004 **and** its deliberation record — recused). Every locus verified against the run's own hash-verified frozen substrate; all emission bodies mechanically field-exact vs their ledger rows; rulings ratified per item by Tad |
| **Companion** | run-015-ddr-004/audit.md (draw B + the union fold-in; §3–§6 union scope live there) · run-015-ddr-004/disposition.md (the ratified disposition record, D1–D7) |

## §1 Scope & method

19 findings (10 MATERIAL / 3 COSMETIC / 6 POSITIVE); 13 classified (6 decision-bearing / 7 resolvable).
Verdict vocabulary per the run-009→012 lineage: TRUE / TRUE- / OVER / FALSE-POS / HELD-MIS-SEV; stance
ON/OFF/AMB. Every finding's claimed entailment checked against the frozen substrate bytes at its locus;
every arbiter authority_locus checked against the cited source's own text. First DDR review — no prior
DDR draw to union against; the method is the SDD reviews', two-draw union conventions per runs 010/011.
The eight ratified positions in the deliberation record are the design intent DDR-004 traces to;
findings reopening a ratified position were handled as re-evaluation candidates (explicit override
required), not auto-accepted or auto-dismissed. Union-scope analysis → companion §3–§6.

## §2 Per-finding rulings

| # | id | hat | sev | locus | verdict | basis (one line) | stance |
|---|---|---|---|---|---|---|---|
| 1 | 551d512f | LAA | M | §4 DeploymentEnvironment + Cond. 1 | **OVER** | "Fix-vs-propose not disambiguated" contradicted by the record's own apparatus (§4's closing amendment declaration; Cond. 1's RBT-54 routing) and the in-substrate Authoring notes; the skill's conditional-DDR pattern. LAA scope-species (092118bf lineage); valid tense residue credited at #10 | ON |
| 2 | b479937f | LAA | M | Decision preamble vs §6 | **OVER** | Preamble verbs accurate at the level claimed: "constant *treatment*" ≠ values; "calibration *governance*" ≠ result. Ratified Items 1/8 drew exactly this line; the arbiter's locus is the finding's rebuttal | ON |
| 3 | 0f93e458 | LAA | M | §3 Reconstructible vs §6/Cond. 2 | **TRUE-** | Core: §3 present-tense property, mechanism Condition-2-gated, DDR-002 §4 supplies no capture-instant meaning (verified). Caveats: "either way" clause makes the property fork-independent; nothing concealed. Fix rides revision (D2a) | ON |
| 4 | 8c502c3c | LAA | M | Reconciliation "no content change" | **OVER** | "Asserts rather than surfaces" fails against in-substrate design intent (Authoring notes routing-satisfaction ruling; RBT-53 anchor-capture) and SDD-001 §3.4.3's own pre-cession ("this SDD does not fix one permanently"). Valid residue = companion #2 (6f5aaa1a TRUE-) | ON |
| 5 | e25bd5ff | LAA | C | check-D identifiers in body | **TRUE** | Verbatim-verified (the six held lines); skill quote exact. The pre-registered hold, formally flagged — check-D confirming datum, LAA lane. Fix = D1 | ON |
| 6 | 353dce7f | LAA | P | §2 1.0-invariant scope | **TRUE** | Determination-vs-canon declaration exact; DDR-002 §4 fixes class-inheritance + ordering, not the literal 1.0 | ON |
| 7 | e9c24932 | LAA | P | §5 composition boundary | **TRUE** | Dependency, bound, and consequence all declared and verbatim-verified | ON |
| 8 | 855242d2 | SA | M | §4 DeploymentEnvironment 0.9 vs §2's 1.0 criterion | **TRUE-** | Core: the discriminator (authority class sets the base; staleness-mode sets only the decay term) is unstated at the §4 locus and §2's two-axis drafting invites the misread. Caveats: §2 anchors 1.0 to the named authoritative planes; Item 6 ratified 0.9. **Re-evaluation declined (ratified): 0.9 stands; discriminator edit = D2c; coupling rider = D3** | ON |
| 9 | 3ed68605 | SA | M | §3/§6 Reconstructible substantiation | **TRUE-** | F-A core, bytes verify; caveats: "either way" under-engaged; disclosed and Condition-2-gated. DB genuine (the Touch-3 addendum's own fork) | ON |
| 10 | 88caf2eb | SA | M | §4 carrier claim vs DDR-002 §2.6/§7 | **TRUE-** | Verbatim-verified: PlaneDefinition carries no basis field, §7 no basis-existence constraint; §4's "is carried"/"fails registration" is present-voice ahead of the amendment. Caveat: contingency disclosed in the same block. F-B's cleanest draw-A statement; fix = D2b | ON |
| 11 | 945a8fb0 | SA | M | §4 basis-4 rejection enforcement | **TRUE-** | Verified: DDR-002 §5/§7 admit any provenance-bearing SOURCED_FROM target; rejection type genuinely unspecified (CONFIDENCE_UNDERIVABLE reserved for malformed definitions). Caveat: the place is pattern-determined (gateway at capture). Rider → RBT-54 Touch 3 (D3) | ON |
| 12 | 882de4e5 | SA | C | check-D | **TRUE** | Same verified miss, SA lane; quote exact. Confirming datum #2 | ON |
| 13 | 3694e187 | SA | P | §5 × #24 | **TRUE** | Verified incl. SDD-001 §3.3.3 returned-uncomposed | ON |
| 14 | ab3ddcd8 | SA | P | §3 Δt anchor | **TRUE** | "At snapshot time," version-pin fidelity, derive-at-capture all verbatim-verified | ON |
| 15 | 40bdc898 | coh | M | §6 `Evidence.observed_at` semantic | **TRUE-** | Sharpest F-A core: DDR-002 §4's posture paragraph pins "`source_node_version` + `observed_at`" — leaning toward the reading DDR-004 flags as fallback trigger. Caveat: the "immune to later KG drift" sentence names only `fact_summary` + `source_node_version`. DB genuine | ON |
| 16 | 21e2a2f8 | coh | M | §3 frozen / §6 re-tune | **TRUE-** | Verified: Evidence sole surrogate-only (no provenance group, no `recorded_at`). Same family core and caveats. DB genuine | ON |
| 17 | ada0828d | coh | C | check-D | **TRUE** | Third lane; extended skill quote verbatim | ON |
| 18 | 5e8fbe94 | coh | P | §5 × #24 | **TRUE** | Ceiling semantics + edge/node split verified exactly | ON |
| 19 | 7dce44f2 | coh | P | §4 Cost dispositions | **TRUE** (rider) | Load-bearing property check holds (no `confidence` on RateCard/CostFactor); rider: misquotes §2.6's italic tag for RateCard ("Reference input" is CostFactor's) | ON |

**POSITIVEs — 6× TRUE** (one citation rider), verified against substrate as genuine holds. Caps held
2/2/2 for the emitting hats — coherence at cap with zero re-labels (gen-4 read → companion §4).

## §3 Families (draw-A scope; union verdicts → companion §3)

**F-A** (reconstructibility/`observed_at`): 4 members here — 0f93e458 · 3ed68605 · 40bdc898 · 21e2a2f8, all TRUE-.
**F-B** (carrier tense/enforcement-pending): 88caf2eb TRUE- + 551d512f OVER (the scope-species re-attack on the same locus).
**F-C** (DeploymentEnvironment 0.9): 855242d2 TRUE-. **F-D** (SDD reconciliation): 8c502c3c OVER — the valid statement is draw B's.
**F-E** (check-D): three lanes, all TRUE COSMETIC.

## §4 Watch items (draw-A scope)

- **Gen-4 at cap:** coherence emitted at its 2-POSITIVE cap (2P + 2M + 1C) with no held check re-labeled — first half of the decisive-case read; completed and closed in companion §4.
- **EA hat_null:** adjudicated at union scope (companion §4, three-way attribution). Draw-local fact: both EA emissions `[]`, re-draw non-recovery.
- **LAA scope-species OVER:** 551d512f — the one-per-draw lineage continues (4dfe13af → 13e08962 → 092118bf → this).

## §5 Arbiter stream (draw A)

13/13 classifications parsed clean, zero retries; 11 high / 2 medium — and the run's calibration datum:
**the draw's one clean DB miss (8c502c3c) carried medium confidence** (run-012's four misses were all
high). DB 6: **3 genuine** (3ed68605 · 40bdc898 · 21e2a2f8) + **945a8fb0 genuine-with-asterisk** (place
pattern-determined; type open) + **8c502c3c MISS** (resolving authority in-substrate: the deliberation
record's routing-satisfaction note) + **855242d2 soft miss** (Item 6 fixed the value; the rationale gap
resolves from canon ordering). Resolvables 7/7 correctly routed, loci byte-verified; the
locus-as-rebuttal validity screen fired on 551d512f and b479937f. Null-locus asymmetry: both miss-class
calls are DB — no authority_locus, so the screen never ran — mechanism continuity with run-012 §5, at a
far better rate (union verdict → companion §5). Cache: 12 of 13 calls read 99,098 cached tokens.

## §6 Scorecard (draw A)

| Metric | Value |
|---|---|
| Findings ruled | 19/19 (13 classified + 6 POSITIVE) |
| Validity | 16/19 — 3 TRUE · 7 TRUE- · 6 POSITIVE-TRUE · **3 OVER** |
| Arbiter | DB 4/6 genuine (1 asterisked) · 1 miss + 1 soft miss (null-locus mechanism) · 7/7 resolvable routed, loci clean |
| Union + cumulative ledger | → companion §6 (164/180 → **203/224**) |

*All dispositions live in the companion folder's disposition.md (D1–D7, ratified per item 2026-07-11);
nothing in this file self-executes.*
