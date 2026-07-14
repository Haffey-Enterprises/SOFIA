##############################################################################
# File: terraform/dev/main.tf
# Config: dev environment root
# Author: Thaddeus Haffey — Executive Architect, Haffey Enterprises LLC
# Created: 2026-07-14
# Revised: 2026-07-14
# Description: Instantiates the neo4j_graph module for dev — the RBT-58 threshold
#   instance. Single-node graph pool (max 1), scale-to-zero floor (min 0).
##############################################################################

module "neo4j_graph" {
  source = "../modules/neo4j_graph"

  project_id              = var.project_id
  region                  = var.region
  zone                    = var.zone
  environment             = "dev"
  master_authorized_cidrs = var.master_authorized_cidrs

  # Dev threshold sizing — single node, scale-to-zero. Topology deferred (ADR-002 §5.2).
  graph_node_min_count = 0
  graph_node_max_count = 1
  data_disk_size_gb    = 32
}

output "cluster_name" {
  description = "Dev GKE cluster name (re-exported)."
  value       = module.neo4j_graph.cluster_name
}

output "neo4j_gsa_email" {
  description = "Neo4j workload GSA email (re-exported) — for the KSA WI annotation."
  value       = module.neo4j_graph.neo4j_gsa_email
}

output "artifact_registry_repo" {
  description = "Artifact Registry repo path (re-exported)."
  value       = module.neo4j_graph.artifact_registry_repo
}
