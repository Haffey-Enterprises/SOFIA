# File: docs/reviews/2026-06-21-rbt-13-ddr-002-graph-schema-substrate-three-hat-review-pass-5.md
# Author: Thaddeus Haffey — Executive Architect, Haffey Enterprises LLC
# Created: 2026-06-21
# Description: Fresh full three-hat review of the DDR-002 Graph Schema design substrate v0.5 (RBT-13), conducted clean-slate ("as if Pass 1") per operator direction. Verifies the v0.5 fold (Pass-4 three-hat + heavyweight antagonistic Pass-2 — 20 findings) against fresh-fetched canonical state (R25 clarification; R27-amendment refinement; RBT-27) and re-derives findings independently.

# Three-Hat Review — 2026-06-21 (RBT-13 DDR-002 Graph Schema Substrate v0.5 — Fresh Full Pass, conducted as Pass 1)

| Field | Value |
|---|---|
| **Review Date** | 2026-06-21 |
| **Reviewer** | Claude (claude.ai design instance) — fresh-eyes three-hat reviewer wearing LAA / SA / EA hats, under DIRECTIVE-026, on behalf of Thaddeus Haffey — Executive Architect, Haffey Enterprises LLC |
| **Conduct** | Clean-slate per operator direction — findings re-derived independently from a full read of v0.5; prior findings used only to confirm folds, not to bound the search. |
| **Scope** | `DDR-002 Graph Schema — Ratified Design Substrate (v0.5)` (RBT-13) — soundness/clarity as authoring input; conformance to fresh-fetched canonical state (R25 clarification; R27-amendment refinement; ADR-002; DDR-001 v1.0.0); independent fresh-eyes pass. |
| **Authority** | RBT-13 acceptance criterion; ENG-STD-001 §12.6 (three-hat) + CSD DIRECTIVE-007 (§7.2 severity vocabulary). |
| **Outcome** | **PASS WITH FINDINGS.** 0 BLOCKING; **2 MATERIAL** (both in this cycle's new constructs — retraction-approval invariant missing, symmetric to #15; `applicability_state` × supersession carry-forward unspecified); 1 COSMETIC. The full 20-finding v0.5 fold and the amended-canonical sync verify clean. Two gates remain before Code authoring: this review converging **and** the B-4 serialize (RBT-39 / DDR-001 v1.1.0 landing). |

---

## §0 Historical Context & Conduct

v0.5 folds the Pass-4 three-hat (0 blocking / 3 material / 3 cosmetic) and a heavyweight **antagonistic Pass-2 (1 blocking / 10 material / 2 cosmetic)** on v0.4 — 20 findings dispositioned one-per-turn. It leans on two ledger updates dated this cycle: the **R25 Clarification** (denormalization boundary) and the **R27-amendment Refinement** (accountability-not-determinism). The substrate is now highly mature (450 lines, 21 CI-only invariants, tiered).

Per operator direction this pass is **clean-slate**: I read v0.5 end-to-end and re-derived findings independently. The fold and the canonical sync are verified (§2.4); the two MATERIAL findings (§2.2) are *new*, surfaced by the fresh read, both in this cycle's newly-introduced surface (retraction; the `applicability_state` marker).

---

## §1 Scope

### 1.1 In-scope

Full v0.5 substrate as authoring input; conformance to fresh-fetched canonical state; independent finding search across the whole schema.

### 1.2 Sources fresh-fetched this pass (DIRECTIVE-026 §26.5)

- **Notion Reboot Decision Ledger** — re-fetched (snapshot 2026-06-21T02:10Z); now carries the **R25 Clarification** (R25 governs hot-path live-fact duplication only; bounded point-in-time/retention-boundary snapshots and sync-checked edge-mirrors are not breaches — the frozen `ProvenanceSummary` node modeled as traversable) and the **R27-amendment Refinement** (the EA gate is the *accountable-consolidation* control restoring accountability/authoritativeness, not determinism — realigned to ADR-001 §2.5; promoted facts in-scope and distinguishable; consolidation-health → RBT-27; vocabulary to `origin_mechanism` + `ProvenanceSummary` node; retraction → reversing `CandidatePromotion` + `RETRACTS`). Ledger-elevation: only R25/R27 clarified/refined this cycle; the v0.5 R-* dispositions remain held in the substrate fold-log (no R28+).
- **Linear RBT-27** (reasoning-machinery, parked) — confirmed exists (Deferred; net-new); an appropriate home for the consolidation-health/weighting question N-7 routes there. **RBT-22/25/14/15/16/17/33/39/40/41** unchanged from prior fetches this session.
- **DDR-001 v1.0.0** (project knowledge) and **ADR-002** — static; used to confirm the v0.5 groundings (DDR-001 lines 62/65/81/89; ADR-002 §2.6; the N-7 ADR-001 §2.5 realignment is a ratified ledger refinement, taken as authority).

### 1.3 Out of scope

Authored DDR-002 (post-authoring gate); DDR-001/DDR-003 internals beyond cross-checks; SDD realization; conformance mechanization (RBT-33); ADR-002 stale author string (RBT-36).

---

## §2 Findings

### 2.1 BLOCKING findings

**None.**

### 2.2 MATERIAL findings

#### Finding P5-1: Retraction is modeled as EA-gated, but §7 carries no retraction-approval invariant symmetric to #15

**Location:** §2.4 (line 109, "un-promoting … is a **reversing `CandidatePromotion`** … EA-approved via a `PromotionDecision -[:DECIDED_ON {approved}]->` it"); §5 (lines 221, 225, the `RETRACTS` edge + retraction traceability); §7 (#15 promotion-approval; #20 retracted-read-discipline) — no retraction-approval invariant.

**Description:** v0.5 re-models retraction as an EA-gated KG mutation: a reversing `CandidatePromotion` (`promotion_type: retraction`), approved via a `PromotionDecision -[:DECIDED_ON {approved}]->`, carrying `(CandidatePromotion)-[:RETRACTS]->(KG node)` and setting `applicability_state: retracted`. That EA-gating is the whole rationale for modeling retraction through the promotion machinery ("DDR-002 schema authority on DDR-001's EA-gated-mutation principle"). But §7 enforces this for *promotion* (#15: a `promoted` node must trace to an approving `DECIDED_ON` edge) and **not** for *retraction*: no invariant requires an `applicability_state: retracted` node to trace, via `RETRACTS` ← reversing `CandidatePromotion` ← an approving `DECIDED_ON` edge, to a `PromotionDecision`. #20 is read-discipline (exclude `retracted` from active traversal), not approval-traceability.

**Why material:** The asymmetry means the "retraction is EA-gated" guarantee is *described* but not *conformance-enforced* — a write that sets `applicability_state: retracted` without an approved `RETRACTS` chain would un-gate a retraction (an unauthorized KG mutation in the un-promote direction), undetected by the §7 set. By v0.5's own N-5 tier criterion (a violation that "lets … unapproved/self-modified KG facts … enter authoritative ground truth … hard to detect or reverse"), an un-gated retraction is safety-critical-tier. The promotion side already has #15; retraction is the missing mirror.

**Disposition:** Add a §7 CI-only invariant symmetric to #15 — *retraction-approval*: every `applicability_state: retracted` node traces, via `RETRACTS` ← a `promotion_type: retraction` `CandidatePromotion` ← an approving `DECIDED_ON {outcome: approved}` edge, to a `PromotionDecision`. Place it in the safety-critical tier (ahead of RBT-15), alongside #15.

#### Finding P5-2: The `applicability_state` marker's interaction with version-lifecycle supersession is unspecified

**Location:** §5 (line 219, `applicability_state` "distinct from the version-lifecycle `status`"); §6 (line 235, Option-A supersession, scoped to versioned-ground-truth types — which a promoted node materialized into Catalog can be); §7 (no carry-forward statement).

**Description:** `applicability_state` (`unconditional`/`conditional`/`retracted`) is a property on each `(business_key, version)` promoted node — so it is inherently per-version. The schema states it is orthogonal to the version-lifecycle `status` but does not specify the **supersession carry-forward**: when a promoted node carrying `conditional` or `retracted` is superseded (Option-A creates a new version node), does the new version inherit the marker or default to `unconditional`? A silent default-to-`unconditional` would either drop a conditional scope (the new version is consumed unconditionally — over-admission past an EA-set `Condition`) or revive a `retracted` fact (the new version re-enters active traversal).

**Why material (lighter than P5-1):** It is a real integrity interaction in the new marker, but narrow (only promoted-then-superseded nodes with a non-default marker) and partly gateway/SDD behavior. The schema should at least fix the granularity (per-version vs per-business-key) and name the integrity expectation (no silent conditional-scope loss or retraction-revival on supersession), even if the carry-forward *mechanism* routes to RBT-15.

**Disposition:** State whether `applicability_state` is per-version (requiring explicit carry-forward on supersession) or business-key-scoped (carrying automatically), and name the integrity expectation; route the carry-forward mechanism to RBT-15 if it is gateway behavior. One or two sentences in §5/§6.

### 2.3 COSMETIC findings — noted, no-action required

- **C5-1 — the three-axis GateDecision provenance is correct but intricate.** `GateDecision` now carries the subtype label, `origin_mechanism` (`ingested`/`authored`), and `decision_origin` (`external`/`self`) as three orthogonal axes, with a current-build self-issued-transmitted case mapping to `origin_mechanism: ingested` + `decision_origin: self` and a future SOFIA-authoritative case (CR-G) to `origin_mechanism: authored` + `decision_origin: self`. The model is internally coherent and well-explained (§2.4 line 116), but dense; a one-line worked example of the three combinations in the authored DDR would lower the chance a future author/reader mis-stamps. Purely a clarity aid.

### 2.4 No-drift confirmations (positive findings) — the verification spine

The 20-finding v0.5 fold and the amended-canonical sync verify clean.

**Pass-4 dispositions — all folded as recommended:**
- **P4-1 (retraction marking)** → R-RETRACT: reversing `CandidatePromotion` + `RETRACTS` edge + `applicability_state: retracted` (#20 read-discipline), traceable to both original and retracting decisions (§2.4 line 109, §5 lines 219/221/225). *(P5-1 is the one residual on this surface — the enforcement invariant, not the model.)*
- **P4-2 (batch outcome)** → R-BATCH: verdict moved to the `DECIDED_ON {outcome}` edge uniformly, supertype `Decision.decision` dropped, `CandidatePromotion.status` kept as lifecycle, #15 re-keyed to the per-candidate edge outcome (§2.4 line 107, §3 line 221, §7 #15). Resolved exactly as dispositioned.
- **P4-3 (Condition manifest sync)** → #10 extended to `PolicyRule` **and** `Condition` (§7 #10), with the deeper declared-but-wired-≠-declared-complete gap honestly named (N-4) and routed to RBT-22.
- **C4-1** → #17 extended to `derivation_class: distilled` (§7 #17). **C4-2** → the dead `#1` hedge dropped as unreachable. **C4-3** → fold-log preamble de-versioned to "deferred to acceptance."

**Antagonistic Pass-2 (the blocking + the batch) — verified:**
- **N-1 (blocking)** → the `applicability_state` marker + the #20 read-discipline invariant — conditional/retracted knowledge is never consumed out-of-scope (§5 line 219, §7 #19/#20).
- **N-3** → `provenance_summary` blob re-modeled as a frozen *traversable* `(:ProvenanceSummary)` node (#21), post-expiry audit stays a traversal — matching the R25 clarification.
- **N-5** → the CI-only set tiered: a safety-critical tier (ahead of RBT-15) with a stated criterion + a follow tier, RBT-33 finalizing — consistent with R27's "ahead of RBT-15," no posture change.
- **N-6** → cost as-of-record permanent retention justified on R24 grounds (decision-paced, variance-needed; structurally unlike Operational's archivable tail), volume-management (not deletion) → RBT-25.
- **N-7** → accountability-not-determinism, realigned to ADR-001 §2.5; promoted facts in-scope/distinguishable; consolidation-health → RBT-27 — matching the R27 refinement.
- **N-8/N-9/N-10/N-11/N-13** → selection = approving gate edge (no `selected` flag); exactly-one-parent re-justified per-conclusion; multi-condition disjunctive; provenance matrix completed (`promoted → N/A`); denormalization boundary consolidated (R25 clarification). All land.

**Canonical sync & governance hygiene:**
- **R25 Clarification & R27 Refinement** — v0.5 reflects both faithfully (§1 lines 64–68; §4 line 195; §5 ProvenanceSummary; #19/#20). In exact sync with the 02:10Z ledger.
- **DDR-001 groundings** — RejectedAlternative-authored (line 65), A-2/ProvenanceSummary schematizing summary-on-evidence-expiry (line 89), `PRODUCED` 0..* (line 62), Artifact node-family (lines 81/87/102/105) all hold against project-knowledge DDR-001.
- **No loose deferral tail** — all forward-pointers exist (RBT-27 verified this pass; RBT-14/15/16/17/22/25/33/39/40/41 prior). "Zero new tickets (DIRECTIVE-025-clean)" holds.
- **Ledger-elevation threshold** — only R25/R27 clarified/refined; R-* forks held in fold-log (no R28+), matching the fresh ledger.
- **Criterion-shift discipline** — the retraction model, ProvenanceSummary, and determinism framing each *supersede* their v0.4 forms as refined-not-reversed (fold-log line 449), cleanly recorded.
- **M-9 honesty, FP-1 tracking, two-gate landing posture** — all preserved (§5 line 224; fold-log line 447; §8 line 314).

### 2.5 Observation

The §7 set is now 21 CI-only invariants, tiered. Both MATERIAL findings imply a §7 addition/clarification (P5-1: a retraction-approval invariant in the safety-critical tier; P5-2: an `applicability_state` carry-forward statement) — they belong in the same set/section when folded.

---

## §3 Forward-Pointer Triage

No new tickets warranted. Carried (held for ratification — no tracker writes made by this review):

| ID | Summary | Status |
|---|---|---|
| RBT-13 (update) | Stale "R12 cost" ledger line → R23 (+R24…R27) | Tracked for the RBT-13 close (fold-log line 447); held |
| RBT-36 (existing) | ADR-002 stale author string | Already tracked; v0.5 authors DDR-002 with current string |

The two MATERIAL findings (P5-1/P5-2) and C5-1 fold into a v0.6 substrate revision — schema-contract refinements to §5/§6/§7, no new tickets.

---

## §4 Audit Outcome

> **PASS WITH FINDINGS.** The v0.5 fold of the Pass-4 three-hat + the heavyweight antagonistic Pass-2 (20 findings) verifies complete and **in exact sync with the amended canonical state** (R25 clarification; R27-amendment refinement) across every cross-reference checked, with the DDR-001 groundings confirmed. The clean-slate pass surfaces **0 BLOCKING**, **2 MATERIAL** — both in this cycle's new constructs: P5-1 (no retraction-approval invariant symmetric to #15 — the EA-gated-retraction guarantee is described but not enforced) and P5-2 (`applicability_state` × supersession carry-forward unspecified) — and **1 COSMETIC**. Neither is a design contradiction; P5-1 is the heavier (a safety-critical-tier integrity invariant that is genuinely absent), P5-2 a contained clarity/granularity fix.

**Per-hat verdicts (ENG-STD-001 §12.6 aggregation):**

| Hat | Read | Verdict |
|---|---|---|
| **LAA** — *what is this change?* | Matches RBT-13's R8 schema half; new policy (retraction, condition-set lifecycle, consolidation-health) correctly routed to DDR-003/RBT-27, schema-contract retained; no loose tail (RBT-27 verified). | `proceed` |
| **SA** — *how does it conform?* | All cross-refs resolve and match the 02:10Z ledger; DDR-001 groundings confirmed. Raises P5-1 (missing retraction-approval invariant, asymmetric with #15), P5-2 (`applicability_state`×supersession), C5-1. | `proceed-with-changes` |
| **EA** — *should it land in this shape, now?* | Posture sound: the accountability-not-determinism realignment to ADR-001 §2.5 is well-grounded; the tiered-invariant sequencing is honest; criterion-shift discipline clean. Concurs P5-1 (an un-gated retraction is an unauthorized KG mutation — an integrity-posture gap the EA-gated-mutation principle is meant to close). | `proceed-with-changes` |

**Gate decision — two gates remain before Code authoring (unchanged in shape):**
1. **This review converges** — fold P5-1 (add the retraction-approval invariant, safety-critical tier) and P5-2 (specify `applicability_state` carry-forward) into v0.6; a short re-confirm closes the review gate. Both are §5/§6/§7 refinements.
2. **The B-4 serialize clears** — **RBT-39 (DDR-001 v1.1.0) must land on `develop`** before Code authors DDR-002 (Todo; its own three-hat cycle on the critical path). The substrate states this (§8 line 314): authoring holds until both gates clear.

The schema is substantively complete and, on the verification spine, exceptionally well-synchronized to canon; the residue is one real integrity-symmetry invariant and one contained clarification, both in this cycle's newest surface.

---

## §5 Cross-References

- **Authority:** RBT-13 acceptance criterion; ENG-STD-001 §12.6; CSD DIRECTIVE-007 (§7.2 severity vocabulary).
- **Substrate reviewed:** `DDR-002 Graph Schema — Ratified Design Substrate (v0.5)`; authoring target `docs/ddr/DDR-002-graph-schema.md` (gated on RBT-39 landing).
- **Prior passes:** `…-review.md` (Pass 1), `…-pass-2.md`, `…-pass-3.md`, `…-pass-4.md`. This pass conducted clean-slate per operator direction.
- **Canonical authorities fresh-fetched:** Reboot Decision Ledger (`374caeea…`, snapshot 02:10Z — R25 clarification, R27-amendment refinement); Linear RBT-27 (+ RBT-22/25/14/15/16/17/33/39/40/41 this session); ADR-002 §2.6; DDR-001 v1.0.0.
- **Findings disposition tracking:** P5-1 → §7 retraction-approval invariant (safety-critical tier); P5-2 → §5/§6 `applicability_state` carry-forward statement; C5-1 → optional DDR worked example; FP-1 → tracked for RBT-13 close.
- **Future cadence:** fold P5-1/P5-2 → short re-confirm closes the review gate → RBT-39 lands DDR-001 v1.1.0 → Code authors DDR-002 → separate post-authoring RBT-13 acceptance three-hat against the authored DDR.
