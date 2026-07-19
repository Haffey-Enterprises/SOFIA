# KG-Entry Governance — Ratified Rulings

**Ratified 2026-07-17 by Thaddeus Haffey (Executive Architect).** These rulings **close** the open questions the triage-001 charter (Appendix A) recorded for the KG-entry-governance record, and are authoritative design intent superseding those items' open status.

## Ruling 1 — Environment-plane checkpoint posture (closes charter Appendix A #5)

The Environment plane uses **confidence-weighting at retrieval**, not a per-write human checkpoint. Rationale: per-write review of continuous CMDB writes is the bottleneck R30 declined; Environment facts age via freshness (DDR-002 §2.2), so a retrieval-time weight fits the plane's signature. The Environment-plane posture is **no longer open**.

## Ruling 2 — Distillation checkpoint scope (closes charter Appendix A #4 for the distillation path)

The distillation substantive-review checkpoint applies to the **distinct durable lesson**, bounded-by-distinctness per DDR-002 §2.3 — **not** the per-event telemetry stream. Because the reviewed set is the small number of distinct `ObservedPattern`s, the checkpoint satisfies the R30 bottleneck constraint (Operational stays writable) by construction. The distillation checkpoint scope is **no longer open**.
