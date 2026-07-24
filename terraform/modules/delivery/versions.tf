##############################################################################
# File: terraform/modules/delivery/versions.tf
# Module: delivery
# Author: Haffey Enterprises LLC
# Created: 2026-07-22
# Revised: 2026-07-22
# Description: Version pins for the delivery module (02 §1). No Kubernetes
#   provider: this module provisions a serverless delivery substrate — there is
#   no cluster to talk to.
##############################################################################

terraform {
  required_version = ">= 1.5.0"

  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 6.0"
    }
  }
}
