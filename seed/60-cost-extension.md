---
doctype: kg-seed
plane: Extension+Cost
load_order: 60
authority: DDR-002 v1.3.0 (sha256 8ec413985f0eba094c815fd58f581311afacc9c083f45ae47e8d0f31bbe1bf16)
---

# Extension + Cost — the first Extension registration (the basis linchpin)

Registering the cost plane is the seed's linchpin — **one act, three bases**:

- `PlaneDefinition` PLANE-COST declares `RateCard`/`CostFactor` as **`non_citable`
  (basis 4)** — the proof surface for the typed `NON_CITABLE_SOURCE` rejection, and
  what §7 #26/#27 key on.
- PLANE-COST is itself a `(:Extension:PlaneDefinition)` — **`flat_base` (basis 2)** by
  construction (§2.6). No separate basis-2 PlaneDefinition needed.
- `CapabilityCostEstimate` EST-001 carries its own `confidence` — **`native_confidence`
  (basis 1)**.

`confidence_basis` and `property_schema` declare the **same label set** (§7 #26 key-set
equality) and are authored here as objects; the loader **serializes them to JSON
strings on write** (§2.6 declarations-not-edges; conformance `extension.py` parses JSON).
`attaches_to: [Capability, Technology]` — both exist in Catalog (§7 #18). `EST-001` is
`derivation_class: aggregated` (derives from internal version-pins) → **no
`source_record_ref`** (#17 scopes to `distilled`, not `aggregated`).

## Graph payload

```yaml
nodes:
  - labels: [Extension, PlaneDefinition]
    properties:
      plane_id: cost
      business_key: planedefinition:cost
      version: "1.0.0"
      status: active
      plane_name: Cost
      attaches_to: [Capability, Technology]
      # Serialized to a JSON string on write. Label set == confidence_basis's (§7 #26).
      property_schema:
        CapabilityCostEstimate: { aggregate_cost: number, confidence: number }
        RateCard: { rates: object }
        CostFactor: { amount: number, unit: string }
      # Per-label declaration OBJECTS (basis + freshness_operand iff aging) — the
      # form conformance/assertions/extension.py #26 requires. DDR-002 §2.6's
      # line-156 illustration shows a flat {label: basis} form that cannot carry
      # the freshness operand the §2.6 prose mandates for aging labels; the nested
      # form is the faithful realization. (Illustration divergence flagged to RBT-62.)
      confidence_basis:
        CapabilityCostEstimate: { basis: native_confidence }
        RateCard: { basis: non_citable }
        CostFactor: { basis: non_citable }
      origin_mechanism: authored
      recorded_at: "2026-07-14T00:00:00Z"

  - labels: [Cost, RateCard]
    properties:
      rate_card_id: RATE-001
      business_key: ratecard:gcp-standard
      version: "1.0.0"
      status: active
      effective_from: "2026-01-01T00:00:00Z"
      rates: { vcpu_hour: 0.031, gib_month: 0.17 }
      origin_mechanism: ingested
      recorded_at: "2026-07-14T00:00:00Z"
      source_record_ref: { source_system_class: he_finops_registry, record_id: "HE-RATE-001" }

  - labels: [Cost, CostFactor]
    properties:
      cost_factor_id: COST-001
      business_key: costfactor:postgresql-license
      version: "1.0.0"
      status: active
      factor_scope: technology
      factor_type: license
      amount: 0.0
      unit: usd_month
      origin_mechanism: ingested
      recorded_at: "2026-07-14T00:00:00Z"
      source_record_ref: { source_system_class: he_finops_registry, record_id: "HE-COST-001" }

  - labels: [Cost, CapabilityCostEstimate]
    properties:
      estimate_id: EST-001
      aggregate_cost: 412.90
      rate_card_version_ref: "ratecard:gcp-standard@1.0.0"
      cost_factor_version_ref: "costfactor:postgresql-license@1.0.0"
      capability_version_ref: "capability:relational-persistence@1.0.0"
      confidence: 0.75
      computed_at: "2026-07-11T00:00:00Z"
      decision_ref: "HE-GATE-0001"
      origin_mechanism: derived
      derivation_class: aggregated
      recorded_at: "2026-07-14T00:00:00Z"

edges:
  - type: FOR_CAPABILITY
    from: { estimate_id: EST-001 }
    to: { capability_id: CAP-001 }
    properties: {}

  - type: HAS_COST_FACTOR
    from: { estimate_id: EST-001 }
    to: { cost_factor_id: COST-001 }
    properties: {}

  - type: FOR_TECHNOLOGY
    from: { cost_factor_id: COST-001 }
    to: { technology_id: TECH-001 }
    properties: {}

  - type: PRICED_BY
    from: { estimate_id: EST-001 }
    to: { rate_card_id: RATE-001 }
    properties: {}
```
