##############################################################################
# File: terraform/modules/neo4j_graph/versions.tf
# Module: neo4j_graph
# Author: Thaddeus Haffey — Executive Architect, Haffey Enterprises LLC
# Created: 2026-07-14
# Revised: 2026-07-14
# Description: Terraform + provider version pins for the neo4j_graph module —
#   the self-managed Neo4j Enterprise system-of-record on GKE Standard
#   (ADR-002 §2.2; RBT-58 DP-1). Pins per the house infrastructure-code standard.
##############################################################################

terraform {
  required_version = ">= 1.5.0"

  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 6.0"
    }
    # No kubernetes provider: this module provisions the GCP substrate only; the
    # Neo4j manifests (k8s/neo4j/) are applied out-of-band by the pipeline (04 §5).
  }
}
