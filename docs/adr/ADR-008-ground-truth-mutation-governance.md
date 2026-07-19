# File: docs/adr/ADR-008-ground-truth-mutation-governance.md
# Author: Thaddeus Haffey — Executive Architect, Haffey Enterprises LLC
# Created: 2026-07-17
# Description: ADR-008 — Ground-Truth Mutation Governance. Establishes that every mutation of enterprise ground truth in the Knowledge Graph is subject to a human-accountable control calibrated to the mutation's source class, and homes the upstream authority for un-promotion that ADR-001 §2.5 does not reach.

# ADR-008: Ground-Truth Mutation Governance — a human-accountable control on every mutation of enterprise ground truth, calibrated per source class

| Field | Value |
|---|---|
| **Document ID** | ADR-008 |
| **Status** | ACCEPTED |
| **Version** | 1.1.0 |
| **Date** | 2026-07-17 |
| **Authors** | Thaddeus Haffey (Executive Architect) |
| **Supersedes** | None — establishes new platform principle |

---

## 1. Context

The Knowledge Graph (KG) is the enterprise's unified ground-truth context, and the graph is its system of record (ADR-001, ADR-002). That ground truth is not static: it is *mutated* through several distinct paths — authoritative-source ingestion into the Catalog and Standards planes, operational distillation of durable lessons into the Operational plane, promotion of Reasoning-Graph findings into authoritative selection knowledge, and the reverse of that promotion (un-promotion / retraction). Each path changes what the platform treats as true, and every downstream reasoning act consumes the result.

The platform commits one narrow accountability rule over that mutation and no general one. ADR-001 §2.5 requires an Executive-Architect (EA) approval gate on the consolidation of SOFIA's *own reasoning* into encoded knowledge — and that authority reaches only that case. It does not reach ingestion, it does not reach distillation, and it does not stretch to un-promotion. The result is that authoritative ground truth can be mutated through paths that no stated principle governs, and that the reversal of an EA-gated promotion has no upstream authority at all.

That gap is now load-bearing. Several accepted records carry *interim* postures that explicitly defer their authority to a forthcoming decision record governing KG entry: the data-architecture ruling's KG-entry-checkpoint clause, the graph-schema ruling's distillation-write checkpoint posture (recorded as "explicitly un-decided") and its un-promotion authority, and the knowledge-service design's cross-origin scope-conflict escalation, which cites this record as its escalation path. The forthcoming feedback-loop governance design is blocked on this record — its promotion-gate criteria instantiate the principle stated here. Authority that multiple accepted records depend on does not yet exist.

This Architecture Decision Record (ADR) ends that indecision. It fixes the human-accountability principle governing all mutation of enterprise ground truth, and homes the authority the downstream records were routed to await.

---

## 2. Decision

**Enterprise ground truth is mutated only under a human-accountable control calibrated to the source class of the mutation.**

The invariant is human accountability; the *form* of the control that discharges it is calibrated per source class and its mechanism is realized in the downstream records this ADR names. This record fixes the invariant, the accountability, and the control-type per class. It fixes no policy, threshold, cadence, or mechanism.

### 2.1 The accountability invariant and its scope

Every mutation of enterprise ground truth in the KG is subject to a human-accountable control appropriate to the mutation's source class. The invariant has two testable parts: such a control **exists** for the mutation, and a **named human is answerable** for it. Accountability is discharged **per-write** for classes that warrant a gate or a review, and **per-policy** for a class whose volume cannot bear a per-write gate (a human is answerable for the governing policy rather than for each individual write). No class is exempt from the invariant; only the control's form varies (§2.2).

"Mutation" spans the full lifecycle of a ground-truth fact — **entry** (ingestion, distillation, promotion), **lifecycle transition** (revalidation, resolution, supersession), and **withdrawal** (un-promotion / retraction). The invariant is scoped to KG **authoritative ground truth**. Reasoning-Graph capture is not ground truth — it is captured judgment, governed by the reasoning-capture invariant and its write-authority assignment (ADR-001 §2.2; ADR-002 §2.6) — and is outside this record's scope.

The sole-owner graph gateway is the **executor** of every mutation and is never the **authoring authority** for it (ADR-002 §2.6): the accountable human or component authors the mutation; the gateway executes it. This ADR names *who is accountable* for a mutation; it does not relocate authorship onto the gateway.

### 2.2 Per-source-class calibration

The control-type for each source class is fixed here; the control's form, mechanics, and thresholds are realized downstream.

| Source class | Control-type | Accountability | Realization routes to |
|---|---|---|---|
| **Promotion** — Reasoning-Graph findings into authoritative selection knowledge (Catalog / Standards) | The existing EA promotion gate | Per-write (EA) | Built — the graph-schema ruling's `PromotionDecision` gate and its promoted-origin invariant |
| **Authoritative-source ingestion** — Catalog / Standards | Pre-entry human **fidelity** verification of the captured representation, gating official (consumable) entry | Per-write | The forthcoming ingestion decision record; the knowledge-service ingestion port |
| **Operational distillation** — a derived `ObservedPattern` into the Operational plane | Substantive, evidence-visible human review of the **distinct distilled judgment**, bounded by distinctness | Per-distinct-lesson | DDR-003 (Feedback Loop Governance); the detection-promotion service design |
| **Environment** — CMDB-observed deployed reality | Per-policy capture-time-frozen aging of confidence (derived at capture, never recomputed at read), governed by the inherited-confidence derivation ruling's two-tier calibration governance; **no** per-write gate | Per-policy | Form built (DDR-004); constants contested/unvalidated (n=0) — the inherited-confidence derivation ruling's aging basis |

The calibration tracks the failure mode each class actually presents: unaccountable consolidation (promotion), unfaithful capture (ingestion), unsound judgment from noisy signal (distillation), and over-reliance on stale reality (Environment). The burden tracks volume, which is what keeps each control clear of the bottleneck that a uniform per-write gate on all KG writes would create.

- **Promotion.** Promotion into authoritative selection knowledge is governed by the existing per-write EA gate. ADR-001 §2.5 authorizes only the narrow sub-case of consolidating SOFIA's own reasoning into encoded knowledge; this ADR is the general upstream authority for promotion as ground-truth mutation, and §2.5 is cited, not superseded, for its sub-case.
- **Authoritative-source ingestion.** The risk is fidelity, not judgment: the source is authoritative, and what a human is accountable for is confirming that the captured representation faithfully reflects it. Because authoritative selection knowledge changes deliberately and at low volume, a per-write fidelity gate is affordable and does not recreate the bottleneck a gate on high-volume writes would.
- **Operational distillation.** A distilled lesson is an inference generated from operational signal, and its own confidence is self-assigned by the distillation step; a reliability weight therefore cannot govern its soundness. It is governed instead by a substantive human review of the *judgment*. The review is **evidence-visible** — the reviewer can inspect the underlying signal the lesson distills — because a review of a judgment that cannot be traced is not substantive. The review is bounded by **distinctness**: the active `ObservedPattern` set is bounded by the number of distinct durable lessons, so the review load is low-cardinality, and the high-volume raw signal remains in the external observability system of record and never enters the KG.
- **Environment.** CMDB-observed reality is continuous and high-volume; a per-write human gate would make the plane unwritable at observation cadence. Its control is a per-policy capture-time-frozen aging of confidence, derived at Evidence capture and never recomputed at read: the plane ages by construction (its aging confidence basis is fixed in the inherited-confidence derivation ruling), and it is never consumed as authoritative *selection* knowledge. A human is answerable for the weighting policy (its calibration is a ratified act under that ruling's governance), not for each observation.

### 2.3 Un-promotion authority

Un-promotion — retraction of a fact that was promoted into authoritative selection knowledge — is the **withdrawal-leg of the promotion class**, governed by the same per-write, EA-gated, human-accountable control as promotion itself. This ADR is the **upstream authority** for un-promotion: ADR-001 §2.5 authorizes promotion only and does not stretch to its reversal. The built retraction shape — the EA-gated reversing `CandidatePromotion` with its `RETRACTS` edge (the graph-schema ruling's §5 and its retraction-gated invariant) — is the instance of this authority, but it traces to *an* approving decision, not the *governing* one, so it does not yet supply promotion's governing-verdict guarantee; the governing-verdict detection analogue for executed retractions is a named follow-up (§5.3). Un-promotion is **never a bare delete**: the withdrawn node is read-excluded from ground-truth synthesis and retained, fully traceable, for audit (§2.4).

### 2.4 Withdrawal and expiry posture

Withdrawal of a ground-truth fact — retraction of a promoted fact, or resolution / expiry of a distilled lesson — is **read-exclusion and retention-demotion, never hard-deletion**. The withdrawn node is retained and remains traceable; the schema's `archived` status and never-delete posture, and the retraction shape's retained-and-traceable node, are the instances of this rule.

**Provenance survives mutation.** The traceable rationale of a decision that consumed a ground-truth fact must survive that fact's later mutation. A design that relied on a lesson which later resolves, or on a promoted fact which is later retracted, must remain answerable by traversal to the fact as it stood when it was consumed. This is the reasoning-capture auditability commitment (ADR-001) applied to the mutation domain: withdrawal removes a fact from *use*, not from the *record* of what informed prior decisions.

**Revalidation obligation (distillation).** A distilled lesson may not persist as authoritative track-record indefinitely without re-grounding. The Operational plane does not age — its confidence is native lesson-reliability, not freshness-decayed — so a lesson whose underlying reality has changed does not self-correct as a stale Environment fact would. An accountability mechanism must therefore surface stale lessons for their governed transition (a resolution or supersession, itself a distillation judgment under §2.2). This ADR commits that the obligation exists; its revalidation cadence and trigger for stale distilled lessons are routed to DDR-003 (Feedback Loop Governance), as is the mechanism that realizes the surfacing (§2.6).

### 2.5 Cross-class precedence

When a mutation from one source class would override or conflict with a human-accountable control set by another class, it **withholds and escalates to human resolution**; it does not silently win. Concretely, observational or ingested reality never silently takes precedence over an EA-set governance scope on promoted knowledge. The cross-class withhold is a **gateway-mechanical conflict-detection** at the sole-owner graph gateway (ADR-002 §2.6), firing only on a structural collision with an EA-set governance scope — not a per-write human gate on the routine, ungated Environment observation stream (§2.2). Under such a conflict the fail-safe direction is to **withhold, not admit** — the colliding write is blocked and surfaced as a governance-significant event, and a human is accountable at the **resolution** step for which reality governs. The knowledge-service design's cross-origin scope-conflict block is the interim instance this principle authorizes; the richer resolution disposition is governance policy (§2.6).

### 2.6 Governance boundary — what this ADR does not rule

This ADR fixes the invariant, the accountability, and the control-type per class. It does **not** rule the governance policy that instantiates them. The **remedy boundary** — when a wrong promoted fact is superseded (replaceable) versus retracted (should never have been promoted, no correct replacement) — together with promotion and review criteria, thresholds, cadence, retention windows, reviewer-role assignments, and multi-condition composition semantics, is owned by DDR-003 (Feedback Loop Governance), which cites this ADR as authority. The accountability principle this ADR commits holds identically whichever remedy applies, which is why the choice between them is policy, not principle, and is not ruled here.

---

## 3. Rationale

Once this decision is in place, the platform can answer "who is accountable for this change to enterprise ground truth?" for every path by which that ground truth is mutated — not only for the one path ADR-001 §2.5 named. The accountability record becomes a structural property of every mutation, in both directions, answerable by traversal to an accountable human decision rather than reconstructed after the fact. That is the reasoning-capture auditability thesis (ADR-001) extended from *how a conclusion was reached* to *how enterprise ground truth was changed*, which is the surface an audit actually reaches for when it asks why a system was built the way it was.

The decision's shape — an invariant plus a per-class-calibrated control — is what makes it both enforceable and practical. Making *accountability* the invariant and the *control's form* the calibrated variable is what lets a continuous, high-volume plane satisfy the principle without a per-write gate, while the highest-stakes selection knowledge carries a per-write human checkpoint. A single uniform gate on all KG writes was the alternative that reads as safest and is in fact unworkable: it makes the observational planes unwritable at their native cadence. Calibrating the control to each class's failure mode and volume is what keeps the principle from collapsing into either a bottleneck or a rubber stamp, and it homes — in one place — the un-promotion authority, the entry checkpoints, and the cross-class precedence rule that several accepted records were left routing to.

---

## 4. Alternatives Considered

### 4.1 Alternative A — Gate all KG writes uniformly

*Description:* Route every write to the KG — ingestion, distillation, promotion — through a single human (EA) approval gate before it becomes authoritative.

*Rejection rationale:* A uniform gate makes the high-volume observational planes unwritable without per-pattern human action. CMDB-observed reality and operational signal arrive continuously; gating each write forces the Operational and Environment planes through a human bottleneck neither the data architecture nor the schema intends, and the plane ceases to track reality at its native cadence. This is the specific failure a uniform gate was declined to avoid; the calibrated-per-class control achieves accountability without it.

### 4.2 Alternative B — No general checkpoint; trust each source and leave the seam implicit

*Description:* Continue with only the narrow ADR-001 §2.5 promotion gate, treat other entry paths as trusted (the source is authoritative; the distillation is derived), and leave the accountability question unstated.

*Rejection rationale:* This is the pre-existing default, and it fails on three counts. Unfaithful capture of an authoritative source silently corrupts the highest-stakes selection knowledge with no accountable verification. Unsound distilled judgments from noisy signal pollute authoritative track-record that reasoning then consumes as citable evidence. And un-promotion is left with no upstream authority at all, so the reversal of an EA-gated fact reads as an unaccountable mutation. Leaving the seam implicit also ships write paths that read as self-modification and invite exactly the flags an explicit principle forecloses.

### 4.3 Alternative C — Uniform reliability-weighting for every class (treat all mutation like Environment)

*Description:* Admit every mutation without a human gate and rely on a per-fact confidence weight to discount unreliable content at retrieval, uniformly across classes.

*Rejection rationale:* Weighting answers *staleness and over-reliance*, not *fidelity or soundness*. For authoritative selection knowledge, a discount does not substitute for a human confirming the capture is faithful — a wrong-but-confident fact still governs downstream selection. For distillation the approach is circular: the confidence that would gate a lesson's pollution is self-assigned by the same step that produced the lesson, so a noisy-signal misjudgment carries a plausible weight and is not caught. Weighting is the correct control for the one class whose risk *is* staleness (Environment); applying it universally mismatches the control to the risk for the others.

---

## 5. Consequences

### 5.1 Positive Consequences

- **Accountability over ground-truth mutation is a stated platform property**, answerable for every entry and withdrawal path, not only the ADR-001 §2.5 sub-case.
- **No gate-all bottleneck.** The observational planes remain writable at their native cadence because their control is per-policy weighting, not a per-write gate.
- **Capture fidelity is institutionalized** where it has repeatedly failed: authoritative-source ingestion carries a verification checkpoint on the captured representation.
- **Un-promotion has an upstream authority**, closing the gap that left the reversal of an EA-gated promotion unhomed.
- **Provenance survives mutation.** A decision's traceable "why" is preserved across the later resolution or retraction of the fact that drove it.

### 5.2 Constraints Imposed

- **Authoritative-source ingestion is no longer a direct write.** The ingestion path must introduce a pre-official-entry human fidelity verification (a provisional-versus-official distinction), a new commitment for the ingestion decision record and the knowledge-service ingestion port.
- **Operational distillation is no longer an unchecked derived write.** A distilled lesson must pass a substantive, evidence-visible human review before it is consumable track-record, to be realized through a forthcoming candidate-`ObservedPattern` shape — introduced downstream, excluded from ground-truth traversal until approved — a downstream governance design and an additive schema shape.
- **Distilled lessons carry a revalidation obligation.** A mechanism must surface stale lessons for governed transition, since the Operational plane does not self-correct by aging.
- **Cross-class conflicts withhold by default.** A mutation that would override another class's human-accountable control is blocked and escalated, never silently admitted.

### 5.3 Risks

- **Empirical floor.** No promotion, ingestion, or capture traffic has run. The *form* of each control is fixed here on design grounds; calibration constants (for example the Environment weighting parameters) are held contested and config-surfaced by the inherited-confidence derivation ruling. The risk is treating a control's provisional constants as settled; the mitigation is that this ADR commits control-*types*, not calibrations, and the constants' governance lives in that ruling.
- **Decision-provenance retention gap.** The frozen-provenance survival guarantee is currently scoped to *promoted* facts; a design decision that consumed a fact without promoting it relies on Reasoning-Graph evidence under bounded retention, which could age out the graph-native trace. *Mitigation / tracking:* the survival requirement is committed in §2.4; extending the mechanism to decision-consumed evidence, and the retention classes that must honor it, is a named follow-up to the graph-schema ruling and the feedback-loop governance design.
- **Executed-retraction re-decision detection.** The retraction invariant traces to an approving decision, not the governing one, so a re-decided executed retraction has no standing detection analogue yet. *Mitigation / tracking:* the accountability principle covers un-promotion and its re-decision; the detection mechanics are a named schema / governance follow-up, and this ADR is consistent with, not blocked on, that gap.

---

## 6. Compliance

Conformance with this ADR is verified at three-hat (LAA / SA / EA — Lead Application Architect / Solution Architect / Enterprise Architect) architecture review, the gate every downstream design passes through. The following are checked for any design that mutates enterprise ground truth:

1. **Accountability-and-type check.** Any mutation of KG ground truth the design introduces names its source class, states the control-type per §2.2, and names the human accountable for it (per-write or per-policy). A mutation with no accountable control is flagged.
2. **Non-exemption check.** No class of ground-truth mutation — entry, transition, or withdrawal — is admitted without its calibrated control; withdrawal is read-exclusion and retention-demotion, never hard-deletion (§2.4).
3. **Un-promotion authority check.** A design that un-promotes authoritative ground truth routes to the EA-gated retraction shape and cites this ADR as its authority (§2.3).
4. **Cross-class precedence check.** A design in which one class's mutation could override another class's human-accountable control withholds and escalates; it never silently admits or silently overrides (§2.5).
5. **Boundary check.** A design does not smuggle a remedy-boundary or governance-policy ruling into this principle layer; the remedy boundary and policy are the feedback-loop governance design's (§2.6).

**Enforcement.** These checks are enforced at three-hat review at design time — platform-development governance over SOFIA's own design work, not a graph-captured gate on produced solutions. Several control instances this ADR names are already mechanized (the EA promotion gate and its promoted-origin invariant; the EA-gated retraction invariant; the Environment weighting derivation). The new commitments — the ingestion fidelity verification, the distillation review, and the revalidation obligation — are aspirational pending their downstream design and mechanization; until then, conformance to them is reviewed at design time.

---

## 7. Cross-References

- **ADR-001 (Reasoning Architecture)** — §2.5 authorizes the narrow promotion sub-case (SOFIA's own reasoning into encoded knowledge) this ADR generalizes and homes; §2.2 / §5.2 own the reasoning-capture invariant and read discipline this ADR's scope excludes.
- **ADR-002 (Graph as System of Record)** — §2.5 (sole-owner gateway) and §2.6 (author / executor / authorizer separation: the gateway executes, never authors) constrain how every control in this ADR is executed; §2.7 (no-PHI) is the co-located classification control at ingestion.
- **DDR-001 (Data Architecture)** — Decision.5 scopes the KG-entry checkpoint to ADR-001 §2.5's object and routes the broader entry principle to this ADR.
- **DDR-002 (Graph Schema)** — the schema instances of this ADR's controls: §2.3 (Operational distillation, distinctness bound, `archived`, checkpoint posture routed here), §2.4 / §5 (`PromotionDecision`, the retraction shape, remedy boundary routed to the governance design), §6 (version pinning / never-delete), and the constraint set (promoted-origin, retraction-gated, conditional-scope carry-forward, never-delete).
- **DDR-004 (Inherited-Confidence Derivation)** — the Environment aging basis and its two-tier calibration governance that realize the per-policy weighting control (§2.2).
- **SDD-001 (knowledge-service)** — the built instances and interim: the promotion boundary port and retraction operation (§3.5), the current direct ingestion path this ADR amends (§3.6), and the cross-origin scope-conflict block this ADR authorizes (§3.5).
- **DDR-003 (Feedback Loop Governance)** — downstream consumer of this ADR; owns the remedy boundary and all governance policy (§2.6). This ADR is its upstream authority. (Pointer resolved at DDR-003's landing, per its definition of done.)
- **The forthcoming file-driven ingestion decision record** — owns the ingestion mechanics realizing the authoritative-source ingestion control (§2.2).
- **Deliberation substrate** — the RBT-59 pre-authoring deliberation record (dispositions ratified per item, 2026-07-17) and the triage-001 charter (Appendix A).

---

## 8. Change Log

| Version | Date | Ticket | Change |
|---|---|---|---|
| 1.1.0 | 2026-07-19 | RBT-14 | Pointer resolution — the body and cross-reference subject-name routings to "the forthcoming feedback-loop governance design" resolve to **DDR-003 (Feedback Loop Governance), ACCEPTED v1.0.0**, landed in this batch. Marker-level; no decision change. |
| 1.0.0 | 2026-07-17 | RBT-59 | **PROPOSED → ACCEPTED.** Acceptance rests on the four-pass three-hat design-review-loop (runs 025–028): every finding resolved or operator-ratified per item, composition coherence-verified. The mechanical converged loop verdict is deferred to a confirming re-review once the loop's cross-pass carry-forward (RBT-67) lands; a genuinely new finding there is amended then. Status promotion only — no decision or body change from v0.1.0. |
| 0.1.0 | 2026-07-17 | RBT-59 | Initial draft. Authored from the RBT-59 pre-authoring deliberation (six items ratified per item, 2026-07-17): doctype and number (ADR-008); the accountability invariant and per-class-calibrated control frame; the four-class calibration with the entry/transition/withdrawal lifecycle scope, the expire-not-delete and provenance-survival commitments, and the revalidation obligation; un-promotion authority; the ADR ↔ feedback-loop-governance boundary; and the cross-class precedence principle. PROPOSED pending three-hat design-review-loop. |
