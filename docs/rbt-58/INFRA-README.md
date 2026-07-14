# RBT-58 — Graph-store infrastructure (Batch B)

Self-managed **Neo4j Enterprise** system-of-record on **GKE Standard** (ADR-002 §2.2;
DP-1 ratified 2026-07-14) + the shutdown/startup scheduler. Authored on the design
surface; **`terraform apply` / cluster provisioning / `kubectl apply` run on Tad's
side** — this repo is the artifact set, not a run from the cloud sandbox.

## Layout

```
terraform/
  modules/neo4j_graph/   # the reusable GCP-substrate module (cluster, pools, IAM, secret, registry)
  dev/                   # dev environment root — calls the module, own backend/state
k8s/neo4j/               # raw Neo4j manifests (DP-1: hand-authored, not Helm)
  00 namespace + KSA (Workload Identity)
  10 SSD StorageClass (zonal at dev; regional-PD is a deferred prod topology)
  20 headless Service
  25 SecretProviderClass (NEO4J_AUTH via Secret Manager CSI, no k8s Secret)
  30 StatefulSet (single-node, Guaranteed QoS, SSD PVC)
  40 scheduler RBAC (least-privilege scaler)
  50 scheduler CronJobs (scale 0<->1; node pool autoscaler is the cost lever)
helpers/                 # operator scripts + cluster prerequisites
```

The schema bootstrap (**Batch A**, `deploy/neo4j/schema/01-constraints.cypher`) and the
seed/loader (**Batch C/D**) are separate deliverables; see the apply order below.

## Apply order (RBT-58 execution)

1. `cd terraform/dev && terraform init && terraform plan -out=tfplan` — review, then
   `terraform apply tfplan` (never apply from source — 05 §2).
2. Add the `NEO4J_AUTH` secret **version** out-of-band (see `modules/neo4j_graph/secrets.tf`).
3. Install the **Secrets Store CSI driver + GCP provider** on the cluster (see `helpers/README.md`).
4. Mirror the pinned `neo4j:5.26-enterprise` image into the Artifact Registry repo;
   set the image path + `neo4j_gsa_email` annotation in the manifests.
5. `kubectl apply -f k8s/neo4j/` (in filename order).
6. Apply Batch A constraints; load Batch C/D seed + manifest; run conformance 1a.

## Open flags carried for the end-of-batch review

- **[L] Enterprise licence** — `NEO4J_ACCEPT_LICENSE_AGREEMENT: "eval"`; production
  Enterprise is a commercial-licence obligation, not a config value.
- **[S] Secret file wiring** — `NEO4J_AUTH_FILE` assumes the image reads the auth string
  from a file; **verify against the pinned image before apply**.
- **[Backend]** the GCS state bucket name is a placeholder (foundational-layer resource,
  its own state/blast-radius); fill before `init`.
- **CI gate sequence** (fmt/validate/tflint/scan/plan/policy/apply, 05 §1) and drift
  detection are **not** authored in this batch — they're the infra-pipeline surface,
  flagged for a follow item, not folded into RBT-58's provisioning scope.

## Standard

Authored against `bedrock/infrastructure-code` (1.4.0), references 01–05. Not yet
`fmt`/`validate`/`tflint`/`trivy`-checked in the cloud sandbox (no GCP creds / no
terraform binary here) — that runs on Tad's side and in the end-of-batch review pass.
