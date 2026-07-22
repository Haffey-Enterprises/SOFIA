##############################################################################
# File: terraform/modules/delivery/locals.tf
# Module: delivery
# Author: Haffey Enterprises LLC
# Created: 2026-07-22
# Revised: 2026-07-22
# Description: Shared naming suffix and common labels (01 §6, 02 §2).
##############################################################################

locals {
  name_suffix = var.environment

  common_labels = {
    environment = var.environment
    managed_by  = "terraform"
  }

  required_apis = [
    "iam.googleapis.com",
    "iamcredentials.googleapis.com",
    "sts.googleapis.com",
    "run.googleapis.com",
    "artifactregistry.googleapis.com",
    "secretmanager.googleapis.com",
  ]
}
