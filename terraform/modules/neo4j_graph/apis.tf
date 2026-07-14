##############################################################################
# File: terraform/modules/neo4j_graph/apis.tf
# Module: neo4j_graph
# Author: Thaddeus Haffey — Executive Architect, Haffey Enterprises LLC
# Created: 2026-07-14
# Revised: 2026-07-14
# Description: Enables the GCP APIs this module needs (02 §6). Gated behind
#   enable_apis; disable_on_destroy=false so destroying one instance never
#   disables an API another needs.
##############################################################################

resource "google_project_service" "required" {
  for_each = var.enable_apis ? toset(local.required_apis) : toset([])

  project            = var.project_id
  service            = each.value
  disable_on_destroy = false
}
