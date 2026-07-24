##############################################################################
# File: terraform/modules/delivery/apis.tf
# Module: delivery
# Author: Haffey Enterprises LLC
# Created: 2026-07-22
# Revised: 2026-07-22
# Description: Enables the GCP APIs this module needs (02 §6). Gated behind
#   enable_apis; disable_on_destroy = false so destroying one instance never
#   disables an API another instance — or another module — still needs. That
#   guard is not theoretical: it is what confined the RBT-58 teardown's blast
#   radius to its own module and left the surviving registries, snapshots, and
#   secrets untouched.
##############################################################################

resource "google_project_service" "required" {
  for_each = var.enable_apis ? toset(local.required_apis) : toset([])

  project            = var.project_id
  service            = each.value
  disable_on_destroy = false
}
