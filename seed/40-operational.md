---
doctype: kg-seed
plane: Operational
load_order: 40
authority: DDR-002 v1.3.0 (sha256 8ec413985f0eba094c815fd58f581311afacc9c083f45ae47e8d0f31bbe1bf16)
---

# Operational — Haffey Enterprises track-record ground truth

The track-record graph: a durable distilled lesson (not telemetry). Basis:
**`native_confidence` (basis 1)** — the node carries its own `confidence` (lesson
reliability); a citation inherits it unchanged.

`OBS-001` is `origin_mechanism: derived` / `derivation_class: distilled`, so it carries
`source_record_ref` to its external telemetry source (§7 #17, the distilled case). The
`OBSERVED_IN` edge carries per-target observation certainty — distinct from the node's
lesson reliability (§4; composed downstream at rollup, not inherited into Evidence).

## Graph payload

```yaml
nodes:
  - labels: [Operational, ObservedPattern]
    properties:
      observed_pattern_id: OBS-001
      polarity: strength
      pattern_type: resilience
      description: "HE-Ledger cross-region failover has reliably met an RTO under one minute across observed events."
      observation_window: "2026-Q1..2026-Q2"
      confidence: 0.82
      first_observed_at: "2026-01-15T00:00:00Z"
      last_observed_at: "2026-06-01T00:00:00Z"
      status: active
      origin_mechanism: derived
      derivation_class: distilled
      recorded_at: "2026-07-14T00:00:00Z"
      source_record_ref: { source_system_class: he_observability_sor, record_id: "HE-AIOPS-LEDGER-FAILOVER" }

edges:
  # Per-target observation certainty on the edge (basis-1 node confidence is separate).
  - type: OBSERVED_IN
    from: { observed_pattern_id: OBS-001 }
    to: { pattern_id: PAT-001 }
    properties: { confidence: 0.9 }
```
