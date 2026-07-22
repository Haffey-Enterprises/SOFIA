##############################################################################
# File: terraform/dev/variables.tf
# Config: dev environment root
# Author: Thaddeus Haffey — Executive Architect, Haffey Enterprises LLC
# Created: 2026-07-14
# Revised: 2026-07-22
# Description: Env-specific inputs for the dev root — no defaults; supplied via
#   dev.auto.tfvars (01 §5, 03 §3). The cluster-era inputs (zone,
#   master_authorized_cidrs) were dropped at RBT-77 with the graph module: a
#   serverless delivery substrate is regional and has no control plane to
#   authorize CIDRs against.
##############################################################################

variable "github_repository" {
  type        = string
  description = "The owner/repo permitted to federate into this project via Workload Identity Federation."
}

variable "project_id" {
  type        = string
  description = "GCP project ID for the dev environment."
}

variable "region" {
  type        = string
  description = "GCP region for the dev environment (Artifact Registry, Secret Manager, Cloud Run)."
}
