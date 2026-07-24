---
doctype: kg-seed
plane: Environment
load_order: 30
authority: DDR-002 v1.3.0 (sha256 8ec413985f0eba094c815fd58f581311afacc9c083f45ae47e8d0f31bbe1bf16)
---

# Environment — Haffey Enterprises as-running ground truth

The as-running graph: the realized deployment environments and the services running in
them. Two bases live here:

- **`DeploymentEnvironment` — `flat_base` (basis 2, per-label override):** a realized
  environment *identity* that does not age. Its **absence of `observed_at` is correct
  by design** (DDR-004 §4 / DDR-002 §2.2) — no freshness field.
- **`DeployedService` / `ConfigurationItem` — `aging` (basis 3):** runtime facts with
  `observed_at` as the freshness operand.

Fiction: `HE-Ledger` (financial ledger) and `HE-Portal` (customer portal), on `he-prod`;
`HE-Portal` also runs in `he-staging` (the deployment-agent's starting datum). All
`origin_mechanism: ingested` (CMDB / runtime source), `derivation_class: primary`.
`observed_at` is set in the past so a future capture derives a non-zero Δt.

## Graph payload

```yaml
nodes:
  - labels: [Environment, DeploymentEnvironment]
    properties:
      environment_id: ENV-PROD
      name: he-prod
      environment_class: production
      origin_mechanism: ingested
      recorded_at: "2026-07-14T00:00:00Z"
      source_record_ref: { source_system_class: he_cmdb, record_id: "HE-ENV-PROD" }
      # NOTE: no observed_at — DeploymentEnvironment does not age (basis 2, by design).

  - labels: [Environment, DeploymentEnvironment]
    properties:
      environment_id: ENV-STG
      name: he-staging
      environment_class: staging
      origin_mechanism: ingested
      recorded_at: "2026-07-14T00:00:00Z"
      source_record_ref: { source_system_class: he_cmdb, record_id: "HE-ENV-STG" }

  - labels: [Environment, DeployedService]
    properties:
      deployed_service_id: SVC-LEDGER-PROD
      service_type: financial-ledger
      lifecycle_state: running
      observed_at: "2026-06-01T00:00:00Z"
      origin_mechanism: ingested
      derivation_class: primary
      recorded_at: "2026-07-14T00:00:00Z"
      source_record_ref: { source_system_class: he_cmdb, record_id: "HE-SVC-LEDGER-PROD" }

  - labels: [Environment, DeployedService]
    properties:
      deployed_service_id: SVC-PORTAL-PROD
      service_type: customer-portal
      lifecycle_state: running
      observed_at: "2026-06-01T00:00:00Z"
      origin_mechanism: ingested
      derivation_class: primary
      recorded_at: "2026-07-14T00:00:00Z"
      source_record_ref: { source_system_class: he_cmdb, record_id: "HE-SVC-PORTAL-PROD" }

  - labels: [Environment, DeployedService]
    properties:
      deployed_service_id: SVC-PORTAL-STG
      service_type: customer-portal
      lifecycle_state: running
      observed_at: "2026-06-15T00:00:00Z"
      origin_mechanism: ingested
      derivation_class: primary
      recorded_at: "2026-07-14T00:00:00Z"
      source_record_ref: { source_system_class: he_cmdb, record_id: "HE-SVC-PORTAL-STG" }

  - labels: [Environment, ConfigurationItem]
    properties:
      ci_id: CI-001
      ci_type: database-instance
      name: he-ledger-postgres-prod
      observed_at: "2026-06-01T00:00:00Z"
      origin_mechanism: ingested
      derivation_class: primary
      recorded_at: "2026-07-14T00:00:00Z"
      source_record_ref: { source_system_class: he_cmdb, record_id: "HE-CI-001" }

edges:
  - type: DEPLOYED_IN
    from: { deployed_service_id: SVC-LEDGER-PROD }
    to: { environment_id: ENV-PROD }
    properties: { confidence: 1.0 }

  - type: RUNS
    from: { deployed_service_id: SVC-LEDGER-PROD }
    to: { technology_id: TECH-001 }
    properties: { confidence: 1.0 }

  - type: REALIZES
    from: { deployed_service_id: SVC-LEDGER-PROD }
    to: { capability_id: CAP-001 }
    properties: { confidence: 1.0 }

  - type: DEPLOYED_IN
    from: { deployed_service_id: SVC-PORTAL-PROD }
    to: { environment_id: ENV-PROD }
    properties: { confidence: 1.0 }

  - type: DEPLOYED_IN
    from: { deployed_service_id: SVC-PORTAL-STG }
    to: { environment_id: ENV-STG }
    properties: { confidence: 1.0 }

  - type: PART_OF
    from: { ci_id: CI-001 }
    to: { deployed_service_id: SVC-LEDGER-PROD }
    properties: { confidence: 1.0 }
```
