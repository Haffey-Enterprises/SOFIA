##############################################################################
# File: terraform/dev/backend.tf
# Config: dev environment root
# Author: Thaddeus Haffey — Executive Architect, Haffey Enterprises LLC
# Created: 2026-07-14
# Revised: 2026-07-22
# Description: Remote, locked GCS backend for dev state (03 §1). The state bucket
#   is provisioned by the foundational layer (its own state / blast radius) with
#   versioning + prevent_destroy, access restricted to the pipeline SA + admins.
#   The prefix moved from env/dev/neo4j-graph to env/dev/delivery at RBT-77: the
#   graph module was removed and this root now carries a different blast radius,
#   so it gets its own state object rather than inheriting the retired one.
##############################################################################

terraform {
  backend "gcs" {
    bucket = "sofia-dev-he-tfstate" # foundational state bucket (03 §1)
    prefix = "env/dev/delivery"
  }
}
