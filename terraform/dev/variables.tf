##############################################################################
# File: terraform/dev/variables.tf
# Config: dev environment root
# Author: Thaddeus Haffey — Executive Architect, Haffey Enterprises LLC
# Created: 2026-07-14
# Revised: 2026-07-14
# Description: Env-specific inputs for the dev root — no defaults; supplied via
#   dev.auto.tfvars (01 §5, 03 §3).
##############################################################################

variable "project_id" {
  type        = string
  description = "GCP project ID for the dev environment."
}

variable "region" {
  type        = string
  description = "GCP region for the dev environment (Artifact Registry, Secret Manager)."
}

variable "zone" {
  type        = string
  description = "GCP zone for the dev (zonal) cluster + zonal PD."
}

variable "master_authorized_cidrs" {
  type        = list(object({ cidr_block = string, display_name = string }))
  description = "CIDRs permitted to reach the dev cluster control plane."
}
