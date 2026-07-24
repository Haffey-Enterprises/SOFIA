# Run-012 Audit — SDD-001 v0.3.0 Review (Verification Draw)

| Field | Value |
|---|---|
| **Run** | run-012-sdd-001 (the single verification draw, union disposition Item 7) |
| **Document** | SDD-001 v0.3.0 PROPOSED — blob `c5f2a16b` (= the ratified amendment text at `b7efc0f`, verified); snapshot sha256 `0e3375b1…` recomputed against reviewed bytes |
| **Corpus tip** | `8e6750c` (feature branch = `b7efc0f` v0.3.0 + `b35c0ef` develop); substrate pins byte-equal to run-011 (probe-verified, gate-8 green) |
| **Mode** | dry · HALT_DECISION @ pass 1 · 219.9s · 3 below-floor first emissions (LAA/EA/coherence, degenerate `[]`, 4 output tokens each) · LAA recovered on one re-draw · **EA + coherence hat_null** (empty re-draws) · 0 parse drops · 0 aborts |
| **Prompts** | generation 5 (first gen-4/gen-5 armed run); all five prompt hashes == the carrier addendum's re-pin values, verified |
| **Audit** | COLD audit, 2026-07-09 successor session (predecessor authored the gen-4/gen-5-adjacent fixes and recused); every locus verified against the run's own substrate bytes (SDD `c5f2a16b`, DDR-002, ADR-002, ADR-001, DDR-001, authoring skill, deliberation record) — fetched, not recalled; rulings ratified per item by Tad |
| **Companion** | run-010/011 audits + union disposition @ develop (the baseline streams this draw is read against) |

## §1 Scope & method

10 findings (4 MATERIAL / 2 COSMETIC / 4 POSITIVE — LAA 5, SA 5); 6 classified (5 decision-bearing /
1 resolvable), all `confidence: high`. Verdict vocabulary per run-009/010/011: TRUE / TRUE- / OVER /
FALSE-POS / HELD-MIS-SEV; stance ON/OFF/AMB. Raw emission bodies verified against ledger rows (exact).
This draw's charter question (union disposition Item 7): did the election-routing dissolve D1, and did
the Item-2 resolvables close? Both answered in §3. First post-corrective read of the armed
zero-recurrence baselines in §4; the EA/coherence hat_null attribution ruling in §4; arbiter stream in §5.

## §2 Per-finding rulings

| # | id | hat | sev | locus | verdict | basis (one line) | stance | pairing |
|---|---|---|---|---|---|---|---|---|
| 1 | 092118bf | LAA | M | §3.4.3 derivation-as-implemented vs routed authority | **OVER** | "Decides more than its stated scope" contradicted by the record's own apparatus — §2.2 declares the interim derivation an in-scope SDD-level determination, §3.4.3 says "not permanently," §10 records the arrangement ratified per item; re-attacks the disposition-ratified routed-to-forthcoming pattern without engaging its declaration | ON | LAA scope-species #3 (4dfe13af d1 · 13e08962 d2 · this d3 — one per draw) |
| 2 | 9c06cd57 | LAA | C | §10 v0.3.0 row vs §9 carrier enumeration | **TRUE** | Verbatim-verified: §9 lists three v0.3.0 revision carriers incl. `disposition.md`; §10's parenthetical lists two — a real internal mismatch, introduced by the amendment text itself; fix ratified to ride the acceptance edit | ON | cross-hat near-dup of e0aaafd7 |
| 3 | d92ba71d | LAA | M | §3.5.4 #25 pre-decision window | **TRUE-** | Core true (window verified against DDR-002 §7 #25 + §5 execution gloss; persists until the DDR-002 scoping amendment lands); caveats: "resting on an amendment that does not yet exist" contradicted by the harness-implements-from-ratified-text clause; "smuggled retraction" horn dissolves against the disclosure. Already-ruled bucket: disposition Items 3/5 govern; amendment ticketed with BUILD sequencing rule; no document action | ON | D2 lineage (708bcb75/8d9f62da); two-sided-locus pair w/ da990373 |
| 4 | 13289e4b | LAA | P | §2.2/§7.1 scope boundary | **TRUE** | Hold verified end-to-end (§3.4.6 `AUTHOR_VIOLATION` rejection of unassigned transitions; Attestation/Actor/Role routed with no operations; no default-to-gateway path); rider: cited DDR-002 §5 routing is loose (nearest text: ownership line's "workflow → SDD") — hold unaffected | ON | authorship-boundary cluster, draw 3 |
| 5 | f1fdb5fb | LAA | P | §3.3.8 no-CI-invariant determination | **TRUE** | Named Gap text verified exact ("whether it warrants its own CI invariant … → knowledge-service SDD"); the record answers precisely the routed question, grounds on #20's verified guarantees, defers gap-pruning to DDR-002 amendment; zero inflation | ON | new credit stratum |
| 6 | 9c774202 | SA | M | §3.4.3 Δt reference-time anchor | **OVER** (close call, minority TRUE- reading recorded) | "DDR-002 §4 doesn't fix the anchor either" fails against §4's "inherits … **at snapshot time**" — the clause that made run-011's 13e08962 an OVER — plus the SDD's derived-at-creation binding (capture-time anchor by entailment); ratified rider: an explicit anchor clause joins the derivation record's question set | ON | resolved-upstream species (13e08962 kin) |
| 7 | 95d6f020 | SA | M | §3.4.3 base-1.0 branch totality | **OVER** | Named branch trivially total (constant 1.0; the branch's own parenthetical resolves freshness — "staleness is handled by supersession, not decay"); "asserted, not substantiated" fails against in-line substantiation. **Audit rider (auditor's finding, surfaced not fixed):** DDR-002 §2.2 gives `observed_at` to `DeployedService`/`ConfigurationItem` but not `DeploymentEnvironment` — a second reachable `CONFIDENCE_UNDERIVABLE` case outside §3.4.3's "the known reachable case" enumeration; fail-closed keeps behavior safe; per-class branch totality joins the derivation record's question set (honest floor: citation reachability unverified) | ON | UNIQ |
| 8 | e0aaafd7 | SA | C | §9 vs §10 carrier enumeration | **TRUE** | Same verified mismatch as #2, stated from the §9 side — the run's only cross-hat convergence, and it converged on something true; fix carried by #2's ratification | ON | near-dup of 9c06cd57 |
| 9 | ad4a9777 | SA | P | §3.2/§3.4.6 Species-2 authorship-unexpressibility | **TRUE** | Verified exact both ends: "authorship-by-gateway is unexpressible" (§3.2), `AUTHOR_VIOLATION` (§3.4.6); ADR-002 §2.6 + §6 check 7 confirmed verbatim ("never named as the authoring authority") | ON | authorship-boundary cluster, draw 3 |
| 10 | da990373 | SA | P | §3.5.4 #25 residue disclosed | **TRUE** | Credit side of the two-sided D2 locus (7b9a0f8b/55ba066a lineage) — third consecutive draw the #25 disclosure reads honest; DDR-002 §5 gloss and harness-binds-ratified-text clause quoted faithfully | ON | two-sided-locus pair w/ d92ba71d |

**POSITIVEs — 4× TRUE**, all verified against substrate as genuine holds. Caps held 2/2 for both
emitting hats — at cap exactly, no overflow, no re-label (see §4, gen-4). The authorship boundary drew
credits from both emitting hats (13289e4b, ad4a9777) — the P1-010 cross-hat credit cluster reproducing
in its third consecutive draw; the #25 honest-disclosure credit likewise (third draw, migrated coh→SA).

## §3 Stream verdicts vs the 010/011 baseline — the Item-7 questions answered

**D1: DISSOLVED.** Ten valid members across 010/011 (all four hats) → **zero valid members this draw.**
The three §3.4.3-adjacent findings are: one OVER re-attack on the ratified routed-to-forthcoming
arrangement (092118bf), and two OVER technical misreads of the interim derivation's text (9c774202,
95d6f020). What D1 leaves behind is not an open authority question but question-set refinements for the
forthcoming derivation record — the explicit Δt-anchor clause and per-class branch totality (incl. the
`DeploymentEnvironment` case) — both ratified as question-set content this audit. The election-routing
did the work the disposition designed it to do.

**Item-2 resolvables: CLOSED.** None of the six touches (#16/#11 re-bucket, stamping-citation
correction, check-6 row split, §6-check-x notation, fail-closed Extension interim, §4.6 tunables) drew
a finding. The run's one valid defect pair (§9/§10 carrier enumeration, COSMETIC) was **introduced by
the v0.3.0 amendment text itself** — a new micro-nit, not a survival; fix ratified to ride the
acceptance edit.

**D2: STANDS AS RULED.** The window restatement earns TRUE- on its core with both framing horns
dissolved by the record's own disclosure; the same bytes drew the honest-disclosure credit from the
other emitting hat. Third consecutive draw the §3.5.4 routing note is read honest by at least one hat.
No document action; the scoping amendment's ticket and the BUILD sequencing rule govern.

**Hat-stream notes.** LAA: the scope-transgression OVER species reaches n=3, exactly one per draw
across three draws — watch continues, no corrective (draw-local each time, species named). SA: first
draw with all defect-severity emissions invalid (both MATERIALs OVER) — read with §6's honesty note:
post-amendment residual surface selects for OVERs. EA + coherence: hat_null — attribution ruled in §4.

## §4 Armed baselines (first post-corrective read) + hat_null attribution + T4

**Gen-4 (severity/cap class → 0): HOLDS — 0 instances — with a named vacuity.** No held check was
re-labeled a defect anywhere; all six defect-severity findings genuinely assert defects; both emitting
hats sat at the 2-POSITIVE cap exactly. Non-vacuous for LAA/SA; **vacuous for coherence** — the class's
only prior host (coherence at cap, both 010/011 draws) emitted nothing this run, so the corrective's
decisive test remains the next run where coherence emits at cap. (Ratified recording.)

**Gen-5 (locus inflation → 0): FIRES — 1 instance — e0aaafd7's authority_locus.** The locus attributes
to the authoring skill's 'Placement, naming, metadata' / 'Status and version' sections the proposition
"Change Log is the authoritative carrier of revision history." Neither section carries it; the nearest
real text ('Authoring discipline') names "the Change Log, Cross-References, or your tracker"
**disjunctively** — cutting against Change-Log-exclusive authority and pointing the reconciliation the
wrong way (toward §10's under-enumeration). Mechanism matches the n=3 lineage exactly: real source,
attributed an entailment its text does not carry. Mitigations on the record: mildest instance of the
four (generic-document-knowledge paraphrase), non-load-bearing (classification correct on independent
grounds), dry mode. Consequences: baseline 0→1; **T3 promotion stays gated**; gen-5 behavioral effect
**not demonstrated** (prior rate ~1/run, post rate 1/run, n=1). (Ratified.)

**Hat_null attribution — ruled three ways, replacing the launch session's binary (ratified):**

1. *Defect-side silence → the v0.3.0 amendment working: SUSTAINED.* By the union's reproduction
   principle, EA/coherence's reproducible defect content was entirely D1/D2. EA's posture/home stratum
   is dissolved by exactly the election-routing (its §7.2 singleton was draw-local); coherence's three
   D1 strata are dissolved by the same routing, its D2 reading survives as the credit side (emitted by
   SA this run), and its HELD-MIS-SEV pair is the gen-4 target class, whose absence is the corrective
   working as designed. The amendment's touches removed exactly those loci.
2. *Gen-4 over-correction: NOT SUSTAINED* — named watch only. LAA/SA on identical gen-4 bytes emitted
   full streams with floors met exactly; the gen-4 text addresses re-labeling at cap, not volume at
   floor; the empty shape predates gen-4 byte-identically. Re-opens only if floor non-compliance recurs
   while the empty pathology is otherwise quiet.
3. *The hat_null mechanics → the pre-existing run-correlated empty pathology, T4, now n=3.* First-draw
   empties 0/4 (run-010) → 3/4 (run-011) → 3/4 (this run); `[]` bodies byte-identical across runs. New
   datum: **re-draw non-recovery** (3/3 recovered in 011 → 1/3 here), correlating with the two
   amendment-dissolved hats — consistent with (1) lowering re-draw yield — but zero-credit silence is
   not "nothing to attack": a floor-compliant null is 2 POSITIVEs, and four credits demonstrably existed
   on these bytes. Scored as pathology; **watch-only, no corrective** (n=1 for non-recovery;
   no-prompt-chasing).

## §5 Arbiter stream

6/6 classifications parsed clean, zero retries; **all six `confidence: high`** — a calibration datum in
itself (in 010/011 the mediums flagged the genuinely hard calls; this run's four misses all carried
high confidence). Cache: 5 of 6 calls read 81,504 cached tokens.

**DB tally: 1/5 genuine · 4 misses (ruled per item).** Applying the run-011 operational test (a DB is a
miss when a resolving authority existed): 092118bf (resolved by the document's own ratification
apparatus — §10 row + §2.2 scope declaration) · 9c06cd57 (resolved by §10's own prose citing the
disposition ratification events) · 9c774202 (resolved by DDR-002 §4 "at snapshot time" + the
derived-at-creation binding — the softest of the four, entailment-grade, asterisked) · 95d6f020
(resolved by the branch's own parenthetical, one sentence from the claimed hole). d92ba71d GENUINE —
the #25 scoping amendment is genuinely open in the reviewed substrate; the rationale even anticipates
the house sequencing logic. Resolvable: 1/1 correct (e0aaafd7 — the "document's own recorded facts"
frame is the right one), locus half-inflated per §4.

**The run's sharpest instrument finding — same defect, two classifications.** 9c06cd57 (LAA's wording)
→ decision-bearing; e0aaafd7 (SA's wording, same mismatch) → resolvable. The two rationales disagree on
whether the reviewed document's own apparatus counts as a resolving authority — a **resolving-authority
frame instability**, with the classifier emission-sensitive (LAA's "a reader cannot tell" framing
pulled DB where SA's dry mismatch statement pulled resolvable).

**Mechanism, unified and previously predicted.** All four misses share one structure: the resolving
authority lives in the reviewed document's own apparatus (or a canonical entailment), and **DB
classifications carry no authority_locus, so the de-facto validity screen never runs** — the exact
structural asymmetry the run-011 audit §5 named as observation. The amendment moved the defect surface
from canonical-authority conflicts to document-internal-apparatus questions, which is precisely the
terrain where the null-locus asymmetry is load-bearing. It has now produced n=4 misses in one run
(cumulative DB-miss class: 4b3e626e + these four). Gen-5 cannot reach this by design — it disciplines
loci that exist. **Observation recorded; no corrective proposed this audit** (no-prompt-chasing
standard; dry mode; a DB-side locus or equivalent screen is a design question for the instrument
backlog, evidence now at threshold-candidate strength for its own deliberation).

## §6 Scorecard

| Metric | Value |
|---|---|
| Findings ruled | 10/10 (6 classified + 4 POSITIVE) |
| Validity | 7/10 — 2 TRUE · 1 TRUE- · 4 POSITIVE-TRUE · **3 OVER** |
| Arbiter | 1/5 DB genuine · 4 misses (null-locus mechanism) · 1/1 resolvable correct · locus inflation n=1 (gen-5 FIRES) |
| Baselines | gen-4 HOLDS (0; coherence-vacuous) · gen-5 FIRES (0→1; T3 stays gated) |
| Cumulative validity-precision ledger | 157/170 → **164/180** |
| Correctives fired | none — all streams watch-only per ratified rulings |

**Honesty note on the validity rate:** 70% is not comparable to 010/011's ~85% as an instrument-quality
signal — the amendment removed the reproducible valid families, so the residual attack surface selects
for OVERs; the valid-finding density *should* drop after a good amendment. The instrument story of this
run is the arbiter §5, not the reviewer validity rate.

*Dispositions carried at session scope (all ratified per item, 2026-07-09): the five dry-mode proposed
escalations → no tickets opened; the §9/§10 carrier fix rides the acceptance edit; the Δt-anchor and
per-class branch-totality riders route to the forthcoming inherited-confidence-derivation record's
question set; the RBT-15 criterion-1 acceptance ruling and its capture live on the ticket, not here.*
