# RBT-58 EXECUTION — Build · Seed · Test the graph instance (the proof point)

*Paste this as the kickoff for a fresh execution session (Claude Code on your machine, or a
Cowork "on your computer" session with the SOFIA repo + `gcloud`/`kubectl`/`terraform` and
network access to GCP). The cloud sandbox cannot reach GCP/private networks — this leg runs
where the cluster does.*

---

Fresh session — you are executing **RBT-58's BUILD · SEED · TEST leg**: provision the
self-managed Neo4j **Enterprise** instance, apply the DDR-002 §7 constraint set, load the KG
seed, and prove **conformance 1a green against the seeded instance**. This lands the
knowledge-service BUILD-prep threshold and starts the n>0 empirical clock the corpus cites.

**Surface & role — two-surface model.** The design, authoring, and adversarial review are
**done** (claude.ai session, 2026-07-14); the four artifact sets are ratified and
self-verified (1 blocking + 5 material + 4 cosmetic findings all remediated and locally
re-verified). **You execute the provisioning/bootstrap/seed/test mechanics against real GCP +
the cluster. You do NOT redesign the ratified artifacts, and you do NOT commit or merge** —
infra transactions, git commits, and merges are Tad's. If execution reveals a genuine design
defect, **surface it and STOP** — do not silently patch. Report at each gate and STOP.

## Ground before acting (fresh-fetch, in this order — do not trust this prompt's summaries or memory)

1. **Repo canon on `develop`** (Haffey-Enterprises/SOFIA, `d775734`+): ADR-002 §2.2/§2.5/§5.2
   (the self-managed-GKE Enterprise warrant), **DDR-002 v1.3.0 §7** (the DB-enforced set) +
   §2/§6, DDR-004 v1.2.0 §4 (basis coverage), SDD-001 §3.6/§4.6, and `conformance/` (README +
   `schema_constants.py` authority pin `8ec41398…` + `assertions/`). **Verify the pin is still
   current** before relying on the constraint file.
2. **The delivered artifacts** (place at these proposed repo paths; confirm with Tad before
   committing):
   - `deploy/neo4j/schema/01-constraints.cypher` — Batch A (DDR-002 §7 DB-enforced set + indexes)
   - `terraform/` + `k8s/neo4j/` + `helpers/` — Batch B (GKE Standard + StatefulSet + scheduler)
   - `seed/*.md` — Batch C (the `.md` ground-truth source set)
   - `tools/` + `RBT-58-code-execution-prompt.md` — Batch D (loader, manifest, 1a runner; the
     step-by-step mechanics live in that in-repo prompt — this session prompt is the gated frame around it)
3. **Skills as needed:** `infrastructure-code` (1.4.0), `testing`, `code-review`.

## Prerequisites (confirm present before step 1)

- A GCP dev project + the foundational Terraform **state bucket** (versioned, `prevent_destroy`,
  pipeline-SA-scoped). Fill `terraform/dev/backend.tf` + `dev.auto.tfvars` (`project_id`,
  `region`, `zone`, `master_authorized_cidrs`).
- **[L] Enterprise licence** resolved: `NEO4J_ACCEPT_LICENSE_AGREEMENT` = `"eval"` for this dev
  proof point, or a commercial Neo4j licence. (A procurement/legal decision, not a config value.)
- The Secrets Store CSI driver + GCP provider install path (`helpers/README.md`).

## Execution sequence — each step: run, VERIFY on the real system, report, STOP

1. **IaC.** `cd terraform/dev`; `terraform init`; `fmt -check -recursive`; `validate`; `tflint`;
   a security scan (`trivy config`/`checkov`); `terraform plan -out=tfplan`. **STOP — Tad reviews
   the plan and runs `apply`** (never apply from source, 05 §2). Then: add the `NEO4J_AUTH` secret
   version out-of-band (`terraform/modules/neo4j_graph/secrets.tf`); install the CSI driver;
   mirror the pinned `neo4j:5.26-enterprise` image into Artifact Registry; set the image path +
   `neo4j_gsa_email` annotation in the manifests.
2. **Workload.** Resolve **[S] the secret-file wiring** first — `NEO4J_AUTH_FILE` assumes the
   image reads the auth string from a file; **verify against the pinned image's docs**; if
   unsupported, use an entrypoint that exports `NEO4J_AUTH="$(cat /etc/neo4j-secrets/neo4j-auth)"`.
   `kubectl apply -f k8s/neo4j/`. Confirm the StatefulSet pod is Ready and bolt (7687) reachable. STOP.
3. **Schema bootstrap.** Apply `01-constraints.cypher` (`cypher-shell -f`). **VERIFY:**
   `SHOW CONSTRAINTS` = **106** (27 PK-uniqueness + 9 `(business_key,version)` + 24
   provenance-existence + 46 T1-existence); `SHOW INDEXES` = **27**. The node property-existence
   constraints being present is the runtime proof the instance is **Enterprise** (ADR-002 §2.2). STOP.
4. **Off-books scrub.** Ephemeral scan of `seed/` for the operator's denylisted proper noun (the
   term is on your profile denylist — never write it into a file, this prompt, or a commit). Rewrite
   any hit to "Haffey Enterprises."
5. **Seed load + manifest.** Make the `conformance` package importable; run `tools` unit tests
   (6/6 pass); set `NEO4J_URI/USER/PASSWORD` from Secret Manager (env, never a flag);
   `python -m seed_loader.cli load --seed-dir seed --manifest seed/manifest.json --now <ISO>`. The
   DB constraints reject a malformed node at write — a load failure here is a real conformance
   signal. Record the manifest digest. STOP.
6. **Acceptance — conformance 1a.** Make `conformance` importable (a SEPARATE install from `tools`);
   `python run_conformance_1a.py` (env → the seeded instance). The runner **fails loud** (exit 2) on
   a skipped module or zero assertions — a swallowed import cannot read as green. **Confirm the
   introspected assertion set against `conformance/assertions/` on disk.** RESULT must be **GREEN**
   (zero violations). 1b gateway contracts stay `xfail` (RBT-15's flip, not here). STOP.

## Acceptance gate (RBT-58 closure — all four)

- Instance up (StatefulSet Ready, bolt reachable).
- DDR-002 §7 DB-enforced set applied **and verified** (106 constraints match §7; existence
  constraints present ⇒ Enterprise confirmed).
- Seed loaded; content-addressed manifest written; digest recorded.
- Conformance 1a **GREEN** against the seeded instance.

## Closure (Tad's, after the gate)

- **Earned tense:** provisioned, populated, DB-enforced set verified, 1a green — **the DDR-004
  n>0 empirical clock is NOT started** (seed data is fixture ground truth, not capture traffic;
  out of scope per the ticket, DDR-004 calibration territory if it ever matters).
- **Three-layer capture on RBT-58** (comment + description prefix + workflow state → Done);
  the git commit + merge are Tad's.
- **Open follow-ups already ticketed:** RBT-63 (ADR-002 managed-Aura-on-GCP re-eval), RBT-62
  (DDR-002 §2.6 `confidence_basis` illustration fix).

## Disciplines that bite here

Design over code; fresh-fetch over recall; report-and-STOP at every gate; do not redesign the
ratified artifacts — a design defect found in execution is surfaced and STOPPED on, never
silently patched. Infra transactions and merges are Tad's.
