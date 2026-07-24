##############################################################################
# File: terraform/dev/main.tf
# Config: dev environment root
# Author: Thaddeus Haffey — Executive Architect, Haffey Enterprises LLC
# Created: 2026-07-14
# Revised: 2026-07-22
# Description: Instantiates the delivery module for dev — the substrate the
#   knowledge-service pipeline runs on: keyless CI federation, the service image
#   registry, the runtime identity, and the Aura credential container. No graph
#   compute is provisioned here: the dev graph is managed Neo4j Aura (ADR-002
#   §2.2), external to this project.
##############################################################################

module "delivery" {
  source = "../modules/delivery"

  project_id        = var.project_id
  region            = var.region
  environment       = "dev"
  github_repository = var.github_repository
}

output "artifact_registry_path" {
  description = "Docker repository path (re-exported) — the GCP_AR_REPO workflow variable."
  value       = module.delivery.artifact_registry_path
}

output "ci_service_account_email" {
  description = "CI delivery SA email (re-exported) — the GCP_CI_SA workflow variable."
  value       = module.delivery.ci_service_account_email
}

output "neo4j_aura_secret_id" {
  description = "Aura credential secret ID (re-exported). Container only — the value is added out-of-band."
  value       = module.delivery.neo4j_aura_secret_id
}

output "runtime_service_account_email" {
  description = "knowledge-service runtime SA email (re-exported) — named in the Cloud Run manifest."
  value       = module.delivery.runtime_service_account_email
}

output "workload_identity_provider" {
  description = "GitHub OIDC provider resource name (re-exported) — the GCP_WIF_PROVIDER workflow variable."
  value       = module.delivery.workload_identity_provider
}
