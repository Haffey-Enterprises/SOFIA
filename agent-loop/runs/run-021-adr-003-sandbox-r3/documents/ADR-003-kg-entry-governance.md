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

**Mutation of enterprise ground truth in the knowledge graph is subject to a human-accountable checkpoint calibrated to the source class of the write** — its weight, and whether a per-write gate or a lighter retrieval-time posture applies, are set per §2.1, with the Environment-plane posture deferred per §2.2. The reverse operation, un-promotion, is governed by the same principle.

### 2.1 Per-source-class calibration

- **Authoritative-source ingestion** → a **verification-weight** checkpoint on the captured representation (confirm the capture faithfully mirrors the external source of record).
- **Operational distillation** → a **substantive review** of the distilled judgment before entry, because noisy-signal pollution of the track-record graph is the driving risk (its bottleneck reconciliation is §2.5).
- **Promotion** → the **existing EA gate** committed at ADR-001 §2.5 is the already-built instance of this principle; no new mechanism is introduced for the promotion path.

### 2.2 Environment plane

Environment-plane facts are CMDB-observed deployed reality and enter continuously at high volume. The checkpoint posture for the Environment plane — per-write review versus confidence-weighting at retrieval — **is deferred to a named follow-up** (see §7), pending deliberation of the volume/bottleneck constraint; this ADR does not rule it here.

### 2.3 Un-promotion authority

Un-promotion of a promoted KG fact is a human-accountable act, and **this ADR is its upstream authority** — supplying the authority ADR-001 §2.5 (promotion only) does not provide. The mechanism is the retraction shape (DDR-002 §5, §7 #21): an EA-gated reversing `CandidatePromotion` whose approving `PromotionDecision` carries `origin_mechanism: ingested`. The **remedy boundary** — when a wrong fact is superseded versus retracted — is DDR-003 governance and is **deferred there**, not ruled here; this ADR governs only the accountability of the un-promotion act.

### 2.4 The checkpoint executor

The **graph gateway is the authoring authority** for each checkpoint approval: the approval is recorded as the gateway's own act at the write boundary.

### 2.5 Distillation entry

The distillation checkpoint is **designed by this ADR** (DDR-002 §2.3 leaves it un-decided); it is not a pre-existing gate. The §2.1 substantive review governs the **distinct durable lesson** at distillation — not the per-event telemetry stream: distillation is update-in-place, bounded by distinctness (DDR-002 §2.3), so the review set is the small number of distinct `ObservedPattern`s, not high-volume raw writes. That is how the checkpoint satisfies the R30 bottleneck constraint (Operational stays writable) without abandoning the checkpoint. A distillation write produces an `ObservedPattern` in the Operational plane carrying a `flat_base` confidence, and the substantive-review checkpoint governs its entry.

## 3. Rationale

No fact reaches authoritative ground truth without a human accountable for it, at a cost proportionate to the harm a bad write would do. A verification-weight touch on faithful external capture is cheap; a substantive review on distilled judgment is where pollution is stopped; the EA gate on promotion is already paid for. Auditability improves because every ground-truth mutation carries a named accountable party, and un-promotion stops being an ungoverned back door.

## 4. Alternatives Considered

### 4.1 Alternative A: No governance — trust the pipelines

Let every entry path write directly, trusting upstream extraction and distillation. This is obviously wrong and nobody would defend it — ungoverned writes to an enterprise system of record are indefensible.

### 4.2 Alternative B: A single uniform checkpoint on all writes

One human review, identical weight, on every KG write regardless of source. Its proponents would argue it is the simplest possible rule and leaves no path ungoverned. Rejected because it treats faithful external capture and noisy distilled judgment as equal risks and does not scale to CMDB-volume ingestion — the bottleneck R30 declined.

## 5. Consequences

- **5.1 Positive** — every ground-truth mutation carries an accountable party; distillation pollution is stopped at entry; un-promotion becomes a governed act; DDR-003 gains the promotion-gate authority it is blocked on.
- **5.2 Constraints imposed** — each ground-truth-mutating path is subject to the per-source-class checkpoint calibration of §2.1; the calibration — not a uniform per-write gate — is the imposed constraint, and the Environment-plane posture is deferred (§2.2).
- **5.3 Risks** — checkpoint latency on higher-volume paths; signal to revisit is checkpoint queue depth.

## 6. Compliance

Compliance is currently aspirational, tracked at the KG-entry-governance implementation ticket. Until enforcement lands, conformance is checked at design-review time against this ADR.

## 7. Cross-References

- ADR-001 §2.5 (EA-gated promotion mechanism); ADR-002 §2.6 (write authority); DDR-002 §2.3 / §2.4 / §5 / §7 #21 (distillation gap, un-promotion routing, retraction shape).
- **DDR-003** (forthcoming, blocked on this ADR) — will cite this ADR as authority for its promotion-gate criteria and owns the remedy-boundary governance deferred at §2.3.
- **Named follow-up (§2.2):** Environment-plane checkpoint posture — deferred pending volume/bottleneck deliberation; tracked at the KG-entry-governance follow-up ticket.
- Deliberation substrate: triage-001 record Appendix A (charter), R30.

## 8. Change Log

| Version | Date | Ticket | Change |
|---|---|---|---|
| 0.1.0 | 2026-07-17 | KG-entry-governance | Initial draft |
