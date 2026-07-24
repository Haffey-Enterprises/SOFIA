# Run-010 Audit — SDD-001 v0.2.0 Review (Draw 1 of 2)

| Field | Value |
|---|---|
| **Run** | run-010-sdd-001 (draw 1 of the RBT-15 two-draw sequence) |
| **Document** | SDD-001 v0.2.0 PROPOSED — blob `fe6c8ee1` |
| **Corpus tip** | `9b960e52` (develop, frozen for the sequence; verified identical across both draw manifests) |
| **Mode** | dry · HALT_DECISION @ pass 1 · 0 empties (armed null held: 4 hat calls, no re-draw) |
| **Audit** | Cold audit, 2026-07-05 session; every locus verified against fetched bytes (SDD `fe6c8ee1`, DDR-002 `8dbabefa`, DDR-001 `7d731426`, ADR-002 `629bb7bd`, ADR-001 `a2c0558b`, deliberation record `eee23a1a`); rulings ratified per item by Tad |
| **Companion** | run-011-sdd-001/audit.md (fold-in; carries the union table and all union-scope analysis) |
| **Prompts** | gen-3 (Ra-2); all five prompt hashes identical across both draw manifests |

## §1 Scope & method

19 findings (7 MATERIAL / 4 COSMETIC / 8 POSITIVE); 11 classified (6 decision-bearing / 5 resolvable).
Verdict vocabulary per run-009 audit: TRUE / TRUE- / OVER / FALSE-POS / HELD-MIS-SEV; stance ON/OFF/AMB.
Every finding's claimed entailment checked against the actual document text at its locus (run-009 §4
watch discipline); every arbiter authority_locus checked against the cited source's own text.
Union-scope questions (cross-draw dup, POSITIVE stability, variance clustering) → fold-in §4.

## §2 Per-finding rulings

| # | id | hat | sev | locus | verdict | basis (one line) | stance | dup | 008∪009 |
|---|---|---|---|---|---|---|---|---|---|
| 1 | 4dfe13af | LAA | M | §9/§7.2 1b flip authorization | **OVER** | "Never surfaced" contradicted by §7.2's own header ("charter-mandated"), §9 charter citation, and RBT-15 acceptance text carrying the commitment verbatim | ON | UNIQ | NOVEL |
| 2 | 4c79e2ac | LAA | M | §3.4.3 authority boundary | **TRUE-** | Genuine open decision (R6 inclination executed, never ratified); caveat: SDD's counter-warrant unengaged | ON | D1-010 root | MATCH-evolved (be9b148e) |
| 3 | 6c1aff22 | LAA | C | §9 proposed amendments | **OVER** | "Under-surfaced" fails against three surfaces incl. §9's dedicated bullet; Routed is the correct change-log bucket (deciding authority is DDR-002's amendment process) | ON | UNIQ; inversion pair w/ f54126c5 (d2) | MATCH-evolved (31cf1fc8) |
| 4 | 9a21625e | SA | M | §3.4.3 τ/decay form | **TRUE-** | Constants genuinely SDD-asserted; caveats: two citation slips (§2.2-for-§4; canon parenthetical attribution) | ON | D1-010 | MATCH-evolved |
| 5 | 6e21f037 | SA | M | §3.4.3 base 1.0 | **TRUE-** | 1.0 anchor genuinely unfixed upstream; caveat: canon promises class-inheritance, not carried-value. Rider: 1.0 is the only constant neither contested-flagged nor in §4.6's tunables | ON | D1-010 | MATCH-evolved |
| 6 | 4e4f33d4 | SA | C | §3.3.8/§7.1 #20 | **OVER** | Constructed dual placement is false (#20 once in §7.1; "DDR-002 §7.1" nonexistent); tier-timing worry dissolves under sole-writer + by-construction; Item 2g-iv ruled exactly this grounding | ON | UNIQ; inversion pair w/ 2cc0c9f1 (d2) | NOVEL (79063465 kinship) |
| 7 | 708bcb75 | SA | M | §3.5.4 #25 window | **TRUE** | Clean; sharpest draw-1 defect; every quote verbatim, no inflation. Rider: #21/#25 jointly unsatisfiable in any pre-decision retraction window — the amendment fixes a latent DDR-002 defect, not an SDD preference | ON | D2-010 root; credit pair w/ 7b9a0f8b | MATCH-evolved (49b7f966) |
| 8 | badeaf00 | SA | C | §3.6.1/§7.1 "#11's stamping half" | **TRUE** | #11 is distinguishability-only; stamping lives in the DB-enforced group; DDR-001 check 6's two parts rescue intent, not citation | ON | UNIQ both draws | NOVEL |
| 9 | f4a5ba9d | coh | C | §9 version pins | **HELD-MIS-SEV** | Content-TRUE (4/4 pins verified vs substrate); self-declared held check emitted as defect — class instance #3; struck from defect set, POSITIVE-equivalent over-cap | ON | UNIQ | class lineage fe2b5642 |
| 10 | 4ab8d42c | coh | M | §3.4.3 branch-(i) dual surface | **TRUE-** | Real seam (edge component structurally unreachable through Evidence chain); caveat: composition-site ≠ inheritance-site conflation. Rider: branch-(i) × #24 ceiling forecloses the routed rollup's access to per-target certainty | ON | D1-010; draw-1-only stratum | NOVEL stratum |
| 11 | 2814cfe0 | coh | M | §3.4.3 determination vs canon | **TRUE-** | Mitigation-insufficiency step genuine (contested flag doesn't relocate authority); caveats: "deferral-sharpens rule" is fabricated named authority (zero repo hits), heavy root overlap | ON | D1-010 #5 | MATCH (be9b148e direct) |

**POSITIVEs — 8× TRUE**, all verified against substrate as genuine holds:
71db9dd2 (LAA, owned/not-owned boundary) · cedbd59a (LAA, §7.1/§7.2 dependency declaration) ·
042a6065 (SA, read-discipline trio) · 943c58ff (SA, write-authorship seam) · 4f99272d (EA, gateway-authors-nothing) ·
6355ae75 (EA, forthcoming-upstream routing; Items 2d(v)/2e(ii) verified) · e305762b (coh, Species-2 vs authors-nothing) ·
7b9a0f8b (coh, #25 honest disclosure — the credit half of D2-010).
Caps held 2/2/2/2. **P1-010:** four of eight credits orbit the authorship boundary (71db9dd2, 943c58ff,
4f99272d, e305762b) — first cross-hat POSITIVE cluster; 943c58ff/4f99272d a genuine SA/EA near-dup.
Read: four altitudes independently electing the document's central claim as its strongest survived attack.

## §3 Families

**D1-010 — §3.4.3 inherited-confidence derivation** (5 members, 3 hats, 4 strata: authority-boundary root
4c79e2ac; τ/form 9a21625e; class-base anchor 6e21f037; branch-(i) dual-surface 4ab8d42c; determination-vs-canon
2814cfe0). All TRUE/TRUE-; all decision-bearing, correctly. The v0.2.0 declaration executed run-009's R6
*inclination* ("a v0.2.0 question, not ruled here"); the family is that unruled question surfacing.
**D2-010 — §3.5.4 #25 window** (defect root 708bcb75 + credit 7b9a0f8b: one locus, two honest sides).
Both families reproduce in draw 2 → union table, fold-in §2.

## §4 Watch-item verdicts (this run's scope)

- **Locus-entailment inflation (arbiter):** instance #2 — 6c1aff22's authority_locus groups "#25 timing"
  under DDR-002 §Named gaps, which does not contain it (the five gaps verified by enumeration). Real source,
  fabricated entailment; non-load-bearing (dry mode). n=2 at this run's close, watch-only. *(n=3 fires in the
  fold-in → gen-5 corrective; see companion §5.)*
- **Cap-pressure severity nit:** instance #3 — f4a5ba9d, textbook class shape (no defect asserted, emitted
  COSMETIC), coherence at its 2-POSITIVE cap, mechanism matching fe2b5642 exactly. **Corrective TRIGGERED and
  ratified (gen-4):** severity discipline restated with the cap interaction named — a held check is a
  POSITIVE-class emission; at cap, drop it, never re-label as defect. All four reviewer prompts (the rule's
  home; the pressure is structural to floor/cap, and draw-level pathologies proved hat-independent);
  own ratified calibration event; own micro RBT ticket post-RBT-15, landing before the next review run.
  Post-gen-4 baseline: this class goes to zero; the first post-gen-4 instance is the corrective's real test.
  Explicit non-instances this run: 4e4f33d4, badeaf00 (defects genuinely asserted).
- **Reviewer-side "never surfaced" species (named this run):** 4dfe13af — real loci, entailment contradicted
  by the record's own surfacing apparatus. Kin of the arbiter §4 species, reviewer-side. *(Fold-in adds
  13e08962: one per draw, LAA both times.)*
- **DB-rate (draw-1 scope):** 6/6 genuine — every decision-bearing call sits on D1/D2's genuinely open
  decisions. No conservatism drift visible in this draw. *(Union verdict → fold-in §5.)*

## §5 Arbiter stream

11/11 classifications, zero corrective retries, zero parse failures. Confidence: 8 high / 3 medium —
the mediums (4c79e2ac, 6c1aff22, 4ab8d42c) all sit on genuinely entangled calls; calibration honest.
Classification precision: 6/6 DB genuine; 5 resolvable with loci 4 clean / 1 half-inflated (§4 above).
**Named pattern:** on 4dfe13af, 6c1aff22, 4e4f33d4, and badeaf00 the resolvable authority_locus was
itself the finding's rebuttal or fix — the locus discipline is functioning as a de-facto validity screen
beyond its classification brief. (Structural asymmetry: DB classifications carry no locus, so this screen
never runs on them — observation recorded here, consequence lands in the fold-in on 4b3e626e.)
Cost note: one wasted arbiter call on the HELD-MIS-SEV emission (~82k in), fourth of its class;
gen-4 addresses the source. Cache: 10 of 11 arbiter calls read 81,376 cached tokens (gen-3 delivered).

## §6 Scorecard

| Metric | Value |
|---|---|
| Findings ruled | 19/19 (11 classified + 8 POSITIVE) |
| Validity | 16/19 — 2 TRUE · 5 TRUE- · 1 HELD-MIS-SEV (content-TRUE) · 8 POSITIVE-TRUE · **3 OVER** |
| Arbiter classification | 6/6 DB genuine · 5/5 resolvable correctly routed · 1 locus half-inflation |
| Cumulative validity-precision ledger | 121/128 → **137/147** |
| Correctives fired | gen-4 (severity/cap restatement — ratified this audit) |

*Disposition of the ruled findings — union disposition list, SDD-001 v0.2.0 disposition, and RBT-15
acceptance check — is carried at session scope, not in this file; see the fold-in §6 and the session's
disposition record.*
