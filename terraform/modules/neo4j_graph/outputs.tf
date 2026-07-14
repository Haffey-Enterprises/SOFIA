##############################################################################
# File: terraform/modules/neo4j_graph/outputs.tf
# Module: neo4j_graph
# Author: Thaddeus Haffey — Executive Architect, Haffey Enterprises LLC
# Created: 2026-07-14
# Revised: 2026-07-14
# Description: Module outputs — cluster coordinates the caller needs to configure
#   the kubernetes provider / kubectl context, and the identities the k8s
#   manifests reference (WI annotation, secret name).
##############################################################################

output "cluster_name" {
  description = "GKE cluster name."
  value       = google_container_cluster.primary.name
}

output "cluster_endpoint" {
  description = "GKE cluster control-plane endpoint."
  value       = google_container_cluster.primary.endpoint
  sensitive   = true
}

output "cluster_location" {
  description = "GKE cluster region."
  value       = google_container_cluster.primary.location
}

output "neo4j_gsa_email" {
  description = "Neo4j workload GSA email — annotate the 'neo4j' KSA with this for Workload Identity."
  value       = google_service_account.neo4j.email
}

output "neo4j_auth_secret_id" {
  description = "Secret Manager secret id holding NEO4J_AUTH (version added out-of-band)."
  value       = google_secret_manager_secret.neo4j_auth.secret_id
}

output "artifact_registry_repo" {
  description = "Artifact Registry Docker repo path for the mirrored Neo4j image."
  value       = "${var.region}-docker.pkg.dev/${var.project_id}/${google_artifact_registry_repository.images.repository_id}"
}
