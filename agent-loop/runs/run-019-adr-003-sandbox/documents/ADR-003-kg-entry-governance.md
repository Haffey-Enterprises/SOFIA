# File: docs/adr/ADR-003-kg-entry-governance.md
# Author: Thaddeus Haffey — Executive Architect, Haffey Enterprises LLC
# Created: 2026-07-17
# Description: ADR-003 — KG-Entry Governance. Establishes a human-accountable checkpoint on mutation of enterprise ground truth, calibrated per source class.

# ADR-003: A Human-Accountable Checkpoint Governs Mutation of Enterprise Ground Truth

| Field | Value |
|---|---|
| **Document ID** | ADR-003 |
| **Status** | PROPOSED |
| **Version** | 0.1.0 |
| **Date** | 2026-07-17 |
| **Authors** | Thaddeus Haffey (Executive Architect) |
| **Supersedes** | None — new principle. |

---

## 1. Context

The knowledge graph (KG) is SOFIA's enterprise system of record. Facts enter it through three paths — external **ingestion**, operational **distillation** (recurring lessons generalized from the observability SoR), and feedback-loop **promotion** (reasoning consolidated into encoded knowledge). Promotion is already human-gated: ADR-001 §2.5 commits the EA-gated promotion mechanism. The other two entry paths, and the reverse operation — **un-promotion** (retraction of a fact that should never have been promoted) — have no equivalent human-accountable checkpoint today.

The forcing function is that two canonical records have routed named gaps here and cannot close without this ADR. DDR-002 §2.3 leaves the distillation write's checkpoint posture "explicitly un-decided," routed to this record; DDR-002 §2.4 states that un-promotion's upstream authority routes here because ADR-001 §2.5 authorizes promotion only. DDR-003 (Feedback Loop Governance) is blocked on this ADR for its promotion-gate criteria. This ADR ends the indecision about whether — and how — mutation of enterprise ground truth is checkpointed.

## 2. Decision

**Every write to the knowledge graph passes a human-accountable checkpoint before it takes effect.** The checkpoint is calibrated to the source class of the write, and the reverse operation (un-promotion) is governed by the same principle.

### 2.1 Per-source-class calibration

The checkpoint's weight is set by source class, not uniform:

- **Authoritative-source ingestion** → a **verification-weight** checkpoint on the captured representation (confirm the capture faithfully mirrors the external source of record).
- **Operational distillation** → a **substantive review** of the distilled judgment before entry, because noisy-signal pollution of the track-record graph is the driving risk.
- **Promotion** → the **existing EA gate** (ADR-001 §2.5) is the already-built instance of this principle; no new mechanism is introduced for the promotion path.

### 2.2 Environment plane

Environment-plane facts are CMDB-observed deployed reality and enter continuously at high volume. The **checkpoint posture for the Environment plane** — per-write review versus confidence-weighting at retrieval — **is deferred to a named follow-up** (see §7), pending deliberation of the volume/bottleneck constraint; this ADR does not rule it here.

### 2.3 Un-promotion authority

Un-promotion of a promoted KG fact is a human-accountable act under this principle. Its upstream authority is **ADR-001 §2.5**, which governs the promotion mechanism and therefore its reversal. Un-promotion is used **whenever a promoted fact is later found to be incorrect** — the retraction shape (DDR-002 §5, §7 #21) is the mechanism, and this ADR rules that retraction, not supersession, is the remedy for an incorrect promoted fact.

### 2.4 The checkpoint executor

The **graph gateway is the authoring authority** for each checkpoint approval: the approval is recorded as the gateway's act at the write boundary, and the gateway both decides and executes the admission.

### 2.5 Distillation entry today

Distillation writes (`origin_mechanism: derived` / `derivation_class: distilled`) into the Operational plane are **already EA-gated today** via the feedback loop; this ADR formalizes the existing gate rather than introducing a new one.

## 3. Rationale

What becomes true after this decision lands is that no fact reaches authoritative ground truth without a human having been accountable for it, at a cost proportionate to the harm a bad write would do. A verification-weight touch on faithful external capture is cheap; a substantive review on distilled judgment is where pollution is stopped; the EA gate on promotion is already paid for. Auditability improves because every ground-truth mutation carries a named accountable party, and un-promotion stops being an ungoverned back door.

## 4. Alternatives Considered

### 4.1 Alternative A: No governance — trust the pipelines

Let every entry path write directly, trusting upstream extraction and distillation to be correct. This is obviously wrong: it is the status quo the forcing function rejects, and nobody would defend ungoverned writes to an enterprise system of record.

### 4.2 Alternative B: A single uniform checkpoint on all writes

One human review, identical weight, on every KG write regardless of source. Rejected because it treats faithful external capture and noisy distilled judgment as equal risks, and it does not scale to CMDB-volume ingestion.

## 5. Consequences

- **5.1 Positive** — every ground-truth mutation carries an accountable party; distillation pollution is stopped at entry; un-promotion becomes a governed act; DDR-003 gains the promotion-gate authority it is blocked on.
- **5.2 Constraints imposed** — every write path must route through the checkpoint before admission; high-volume paths inherit review latency.
- **5.3 Risks** — the per-write Environment review is a throughput bottleneck; if reviewers cannot keep pace, deployed-reality facts age before admission. Signal to revisit: checkpoint queue depth on the Environment plane.

## 6. Compliance

Compliance is currently aspirational, tracked at the KG-entry-governance implementation ticket. Until enforcement lands, conformance is checked at design-review time against this ADR.

## 7. Cross-References

- **DDR-003 §4** — defines the promotion-gate criteria this ADR relies on for the promotion-path checkpoint.
- DDR-002 §2.3 (distillation checkpoint gap), §2.4 / §5 / §7 #21 (retraction shape and un-promotion routing).
- ADR-001 §2.5 (EA-gated promotion mechanism); ADR-002 §2.6 (write authority).
- Deliberation substrate: triage-001 record Appendix A (charter), R30.
- **Named follow-up (§2.2):** Environment-plane checkpoint posture — deferred pending volume/bottleneck deliberation; tracked at the KG-entry-governance follow-up ticket.

## 8. Change Log

| Version | Date | Ticket | Change |
|---|---|---|---|
| 0.1.0 | 2026-07-17 | KG-entry-governance | Initial draft |
