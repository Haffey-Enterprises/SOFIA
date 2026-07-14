# Module: `neo4j_graph`

Provisions the self-managed **Neo4j Enterprise** system-of-record on **GKE Standard**
for SOFIA (ADR-002 §2.2; RBT-58 DP-1, ratified 2026-07-14). GKE Standard — not
Autopilot — because a self-managed stateful database needs node-pool and
storage-class control (infrastructure-code 02 §7 / 04 §4).

This module provisions the **GCP substrate only**. The Neo4j workload itself — the
StatefulSet, headless Service, StorageClass, and the scale-up/down scheduler — is
declared as **raw Kubernetes manifests** in `k8s/neo4j/` and applied by the delivery
pipeline (04 §5), not by this module. DP-1 ratified hand-authored manifests over the
Neo4j Helm chart.

## What it provisions

- **GKE Standard private cluster** — Workload Identity on, `REGULAR` release channel,
  managed Prometheus, private nodes, control plane restricted to
  `master_authorized_cidrs`.
- **Two node pools:**
  - `system-<env>` — small, always-on; hosts kube-system + the scheduler CronJobs
    (they need a node to run on when the graph pool is scaled to zero).
  - `graph-<env>` — dedicated, **autoscales `min_node_count`(0)..`max_node_count`(1)**,
    tainted `workload=neo4j:NoSchedule`. Scaling the StatefulSet to 0 lets the
    autoscaler drain this pool to 0 nodes — the cost lever.
- **Least-privilege identities** — a node SA (logging/metrics/AR-read) and a Neo4j
  workload GSA that the pod assumes via Workload Identity to read the auth secret.
- **Secret Manager** — the `neo4j-auth-<env>` secret *container*; the value is added
  out-of-band so it never lands in Terraform state (03 §4).
- **Artifact Registry** — a Docker repo for the mirrored Neo4j Enterprise image.

## Inputs

| Name | Type | Default | Notes |
|---|---|---|---|
| `project_id` | string | — | env-specific |
| `region` | string | — | env-specific (regional resources + prod regional cluster) |
| `zone` | string | — | env-specific; the non-prod cluster is zonal (true single node) |
| `environment` | string | — | dev \| staging \| prod (prod = regional cluster; else zonal) |
| `master_authorized_cidrs` | list(object) | — | control-plane allowlist |
| `enable_apis` | bool | `true` | |
| `system_node_machine_type` | string | `e2-small` | |
| `graph_node_machine_type` | string | `e2-standard-4` | |
| `graph_node_min_count` | number | `0` | scale-to-zero floor |
| `graph_node_max_count` | number | `1` | single-node threshold; topology deferred (ADR-002 §5.2) |
| `data_disk_size_gb` | number | `32` | consumed by the StatefulSet PVC manifest |

## Outputs

`cluster_name`, `cluster_endpoint` (sensitive), `cluster_location`, `neo4j_gsa_email`,
`neo4j_auth_secret_id`, `artifact_registry_repo`.

## Hand-off order (RBT-58 execution — Tad's side)

1. `terraform apply` this module (via the `dev/` root) → cluster + pools + identities.
2. Add the NEO4J_AUTH secret version out-of-band (see `secrets.tf`).
3. Mirror `neo4j:5-enterprise` (pinned) into the Artifact Registry repo.
4. Apply `k8s/neo4j/` manifests → StorageClass, headless Service, StatefulSet, scheduler.
5. Apply `deploy/neo4j/schema/01-constraints.cypher` → the DDR-002 §7 DB-enforced set.
6. Load the seed (Batch C/D) + manifest; run conformance 1a against the seeded instance.

> **VERIFY-AT-BUILD (honest flag):** the NEO4J_AUTH secret-file wiring (Secret Manager
> CSI mount → `NEO4J_AUTH_FILE` vs an entrypoint that exports `NEO4J_AUTH`) must be
> confirmed against the pinned Neo4j image's documented secret handling before apply —
> see `k8s/neo4j/30-statefulset.yaml`. Do not assume the `_FILE` convention without
> checking the image.
