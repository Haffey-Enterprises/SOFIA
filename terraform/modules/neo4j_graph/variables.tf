##############################################################################
# File: terraform/modules/neo4j_graph/variables.tf
# Module: neo4j_graph
# Author: Thaddeus Haffey — Executive Architect, Haffey Enterprises LLC
# Created: 2026-07-14
# Revised: 2026-07-14
# Description: Inputs for the neo4j_graph module. Environment-specific values
#   (project_id, region, environment, authorized networks) carry NO default —
#   the caller supplies them (01 §5). Environment-independent sizing gets
#   sensible defaults tuned for the RBT-58 dev threshold instance.
##############################################################################

variable "project_id" {
  type        = string
  description = "GCP project ID this module provisions into. Environment-specific, no default."
}

variable "region" {
  type        = string
  description = "GCP region (regional resources: Artifact Registry, Secret Manager, and a prod regional cluster). Environment-specific, no default."
}

variable "zone" {
  type        = string
  description = "GCP zone for the non-prod (zonal) cluster + zonal PD. In GKE, node-pool counts are per-zone, so a zonal cluster keeps the dev threshold at a true single node. Environment-specific, no default."
}

variable "environment" {
  type        = string
  description = "Environment name (e.g. dev, staging, prod). Drives naming, labels, and hardening conditionals."

  validation {
    condition     = contains(["dev", "staging", "prod"], var.environment)
    error_message = "environment must be one of: dev, staging, prod."
  }
}

variable "master_authorized_cidrs" {
  type        = list(object({ cidr_block = string, display_name = string }))
  description = "CIDRs permitted to reach the private GKE control plane. Environment-specific, no default."
}

variable "enable_apis" {
  type        = bool
  description = "Whether this module enables the required GCP APIs (01 §8; set false if enabled elsewhere)."
  default     = true
}

variable "system_node_machine_type" {
  type        = string
  description = "Machine type for the always-on system node pool (hosts kube-system + the scheduler CronJobs)."
  default     = "e2-small"
}

variable "graph_node_machine_type" {
  type        = string
  description = "Machine type for the dedicated Neo4j node pool. Sized for the graph workload."
  default     = "e2-standard-4"
}

variable "graph_node_min_count" {
  type        = number
  description = "Min nodes in the graph pool. 0 lets the shutdown scheduler drain it to zero when the StatefulSet scales to 0 (the cost lever)."
  default     = 0
}

variable "graph_node_max_count" {
  type        = number
  description = "Max nodes in the graph pool. 1 for the single-node dev threshold instance; topology deferred per ADR-002 §5.2."
  default     = 1
}

variable "data_disk_size_gb" {
  type        = number
  description = "Per-replica SSD data disk size in GiB for the Neo4j PVC (zonal PD at the dev threshold)."
  default     = 32
}
