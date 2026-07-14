##############################################################################
# File: terraform/modules/neo4j_graph/providers.tf
# Module: neo4j_graph
# Author: Thaddeus Haffey — Executive Architect, Haffey Enterprises LLC
# Created: 2026-07-14
# Revised: 2026-07-14
# Description: Default google provider config. There is NO kubernetes provider:
#   this module provisions the GCP substrate only, and the raw StatefulSet
#   manifests (k8s/neo4j/) are applied out-of-band with kubectl by the delivery
#   pipeline against the cluster's outputs — not through Terraform (04 §5).
##############################################################################

provider "google" {
  project = var.project_id
  region  = var.region
}
