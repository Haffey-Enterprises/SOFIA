---
doctype: kg-seed
plane: Catalog
load_order: 10
authority: DDR-002 v1.3.0 (sha256 8ec413985f0eba094c815fd58f581311afacc9c083f45ae47e8d0f31bbe1bf16)
---

# Catalog — Haffey Enterprises selection ground truth

The versioned selection graph: the approved patterns, technologies, and the
capabilities they satisfy. Reshaped from the Haffey Enterprises approved-technology /
implementation-pattern registry to the DDR-002 §2.1 schema (the registry's own
document framing is dropped; the content is remapped, not imported wholesale).

Confidence-derivation basis: **`flat_base` (basis 2)** — versioned authoritative ground
truth; staleness is supersession, not decay. All nodes `origin_mechanism: ingested`
(sourced from the HE architecture registry) and therefore carry `source_record_ref`.

## Graph payload

```yaml
nodes:
  - labels: [Catalog, Capability]
    properties:
      capability_id: CAP-001
      business_key: capability:relational-persistence
      version: "1.0.0"
      status: active
      name: Relational Persistence
      l1_taxonomy: data
      l2_taxonomy: persistence
      l3_taxonomy: relational
      origin_mechanism: ingested
      recorded_at: "2026-07-14T00:00:00Z"
      source_record_ref: { source_system_class: he_arch_registry, record_id: "HE-CAP-001" }

  - labels: [Catalog, Capability]
    properties:
      capability_id: CAP-002
      business_key: capability:container-orchestration
      version: "1.0.0"
      status: active
      name: Container Orchestration
      l1_taxonomy: compute
      l2_taxonomy: orchestration
      l3_taxonomy: kubernetes
      origin_mechanism: ingested
      recorded_at: "2026-07-14T00:00:00Z"
      source_record_ref: { source_system_class: he_arch_registry, record_id: "HE-CAP-002" }

  - labels: [Catalog, Technology]
    properties:
      technology_id: TECH-001
      business_key: technology:postgresql
      version: "1.0.0"
      name: PostgreSQL
      vendor: PostgreSQL Global Development Group
      platform: gcp-cloudsql
      approval_status: approved
      approved_data_classifications: [internal, confidential]
      tier_applicability: [1, 2, 3, 4]
      origin_mechanism: ingested
      recorded_at: "2026-07-14T00:00:00Z"
      source_record_ref: { source_system_class: he_arch_registry, record_id: "HE-TECH-001" }

  - labels: [Catalog, Technology]
    properties:
      technology_id: TECH-002
      business_key: technology:gke
      version: "1.0.0"
      name: Google Kubernetes Engine
      vendor: Google Cloud
      platform: gcp
      approval_status: approved
      approved_data_classifications: [internal, confidential]
      tier_applicability: [1, 2, 3, 4]
      origin_mechanism: ingested
      recorded_at: "2026-07-14T00:00:00Z"
      source_record_ref: { source_system_class: he_arch_registry, record_id: "HE-TECH-002" }

  - labels: [Catalog, Pattern]
    properties:
      pattern_id: PAT-001
      business_key: pattern:microservices-architecture
      version: "1.0.0"
      status: active
      pattern_type: application_architecture
      name: Microservices Architecture
      origin_mechanism: ingested
      recorded_at: "2026-07-14T00:00:00Z"
      source_record_ref: { source_system_class: he_arch_registry, record_id: "HE-PAT-001" }

  - labels: [Catalog, IacTemplate]
    properties:
      iac_template_id: IAC-001
      business_key: iactemplate:microservices-gke-base
      version: "1.0.0"
      status: active
      template_type: terraform
      name: Microservices GKE Base
      origin_mechanism: ingested
      recorded_at: "2026-07-14T00:00:00Z"
      source_record_ref: { source_system_class: he_arch_registry, record_id: "HE-IAC-001" }

edges:
  - type: REQUIRES_CAPABILITY
    from: { pattern_id: PAT-001 }
    to: { capability_id: CAP-001 }
    properties: { required: true, tier_conditional: false }

  - type: REQUIRES_CAPABILITY
    from: { pattern_id: PAT-001 }
    to: { capability_id: CAP-002 }
    properties: { required: true, tier_conditional: false }

  # APPROVED_OPTION_FOR is an ingested asserted-fact + temporal edge (§3): carries
  # edge provenance (origin_mechanism) + effective_from/status.
  - type: APPROVED_OPTION_FOR
    from: { technology_id: TECH-001 }
    to: { capability_id: CAP-001 }
    properties: { conditional: false, justification: "Approved relational store for HE workloads", origin_mechanism: ingested, effective_from: "2026-01-01T00:00:00Z", status: active }

  - type: APPROVED_OPTION_FOR
    from: { technology_id: TECH-002 }
    to: { capability_id: CAP-002 }
    properties: { conditional: false, justification: "Approved orchestration platform", origin_mechanism: ingested, effective_from: "2026-01-01T00:00:00Z", status: active }

  - type: IMPLEMENTS
    from: { iac_template_id: IAC-001 }
    to: { pattern_id: PAT-001 }
    properties: {}
```
