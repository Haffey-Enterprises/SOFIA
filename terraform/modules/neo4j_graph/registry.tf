##############################################################################
# File: terraform/modules/neo4j_graph/registry.tf
# Module: neo4j_graph
# Author: Thaddeus Haffey — Executive Architect, Haffey Enterprises LLC
# Created: 2026-07-14
# Revised: 2026-07-14
# Description: Artifact Registry Docker repo (one per env, 02 §7). The pinned
#   Neo4j Enterprise image is MIRRORED here (not pulled from Docker Hub at
#   runtime) for supply-chain hygiene; the StatefulSet references this repo path.
##############################################################################

resource "google_artifact_registry_repository" "images" {
  project       = var.project_id
  location      = var.region
  repository_id = "graph-${local.name_suffix}"
  format        = "DOCKER"
  description   = "Mirrored container images for the Neo4j graph SoR (${var.environment})."

  labels = local.common_labels

  depends_on = [google_project_service.required]
}
