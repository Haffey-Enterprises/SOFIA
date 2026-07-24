# File: docs/reviews/2026-06-21-rbt-13-ddr-002-substrate-v0_5-antagonistic-review.md
# Author: Thaddeus Haffey — Executive Architect, Haffey Enterprises LLC
# Created: 2026-06-21
# Description: Fresh Pass-1 antagonistic review (DIRECTIVE-032) of the DDR-002 Graph Schema design substrate v0.5 — read and attacked as a first-time artifact, challenging every assumption and design decision (with emphasis on the new machinery the prior folds introduced and the schema's trajectory against R25), to find every gap, loophole, and issue before the substrate is used to author a DDR.

# BRUTAL Antagonistic Review — DDR-002 Graph Schema Substrate (v0.5) — 2026-06-21 (fresh Pass 1)

| Field | Value |
|---|---|
| **Review Date** | 2026-06-21 |
| **Reviewer** | claude.ai antagonistic reviewer (architecture leadership team — adversarial stance), DIRECTIVE-032; read as a first-time artifact |
| **Subject** | `DDR-002-graph-schema-design-substrate-v0.5.md` (RBT-13) |
| **Mandate** | Full fresh read; pressure-test for every gap, loophole, and issue **if used to author a DDR**; challenge every assumption and design decision. |
| **Canon fresh-fetched** | Decision Ledger (R25 clarification + R27-amendment refinement, both verified present and truthful); DDR-001 v1.0.0 (project knowledge). |
| **Outcome** | **NO BLOCKERS — 9 MATERIAL, 2 COSMETIC.** v0.5 is the most coherent version yet and carries no broken or self-contradictory design. The material findings are real gaps in the *new machinery* the last fold introduced — plus one **strategic** finding that matters more than the rest: the five-cycle review process is now driving the schema *past* its empirical base, against R25's own warning. |

---

## §0 Stance — and the honest read of where this is

Read cold, attacked cold. The trend across the cycle is unambiguous and worth stating plainly because it shapes what a useful brutal pass should now say:

| Pass | Subject | Blocking | Material |
|---|---|---|---|
| Antagonistic Pass-1 | v0.3 | 3 | 14 |
| Antagonistic Pass-2 | v0.4 | 1 | 10 |
| **This pass** | **v0.5** | **0** | **9** |

This is genuine convergence — each blocker found has been resolved soundly, not papered over, and the capture layer is verifiably truthful again (R25 clarification + R27 refinement both in the ledger, saying what the substrate says). A reviewer who manufactured a blocker here to "stay brutal" would be lying.

**But brutal has a different job at iteration 5 than at iteration 1.** Early passes hunt holes in the design. This pass's sharpest finding (F-9) is about the *process*: the antagonistic loop has started **adding machinery faster than the empirical base justifies it**, which R25 explicitly warns against. Retraction protocols, multi-condition disjunction, `ProvenanceSummary` materialization, three-axis `Decision` provenance — these are review-induced elaborations with *zero empirical instances*, now being locked as T1/T2 contract. The honest brutal read is not "find a 4th blocker"; it is "you have converged on the findings, and the live risk has flipped from *under*-specification to *over*-specification." That is §2's headline.

Closed rulings (R3, R6, the closed Option sets) are not relitigated. Where a finding cites R25/R27, it tests the soundness of this cycle's clarification, which is fair game.

---

## §1 MATERIAL — gaps in the new machinery

### F-1 — Conditionality is now expressed two unreconciled ways; a consumer can honor one and miss the other
**Location:** §2.1 `Catalog:Technology` (`tier_applicability[]`, `approved_data_classifications[]`); §5 `applicability_state: conditional` + §2.4 `Condition` (D-3); §7 #19.
**The attack.** "May I use this Technology in this context?" now has **two** schema answers. An *ingested* Technology constrains applicability via Catalog fields (`tier_applicability[]`, `approved_data_classifications[]`). A *promoted* Technology constrains it via `applicability_state: conditional` + a `Condition` predicate evaluated at retrieval (#19). These are different mechanisms, on different node-origins, checked on different paths — and nothing unifies them. The N-1 fix added a *second* conditionality model rather than reconciling with the Catalog one that already existed. A consumer (or SDD) that implements the `Condition`-predicate check but reads `tier_applicability[]` as advisory — or vice versa — silently mis-scopes.
**Risk.** The exact safety failure N-1 was raised to prevent (using knowledge out of its approved scope) re-opens through the *other* conditionality path; the schema has two answers and no statement of how they compose.
**Reconcile.** State the unified applicability model: is `applicability_state`/`Condition` the general mechanism (with `tier_applicability[]` a Catalog-specific special case the validator also reads), or are they parallel-and-both-binding? Name the composition rule so a consumer can't satisfy one and violate the other.

### F-2 — Verdict-on-the-edge + append-only governance lets one candidate carry conflicting outcomes with no precedence rule
**Location:** §2.4/§3/§5 (`DECIDED_ON {outcome}`, P4-2; supertype `Decision.decision` dropped); §5 (`CandidatePromotion.status` "legitimately diverges from the edge verdict"); §7 #15.
**The attack.** Moving the verdict onto the `DECIDED_ON {outcome}` edge is clean for the batch case — but governance is **append-only** ("a re-decision is a new node"). So a single `CandidatePromotion` can accumulate **multiple `DECIDED_ON` edges with conflicting outcomes** — rejected by decision D1, then approved by a re-decision D2 — and there is **no edge-level ordering or supersession** to say which governs. `CandidatePromotion.status` can't be the tiebreaker because the schema explicitly says it "legitimately diverges" from the edge verdict. And #15 (promoted-origin → an approving edge) is satisfied by **any** approving edge, so a candidate whose *governing* verdict is "rejected" still passes #15 if a stale earlier `approved` edge exists.
**Risk.** Ambiguous promotion authority — a node can be materialized/retained as promoted on the strength of a superseded approval, with no schema rule to detect that the operative verdict is now a rejection.
**Reconcile.** Define verdict precedence for multi-edge candidates: latest `decided_at` wins, or an explicit `SUPERSEDES` between decisions, and re-key #15 to "the **governing** approving edge," not "any."

### F-3 — The retraction protocol has no terminal lifecycle state and no enumerated approving-decision invariant
**Location:** §2.4/§5 (R-RETRACT: reversing `CandidatePromotion` `promotion_type: retraction` + `RETRACTS` edge); §5 `CandidatePromotion.status` enum; §7 #15.
**The attack.** Two gaps in the re-modeled retraction. (a) A reversing `CandidatePromotion` is still a `CandidatePromotion`, whose `status` enum is `{proposed…promoted/rejected}` — there is **no "retraction-executed" terminal status**, so a successful retraction candidate either misuses `status: promoted` (it retracted, it didn't promote) or needs a value the enum lacks. (b) #15 enforces the approving-decision trace only along `PROMOTES_TO_KNOWLEDGE`; the `RETRACTS` path has **no parallel enumerated invariant**, so a node could be set `applicability_state: retracted` without an approving `PromotionDecision` and **no §7 check catches it** — the retraction-traceability is described in §5 prose but not in the enforced set. Retraction is an EA-gated KG mutation (correctly, per the R-RETRACT principle); an unguarded one is exactly the self-modification DDR-001 check #4 forbids.
**Risk.** Retraction is under-modeled in the same way promotion was before #15 existed — an un-gated `retracted` flip is structurally possible and uncaught.
**Reconcile.** Add a retraction terminal status (or fold retraction lifecycle onto `promotion_type` + the edge outcome), and add a §7 invariant: "every `applicability_state: retracted` node traces via `RETRACTS` ← reversing `CandidatePromotion` ← an approving `DECIDED_ON` edge to a `PromotionDecision`" (the §5 prose, promoted to enforced).

### F-4 — `ProvenanceSummary`'s post-expiry guarantee depends on materialization timing the schema defers
**Location:** §5 `(:Reasoning:ProvenanceSummary)` ("materialization timing … snapshot at-promotion vs at-expiry … → DDR-003/RBT-15"); §7 #21.
**The attack.** #21 requires the `ProvenanceSummary` to "remain traversable after the originating `Evidence` is retained-out." But whether the summary *exists at expiry* depends on **when it's materialized**, which is deferred. If it's built **at expiry**, there's an ordering race: the retention process must construct the frozen summary *before* deleting the `Evidence` it snapshots — and if that ordering isn't guaranteed, #21 is violated by construction (the summary references Evidence that's already gone). The invariant is written as if the summary is always present; its presence is an unspecified timing/ordering contract.
**Risk.** The A-2 fix (preserve provenance past expiry) silently fails if materialization races expiry — and the schema can't catch it because it deferred the one ordering constraint that makes #21 sound.
**Reconcile.** Even if the *trigger/process* is DDR-003/RBT-15, DDR-002 should own the **binding ordering invariant**: "a durable terminal-`promoted` candidate's `ProvenanceSummary` is materialized no later than, and atomically with respect to, the expiry of any `Evidence` it summarizes." That's schema-level, not policy.

### F-5 — `#19` filters on "active `Condition` predicates," but `Condition` has no active/superseded field
**Location:** §2.4 `Condition` (`condition_id`, `predicate`, `created_at`, provenance — no status); §7 #19 ("at least one of the node's **active** `Condition` predicates"); §2.4 (condition-set lifecycle → DDR-003).
**The attack.** #19's disjunctive consumption is over the node's **active** conditions — which is the mechanism by which a conditional grant can be *narrowed* (deactivate a condition). But the `Condition` node carries **no status/active field**. So "active vs superseded condition" is **unrepresentable in the schema**, and the narrowing path #19 presupposes has no structural support. The lifecycle is deferred to DDR-003 — but DDR-002 gave DDR-003 no field to express the state #19 already depends on.
**Risk.** Conditional grants can only ever *accrete* (union widens) in practice, because there's no way to mark a condition inactive — the opposite of what #19's "active" wording implies, and a real over-permissioning path (a condition that should be retired stays binding-eligible forever).
**Reconcile.** Give `Condition` a `status`/`active` T2 field (the version-lifecycle pattern), so #19's "active" has a structural referent and DDR-003 can narrow by superseding. Tiny addition, closes the gap the disjunctive model opened.

### F-6 — `ProvenanceSummary` is a fourth RG-namespace type outside the provenance-existence-constraint scope
**Location:** §5 `(:Reasoning:ProvenanceSummary)` ("provenance (T1)"); §7 existence-constraint scope ("KG nodes + the **three** authored RG types + Artifact family").
**The attack.** The §7 provenance existence constraint still enumerates exactly three RG types (`ReasoningSession`, `ReasoningProgress`, `RejectedAlternative`). `ProvenanceSummary` is a **new, fourth** `:Reasoning:`-namespace node that carries `provenance (T1)` — but it's neither in the enforced scope nor exempted, and its `origin_mechanism` is unspecified (it's a derived snapshot — `derived`?). A node that carries provenance but sits outside the constraint that enforces provenance is exactly the kind of scope-drift the M-7/A-α scoping work existed to close.
**Risk.** `ProvenanceSummary` can be written provenance-incomplete with no constraint catching it; the carefully-bounded RG provenance scope has quietly grown a member it doesn't cover.
**Reconcile.** Add `ProvenanceSummary` to the existence-constraint scope (it's authored/derived frozen state — it should carry the group) and specify its `origin_mechanism`.

### F-7 — `decision_origin` and `origin_mechanism` on `GateDecision` look correlated, not orthogonal
**Location:** §2.4 `GateDecision` (CR-G: `decision_origin` external/self **and** `origin_mechanism` ingested/authored, "the orthogonal originator axis").
**The attack.** The cold-read fold added `decision_origin` (who originated) as "orthogonal" to `origin_mechanism` (how the node entered). But the two stated states track 1:1: a current external gate is `decision_origin: external` + `origin_mechanism: ingested`; the future SOFIA-authoritative gate is `decision_origin: self` + `origin_mechanism: authored`. No case is given where they diverge (external-originated yet authored? self-originated yet ingested?). If they're genuinely 1:1, `decision_origin` is **redundant** with `origin_mechanism`, and the "orthogonal axis" framing adds a field without adding information — against R25's lean-payload posture.
**Risk.** A redundant T2 field that two writers can set inconsistently (now there are two ways to say "external," and a node could carry `external` + `authored` by mistake, with no invariant forbidding it).
**Reconcile.** Either name the concrete case where the two axes diverge (justifying both), or drop `decision_origin` and derive originator from `origin_mechanism` + the subtype label.

### F-8 — The tiering criterion (N-5 fix) is applied inconsistently, and "RBT-33 finalizes" makes it advisory
**Location:** §7 "Named exposure window + sequencing" (safety-critical tier vs follow tier; "RBT-33 finalizes the placement"); #21 in the follow tier.
**The attack.** The N-5 fix triages the 21 CI-only invariants into a safety-critical tier (ahead of RBT-15) and a follow tier — a good move. But (a) the stated criterion ("hard to detect or reverse" integrity violations precede RBT-15) puts **#21 in the *follow* tier**, even though a provenance chain broken at `Evidence` expiry is both hard-to-detect *and* irreversible (the Evidence is gone) — it meets the safety-critical criterion as written. (b) "**RBT-33 finalizes** the per-invariant placement" makes the tier a *recommendation*, not a binding contract — so the protection N-5 sought ("the safety-critical set is enforced before the gateway writes") is only as strong as RBT-33 honoring a tier DDR-002 can't bind.
**Risk.** Either #21 (and possibly others) writes ahead of its enforcement despite meeting the safety bar, or the whole tier slips because RBT-33 re-triages — and DDR-002's landing posture leaned on the tier being real.
**Reconcile.** Re-test each invariant against the stated criterion (move #21 up, or refine the criterion to exclude it explicitly), and state which tier placements DDR-002 treats as *binding* on RBT-33 vs. advisory.

### F-9 — (STRATEGIC, the headline) The review cycle is now driving the schema past its empirical base, against R25
**Location:** whole-substrate; **R25** ("Anchored against the thin POC-spreadsheet origin … over-specifying from a thin empirical base is guessing").
**The attack.** R25's load-bearing warning is that the prior schema's origin is a *single thin POC spreadsheet*, and that completing structure beyond what the empirical base supports is **guessing**. Across five cycles, the antagonistic loop has added: a retraction protocol (reversing candidate + `RETRACTS` + `applicability_state: retracted` + dual-decision traceability), multi-condition **disjunctive** consumption with compound-predicate fallback, a `ProvenanceSummary` node with at-promotion-vs-at-expiry materialization semantics, three-axis `Decision` provenance, and a 21-invariant tiered CI set. **None of these has a single empirical instance** — they are responses to *hypothetical* holes a reviewer (me) imagined. That is precisely the over-specification R25 names: the schema is increasingly fit to *imagined* cases, locked at T1/T2 (expensive to reverse), on a POC-thin base. The antagonistic process, past a point, stops de-risking the schema and starts *manufacturing* surface to maintain.
**Why it's the headline.** Every other finding here is "tighten the new machinery." This one asks whether the new machinery should exist *yet*. A schema over-fit to a reviewer's imagination is a worse authoring source than a lean one with named gaps — it locks speculative decisions as contract and enlarges the blast radius R25/C-3 are trying to keep small.
**Risk.** DDR-002 ships as a large, elaborate contract whose speculative mechanisms (retraction lifecycle, condition disjunction, summary timing) get falsified by first real use — and reversing a T1/T2 contract is the expensive case R25 exists to avoid.
**Reconcile.** Before authoring, run one **empirical-warrant pass**: for each mechanism added during review, ask "is there a real instance that needs this, or is it closing an imagined hole?" Demote the imagined-hole mechanisms from locked T1/T2 contract to **T3 / named-gap** (R25's explicit lever — "gaps named, not speculatively filled"), keeping only the structural keys and the empirically-grounded invariants as binding. The discipline that made the early passes valuable (find real holes) should now include the discipline to *not* fill imagined ones.

---

## §2 COSMETIC

- **F-10:** `applicability_state` is a **mutable** field (set by promotion, changed by retraction) on an otherwise **append-only / supersede-only** versioned node — so the node now carries *two* mutable lifecycle fields (`status` for version-lifecycle, `applicability_state` for promotion-lifecycle). It's defensible (status transitions are already in-place), but the re-promotion-after-retraction transition is unspecified (can a `retracted` node return to `unconditional`, and by what act?). Name the transition rules, or the FSM is implicit.
- **F-11:** The substrate is now 449 lines / 21 CI invariants / 4 RG node-types / a 3-axis governance-provenance model. The authored DDR will be correspondingly large — worth a deliberate check that the *DDR* (not the substrate) stays within the layer-of-abstraction §0/C-3 commits, rather than carrying every substrate elaboration into the contract. (Related to F-9; this is the output-shape symptom of it.)

---

## §3 What survived the attack (kept honest)

Most of v0.5 is sound, and several prior-pass fixes hold up cleanly under fresh load: the **`applicability_state` marker** correctly gives conditional/retracted knowledge a local structural key (closing the v0.4 N-1 invisibility — modulo F-1's reconciliation gap); the **`ProvenanceSummary` node** keeps post-expiry audit graph-native (modulo F-4's timing); the **accountability-not-determinism** reframe (N-7 → R27 refinement) is genuinely correct and well-realigned to ADR-001 §2.5 — the "encoding-density-growth, promoted facts in-scope and distinguishable" framing is the right model, and the as-of machinery handles temporal reproducibility; the **`DECIDED_ON {outcome}`** move is the right shape for batch decisions (modulo F-2's precedence gap); the **two-axis provenance matrix** is now total and N/A-for-promoted is correct; and the **capture layer is verifiably truthful** across all five cycles. This is a mature artifact — which is exactly why F-9, not a fabricated blocker, is the finding that matters.

---

## §4 Outcome

> **NO BLOCKERS — 9 MATERIAL · 2 COSMETIC.** v0.5 has converged: no broken or self-contradictory design remains, and the new machinery is mostly sound. Eight material findings tighten that machinery (F-1 dual conditionality, F-2 conflicting edge-verdicts, F-3 retraction lifecycle+invariant, F-4 summary timing, F-5 missing `Condition.status`, F-6 `ProvenanceSummary` scope, F-7 redundant `decision_origin`, F-8 tier inconsistency). The ninth (F-9) is the one to act on first: **the review loop is now over-specifying against R25**, and the highest-value next move is an empirical-warrant pass that *removes* speculative mechanism, not adds more.

**The recommendation that matters.** Resolve F-1/F-2/F-3 as genuine integrity gaps (they're real). Then **stop adding and start subtracting**: run F-9's empirical-warrant pass, demote the imagined-hole mechanisms to R25 named-gaps, and let the DDR author from the lean, empirically-grounded core. The trend (3→1→0 blockers) says the schema is ready on soundness; the risk now is shipping it *heavier* than its evidence supports. A sixth antagonistic pass that only adds machinery would be the process failing R25, not the schema.

**Disposition (returns to the primary session).** None folded here. The serialize gate (RBT-39) and RBT-33 tiering are unaffected — these are schema-design and schema-scope findings, upstream of both.

---

## §5 Cross-references
- **Subject:** `DDR-002-graph-schema-design-substrate-v0.5.md` (RBT-13).
- **Canon (fresh-fetched, verified truthful):** Decision Ledger R25 clarification (denormalization boundary) + R27-amendment refinement (accountability-not-determinism), Notion `374caeea-…`; DDR-001 v1.0.0 (project knowledge).
- **Prior passes:** antagonistic Pass-1 (v0.2), Pass-2 (DDR-001 cross-check), three-hat Pass-3 (v0.3), antagonistic Pass-2 (v0.3), three-hat Pass-4 + antagonistic (v0.4). This pass reads v0.5 fresh.
- **Ruling whose intent is invoked (not relitigated):** R25 (the over-specification warning — F-9), R27 refinement (accountability framing — confirmed sound).
