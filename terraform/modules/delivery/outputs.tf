##############################################################################
# File: terraform/modules/delivery/outputs.tf
# Module: delivery
# Author: Haffey Enterprises LLC
# Created: 2026-07-22
# Revised: 2026-07-22
# Description: The values the delivery pipeline is wired from. These feed the
#   three GitHub repository variables the app workflow reads — GCP_WIF_PROVIDER,
#   GCP_CI_SA, GCP_AR_REPO — plus the runtime SA the Cloud Run manifest names.
#   None is a secret: they are identifiers, and the credential they gate is
#   never emitted here.
##############################################################################

output "artifact_registry_path" {
  description = "Docker repository path images are pushed to and pulled from. Feeds the GCP_AR_REPO repository variable."
  value       = "${var.region}-docker.pkg.dev/${var.project_id}/${google_artifact_registry_repository.services.repository_id}"
}

output "ci_service_account_email" {
  description = "CI delivery service account the workflow impersonates. Feeds the GCP_CI_SA repository variable."
  value       = google_service_account.ci_delivery.email
}

output "neo4j_aura_secret_id" {
  description = "Secret Manager secret ID holding the Aura credential. The container only — its value is added out-of-band by the operator."
  value       = google_secret_manager_secret.neo4j_aura.secret_id
}

output "runtime_service_account_email" {
  description = "Service account the knowledge-service Cloud Run revision runs as. Named in deploy/knowledge-service/service.dev.yaml."
  value       = google_service_account.knowledge_service_runtime.email
}

output "workload_identity_provider" {
  description = "Full resource name of the GitHub OIDC provider. Feeds the GCP_WIF_PROVIDER repository variable."
  value       = google_iam_workload_identity_pool_provider.github.name
}
