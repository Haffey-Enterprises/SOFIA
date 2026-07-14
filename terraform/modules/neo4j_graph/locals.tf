##############################################################################
# File: terraform/modules/neo4j_graph/locals.tf
# Module: neo4j_graph
# Author: Thaddeus Haffey — Executive Architect, Haffey Enterprises LLC
# Created: 2026-07-14
# Revised: 2026-07-14
# Description: Shared naming suffix + common labels (01 §6, 02 §2).
##############################################################################

locals {
  name_suffix = var.environment

  # prod = regional cluster (HA, regional PD); non-prod = ZONAL (single-zone), so
  # per-zone node-pool counts deliver a true single-node dev threshold and the
  # zonal PD is consistent with a single-zone cluster (regional PD needs 2 zones).
  cluster_location = var.environment == "prod" ? var.region : var.zone

  common_labels = {
    environment = var.environment
    managed_by  = "terraform"
    component   = "neo4j-graph"
    ticket      = "rbt-58"
  }

  required_apis = [
    "container.googleapis.com",
    "compute.googleapis.com",
    "secretmanager.googleapis.com",
    "artifactregistry.googleapis.com",
  ]
}
