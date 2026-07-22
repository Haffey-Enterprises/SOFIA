##############################################################################
# File: terraform/modules/delivery/wif.tf
# Module: delivery
# Author: Haffey Enterprises LLC
# Created: 2026-07-22
# Revised: 2026-07-22
# Description: Workload Identity Federation for GitHub Actions (05 §4). The
#   runner exchanges its OIDC token for short-lived GCP credentials; no service
#   account key is ever created, downloaded, or stored. The attribute condition
#   is the security boundary — without it, any GitHub repository in the world
#   could present a valid token from this issuer.
##############################################################################

resource "google_iam_workload_identity_pool" "github_actions" {
  project                   = var.project_id
  workload_identity_pool_id = "github-actions"
  display_name              = "GitHub Actions"
  description               = "Federated identity for GitHub Actions workflows (${var.environment})."

  depends_on = [google_project_service.required]
}

resource "google_iam_workload_identity_pool_provider" "github" {
  project                            = var.project_id
  workload_identity_pool_id          = google_iam_workload_identity_pool.github_actions.workload_identity_pool_id
  workload_identity_pool_provider_id = "github"
  display_name                       = "GitHub OIDC"
  description                        = "OIDC provider for ${var.github_repository}."

  # Only tokens asserting this repository are accepted. Google rejects a
  # provider whose mapped attributes omit google.subject, so it is mapped even
  # though the repository attribute is what authorization keys off.
  attribute_condition = "assertion.repository == \"${var.github_repository}\""

  attribute_mapping = {
    "google.subject"       = "assertion.sub"
    "attribute.repository" = "assertion.repository"
    "attribute.ref"        = "assertion.ref"
  }

  oidc {
    issuer_uri = "https://token.actions.githubusercontent.com"
  }
}
