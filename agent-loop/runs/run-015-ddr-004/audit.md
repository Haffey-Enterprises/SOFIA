# Run-015 Audit — DDR-004 v0.1.0 Review (Draw B of 2) + Union

| Field | Value |
|---|---|
| **Run** | run-015-ddr-004 (draw B of the RBT-53 two-draw sequence) |
| **Document** | DDR-004 v0.1.0 PROPOSED — snapshot sha256 `bc69dc6b…` recomputed against the reviewed bytes; byte-identical to draw A's (same-input, same-prompt, k=2 sample confirmed) |
| **Corpus tip** | `f377f625` — identical across both draw manifests; all five prompt hashes identical (gen-5 re-pin, four-source agreement per the primary) |
| **Mode** | dry · HALT_DECISION:decision-bearing @ pass 1 · 256.9s · EA below-floor first emission (`[]`, 4 output tokens) **recovered on one re-draw** with a full valid stream · 0 hat_null · **all four hats at the 2-POSITIVE cap** · 0 parse drops · 0 aborts |
| **Audit** | COLD audit, same successor session and hash-verified substrate as the primary; emission bodies mechanically field-exact vs ledger rows; rulings ratified per item by Tad |
| **Companion** | run-014-ddr-004/audit.md (primary). This file carries the union table and all union-scope analysis (§3–§6); disposition.md (this folder) carries the ratified D1–D7 |

## §1 Scope & method

25 findings (15 MATERIAL / 2 COSMETIC / 8 POSITIVE); 17 classified (7 decision-bearing / 10 resolvable).
Method identical to the primary. This draw's classified set includes the recovered EA's three MATERIALs —
the decisive input to the union's EA-divergence adjudication (§4).

## §2 Per-finding rulings (draw B)

| # | id | hat | sev | locus | verdict | basis (one line) | stance |
|---|---|---|---|---|---|---|---|
| 1 | a975e568 | LAA | M | Decision/title vs §4/§6 amendment content | **OVER** | "Decide-vs-entail not cleanly separated" contradicted by §4's amendment declaration + Cond. 1 + the in-substrate Authoring notes; DDR-004 decides the dispositions, RBT-54 Touch 3 carries "only the mechanization it entails." LAA scope-species, draw-B instance | ON |
| 2 | 6f5aaa1a | LAA | M | Reconciliation "no content change" | **TRUE-** | F-D's valid statement: the unqualified sentence overstates — SDD-001 §3.4.3's interim description ("Environment-class treatment" heuristic; "the known reachable case") is substantively superseded, so a downstream SDD content touch is entailed (Touch-3-coupled, not acceptance-gated). Caveats: §3.4.3 pre-authorizes the supersession; ratified routing-satisfaction untouched. **Codification-refinement (ratified): D2d qualification + RBT-54 refresh rider; anchor-capture unopened.** DB genuine-with-asterisk (acceptance-scope half had authority; downstream half genuinely unruled) | ON |
| 3 | 01369e21 | LAA | M | §1/§4 totality vs unbuilt carrier | **TRUE-** | F-B core verified; caveats: in-line disclosure; "current planes only" recasts a design contract as an empirical claim. Rides D2b | ON |
| 4 | 1fb9a276 | LAA | C | check-D | **TRUE** | Verified; confirming datum #4. Fix = D1 | ON |
| 5 | d298a9d6 | LAA | P | §2 1.0-invariant | **TRUE** | Cross-draw reproduction of 353dce7f | ON |
| 6 | 9e55dd99 | LAA | P | §5 quiet-retraction attack | **TRUE** | Consequence declared, owner named; repro of e9c24932 | ON |
| 7 | 7190c023 | SA | M | §6 `Evidence.observed_at` | **TRUE-** | F-A core verified (§3's Δt "from" point correctly the *cited node's* `observed_at`); caveats: the concession is the disclosure; "either way" unengaged. DB genuine | ON |
| 8 | 185c6d81 | SA | M | §4 DeploymentEnvironment 0.9 reuse | **TRUE** | The 0.9 family's clean statement: §6's calibration (fresh aging-fact reliability via re-observation) never substantiates a non-aging use — the flat base is *uncalibratable by the stated process*. Zero inflation. DB genuine | ON |
| 9 | 9bddf949 | SA | M | check-D | **TRUE-** (severity demur) | Content identical to the four COSMETIC lanes; MATERIAL over-weights an authoring-convention miss already ratified-for-revision. Not HELD-MIS-SEV — a real defect at inflated severity; the union's one severity variance | ON |
| 10 | 480db100 | SA | M | §1/§4 totality vs RBT-54 dependency | **TRUE-** | F-B core restated; arbiter locus (template conditional-acceptance + Item 4) verified correct. Rides D2b | ON |
| 11 | 0b94cfae | SA | C | References header §2.2/§2.6 vs Cond. 1 §2.2–2.5 | **TRUE** | Verbatim-verified internal mismatch — a new micro-defect introduced by the record itself (run-012's §9/§10 analog). Fix = D2f | ON |
| 12 | 1811dcec | SA | P | §5 × #24 | **TRUE** | Verified; repro of 3694e187 | ON |
| 13 | 07dc8e9d | SA | P | §1/§4 derive-or-reject vs SDD-001 | **TRUE** | Verified against §3.4.3/§3.2 bytes exactly | ON |
| 14 | a80870ab | EA | M | §4 totality timing posture | **TRUE-** | F-B core through the EA lens; caveat: the posture worry dissolves into the record's own Pre-Acceptance mechanism. Locus borderline → §4 gen-5 read | ON |
| 15 | b27f42d7 | EA | M | §3/§6 reconstructibility fork | **TRUE-** | F-A core verified; caveat: "premature against upstream" mischaracterizes the ratified either-way discharge — the anti-premature device. DB genuine | ON |
| 16 | 9e710b13 | EA | M | Pre-Acceptance posture | **TRUE-** | Core true: the acceptance posture is the open question, and the conditions structure supports ACCEPTED-WITH-CONDITIONS — the EA's designed emission (its own prompt's dry-mode note names this shape). Caveats: posing the posture is the acceptance act's job; "sound as authored" is template language; cited-authority attributes template text to the skill (rider). **Bucket: acceptance-posture input (D6), no document edit** | ON |
| 17 | f9c7d06b | EA | P | §2 1.0 vs authors-nothing | **TRUE** (rider) | Verified vs ADR-001 §2.2 + DDR-002 §4; rider: "gateway authors nothing" is SDD-001's line, non-load-bearing | ON |
| 18 | 86626098 | EA | P | §5 boundary as own-record question | **TRUE** | Verified — integrates with the ratified ceiling, commits nothing new | ON |
| 19 | da6eccd6 | coh | M | §4/§6 base-coupling on re-tune | **TRUE** | The union's sharpest novel finding, fully verified: a §6 re-tune of `base` (aging-fact evidence only) silently moves DeploymentEnvironment's flat confidence — a coupling Items 6/8 never addressed. DB genuine → **D3 decision rider** | ON |
| 20 | 8a01ef39 | coh | M | §4 basis table node-vs-edge scope | **OVER** | The claimed gap is supplied verbatim by §5 one section away, and the finding concedes the sections are consistent — self-refuting underspecification claim | ON |
| 21 | 354e92da | coh | M | §6 observed_at two-semantics | **TRUE-** | F-A's most precise statement (same-named field, two proposed meanings, T2 typing correct); family caveats. DB genuine | ON |
| 22 | df2dc420 | coh | M | §4 carrier claim vs §2.6/§2.2–2.5 | **TRUE** | F-B's cleanest statement: enumerates PlaneDefinition's actual fields correctly, integrates the record's own disclosure, asserts exactly the present-tense contingency. Rides D2b | ON |
| 23 | 61f87db6 | coh | M | Reconciliation double-listing | **TRUE-** | Core true: CONFIDENCE_UNDERIVABLE listed both "confirmed unchanged" and "superseded," and reachability genuinely flips vs SDD-001's "known reachable case." Caveat: a coherent reading exists (behavior vs role). Fix = D2e | ON |
| 24 | 029a9a92 | coh | P | §5 × #24 | **TRUE** | Verified incl. SDD-001 §3.3.3/§2.2 | ON |
| 25 | 7ffac1ab | coh | P | §2/§6 1.0-invariant consistency | **TRUE** | Verified — §6's calibration scope excludes 1.0; no self-contradiction | ON |

**POSITIVEs — 8× TRUE** (one attribution rider); caps held 2/2/2/2 — all four hats at cap, zero re-labels.

## §3 Union table — 44 findings, both draws

**F-A — reconstructibility / `Evidence.observed_at` (7 members, all four hats, both draws — the union's largest family):**

| draw | LAA | SA | EA | coherence |
|---|---|---|---|---|
| A | 0f93e458 TRUE- | 3ed68605 TRUE- | — | 40bdc898 TRUE- · 21e2a2f8 TRUE- |
| B | — | 7190c023 TRUE- | b27f42d7 TRUE- | 354e92da TRUE- |

Seven valid rulings, five DB, zero survivals beyond what Item 8 + the RBT-54 Touch-3 addendum already
carry. Document action: one edit (D2a). The family's function is confirmation that the ratified
verify-intent fork is genuinely load-bearing.

**F-B — carrier tense / enforcement-pending (7 members, all four hats, both draws):** valid core
88caf2eb TRUE- (A) · 01369e21 · 480db100 · a80870ab TRUE-, df2dc420 TRUE (B); plus the scope-species
OVERs on the same locus (551d512f A · a975e568 B — the LAA re-attack species, n=5 in lineage at exactly
one per draw). One edit resolves the valid core (D2b).

**F-C — DeploymentEnvironment 0.9 (3 members, 2 hats, both draws, all DB):** 855242d2 TRUE- (A) ·
185c6d81 TRUE · da6eccd6 TRUE (B). Item 6's 0.9 stands (re-evaluation declined); discriminator edit D2c;
the coupling question is the union's one novel decision item → **D3 (ratified: decouple)**.

**F-D — SDD reconciliation (same hat, both draws):** 8c502c3c OVER (A) → 6f5aaa1a TRUE- (B); the draw-B
statement engages the bytes the draw-A one skipped. Codification-refinement D2d; anchor-capture stands.

**F-E — check-D (5 members, 3 lanes, both draws):** e25bd5ff · 882de4e5 · ada0828d (A, all TRUE
COSMETIC) · 1fb9a276 TRUE COSMETIC · 9bddf949 TRUE- MATERIAL (B; the severity demur).
The pre-registered hold, formally flagged — expectation CONFIRMED, no instrument gap. Mechanical check-D
reproduction on the frozen bytes: six violation lines (Rationale 1 · Pre-Acceptance 4 · Reconciliation 1),
seven identifier instances of three types (R6 ×1, RBT-53 ×3, RBT-54 ×3). Reviewer scope was broader than
the validator regex (run-IDs, "union disposition Item 1") — the D1 sweep covers both.

**Valid singletons (none reproduced):** 945a8fb0 TRUE- (basis-4 typing → D3 rider) · 0b94cfae TRUE (D2f) ·
61f87db6 TRUE- (D2e) · 9e710b13 TRUE- (acceptance-posture input, D6). **Invalid singletons:** b479937f
OVER (A) · 8a01ef39 OVER (B). The run-011 principle reproduces on DDR terrain: **families reproduce;
one-offs are draw-local — on both the valid and invalid sides.**

**POSITIVE stability:** the §5 × #24 composition boundary drew credits from **every emitting hat in both
draws** — 7 of 14 credits (e9c24932 · 3694e187 · 5e8fbe94 / 9e55dd99 · 1811dcec · 86626098 · 029a9a92);
the 1.0-invariant ruling drew 4 across 3 hats (353dce7f / d298a9d6 · f9c7d06b · 7ffac1ab). The two
largest credit clusters sit precisely on Items 7 and 3 — the record's two boundary rulings.

**Union validity: 39/44 — 8 TRUE · 17 TRUE- · 14 POSITIVE-TRUE · 5 OVER** (all OVERs draw-local).

## §4 Baselines + watches (union scope; all rulings ratified per item)

**Gen-4 (severity/cap → 0): HOLDS — 0 instances — and the vacuity is RESOLVED.** The decisive untested
case ran: coherence emitted at cap in **both** draws (A: 2P+2M+1C; B: 2P+5M) with no held check
re-labeled (its invalid emissions assert defects — misread species, not converted credits). Draw B had
all four hats at cap simultaneously. Class at 0 across runs 012/014/015 with coverage now non-vacuous
for every hat. **The coherence-at-cap watch closes.**

**Gen-5 (locus inflation): 0 firings — one named borderline.** Every resolvable authority_locus in both
draws byte-verified. Borderline: a80870ab places a ddr-template sentence under an
"author-decision-record SKILL (DDR route)" umbrella before also naming ddr-template — ruled NOT a firing
(the proposition exists verbatim in a co-named, in-substrate component; the template ships as a skill
component). Attribution-smear, not entailment-fabrication (e0aaafd7's mechanism). Baseline stays at
cumulative 1; **first clean read post-reset — T3 promotion remains gated** pending the zero-recurrence streak.

**EA divergence — adjudicated three ways:**
1. *"Nothing to attack on these bytes": NOT SUSTAINED* — draw B's recovered EA emitted a fully valid
   5-finding stream on byte-identical inputs. Run-012's amendment-dissolved-content explanation is
   unavailable (fresh document).
2. *Gen-4 over-correction: NOT SUSTAINED* — floor/cap mechanics unchanged; three hats clean at floor and
   cap on identical bytes, both runs.
3. *T4 empty-emission pathology, now EA-localized: SUSTAINED.* Geometry shift recorded: the 011/012
   stream read run-correlated (0/4 → 3/4 → 3/4 first-emission empties); runs 014/015 show EA-only
   first-emission empties in both draws while LAA/SA/coherence ran clean — **EA's first emission empty
   three consecutive runs** (012 · 014 · 015). Re-draw recovery cumulative 5/8 (011: 3/3 · 012: 1/3 ·
   014: 0/1 · 015: 1/1). Draw A's hat_null scores as a straight instrument miss for the single-draw
   counterfactual — **absorbed completely by the two-draw union**, the design vindication this union
   existed to test. Watch-only, no corrective (no-prompt-chasing; n=3 for the EA streak). Recipe-level
   note, not a prompt change: until the streak breaks, a single-draw DDR review cannot rely on the EA
   lane — the two-draw union (or an EA-redraw budget) is the operative mitigation.

## §5 Arbiter stream — union verdicts

30/30 classifications parsed clean, zero retries; confidence 25 high / 5 medium. **DB tally: 10/13
genuine (1 asterisked) · 1 clean miss · 2 soft misses** (run-011 operational test). Genuine: the F-A six
(3ed68605 · 40bdc898 · 21e2a2f8 · 7190c023 · b27f42d7 · 354e92da) · 185c6d81 · da6eccd6 · 9e710b13 (it
*is* the acceptance question) · 945a8fb0 genuine-with-asterisk (place pattern-determined; type open).
Miss: 8c502c3c (resolving authority in-substrate — the deliberation record's routing-satisfaction note);
softs: 855242d2 (Item 6 fixed the value; rationale resolves from canon ordering) · 6f5aaa1a's
acceptance-scope half (its downstream half genuinely unruled). **Same null-locus mechanism as run-012 §5**
— every miss-class call sits where the resolving authority is design-intent material, and DB calls carry
no authority_locus so the validity screen never runs — **at a far better rate** (run-012: 1/5 genuine;
here 10/13), and with a calibration improvement: **the clean miss carried medium confidence** (run-012's
four misses were all high; draw-B's three mediums all sat on the F-B family's thinnest OVER/TRUE-
boundary). Resolvables **17/17 correctly routed**, loci byte-verified; the locus-as-rebuttal validity
screen fired on 551d512f · b479937f · a975e568 · 01369e21 · 480db100. The named DB-side-locus/validity-
screen candidate gains this run's data; **remains unelected, own deliberation — reported, not chased.**
Cache: 29 of 30 arbiter calls read 99,098 cached tokens (warm across the two runs).

## §6 Scorecard — draw B and union

| Metric | Draw B | Union (both draws) |
|---|---|---|
| Findings ruled | 25/25 | **44/44** |
| Validity | 23/25 (5 TRUE · 10 TRUE- · 8 POS-TRUE · 2 OVER) | 39/44 (8 TRUE · 17 TRUE- · 14 POS-TRUE · 5 OVER) |
| Arbiter | 7 DB (6 genuine, 1 asterisked-half) · 10/10 resolvable routed | DB 10/13 genuine · 1 miss + 2 softs (null-locus mechanism) · 17/17 resolvable · gen-5 0 firings (1 borderline) |
| Baselines | — | gen-4 HOLDS (decisive case closed) · gen-5 clean read #1, T3 gated · T4 EA-streak n=3, watch-only |
| Cumulative validity-precision ledger | — | 164/180 → **203/224** |
| Correctives fired | — | **none — all streams watch-only per ratified rulings** |

*Dispositions: this folder's disposition.md (D1–D7, each ratified individually by Tad, 2026-07-11);
nothing in this file self-executes. The 13 dry-mode proposed escalations opened no tickets — their
content is fully absorbed into the disposition record.*
