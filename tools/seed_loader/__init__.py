##############################################################################
# Package: seed_loader
# Service: RBT-58 provisioning tooling (bootstrap-era; NOT the gateway)
# Author: Haffey Enterprises LLC
# Created: 2026-07-14
# Description: The .md-source -> graph seed loader + content-addressed manifest
#   for the RBT-58 KG bootstrap (DP-2: bootstrap fixture). Parses the seed .md
#   files (frontmatter + fenced yaml graph payload), loads them into the
#   provisioned Neo4j Enterprise instance via idempotent MERGE, and emits a
#   content-addressed manifest so the seeded state is verifiable substrate.
#
#   BOUNDARY (design-over-code): this is a PROVISIONING-ERA tool that precedes
#   the knowledge-service gateway (ADR-002 §2.5). It is the update pipeline for
#   the bootstrap era; once the gateway exists, .md updates route through the
#   SDD-001 §3.6 `ingest` port. This loader therefore does NOT reimplement the
#   gateway's owned atomic supersession-with-edge-repointing (§6) — it marks
#   predecessor versions superseded and flags rebind:current re-point as
#   gateway-owned. See loader.apply_supersession.
##############################################################################
