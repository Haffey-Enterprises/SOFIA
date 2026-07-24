# File: docs/adr/ADR-003-kg-entry-governance.md
# Author: Thaddeus Haffey — Executive Architect, Haffey Enterprises LLC
# Created: 2026-07-17
# Description: ADR-003 — KG-Entry Governance. Establishes a human-accountable checkpoint on mutation of enterprise ground truth, calibrated per source class.

# ADR-003: A Human-Accountable Checkpoint Governs Mutation of Enterprise Ground Truth

| Field | Value |
|---|---|
| **Document ID** | ADR-003 |
| **Status** | DRAFT |
| **Version** | 0.1.0 |
| **Date** | 2026-07-17 |
| **Authors** | Thaddeus Haffey (Executive Architect) |
| **Supersedes** | None — new principle. |

---

## 1. Context

The knowledge graph (KG) is SOFIA's enterprise system of record. Facts enter it through three paths — external **ingestion**, operational **distillation** (recurring lessons generalized from the observability SoR), and feedback-loop **promotion** (reasoning consolidated into encoded knowledge). Promotion is already human-gated: ADR-001 §2.5 commits the EA-gated promotion mechanism. The other two entry paths, and the reverse operation — **un-promotion** (retraction of a fact that should never have been promoted) — have no equivalent human-accountable checkpoint today.

The forcing function is that two canonical records route named gaps here. DDR-002 §2.3 leaves the distillation write's checkpoint posture explicitly un-decided, routed to this record; DDR-002 §2.4 routes un-promotion's upstream authority here, because ADR-001 §2.5 authorizes promotion only and does not stretch to un-promotion. DDR-003 (Feedback Loop Governance) is blocked on this ADR for its promotion-gate criteria. This ADR ends the indecision about how mutation of enterprise ground truth is checkpointed.

## 2. Decision

**Mutation of enterprise ground truth in the knowledge graph is subject to a human-accountable checkpoint calibrated to the source class of the write** — its form (a per-write gate, or retrieval-time confidence-weighting) and weight are set per §2.1. The reverse operation, un-promotion, is governed by the same principle.

### 2.1 Per-source-class calibration

- **Authoritative-source ingestion** → a **verification-weight** checkpoint on the captured representation (confirm the capture faithfully mirrors the external source of record).
- **Operational distillation** → a **substantive review** of the distilled judgment before entry, scoped to the distinct durable lesson (§2.5), because noisy-signal pollution of the track-record graph is the driving risk.
- **Promotion** → the **existing EA gate** committed at ADR-001 §2.5 is the already-built instance of this principle; no new mechanism is introduced for the promotion path.

### 2.2 Environment plane

Environment-plane facts are CMDB-observed deployed reality and enter continuously at high volume. The Environment plane uses **confidence-weighting at retrieval**, not a per-write checkpoint: CMDB-observed facts age via freshness (DDR-002 §2.2), and per-write review of that continuous volume would be the bottleneck R30 declined. (Ratified — KG-Entry-Governance Rulings, Ruling 1.)

### 2.3 Un-promotion authority

Un-promotion of a promoted KG fact is a human-accountable act, and **this ADR is its upstream authority** — supplying the authority ADR-001 §2.5 (promotion only) does not provide. The mechanism is the retraction shape (DDR-002 §5, §7 #21): an EA-gated reversing `CandidatePromotion` whose approving `PromotionDecision` carries `origin_mechanism: ingested`. This ADR supplies the un-promotion **authority**; the **remedy boundary** — supersession versus retraction — is DDR-003's governance **policy** per DDR-002 §2.4. The two are distinct roles, not a circular dependency: authority flows from this ADR to DDR-003, and DDR-003 owns only the remedy policy.

### 2.4 The checkpoint executor

The **graph gateway is the authoring authority** for each checkpoint approval: the approval is recorded as the gateway's own act at the write boundary.

### 2.5 Distillation entry

The distillation checkpoint is **designed by this ADR** (DDR-002 §2.3 leaves it un-decided); it is not a pre-existing gate. The §2.1 substantive review governs the **distinct durable lesson**, not the per-event telemetry stream: distillation is update-in-place, bounded by distinctness (DDR-002 §2.3), so the reviewed set is the small number of distinct `ObservedPattern`s and Operational stays writable. (Ratified — KG-Entry-Governance Rulings, Ruling 2.) A distillation write produces an `ObservedPattern` in the Operational plane carrying a `flat_base` confidence, and the substantive-review checkpoint governs its entry.

## 3. Rationale

No fact reaches authoritative ground truth without a human accountable for it, at a cost proportionate to the harm a bad write would do. A verification-weight touch on faithful external capture is cheap; a substantive review on distilled judgment is where pollution is stopped; the EA gate on promotion is already paid for. Auditability improves because every ground-truth mutation carries a named accountable party, and un-promotion stops being an ungoverned back door.

## 4. Alternatives Considered

### 4.1 Alternative A: No governance — trust the pipelines

Let every entry path write directly, trusting upstream extraction and distillation. This is obviously wrong and nobody would defend it — ungoverned writes to an enterprise system of record are indefensible.

### 4.2 Alternative B: A single uniform checkpoint on all writes

One human review, identical weight, on every KG write regardless of source. Its proponents would argue it is the simplest possible rule and leaves no path ungoverned. Rejected because it treats faithful external capture and noisy distilled judgment as equal risks and does not scale to CMDB-volume ingestion — the bottleneck R30 declined.

## 5. Consequences

- **5.1 Positive** — every ground-truth mutation carries an accountable party; distillation pollution is stopped at entry; un-promotion becomes a governed act; DDR-003 gains the promotion-gate authority it is blocked on.
- **5.2 Constraints imposed** — each ground-truth-mutating path is subject to the per-source-class checkpoint calibration of §2.1 (a per-write gate for authored and distilled entry; retrieval-time weighting for the Environment plane); the calibration, not a uniform gate, is the imposed constraint.
- **5.3 Risks** — checkpoint latency on higher-volume gated paths; signal to revisit is checkpoint queue depth.

## 6. Compliance

Compliance is currently aspirational, tracked at RBT-59 (KG-Entry-Governance). Until enforcement lands, conformance is checked at design-review time against this ADR. The distillation substantive-review checkpoint this ADR designs is a **gateway-behavioral contract**, and its conformance is mechanized per the DDR-002 §7 harness pattern — a 1b gateway-behavioral check whose required-flip is reserved to the gateway build, joining that harness increment.

## 7. Cross-References

- ADR-001 §2.5 (EA-gated promotion mechanism); ADR-002 §2.6 (write authority); DDR-002 §2.3 / §2.4 / §5 / §7 / §7 #21 (distillation gap, un-promotion routing, retraction shape, conformance-harness pattern).
- **DDR-003** (forthcoming, blocked on this ADR) — will cite this ADR as authority for its promotion-gate criteria and owns the remedy-boundary policy referenced at §2.3.
- Deliberation substrate: triage-001 record Appendix A (charter), R30, and the **KG-Entry-Governance Rulings** (closing charter Appendix A #4 and #5).

## 8. Change Log

| Version | Date | Ticket | Change |
|---|---|---|---|
| 0.1.0 | 2026-07-17 | KG-entry-governance | Initial draft |
