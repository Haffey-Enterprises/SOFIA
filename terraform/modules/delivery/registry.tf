##############################################################################
# File: terraform/modules/delivery/registry.tf
# Module: delivery
# Author: Haffey Enterprises LLC
# Created: 2026-07-22
# Revised: 2026-07-22
# Description: The Docker repository the app pipeline pushes to and Cloud Run
#   pulls from (02 §7). One repository per environment. The image tagging
#   discipline itself belongs to the app-delivery-pipeline skill; this file
#   only provisions the registry it lands in.
##############################################################################

resource "google_artifact_registry_repository" "services" {
  project       = var.project_id
  location      = var.region
  repository_id = "services"
  format        = "DOCKER"
  description   = "SOFIA service images (${var.environment})."
  labels        = local.common_labels

  depends_on = [google_project_service.required]
}
