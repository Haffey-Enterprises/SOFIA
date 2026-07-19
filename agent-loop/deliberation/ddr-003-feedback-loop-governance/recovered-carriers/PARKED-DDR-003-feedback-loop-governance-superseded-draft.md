# File: docs/ddr/DDR-003-feedback-loop-governance.md
# Author: Thaddeus Haffey — Executive Architect, Haffey Enterprises LLC
# Created: 2026-06-22
# Description: DDR-003 — Feedback Loop Governance. Fixes the policy layer governing DDR-001's EA-gated promotion architecture — the engine by which recurring reasoning consolidates into encoded knowledge (ADR-001 §2.5) — ruling EA-gate authority/diagnosis, signal detection, retention/audit/provenance-survival, and conditional/retraction governance, while deferring calibration values to operational onboarding and routing named gaps to their owners.

# DDR-003 — Feedback Loop Governance

| Field | Value |
|---|---|
| **Document ID** | DDR-003 |
| **Version** | 0.1.0 |
| **Status** | PROPOSED |
| **Date** | 2026-06-22 |
| **Authors** | Thaddeus Haffey (Executive Architect, Haffey Enterprises LLC) |
| **Supersedes** | None — new design ruling. |
| **References** | ADR-001 v1.0.0 (§2.5 EA-gated consolidation; Position 5 → 4 trajectory); ADR-002 v1.0.0 (graph system-of-record); DDR-001 v1.1.0 (feedback-loop *architecture* / data-path; proposal-visibility check #4; store assignments); DDR-002 v1.1.0 (graph *schema contract* — the EA-gate node/edge shapes, `archived` status, `ProvenanceSummary`, `RETRACTS`, §7 invariants incl. #15/#20/#21); Reboot Decision Ledger R22 / R24 / R25 / R26 / R27 / R29 / R30 / R31. |

---

## Decision

DDR-003 fixes the **policy layer** governing DDR-001's EA-gated promotion *architecture* — the feedback loop by which recurring reasoning and operational track-record consolidate into encoded, authoritative knowledge (ADR-001 §2.5; the Position-5 → Position-4 trajectory). It owns **governance policy**; it does **not** own architecture (DDR-001), schema (DDR-002), or service realization (the SDDs). It governs a loop that **has never run** — no deployed services, no telemetry, no promotion cycles — so the whole ruling holds one ratified **completeness cut line**:

- **Rule now** — governance that is reversibility-expensive or already anchored upstream.
- **Structure now, parameterize at operational onboarding** — calibration-dependent values with no empirical floor (R4 / R25 empirical-warrant discipline): the *mechanism* is ruled, the *value* is a named, deferred calibration gap.
- **Name as gap, with a reversal path** — mechanisms with no driving instance, or owned by a downstream consumer.

Decomposed into testable ruling components:

- **Decision.1 — The EA gate (spine).** Every materialized promotion traces to an approving `PromotionDecision`; the one concrete enforceable authority is **Enterprise-Architect promotion-approval** (§3). The broader RBAC surface is a routed gap.
- **Decision.2 — Diagnosis policy.** The EA diagnoses each candidate across **five named dimensions** to separate genuine knowledge from data-defect / transient workaround / spurious artifact; **weights and decision rules are EA judgment + operational calibration, not ruled** (§3.2).
- **Decision.3 — Action-class routing with a no-leak invariant.** Two paths — EA-gated knowledge promotion vs. non-gated source-quality feedback — and a source-quality signal **never crosses into promotion** except by independently re-entering as a promotion-eligible signal (§3.3).
- **Decision.4 — Signals & detection.** A closed-but-additively-extensible signal taxonomy keyed on `PROPOSED_FROM` source + action path; one EA-owned, data-configured, audit-logged **calibration-parameter mechanism** (threshold / lookback / cadence) whose **values are deferred**; and the distillation **derive/promote authority seam** (§4).
- **Decision.5 — Retention, audit, provenance-survival.** A non-uniform retention-class framework with two binding invariants (**never silently delete**; **explainability survives expiry**); a two-record audit model (Neo4j `PromotionDecision` + PostgreSQL operational trail) with an **audit-first invariant**; and the at-promotion `(:Reasoning:ProvenanceSummary)` snapshot (§5).
- **Decision.6 — Conditional & retraction governance.** `approved_conditional` scope-setting is an EA accountability with a carry-forward requirement; multi-condition composition stays a DDR-002 named gap under a safe interim posture; **retraction** is an EA-gated reversing `CandidatePromotion` distinguished from supersession by a ruled remedy boundary (§6).
- **Decision.7 — Boundary.** DDR-003 owns *policy*; promotion *data-path* → DDR-001; *schema shape* → DDR-002 v1.1.0; *workflow / job lifecycle / mechanics* → the SDDs (§Cross-References).

---

## Rationale

This ruling is **deliberation-grounded**: it is the output of the RBT-14 pre-authoring design session (the ratified substrate), which deliberated the governance of a feedback loop that has no empirical instance yet. The design space, the alternatives weighed at each seam, and the disposition of every ruling were worked through in that session; this DDR carries the settled policy.

The governing tension is that the loop **has never run** — so authoring it richly would over-specify against R25's empirical-warrant discipline, while under-specifying it would leave the EA gate (the accountability control that converts judgment-derived proposals into authoritative KG facts, ADR-001 §2.5) ungoverned. The cut line in §Decision resolves this: anything reversibility-expensive or upstream-anchored is **ruled now** (the gate's existence, the accountability contract, the action-path no-leak invariant, the retention/audit invariants, the diagnosis *dimensions*); anything that is a pure calibration value with no empirical floor is **structured now and parameterized at operational onboarding** (thresholds, windows, cadence, retention dwell); anything with no driving instance or a downstream owner is **named as a gap with a reversal path** (multi-condition composition → DDR-002; retrieval affordances → RBT-15; predicate vocabulary → RBT-22). This is the same R25 lever DDR-002 applies to schema, applied here to policy.

Two upstream commitments make the gate sound without determinism loss. First, the EA gate restores **accountability and authoritativeness, not determinism** (ADR-001 §2.5; DDR-002 §4 accountability boundary): a promoted fact is distinguishable (`origin_mechanism: promoted`) and traces to an accountable decision, but the gap/override *derivation* remains a structural function of graph facts independent of how any fact entered. Second, **SOFIA never self-modifies the KG** (DDR-001 check #4): the loop *proposes* (`CandidatePromotion`, proposal-class, excluded from ground-truth reads until approved), and a human *materializes* (the `PromotionDecision`). DDR-003 governs the policy around that architecture; it does not re-open it.

---

## The EA Gate (the spine)

### Authority & accountability

Every materialized promotion must trace to an approving `PromotionDecision` — the accountability contract (DDR-002 §2.4; check #15 keys promotion authority off the *governing* approving edge). DDR-003 pins **one** concrete enforceable authority, the single authorization the gate cannot function without: **Enterprise-Architect promotion-approval**, grounded in ADR-001's "EA-gated consolidation." DDR-002 check #15's role-authorization tightens onto this authority.

The broader non-EA role/permission surface — who is SA/LAA, view/defer/queue-access rights — is a **routed RBAC gap**, not ruled here.

### Diagnosis policy

The EA diagnoses each candidate to separate **genuine knowledge** from **data-defect / transient workaround / spurious artifact**. Dispositions map to DDR-002's `DECIDED_ON` outcomes (`approved` / `approved_conditional` / `rejected`) plus the three correction flavors (Refine / Request-new / Correct-scope, DDR-002 §5 generalized-correction). A decision weighs **five diagnosis dimensions**:

1. **Recurrence strength** — how strongly the signal recurs.
2. **Evidence quality / source authority** — the confidence and authoritativeness of the supporting evidence.
3. **Genuine-pattern-vs-data-defect** — whether the recurrence reflects real knowledge or an upstream defect.
4. **Target deprecation / staleness state** — whether the knowledge target is current.
5. **Conditional-vs-unconditional applicability** — whether the knowledge is universally safe or scope-bounded (drives `approved_conditional`, §6.1).

**Weights and decision rules are EA judgment + operational calibration — not ruled.** DDR-003 rules *which* dimensions a decision must weigh, not how to score them.

### Action-class routing — the no-leak invariant

Two action paths, with a binding **no-leak invariant** between them:

- **Path 1 — EA-gated knowledge promotion.** Gap-recurrence + override-recurrence signals → `CandidatePromotion` → EA gate → possible KG materialization.
- **Path 2 — source-quality feedback.** Evidence-quality signals → ingestion-scoring / data-quality signal; **no EA gate, no KG mutation.**

**No-leak invariant:** a source-quality signal **never crosses into promotion** except by independently re-entering as a promotion-eligible signal. Both paths' detection/delivery mechanisms → SDD. A novel action class registers **additively** into one of the two paths.

### Batch eligibility

Batching is permitted (DDR-002's `(PromotionDecision)-[:DECIDED_ON]->` is 1:many). But every candidate in a batch retains its **own diagnosis** (the five dimensions) and its **own per-candidate verdict** (on its `DECIDED_ON {outcome}` edge). **Batching bundles the recording act, never the diagnosis.** Volume-driven guardrails (auto-batching, size caps, queue-flood guards) are a **calibration gap**.

### Authorship & gate completion

The `CandidatePromotion` is **system-authored** by the out-of-band feedback process as a **proposal-class node** — excluded from ground-truth traversal until approved (confirms DDR-001's proposal-visibility / check #4) — and **carries the diagnosis substrate** the EA needs (supporting signal instances, recurrence count, the five-dimension inputs). **Gate completion** = recording a `PromotionDecision` with a per-candidate outcome; **approval precedes materialization** (the loop proposes, a human materializes); a **rejected verdict is terminal and durably explained** so the same gap does not re-surface and re-burn EA attention; and the promotion must be **auditable** (§5.2). Scheduled-job lifecycle, review queue / portal, and the dual-store write sequence → SDD.

---

## Signals & Detection

### Signal taxonomy

Organized by `PROPOSED_FROM` source + action path; **closed-but-additively-extensible**; detection mechanics → SDD:

- **RG reasoning-recurrence → promotion path:** *gap-recurrence* (recurring `GapConclusion`) and *override-recurrence* (recurring human override: `ReasoningProgress{overridden_by_human}` → `REJECTED` → `RejectedAlternative{human_accepted}` → `WOULD_HAVE_USED` — the primary feedback input per DDR-001).
- **Operational track-record → promotion path:** `ObservedPattern` strength/weakness trends. *(This source is the reboot's advance over the prior-SOFIA RG-only model — retained deliberately.)*
- **RG evidence-quality → source-quality path (not promotion):** low-confidence `Evidence` under overridden conclusions.
- **KG participates as ground-truth-checked-against** (de-dup: do not re-propose already-promoted knowledge; the target-node references) — mechanics → SDD.

### Calibration-parameter mechanism

One mechanism, named parameter set, **values deferred**. The loop's tunable parameters are **data-configured (not code), EA-owned** (only the §EA-gate EA may change them), **audit-logged on every change** (→ §5.2), and **read fresh per run** (a change takes effect next run, no redeploy). Parameter set:

- **Detection threshold** — minimum qualifying instances to surface a candidate.
- **Lookback window** — the rolling period instances are counted over.
- **Run cadence** — how often detection runs.

**Values are operational-onboarding calibration gaps — none are asserted.** Config store: **PostgreSQL** (DDR-001's existing workflow/staging assignment).

### Distillation governance — the derive/promote authority seam (R30)

Distillation *deriving* an `ObservedPattern` into Operational is a permitted **non-EA-gated `derived` write** (distilled track-record, `derivation_class: distilled`, never authoritative selection knowledge); *promoting* it into authoritative selection knowledge (Catalog / Standards) stays **EA-gated** via the loop. Operational is the **staging tier**; the EA gate sits between it and the **authoritative tier** — which is **why a non-EA-gated KG write does not breach ADR-001's SOFIA-never-self-modifies invariant** (the derived write lands in a non-authoritative staging tier, not authoritative ground truth). Distillation cadence + generalization sensitivity reuse the calibration-parameter mechanism above; the **generalization algorithm and job ownership → SDD**.

---

## Retention, Audit, Provenance-Survival

### Retention-class framework

Non-uniform, with two cross-cutting invariants binding all classes:

- **Durable / never-expire:** terminal-`promoted` `CandidatePromotion`, cost as-of records, the promotion audit trail, and all terminal `CandidatePromotion`s (rejected included) as governance audit trail.
- **Bounded / non-uniform (RG reasoning state), by structural role:** `Evidence` shortest-lived (point-in-time snapshot; its **expiry is the trigger** for the §5.3 preservation step — build-before-expiry); `RejectedAlternative` longest-lived (primary feedback input, authored — must outlive the detection windows that might promote it); `ReasoningProgress` / `ReasoningSession` between. **Relative ordering is ruled; absolute windows are calibration parameters, deferred.**
- **Archivable-on-terminal:** Operational `ObservedPattern`s in `resolved` / `superseded` — trigger keyed to terminal state + a **dwell** parameter (deferred); archival is **retention-tier demotion, never deletion** (an `archived` pattern stays traceable; reversible if a dormant pattern recurs). Realized in schema by DDR-002 v1.1.0 §2.3 (`ObservedPattern.status` gains `archived`); the **when / dwell-trigger / cadence is DDR-003's policy, deferred to onboarding**.
- **Two binding invariants:** **never silently delete**; **explainability survives expiry** (when bounded retention removes an `Evidence`, any promotion sourced from it has its traceability preserved **before** the `Evidence` is removed — §5.3).
- **Cost-record volume management** (partitioning / indexing / cold-tiering — *not* deletion) is shared-ownership with **RBT-25**; named, not ruled.

### Audit policy — the two-record model

- **Accountable decision:** the append-only `PromotionDecision` in the Neo4j Governance plane (authoritative who-approved-what; DDR-002-settled).
- **Operational audit trail:** the workflow event stream (candidate surfaced → decided → materialized / failed) + calibration-config changes, append-only in **PostgreSQL** (DDR-001 audit assignment).
- **Audit-first invariant:** no KG promotion materializes without its audit record committed first; a successful KG mutation with no audit record is the **unaudited-mutation failure mode — prohibited**.
- **Recoverability requirement:** for any promoted fact, the audit answers who approved it, when, on what diagnosis basis, and the full provenance chain to source.
- Write sequence + event-type taxonomy → SDD. *(R24 note: the PostgreSQL trail is durable governance audit — not in the graph, and not the transient per-action disposition stream R24 excludes; no tension with R24.)*

### Provenance-survival snapshot

A dedicated frozen **`(:Reasoning:ProvenanceSummary)`** node (DDR-002 v1.1.0 §4 — `origin_mechanism: derived`; traversable, **not** a subgraph snapshot, **not** a blob — R25/R27-blessed), carrying the frozen lineage a post-expiry audit needs: the originating `Evidence`-set `fact_summary` content (`frozen_fact_summaries`), the corresponding source-version pins (`frozen_source_version_pins`), and — via `MATERIALIZES_PROVENANCE_OF` and the append-only Governance edges — the live-traversable chain to the governing `PromotionDecision`. **Materialize at promotion** (not at expiry), so build-before-expiry holds **by construction** — the ordering is an invariant of the promotion act (DDR-002 §7 #20), not a sweep that races retention. The **reverse-lookup index / affordance, query patterns, and CI-invariant-or-not → RBT-15**; the **`Evidence`-expiry retention windows → DDR-003 policy (this framework), deferred to onboarding**.

---

## Conditional Governance & Retraction

### Conditional → promoted transition

`approved_conditional` is a first-class EA diagnosis outcome (the fifth diagnosis dimension) — chosen when a pattern is genuine but **scope-bounded**. Authoring the `Condition` is part of the approval act. **Scope-setting is an EA accountability:** the predicate defines where the knowledge is safe to reuse — too broad over-admits (the safety failure DDR-002 check #19 prevents), too narrow strands genuine knowledge — so it is **EA-authored and audit-recorded as diagnosis basis** (§5.2). **Carry-forward requirement:** on supersession, a conditional scope is **preserved** unless an explicit EA `PromotionDecision` re-scopes it — silent default-to-`unconditional` is prohibited. The *mechanism* + CI-invariant-or-not → **RBT-15 / RBT-33**; predicate **vocabulary / grammar → RBT-22** (constraint-validator). *(No DDR-002 amendment — conditional schema already locked.)*

### Multi-condition — named gap + safe interim posture

The multi-`HAS_CONDITION` **consumption combinator** (disjunctive vs. otherwise), the **condition-set lifecycle** (activation / retirement / `status`), and any `Condition.status` field **stay the DDR-002 named gap**, resolved on first real instance. DDR-003 rules **only** the safe interim posture: a second conditional promotion of an already-conditional fact **surfaces to the EA as a scope-conflict** requiring explicit diagnosis (widen / replace / add a disjunctive branch?) — **never silently auto-composed**. This preserves DDR-002 check #19's never-consumed-out-of-scope guarantee through the unresolved case. *(No DDR-002 amendment — rides existing machinery.)*

### Retraction governance (R31)

**Remedy boundary:** **supersession** (the default) when promoted knowledge is *wrong-but-replaceable* (DDR-002 §6 versioning already supports it); **retraction** (the exception) when it *should never have been promoted* and has no correct replacement (a data-defect promotion, a spurious pattern). Retraction is itself an **EA-gated** decision — a reversing `CandidatePromotion` (`promotion_type: retraction`) + `RETRACTS` edge that the EA approves (DDR-002 v1.1.0 §5 / §7 #21) — with the same accountability + audit as a forward promotion (the un-promotion mirror of check #15). **Record discipline:** a retraction requires **durable rationale** (why this should never have been knowledge), captured on the audit trail + decision rationale, **not** a separate per-retraction DDR. The retracted node is **retained and read-excluded** (gateway-enforced read-discipline keyed on the EA-approved `RETRACTS` edge), never hard-deleted. *(Schema shape locked in DDR-002 v1.1.0; DDR-003 owns the remedy-boundary governance.)*

---

## Pre-Acceptance Conditions

The ruling is sound as authored; promotion from PROPOSED (0.1.0) to ACCEPTED (1.0.0) is gated on:

1. **Three-hat review (DIRECTIVE-007) — pending.** The LAA → SA → EA review of record is a subsequent claude.ai design leg; this PR lands the draft at PROPOSED for that review. Promotion to ACCEPTED follows on a converged review.

**Structure-now-parameterize-later (not blocking acceptance — onboarding calibration gaps, tracked):** detection threshold / lookback window / run cadence (§Signals); retention absolute windows + `ObservedPattern` archival dwell (§Retention); batch volume guardrails (§EA-gate). Each is a ruled *mechanism* whose *value* is asserted at operational onboarding, per R25.

**No new schema prerequisites:** DDR-003's schema dependencies (`archived` status, `ProvenanceSummary` + `MATERIALIZES_PROVENANCE_OF`, reversing `CandidatePromotion` + `RETRACTS`) all landed in **DDR-002 v1.1.0** (RBT-43) before this DDR cites them.

---

## Migration Path

**No migration path** — greenfield governance of a loop that has never run; no prior feedback-loop policy to migrate from.

---

## Cross-References

**Boundary routing map** (named here, owned elsewhere):

- **← ADR-001 v1.0.0** (§2.5 EA-gated consolidation — the spine; the Position-5 → Position-4 trajectory this loop advances). Cited, not re-opened.
- **← ADR-002 v1.0.0** (graph system-of-record; no-PHI; classification at the boundary).
- **← DDR-001 v1.1.0** (one-way, R8/R22): feedback-loop *architecture* / promotion data-path; proposal-visibility invariant + check #4; the three-store persistence assignment (Neo4j Governance plane for `PromotionDecision`; **PostgreSQL** for workflow/staging/audit). Cited, never re-authored.
- **← DDR-002 v1.1.0** (one-way): the *schema contract* DDR-003 governs the policy around — the `Decision`/`PromotionDecision`/`CandidatePromotion`/`Condition` shapes; `ObservedPattern.status archived`; `(:Reasoning:ProvenanceSummary)` + `MATERIALIZES_PROVENANCE_OF`; reversing `CandidatePromotion` + `RETRACTS`; §7 invariants #4/#9/#15/#19/#20/#21.
- **→ RBT-15 (knowledge-service SDD):** the gateway that enforces the read-discipline (proposal-visibility, conditional-consumption, retracted-node exclusion); the `ProvenanceSummary` reverse-lookup index/affordance; the `applicability_state` supersession carry-forward mechanism (with RBT-33); the dual-store write sequence realizing the audit-first invariant.
- **→ RBT-16 / RBT-17 (AOE / ASA SDDs):** detection-job lifecycle, candidate-surfacing, review queue/portal, the per-run parameter reads.
- **→ RBT-22 (governance-state-manager / constraint-validator):** the `Condition` predicate vocabulary/grammar.
- **→ RBT-25 (cost-estimation SDD):** cost-record volume management (shared ownership).
- **→ RBT-27 (reasoning-machinery, parked):** judgment-consolidation health / weighting (promoted-vs-ingested) — a forward dependency DDR-003 *names*, does not author.
- **→ RBT-33:** mechanization of DDR-002 §7 #20 (follow tier) / #21 (safety-critical, 1b gateway-behavioral contract per R28) — the two v1.1.0 invariants this loop relies on.

**Named gaps (R25 lever) — carried, not dropped:**

- **Multi-condition consumption combinator + condition-set lifecycle** → DDR-002 amendment on first instance (§6.2).
- **Provenance-survival reverse-lookup index/affordance + CI-invariant-or-not** → RBT-15 (§5.3).
- **Conditional carry-forward mechanism + CI-invariant-or-not** → RBT-15 / RBT-33 (§6.1).
- **Non-EA RBAC surface** (roles/permissions beyond EA promotion-approval) → routed (§EA-gate).
- **All calibration values** (thresholds, windows, cadence, dwell, batch guardrails) → operational onboarding.

**Backlog:** RBT-14 (this); RBT-43 (the DDR-002 v1.1.0 amendment, landed); RBT-15 / RBT-16 / RBT-17 / RBT-22 / RBT-25 / RBT-27 / RBT-33 (downstream / forward).

**Ledger:** Reboot Decision Ledger R22 / R24 / R25 / R26 / R27 / R29 / R30 / R31.

---

## Layer-of-Abstraction Note

This DDR operates at the **governance / policy layer** — it constrains *how the feedback loop decides, retains, and audits*, sitting atop DDR-001's promotion *architecture* and DDR-002's *schema*, and is consumed by the SDDs at the service layer (the gateway, the detection jobs, the review portal). It is not a data-substrate document (that is DDR-002); it is the policy that the data-substrate machinery executes.

---

## Substrate-Stability Tracking

DDR-003 is consumed by the feedback-loop-touching SDDs (RBT-15 knowledge-service, RBT-16 AOE, RBT-17 ASA, RBT-22 constraint-validator, RBT-25 cost). Its **ruled** surfaces — the EA-gate authority, the action-path no-leak invariant, the audit-first invariant, the retention binding invariants, and the retraction remedy-boundary — carry blast radius into those consumers and require coordinated review to amend. Its **deferred** surfaces (the calibration values and the named gaps above) are the designated additive-amendment surface; asserting a calibration value or resolving a named gap is an additive amendment, not a breaking change. The one-way reference direction to DDR-001 / DDR-002 (R8) is explicit: DDR-003 references them, never the reverse.

---

## Change Log

| Version | Date | Ticket | Change |
|---|---|---|---|
| 0.1.0 | 2026-06-22 | RBT-14 | Initial draft authored from the ratified RBT-14 design substrate, against the landed DDR-002 v1.1.0 schema. PROPOSED pending the DIRECTIVE-007 three-hat review of record. |
