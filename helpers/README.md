# helpers/ — operator scripts + cluster prerequisites

Run by a human, not by Terraform (01 §9).

## Cluster prerequisites (one-time, after `terraform apply`)

The StatefulSet reads `NEO4J_AUTH` from Secret Manager via the **Secrets Store CSI
driver + GCP provider**. Install these before `kubectl apply -f k8s/neo4j/`.

### Zero-egress posture — mirror every image to Artifact Registry FIRST

The `graph-dev` cluster is **private with no Cloud NAT** (a deliberate zero-egress
posture — see `terraform/modules/neo4j_graph/cluster.tf`). Nodes **cannot** pull from
`registry.k8s.io` or Docker Hub (i/o timeout); **Private Google Access reaches Artifact
Registry** (`*.pkg.dev`), so *every* image must be mirrored to AR before it is referenced.
`REPO` below is the module output `artifact_registry_repo`.

Mirror **multi-arch** with `docker buildx imagetools create` (registry-to-registry — a
plain `docker pull`/`push` from an arm64 workstation lands an arm64-only image that the
amd64 nodes reject with `exec format error`):

```bash
REPO=us-central1-docker.pkg.dev/sofia-dev-he/graph-dev
gcloud auth configure-docker us-central1-docker.pkg.dev --quiet

# Neo4j Enterprise (the StatefulSet image)
docker buildx imagetools create --tag $REPO/neo4j:5.26-enterprise neo4j:5.26-enterprise
# CSI driver chart images (v1.6.0)
docker buildx imagetools create --tag $REPO/csi-secrets-store/driver:v1.6.0            registry.k8s.io/csi-secrets-store/driver:v1.6.0
docker buildx imagetools create --tag $REPO/csi-secrets-store/driver-crds:v1.6.0       registry.k8s.io/csi-secrets-store/driver-crds:v1.6.0
docker buildx imagetools create --tag $REPO/sig-storage/csi-node-driver-registrar:v2.16.0 registry.k8s.io/sig-storage/csi-node-driver-registrar:v2.16.0
docker buildx imagetools create --tag $REPO/sig-storage/livenessprobe:v2.18.0          registry.k8s.io/sig-storage/livenessprobe:v2.18.0
# busybox (GCP provider initContainer). The provider's own plugin image lives on
# us-docker.pkg.dev (Google-hosted, PGA-reachable) — no mirror needed.
docker buildx imagetools create --tag $REPO/busybox:latest busybox:latest
```

### Install the driver + provider (AR-pinned)

```bash
REPO=us-central1-docker.pkg.dev/sofia-dev-he/graph-dev
helm repo add secrets-store-csi-driver https://kubernetes-sigs.github.io/secrets-store-csi-driver/charts

# CSI driver — override every chart image repo to the AR mirror
helm install csi-secrets-store secrets-store-csi-driver/secrets-store-csi-driver \
  --namespace kube-system --version 1.6.0 --set syncSecret.enabled=false \
  --set linux.image.repository=$REPO/csi-secrets-store/driver           --set linux.image.tag=v1.6.0 \
  --set linux.crds.image.repository=$REPO/csi-secrets-store/driver-crds --set linux.crds.image.tag=v1.6.0 \
  --set linux.registrarImage.repository=$REPO/sig-storage/csi-node-driver-registrar --set linux.registrarImage.tag=v2.16.0 \
  --set linux.livenessProbeImage.repository=$REPO/sig-storage/livenessprobe          --set linux.livenessProbeImage.tag=v2.18.0

# GCP provider — the AR-pinned copy in this dir (busybox -> AR; and it carries an
# `operator: Exists` toleration so it also runs on the tainted graph node, else the
# Neo4j pod finds no `gcp` provider and the secret mount hangs).
kubectl apply -f helpers/provider-gcp-plugin.ar.yaml
```

> Versions are pinned above (chart 1.6.0; registrar v2.16.0; livenessprobe v2.18.0).
> The durable Terraform version of all this is tracked as RBT-64.

## `neo4j-scale.sh` — manual scale override

```bash
./neo4j-scale.sh down   # scale StatefulSet to 0 (pod removed; PVC retained)
./neo4j-scale.sh up     # scale StatefulSet to 1 (autoscaler adds a node)
```

The scheduled CronJobs (`k8s/neo4j/50-scheduler-cronjobs.yaml`) do this automatically;
this script is for ad-hoc override (e.g., spinning the instance up outside work hours).
