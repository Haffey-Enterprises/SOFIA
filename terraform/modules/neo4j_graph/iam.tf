##############################################################################
# File: terraform/modules/neo4j_graph/iam.tf
# Module: neo4j_graph
# Author: Thaddeus Haffey — Executive Architect, Haffey Enterprises LLC
# Created: 2026-07-14
# Revised: 2026-07-14
# Description: Least-privilege service accounts + keyless Workload Identity
#   (02 §4). Two identities: (1) a node SA with minimal node roles; (2) a Neo4j
#   workload GSA the pod assumes via WI to read the NEO4J_AUTH secret. All IAM is
#   ADDITIVE (google_*_iam_member) — never authoritative. No SA keys anywhere.
##############################################################################

# --- Node service account (least privilege; not the default compute SA) -----
resource "google_service_account" "node" {
  account_id   = "graph-node-${local.name_suffix}"
  display_name = "GKE graph node SA (${var.environment})"
  project      = var.project_id
}

resource "google_project_iam_member" "node_logging" {
  project = var.project_id
  role    = "roles/logging.logWriter"
  member  = "serviceAccount:${google_service_account.node.email}"
}

resource "google_project_iam_member" "node_metrics" {
  project = var.project_id
  role    = "roles/monitoring.metricWriter"
  member  = "serviceAccount:${google_service_account.node.email}"
}

resource "google_project_iam_member" "node_artifact_reader" {
  project = var.project_id
  role    = "roles/artifactregistry.reader"
  member  = "serviceAccount:${google_service_account.node.email}"
}

# --- Neo4j workload GSA — assumed by the pod's KSA via Workload Identity -----
# Grants exactly one privilege: read the NEO4J_AUTH secret version. The pod
# fetches the credential via the Secret Manager CSI driver (SecretProviderClass);
# no credential is ever written to a Kubernetes Secret (SDD-001 §4.6).
resource "google_service_account" "neo4j" {
  account_id   = "neo4j-graph-${local.name_suffix}"
  display_name = "Neo4j graph workload SA (${var.environment})"
  project      = var.project_id
}

resource "google_secret_manager_secret_iam_member" "neo4j_auth_accessor" {
  project   = var.project_id
  secret_id = google_secret_manager_secret.neo4j_auth.secret_id
  role      = "roles/secretmanager.secretAccessor"
  member    = "serviceAccount:${google_service_account.neo4j.email}"
}

# WI binding: the in-namespace KSA (namespace/name below) impersonates the GSA.
# KSA is created by the k8s manifests (k8s/neo4j/30-statefulset.yaml serviceAccountName).
resource "google_service_account_iam_member" "neo4j_wi" {
  service_account_id = google_service_account.neo4j.name
  role               = "roles/iam.workloadIdentityUser"
  member             = "serviceAccount:${var.project_id}.svc.id.goog[neo4j/neo4j]"
}
