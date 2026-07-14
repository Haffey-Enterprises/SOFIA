# helpers/ — operator scripts + cluster prerequisites

Run by a human, not by Terraform (01 §9).

## Cluster prerequisites (one-time, after `terraform apply`)

The StatefulSet reads `NEO4J_AUTH` from Secret Manager via the **Secrets Store CSI
driver + GCP provider** — install these before `kubectl apply -f k8s/neo4j/`:

```bash
# Secrets Store CSI driver
helm repo add secrets-store-csi-driver https://kubernetes-sigs.github.io/secrets-store-csi-driver/charts
helm install csi-secrets-store secrets-store-csi-driver/secrets-store-csi-driver \
  --namespace kube-system --set syncSecret.enabled=false

# GCP provider for the driver
kubectl apply -f https://raw.githubusercontent.com/GoogleCloudPlatform/secrets-store-csi-driver-provider-gcp/main/deploy/provider-gcp-plugin.yaml
```

> Pin both to specific chart/manifest versions for a real environment — the URLs above
> are the install entry points, not version pins.

## `neo4j-scale.sh` — manual scale override

```bash
./neo4j-scale.sh down   # scale StatefulSet to 0 (pod removed; PVC retained)
./neo4j-scale.sh up     # scale StatefulSet to 1 (autoscaler adds a node)
```

The scheduled CronJobs (`k8s/neo4j/50-scheduler-cronjobs.yaml`) do this automatically;
this script is for ad-hoc override (e.g., spinning the instance up outside work hours).
