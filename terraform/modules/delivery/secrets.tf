##############################################################################
# File: terraform/modules/delivery/secrets.tf
# Module: delivery
# Author: Haffey Enterprises LLC
# Created: 2026-07-22
# Revised: 2026-07-22
# Description: The Neo4j Aura credential CONTAINER for this environment — the
#   dev graph runs on managed Neo4j Aura (ADR-002 §2.2), so the gateway holds an
#   Aura password rather than a cluster-local one.
#
#   Deliberately container-only: there is no google_secret_manager_secret_version
#   resource here, and there never should be. A version resource would put the
#   credential into Terraform configuration AND into state, where the whole file
#   must then be treated as the secret (03 §4, 02 §7). The value is added
#   out-of-band by the operator, by their own hand, after apply.
##############################################################################

resource "google_secret_manager_secret" "neo4j_aura" {
  project   = var.project_id
  secret_id = "neo4j-aura-${local.name_suffix}"

  labels = merge(local.common_labels, {
    sensitivity = "high"
  })

  replication {
    user_managed {
      replicas {
        location = var.region
      }
    }
  }

  depends_on = [google_project_service.required]
}
