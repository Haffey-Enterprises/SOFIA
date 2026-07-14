##############################################################################
# File: terraform/modules/neo4j_graph/cluster.tf
# Module: neo4j_graph
# Author: Thaddeus Haffey — Executive Architect, Haffey Enterprises LLC
# Created: 2026-07-14
# Revised: 2026-07-14
# Description: The GKE Standard private cluster and its two node pools — a small
#   always-on SYSTEM pool (kube-system + the scale-up/down CronJobs, which must
#   have a node to run on even when the graph is scaled down) and a dedicated
#   GRAPH pool that autoscales 0..1 (the shutdown scheduler's cost lever). GKE
#   Standard (not Autopilot) per ADR-002 §2.2 + infrastructure-code 02 §7 / 04 §4:
#   a self-managed stateful DB needs node-pool + storage-class control.
##############################################################################

resource "google_container_cluster" "primary" {
  name     = "graph-${local.name_suffix}"
  project  = var.project_id
  location = local.cluster_location

  # Run cluster without the default node pool; manage pools explicitly below.
  remove_default_node_pool = true
  initial_node_count       = 1

  release_channel {
    channel = "REGULAR"
  }

  # Workload Identity — keyless pod->GSA auth (02 §4; no k8s Secrets for creds).
  workload_identity_config {
    workload_pool = "${var.project_id}.svc.id.goog"
  }

  # Private cluster (02 §5): private nodes; control plane reachable only from
  # the authorized CIDRs. NOTE: no Cloud NAT is provisioned — a deliberate
  # zero-egress posture. Nodes cannot pull from public registries; every image is
  # mirrored to Artifact Registry (PGA-reachable) instead (helpers/README.md).
  # Revisit at the operational design (RBT-64) if outbound egress is ever needed.
  private_cluster_config {
    enable_private_nodes    = true
    enable_private_endpoint = false
    master_ipv4_cidr_block  = "172.16.0.0/28"
  }

  # Static block (not a dynamic wrapper) so the authorized-networks control is
  # statically visible to config scanners (trivy GCP-0061); functionally identical.
  master_authorized_networks_config {
    dynamic "cidr_blocks" {
      for_each = var.master_authorized_cidrs

      content {
        cidr_block   = cidr_blocks.value.cidr_block
        display_name = cidr_blocks.value.display_name
      }
    }
  }

  # Managed Prometheus on (02 §7).
  monitoring_config {
    managed_prometheus {
      enabled = true
    }
  }

  # DEFERRED — NetworkPolicy (trivy GCP-0056) is intentionally not enabled here.
  # Turning it on now stands up Calico for a consumer that does not yet exist;
  # the graph pool is single-workload and taint-isolated. Add the policy with the
  # knowledge-service gateway build (RBT-15), when there is real bolt (7687)
  # ingress to restrict.

  # prod can't be destroyed out from under us; dev/staging stay disposable (02 §3).
  deletion_protection = var.environment == "prod"

  resource_labels = local.common_labels

  depends_on = [google_project_service.required]
}

# --- System node pool — small, always-on ------------------------------------
# Hosts kube-system and the scale-up/scale-down CronJobs. Must stay up so the
# scale-UP job has somewhere to run when the graph pool is at zero nodes.
resource "google_container_node_pool" "system" {
  name     = "system-${local.name_suffix}"
  project  = var.project_id
  location = local.cluster_location
  cluster  = google_container_cluster.primary.name

  node_count = 1

  node_config {
    machine_type    = var.system_node_machine_type
    service_account = google_service_account.node.email
    oauth_scopes    = ["https://www.googleapis.com/auth/cloud-platform"]

    workload_metadata_config {
      mode = "GKE_METADATA"
    }

    # Disable legacy (v0.1 / v1beta1) metadata endpoints (trivy GCP-0048).
    metadata = {
      disable-legacy-endpoints = "true"
    }

    labels = local.common_labels
  }

  management {
    auto_repair  = true
    auto_upgrade = true
  }
}

# --- Graph node pool — dedicated, autoscales 0..1 ---------------------------
# The Neo4j StatefulSet is the only workload here (taint + toleration). When the
# StatefulSet scales to 0, the autoscaler drains this pool to graph_node_min_count
# (0) — the cost lever. Scale-up re-provisions a node for the pod.
resource "google_container_node_pool" "graph" {
  name     = "graph-${local.name_suffix}"
  project  = var.project_id
  location = local.cluster_location
  cluster  = google_container_cluster.primary.name

  autoscaling {
    min_node_count = var.graph_node_min_count
    max_node_count = var.graph_node_max_count
  }

  node_config {
    machine_type    = var.graph_node_machine_type
    service_account = google_service_account.node.email
    oauth_scopes    = ["https://www.googleapis.com/auth/cloud-platform"]

    workload_metadata_config {
      mode = "GKE_METADATA"
    }

    # Disable legacy (v0.1 / v1beta1) metadata endpoints (trivy GCP-0048).
    metadata = {
      disable-legacy-endpoints = "true"
    }

    # Only the Neo4j StatefulSet tolerates this taint (see k8s/neo4j/30-statefulset.yaml).
    taint {
      key    = "workload"
      value  = "neo4j"
      effect = "NO_SCHEDULE"
    }

    labels = merge(local.common_labels, { workload = "neo4j" })
  }

  management {
    auto_repair  = true
    auto_upgrade = true
  }
}
