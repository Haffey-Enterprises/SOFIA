##############################################################################
# File: terraform/modules/delivery/variables.tf
# Module: delivery
# Author: Haffey Enterprises LLC
# Created: 2026-07-22
# Revised: 2026-07-22
# Description: Inputs to the delivery module. Environment-specific values carry
#   no default (01 §5) — the caller supplies them.
##############################################################################

variable "enable_apis" {
  type        = bool
  description = "Whether this module enables the GCP APIs it depends on."
  default     = true
}

variable "environment" {
  type        = string
  description = "Environment name for this instance (e.g. dev). Forms the name suffix and the environment label."
}

variable "github_repository" {
  type        = string
  description = "The owner/repo permitted to federate into this project, e.g. Haffey-Enterprises/SOFIA. Bound into the OIDC provider's attribute condition, so no other repository can mint credentials against this pool."
}

variable "project_id" {
  type        = string
  description = "GCP project ID this module provisions into."
}

variable "region" {
  type        = string
  description = "GCP region for Artifact Registry, Secret Manager replication, and Cloud Run."
}
