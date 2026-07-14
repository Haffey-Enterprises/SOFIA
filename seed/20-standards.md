---
doctype: kg-seed
plane: Standards
load_order: 20
authority: DDR-002 v1.3.0 (sha256 8ec413985f0eba094c815fd58f581311afacc9c083f45ae47e8d0f31bbe1bf16)
---

# Standards — Haffey Enterprises governance-of-knowledge ground truth

The versioned governance-of-knowledge graph: a Haffey Enterprises standard, a policy
rule it defines, and the compliance control the rule maps to. Basis: **`flat_base`
(basis 2)** — versioned authoritative ground truth.

`POL-001`'s `dependency_manifest` declares `[Technology]`, and the rule is edge-backed
by `MANDATES → TECH-001` — so §7 #10 (`rule_definition`↔edge sync: every manifest
entity-type is a `GOVERNED_BY`/`MANDATES` target) holds. All `origin_mechanism:
ingested` (from the HE standards registry); `source_record_ref` carried.

## Graph payload

```yaml
nodes:
  - labels: [Standards, Standard]
    properties:
      standard_id: STD-001
      business_key: standard:he-data-protection
      version: "1.0.0"
      status: active
      name: Haffey Enterprises Data Protection Standard
      authority: Haffey Enterprises Architecture Review Board
      origin_mechanism: ingested
      recorded_at: "2026-07-14T00:00:00Z"
      source_record_ref: { source_system_class: he_standards_registry, record_id: "HE-STD-001" }

  - labels: [Standards, PolicyRule]
    properties:
      policy_rule_id: POL-001
      business_key: policyrule:approved-data-stores-only
      version: "1.0.0"
      status: active
      rule_name: Approved Data Stores Only
      domain: data-protection
      enforcement_level: hard
      enforced_at_gate: gate_1
      statement: "Persistent data stores MUST be drawn from the approved technology registry."
      rule_definition: "IF solution.uses_data_store AND data_store NOT IN approved_technologies THEN violation"
      dependency_manifest: [Technology]
      origin_mechanism: ingested
      recorded_at: "2026-07-14T00:00:00Z"
      source_record_ref: { source_system_class: he_standards_registry, record_id: "HE-POL-001" }

  - labels: [Standards, ComplianceControl]
    properties:
      control_id: CTL-001
      framework: he_internal
      control_ref: HE-DP-01
      control_name: Approved persistence controls
      origin_mechanism: ingested
      recorded_at: "2026-07-14T00:00:00Z"
      source_record_ref: { source_system_class: he_standards_registry, record_id: "HE-CTL-001" }

edges:
  - type: DEFINES
    from: { standard_id: STD-001 }
    to: { policy_rule_id: POL-001 }
    properties: {}

  - type: MAPS_TO
    from: { policy_rule_id: POL-001 }
    to: { control_id: CTL-001 }
    properties: {}

  # Edge-backs POL-001's dependency_manifest [Technology] -> satisfies §7 #10.
  - type: MANDATES
    from: { policy_rule_id: POL-001 }
    to: { technology_id: TECH-001 }
    properties: {}
```
