##############################################################################
# File: terraform/modules/delivery/iam.tf
# Module: delivery
# Author: Haffey Enterprises LLC
# Created: 2026-07-22
# Revised: 2026-07-22
# Description: The two workload identities and their least-privilege grants
#   (02 §4). Two accounts, not one: CI needs to push images and deploy, the
#   running service needs to read one secret, and neither should hold the
#   other's rights. Every binding is additive (google_*_iam_member), never the
#   authoritative form, which would silently strip Google-managed bindings.
#
#   Scoping note: every grant that CAN be resource-scoped IS. The two
#   project-level grants are project-level of necessity, not convenience —
#   roles/run.developer must exist before the Cloud Run service it will create,
#   so there is no service resource to scope it to at apply time.
##############################################################################

# --- CI delivery identity ---------------------------------------------------

resource "google_service_account" "ci_delivery" {
  account_id   = "ci-delivery"
  display_name = "CI delivery pipeline (${var.environment})"
  description  = "GitHub Actions federated identity: builds, pushes, and deploys knowledge-service."
  project      = var.project_id

  depends_on = [google_project_service.required]
}

# The federation binding: only tokens from the permitted repository, via the
# pool, may impersonate this account. Scoped to attribute.repository rather than
# the whole pool — a pool-wide principalSet would admit any repository the
# provider's condition later allowed.
resource "google_service_account_iam_member" "ci_delivery_workload_identity" {
  service_account_id = google_service_account.ci_delivery.name
  role               = "roles/iam.workloadIdentityUser"
  member             = "principalSet://iam.googleapis.com/${google_iam_workload_identity_pool.github_actions.name}/attribute.repository/${var.github_repository}"
}

# Push rights on THIS repository only — not roles/artifactregistry.writer at
# the project level, which would grant write to every present and future repo
# in the project (including sofia-dev and sofia-archive).
resource "google_artifact_registry_repository_iam_member" "ci_delivery_writer" {
  project    = google_artifact_registry_repository.services.project
  location   = google_artifact_registry_repository.services.location
  repository = google_artifact_registry_repository.services.name
  role       = "roles/artifactregistry.writer"
  member     = "serviceAccount:${google_service_account.ci_delivery.email}"
}

# Deploy rights. Project-scoped because the Cloud Run service does not exist
# until CI creates it; there is no narrower resource to bind at apply time.
resource "google_project_iam_member" "ci_delivery_run_developer" {
  project = var.project_id
  role    = "roles/run.developer"
  member  = "serviceAccount:${google_service_account.ci_delivery.email}"
}

# Deploying a Cloud Run revision that runs AS the runtime SA requires
# actAs on it. Bound to that one service account — a project-level
# roles/iam.serviceAccountUser would let CI impersonate every SA in the project.
resource "google_service_account_iam_member" "ci_delivery_act_as_runtime" {
  service_account_id = google_service_account.knowledge_service_runtime.name
  role               = "roles/iam.serviceAccountUser"
  member             = "serviceAccount:${google_service_account.ci_delivery.email}"
}

# --- knowledge-service runtime identity -------------------------------------

resource "google_service_account" "knowledge_service_runtime" {
  account_id   = "knowledge-service-runtime"
  display_name = "knowledge-service runtime (${var.environment})"
  description  = "The identity the knowledge-service Cloud Run revision runs as."
  project      = var.project_id

  depends_on = [google_project_service.required]
}

# Read rights on the Aura credential ONLY. The service reads exactly one secret;
# a project-level secretAccessor would also expose anthropic-api-key,
# db-password, sofia-token-signing-key, and every future secret.
resource "google_secret_manager_secret_iam_member" "runtime_neo4j_aura_accessor" {
  project   = google_secret_manager_secret.neo4j_aura.project
  secret_id = google_secret_manager_secret.neo4j_aura.secret_id
  role      = "roles/secretmanager.secretAccessor"
  member    = "serviceAccount:${google_service_account.knowledge_service_runtime.email}"
}
