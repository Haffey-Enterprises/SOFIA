#!/usr/bin/env bash
##############################################################################
# File: helpers/neo4j-scale.sh
# Author: Thaddeus Haffey — Executive Architect, Haffey Enterprises LLC
# Created: 2026-07-14 / Revised: 2026-07-14
# Description: Manual override for the Neo4j StatefulSet scale (the CronJobs in
#   k8s/neo4j/50-scheduler-cronjobs.yaml do this on a schedule). Scaling to 0
#   deletes the pod only; the regional-SSD PVC (Retain) survives. Operator script
#   (01 §9) — run by a human, not Terraform. Verifies the result on the cluster
#   rather than trusting the exit code (the unforgiving-substrate discipline).
##############################################################################
set -euo pipefail

NAMESPACE="neo4j"
STATEFULSET="neo4j"

usage() {
  cat <<EOF
Usage: $(basename "$0") up|down

  up    Scale the Neo4j StatefulSet to 1 (node pool autoscaler adds a node).
  down  Scale the Neo4j StatefulSet to 0 (node pool autoscaler drains to 0).

Requires: kubectl context pointed at the target cluster.
EOF
}

if [[ $# -ne 1 ]]; then
  usage >&2
  exit 2
fi

case "$1" in
  up)   REPLICAS=1 ;;
  down) REPLICAS=0 ;;
  -h | --help)
    usage
    exit 0
    ;;
  *)
    echo "error: unknown argument '$1'" >&2
    usage >&2
    exit 2
    ;;
esac

echo "Scaling ${STATEFULSET} to ${REPLICAS} replica(s) in namespace ${NAMESPACE}..."
kubectl scale "statefulset/${STATEFULSET}" --namespace="${NAMESPACE}" --replicas="${REPLICAS}"

# Verify what actually landed, don't trust exit 0.
ACTUAL="$(kubectl get "statefulset/${STATEFULSET}" --namespace="${NAMESPACE}" \
  -o jsonpath='{.spec.replicas}')"
if [[ "${ACTUAL}" != "${REPLICAS}" ]]; then
  echo "error: expected spec.replicas=${REPLICAS} but cluster reports ${ACTUAL}" >&2
  exit 1
fi
echo "OK — spec.replicas=${ACTUAL}. (PVC is retained regardless of replica count.)"
