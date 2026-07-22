# `delivery` module

The **delivery substrate** for SOFIA services: the keyless identity CI federates
into, the registry images land in, the identity the service runs as, and the
container holding its graph credential.

It provisions no compute. Cloud Run services are created by the application
pipeline (`.github/workflows/knowledge-service.yml`) from the declarative
manifest in `deploy/knowledge-service/`, not from Terraform — the seam is the
image: `application-code` builds it, `app-delivery-pipeline` deploys it, and
this module provisions what both of those need to exist first.

## What it creates

| Resource | Purpose |
|---|---|
| Workload Identity Pool `github-actions` + provider `github` | Keyless OIDC federation for GitHub Actions (05 §4) |
| Service account `ci-delivery` | The identity CI impersonates to push and deploy |
| Service account `knowledge-service-runtime` | The identity the Cloud Run revision runs as |
| Artifact Registry `services` (DOCKER) | Where service images are pushed and pulled |
| Secret Manager `neo4j-aura-<env>` | **Container only** for the Aura credential |
| Project services | `iam`, `iamcredentials`, `sts`, `run`, `artifactregistry`, `secretmanager` |

## The two identities, and why they are two

`ci-delivery` builds, pushes, and deploys. `knowledge-service-runtime` runs and
reads one secret. Collapsing them into one account would give the running
service the right to deploy itself, and would give CI standing read access to
the graph credential — neither of which either party needs.

Every grant that can be resource-scoped is:

| Identity | Role | Scope |
|---|---|---|
| `ci-delivery` | `roles/iam.workloadIdentityUser` | The pool's `attribute.repository` principalSet — not the whole pool |
| `ci-delivery` | `roles/artifactregistry.writer` | The `services` repository — not the project |
| `ci-delivery` | `roles/iam.serviceAccountUser` | The runtime SA — not the project |
| `ci-delivery` | `roles/run.developer` | **Project** — of necessity (see below) |
| `knowledge-service-runtime` | `roles/secretmanager.secretAccessor` | The Aura secret — not the project |

`roles/run.developer` is the one project-level grant, and it is project-level
because it must exist *before* the Cloud Run service it will create; there is no
service resource to bind at apply time. When the service exists and its identity
stabilises, this is worth narrowing to a service-scoped
`google_cloud_run_v2_service_iam_member`.

## The secret is a container, never a value

`google_secret_manager_secret` is declared here. `google_secret_manager_secret_version`
deliberately is **not**, and must not be added. A version resource puts the
credential into Terraform configuration and into state, after which the entire
state file is the secret (03 §4). The value is added out of band:

```bash
echo -n '<password>' | gcloud secrets versions add neo4j-aura-dev \
  --data-file=- --project <project_id>
```

That command is the operator's to run. It does not belong in this module, in
CI, or in any automation that reads this repository.

## Usage

```hcl
module "delivery" {
  source = "../modules/delivery"

  project_id        = var.project_id
  region            = var.region
  environment       = "dev"
  github_repository = var.github_repository
}
```

## Inputs

| Name | Type | Default | Description |
|---|---|---|---|
| `project_id` | `string` | — | GCP project to provision into. |
| `region` | `string` | — | Region for Artifact Registry, Secret Manager replication, Cloud Run. |
| `environment` | `string` | — | Environment name; forms the name suffix and `environment` label. |
| `github_repository` | `string` | — | `owner/repo` permitted to federate. Bound into the provider's attribute condition. |
| `enable_apis` | `bool` | `true` | Whether this module enables its required APIs. |

## Outputs

`workload_identity_provider` · `ci_service_account_email` ·
`artifact_registry_path` · `runtime_service_account_email` ·
`neo4j_aura_secret_id`

The first three feed the GitHub repository variables `GCP_WIF_PROVIDER`,
`GCP_CI_SA`, and `GCP_AR_REPO` that the app workflow's jobs are guarded on.

## Relationship to the RBT-58 graph module

This module **replaces** `modules/neo4j_graph`, removed in RBT-77. That module
ran Neo4j self-managed on GKE; ADR-002 §2.2 places the **dev** graph on managed
Neo4j Aura, so the dev environment needs a credential to reach Aura, not a
cluster to run a database in. The production deployment runtime remains deferred
(ADR-002 §5.2) — if it adopts self-managed Neo4j, that is a new module and an
ADR act, not a revival of this one.
