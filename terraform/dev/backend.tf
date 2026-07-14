##############################################################################
# File: terraform/dev/backend.tf
# Config: dev environment root
# Author: Thaddeus Haffey — Executive Architect, Haffey Enterprises LLC
# Created: 2026-07-14
# Revised: 2026-07-14
# Description: Remote, locked GCS backend for dev state (03 §1). The state bucket
#   is provisioned by the foundational layer (its own state / blast radius) with
#   versioning + prevent_destroy, access restricted to the pipeline SA + admins.
#   Fill the bucket name in for your project before `terraform init`.
##############################################################################

terraform {
  backend "gcs" {
    bucket = "sofia-dev-he-tfstate" # foundational state bucket (03 §1)
    prefix = "env/dev/neo4j-graph"
  }
}
