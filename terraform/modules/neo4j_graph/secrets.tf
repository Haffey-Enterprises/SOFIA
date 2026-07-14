##############################################################################
# File: terraform/modules/neo4j_graph/secrets.tf
# Module: neo4j_graph
# Author: Thaddeus Haffey — Executive Architect, Haffey Enterprises LLC
# Created: 2026-07-14
# Revised: 2026-07-14
# Description: The NEO4J_AUTH secret CONTAINER only. The secret VALUE (the
#   'neo4j/<password>' auth string) is added OUT-OF-BAND (gcloud / console) so
#   the credential never materializes in Terraform state (03 §4 — state is
#   plaintext). user_managed replication pinned to the region; sensitivity label.
##############################################################################

resource "google_secret_manager_secret" "neo4j_auth" {
  project   = var.project_id
  secret_id = "neo4j-auth-${local.name_suffix}"

  labels = merge(local.common_labels, { sensitivity = "high" })

  replication {
    user_managed {
      replicas {
        location = var.region
      }
    }
  }
}

# NOTE (out-of-band, do NOT add a google_secret_manager_secret_version here):
#   printf 'neo4j/%s' "$STRONG_PASSWORD" | \
#     gcloud secrets versions add neo4j-auth-<env> --data-file=- --project <project>
#   Keeping the version out of Terraform keeps the credential out of state.
