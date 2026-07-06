# Run-011 Audit — SDD-001 v0.2.0 Review (Draw 2 of 2) + Union

| Field | Value |
|---|---|
| **Run** | run-011-sdd-001 (draw 2 of the RBT-15 two-draw sequence) |
| **Document** | SDD-001 v0.2.0 PROPOSED — blob `fe6c8ee1` (same bytes as draw 1; verified) |
| **Corpus tip** | `9b960e52` — identical across both draw manifests; all five prompt hashes identical (gen-3, Ra-2). Same-input, same-prompt, k=2 sample confirmed |
| **Mode** | dry · HALT_DECISION @ pass 1 · 3 empties (LAA-1, SA-1, coherence-1; `output_tokens: 4` each), each recovered on one re-draw; 0 `hat_null`; EA clean first draw |
| **Audit** | Cold audit, same session and substrate set as the primary; rulings ratified per item by Tad |
| **Companion** | run-010-sdd-001/audit.md (primary). This file carries the union table and all union-scope analysis (§2, §4–§6) |

## §1 Scope & method

23 findings (11 MATERIAL / 4 COSMETIC / 8 POSITIVE); 15 classified (11 decision-bearing / 4 resolvable).
Method identical to the primary. This draw's classified set includes the ledger's first two
COSMETIC-decision-bearing classifications — ruled below, both correct: the DB test is
decision-dependence, not severity.

## §2 Per-finding rulings (draw 2)

| # | id | hat | sev | locus | verdict | basis (one line) | stance | union pairing |
|---|---|---|---|---|---|---|---|---|
| 1 | 9c4173b7 | LAA | M | §3.4.3 exceeds cited authorization | **TRUE-** | Genuine D1 question; caveats: rollup-routing quoted as inheritance authority; counter-warrant unengaged | ON | D1 root d2; same-hat repro of 4c79e2ac |
| 2 | 13e08962 | LAA | M | §2.2/§3.4.3 undeclared boundary | **OVER** | "Not declared" contradicted by Declared-determinations apparatus + species warrant; who-computes resolved upstream ("at snapshot time") | ON | never-surfaced species #2 (pairs 4dfe13af d1) |
| 3 | 0d3b0fe3 | LAA | C·DB | §3.5.4 #25 self-declared consequence | **TRUE** | Exact claim, zero inflation; COSMETIC altitude-appropriate (claim-fidelity lane; substance carried at MATERIAL by SA/coh) | ON | D2 |
| 4 | cee27acc | SA | M | §3.4.3 Extension `observed_at` | **TRUE** | Domain-totality hole, confirmed reachable (RateCard/CostFactor: no confidence, no `observed_at`); `recorded_at` fallback foreclosed by §1's never-conflated rule | ON | D1, novel stratum; draw-2-only |
| 5 | 9cab8be9 | SA | M | §3.4.3 routing asymmetry | **TRUE-** | Fusion of d1's asymmetry + substantiation arguments; caveats: ADR-001 §2.2 joint-attribution slip; counter-warrant unengaged | ON | D1; near-dup pair w/ 4c79e2ac (cross-hat, cross-draw) |
| 6 | ce68153c | SA | C | §7.1 "ADR-002 §6.x" notation | **TRUE-** | §6 has no subsections — real micro-nit; caveats: References-table misattribution; substantive-loci thread dissolves. Fix ruled: normalize to "§6 check x" | ON | UNIQ |
| 7 | 8d9f62da | SA | M | §3.5.4 #25 + §7.2 entanglement | **TRUE-** | D2 core true; caveats: "safety-adjacent" inflates a Follow-tier invariant; §7.2 collision contingent on unruled 1a/1b bucketing. Rider: amendment-vs-BUILD sequencing rule → disposition | ON | D2; same-hat repro of 708bcb75, with degradation |
| 8 | 4c380603 | SA | M | §2.1/§4.2 #19 admit-half | **OVER** | Population empty by construction (feedback-loop job is DDR-003-gated); §4.2 leg two is the disclosure; Item 2d(v) ruled exactly this | ON | inversion pair w/ 042a6065 (d1 credit, same surface) |
| 9 | 5f977db3 | SA | C·DB | §3.2 unreachable SUBTYPE_VIOLATION | **TRUE** | Dead error by operation shape; SDD's own #2/by-construction precedent names the fix. Riders: reclassify #16 by-construction (mediated writes); retain the enum as documented defense-in-depth | ON | UNIQ; draw-2-only |
| 10 | 5e4433c5 | EA | M | §3.4.3 posture/home | **TRUE-** | The election question stated clean; verification tooth: the derivation is the only Declared determination with no deliberation lineage (Items 2a–2h contain no derivation item). Caveats: DDR-002/SDD splice; corollary applied by analogy | ON | D1; four-hat completion |
| 11 | cda1b780 | EA | M | §7.2 moving-target gate | **TRUE-** | Real risk on a genuinely open item (= general form of the sequencing rule); caveats: charter provenance unengaged (set-generic is RBT-15's own mandate); "expand" loose; reversibility argument inverts | ON | UNIQ; §7.2 drew different seams per draw (4dfe13af authorization OVER / this risk TRUE-) |
| 12 | 96d51147 | coh | M | §3.4.3 canon supplies no function | **TRUE-** | D1 substantiation stratum; caveats: canon-shape undersell (shape/ordering/keying ARE fixed); counter-warrant unengaged | ON | D1 #5; same-hat repro of 2814cfe0 (complementary: adds Extension leg, drops mitigation analysis, drops fabricated rule-name) |
| 13 | 55ba066a | coh | M | §3.5.4 downstream-only qualifier | **TRUE** | Sharpest D2 statement: the reconciling text has no ratified home; clean of both sibling overreaches | ON | D2; two-sided-locus pair w/ 7b9a0f8b (d1 credit, same hat, same locus, both valid) |
| 14 | 4b3e626e | coh | M | §3.2 one-payload unification | **OVER** | Misparse: payload = base fields + manifest fields, surfaces read different components; DDR-002 §5 commissions (not prohibits) the unification; Item 2f(ii) ruled it | ON | UNIQ; the DB tally's one miss |
| 15 | 86a16eac | coh | C | §3.3.3 routing-chain audit | **HELD-MIS-SEV** | Content-TRUE (chain verifies 4/4); zero defect asserted — class instance, coherence at cap; struck from defect set, POSITIVE-equivalent over-cap. Pre-gen-4 instance: strengthens mechanism, doesn't test the corrective | ON | class lineage fe2b5642/f4a5ba9d |

**POSITIVEs — 8× TRUE**, all verified: 9936254d (LAA, authors-nothing) · 2cc0c9f1 (LAA, §3.3.8 determination —
credit side of 4e4f33d4) · 6ea55ce4 (SA, #15 split) · ba859ba3 (SA, uncomposed confidences) · 37b2921e (EA,
write-authorship; DDR-001 Decision.7/check 7 verified) · f54126c5 (EA, amendments held as proposed — credit
side of 6c1aff22) · c6823b89 (coh, #15 split; within-draw near-dup of 6ea55ce4) · d77eadf7 (coh,
retrieves-never-recommends). Caps held 2/2/2/2; zero fabrication in the credit stream, both draws.

## §3 Union table — 42 findings, both draws

**D1 — §3.4.3 inherited-confidence derivation (10 members; the election):**

| draw | LAA | SA | EA | coherence |
|---|---|---|---|---|
| 1 | 4c79e2ac TRUE- (root) | 9a21625e TRUE- · 6e21f037 TRUE- | — | 4ab8d42c TRUE- · 2814cfe0 TRUE- |
| 2 | 9c4173b7 TRUE- (root) | 9cab8be9 TRUE- · cee27acc TRUE | 5e4433c5 TRUE- | 96d51147 TRUE- |

3 hats d1 → **all four** d2. Ten members, ten valid rulings, zero survivals of the underlying question,
all correctly decision-bearing. Strata: authority-boundary · τ/form · class-base anchor · branch-(i)
dual-surface · determination-vs-canon · routing-asymmetry · posture/home · **domain-totality (d2-only,
novel)**. Same-hat cross-draw reproduction at three altitudes (LAA, coh; SA reproduces the family though
not the identical stratum). The deliberation record contains no derivation item — the concrete function
entered via run-009 R6's explicitly-unruled inclination. **This is the headline disposition candidate:
elect the derivation for its own decision record** (→ session disposition, output b).

**D2 — §3.5.4 #25 pre-decision window (4 defects + the credit side):**
d1: 708bcb75 TRUE (SA) + 7b9a0f8b POSITIVE (coh). d2: 0d3b0fe3 TRUE (LAA, C·DB) · 8d9f62da TRUE- (SA) ·
55ba066a TRUE (coh). Multi-hat both draws; audit rider: #21/#25 jointly unsatisfiable in any pre-decision
retraction window — the amendment fixes a latent DDR-002 defect. Disposition carries the sequencing rule
(amendment ratified before BUILD, or #25's 1a/1b bucket ruled).

**Singletons (valid):** badeaf00 TRUE (d1) · cee27acc TRUE (d2) · 5f977db3 TRUE (d2) · ce68153c TRUE- (d2) ·
cda1b780 TRUE- (d2). Every singleton defect appeared in exactly one draw — none reproduced.

**False positives (6 OVER):** 4dfe13af · 6c1aff22 · 4e4f33d4 (d1); 13e08962 · 4c380603 · 4b3e626e (d2).
3 per draw, symmetric. Species: "never surfaced" contradicted by the record's own apparatus (4dfe13af,
13e08962 — LAA, one per draw); reconciliation-demanded-but-present (4e4f33d4, 4c380603); bucket/parse
misreads (6c1aff22, 4b3e626e). None reproduced across draws.

**Defect/credit inversion pairs (one draw's defect is the other's verified hold):**
6c1aff22 (d1 OVER) ↔ f54126c5 (d2 TRUE) · 4e4f33d4 (d1 OVER) ↔ 2cc0c9f1 (d2 TRUE) ·
4c380603 (d2 OVER) ↔ 042a6065 (d1 TRUE) — in each pair the credit side is the correct reading.
Distinct case: 55ba066a (d2 TRUE) ↔ 7b9a0f8b (d1 TRUE) — same hat, same locus, defect AND credit both
valid: a genuinely two-sided locus (honest disclosure of a state that needs a ruling), correctly read twice.

**POSITIVE cross-run stability (the fold-in §4 precedent, answered):** the authorship boundary drew 4
credits in each draw (8 of the union's 16); the #15 split reproduced 1→2; two d2 credits are the healthy
sides of d1's failed defects. **Refined finding: convergence reproduces — as credit clusters and as
decision-bearing families — while one-off findings, valid and invalid alike, are draw-local.** This is the
two-draw design's empirical yield: reproduction across independent draws separates document signal from
draw noise on both the defect and credit sides.

## §4 Variance-to-zero — T4 installment (honest floor: n=2 armed runs)

Draw 1: 0/4 empties. Draw 2: 3/4 empties (LAA, SA, coherence — degenerate `[]`, 4 output tokens each),
each recovered on a single re-draw, zero `hat_null`. EA — the run-009 empty hat — was draw 2's only clean
hat. **Empties are run-correlated, not per-hat-independent:** under independence at the observed marginal
rate, one run drawing 0/4 and the next 3/4 is the improbable pattern; the clustering hypothesis (a
run-level latent factor) is scored into the T4 stream at n=2 armed runs, held loosely. Contrast pair for
the mechanism ledger: cap-pressure is **hat-correlated** (coherence at cap, both draws, different
surfaces); empties are **run-correlated** (three hats, one draw). Two distinct pathology geometries now
named. The re-draw mechanic (RBT-49) carried the entire recovery load — 3/3 single-re-draw recoveries —
and its cost profile is what makes the ruled reviewer-side caching event (gen-6) economically pointed:
re-draws cluster, so making them near-free matters. Runner note: live-read at launch made the develop
freeze load-bearing by hand — root-cause fix (snapshot-or-pin at launch) is a named follow-up, queued.

## §5 Arbiter stream — union verdicts

**DB-rate drift (6/11 → 11/15): verdict — decision-density, not conservatism drift.** 10/11 DB
classifications genuine (D1's ten-member election + D2's open decision + the 5f977db3 edge, correct-with-
asterisk: its reclassification half is precedent-guided, its enum half a real choice — medium confidence
honestly calibrated). The rate rose because draw 2 put four hats on §3.4.3 and three on #25 — the density
was in the document's open questions, and the two COSMETIC-DB calls show the classifier correctly keying
decision-dependence over severity. **One miss:** 4b3e626e classified DB while a resolving authority
existed (Item 2f(ii)) — isolated, not a trend.
**Structural asymmetry, named:** resolvable classifications carry an authority_locus that functioned as a
de-facto validity screen five times across the union (4dfe13af, 6c1aff22, 4e4f33d4, badeaf00, 4c380603 —
locus = rebuttal or fix); DB classifications carry no locus, so the screen never runs where a miss like
4b3e626e would need it. Observation recorded; no corrective (no-prompt-chasing; one miss in eleven).
**Locus-entailment inflation: n=3 → corrective FIRED (gen-5, ratified).** Instances: 24b85a37 (run-009) ·
6c1aff22 (run-010, #25-under-Named-Gaps) · 13e08962 (run-011, DDR-002 species idea attributed to ADR-001
§2.3). Consistent mechanism: one element of a multi-source locus extended past its home's stated scope.
All three non-load-bearing (dry mode), but the loci now do real evidentiary work. Corrective: one
attribution-discipline line in the arbiter prompt — each locus element attributed to the document that
actually carries it, within its stated scope. Own calibration event (gen-5); reviewer-caching renumbers
to gen-6; same loop-instrument micro-ticket as gen-4, each event separately scoped.
**EA roster: verdict — surface-driven variance, not hat dysfunction.** The all-POSITIVE streak broke on
the D1 family's gravity: both d2 EA MATERIALs ruled TRUE-. Productivity recovered where the document
offered EA-lane substance; the streak was a property of prior documents' posture surfaces, not the hat.
**Confidence calibration:** d2 13 high / 2 medium; both mediums (5f977db3, 4b3e626e) sat on the two
genuinely hardest calls — including the one miss. Calibration continues honest.
Cost: 15/15 classifications, zero retries; 14 of 15 calls read 81,376 cached tokens.

## §6 Scorecard — draw 2 and union

| Metric | Draw 2 | Union (both draws) |
|---|---|---|
| Findings ruled | 23/23 | **42/42** |
| Validity | 20/23 (4 TRUE · 7 TRUE- · 1 HELD-MIS-SEV · 8 POS-TRUE · 3 OVER) | 36/42 (6 TRUE · 12 TRUE- · 2 HELD-MIS-SEV · 16 POS-TRUE · 6 OVER) |
| Arbiter classification | 10/11 DB genuine · 4/4 resolvable routed, loci clean | 16/17 DB · 9/9 resolvable · locus inflation n=3 → gen-5 |
| Cumulative ledger | 137/147 → **157/170** | 121/128 → 157/170 |
| Correctives fired (session) | — | gen-4 (severity/cap) · gen-5 (locus attribution); gen-6 = reviewer caching (renumbered) |

*Disposition of the union — the multi-bucket SDD-001 v0.2.0 disposition (D1 election headline, D2
sequencing rule, revision-batch resolvables, riders) — is the session's output (b), recorded in the
session disposition record; RBT-15 acceptance check follows it.*
