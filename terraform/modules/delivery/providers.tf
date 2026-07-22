##############################################################################
# File: terraform/modules/delivery/providers.tf
# Module: delivery
# Author: Haffey Enterprises LLC
# Created: 2026-07-22
# Revised: 2026-07-22
# Description: Default provider configuration for the delivery module (02 §1).
##############################################################################

provider "google" {
  project = var.project_id
  region  = var.region
}
