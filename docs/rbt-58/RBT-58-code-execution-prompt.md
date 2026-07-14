# File: docs/rbt-58/RBT-58-code-execution-prompt.md
# Author: Thaddeus Haffey — Executive Architect, Haffey Enterprises LLC
# Created: 2026-07-14
# Description: RBT-58 in-repo Code execution prompt (provision/bootstrap/seed/test steps).

# RBT-58 — Claude Code execution prompt (BUILD-prep: provision + bootstrap + seed)

**Surface roles.** This prompt is authored on the design surface (claude.ai). **You are
Claude Code — you execute the provisioning/bootstrap/seed/load mechanics. You do NOT
commit or merge; Tad reviews against ground truth and commits.** Report and STOP at each
gate.

## Fresh-fetch guard (do this first, every run — do not trust memory or this prompt's summaries)

Re-read from disk on `develop` (Haffey-Enterprises/SOFIA, HEAD `d775734` or later) and
treat these as the authorities; if this prompt disagrees with them, the canon wins:

- `CLAUDE.md` (repo doctrine) · `docs/adr/ADR-002-graph-system-of-record.md` §2.2/§2.5/§2.6
- `docs/ddr/DDR-002-graph-schema.md` §2, §6, **§7** (the DB-enforced set) · `docs/ddr/DDR-004-*` §4
- `docs/sdd/SDD-001-knowledge-service.md` §3.6/§4.6 · `conformance/` (README + `schema_constants.py` pin + `assertions/`)
- Verify each delivered artifact's stated authority pin (`schema_constants.py` sha256
  `8ec41398…`) is still current before use. Re-fetch, don't recall.

## The three artifact sets (delivered from the design surface)

Place them in the repo (proposed locations — confirm with Tad):

- **Batch A** → `deploy/neo4j/schema/01-constraints.cypher` (DDR-002 §7 DB-enforced set + lean indexes)
- **Batch B** → `terraform/` + `k8s/neo4j/` + `helpers/` (GKE Standard + StatefulSet + scheduler)
- **Batch C** → `seed/*.md` (the `.md` ground-truth source set)
- **Batch D** → `tools/seed_loader/`, `tools/run_conformance_1a.py`, `tools/tests/` (this package)

## Execution sequence (each step: run, verify on the real system, report, STOP)

1. **IaC.** `cd terraform/dev`; `terraform init`; `terraform fmt -check -recursive`;
   `terraform validate`; `tflint`; a security scan (`trivy config` / `checkov`);
   `terraform plan -out=tfplan`. **STOP — Tad reviews the plan and runs `apply` (05 §2:
   never apply from source).** Then: add the `NEO4J_AUTH` secret version out-of-band
   (see `terraform/modules/neo4j_graph/secrets.tf`); install the Secrets Store CSI driver
   + GCP provider (`helpers/README.md`); mirror the pinned `neo4j:5.26-enterprise` image
   into Artifact Registry; fill the image path + `neo4j_gsa_email` annotation in the manifests.
2. **Workload.** `kubectl apply -f k8s/neo4j/` (filename order). Confirm the StatefulSet
   pod is Ready and bolt (7687) is reachable. Resolve the two in-file flags first:
   **[L]** Enterprise licence acceptance and **[S]** the `NEO4J_AUTH_FILE` vs entrypoint
   secret wiring — verify [S] against the pinned image's docs; do NOT assume the `_FILE`
   convention.
3. **Schema bootstrap.** Apply `deploy/neo4j/schema/01-constraints.cypher`
   (`cypher-shell -f ...`). **Verify:** `SHOW CONSTRAINTS` / `SHOW INDEXES`; the node
   property-existence constraints must be present — their presence is the runtime proof
   the instance is Enterprise (ADR-002 §2.2). Report the counts against the file's
   Section-6 expectations. STOP.
4. **Off-books scrub (pre-load).** Run an ephemeral scan of `seed/` for the operator's
   denylisted proper noun — the term comes from Tad's out-of-band denylist / profile and
   is NEVER written into a committed file, this prompt, or the loader. If found, rewrite
   to "Haffey Enterprises" before loading. (There is deliberately no in-repo scrub control
   — a committed check would itself commit the term.)
5. **Seed load + manifest.** `cd tools`; `pip install -e .` (or `-r requirements.txt`);
   `PYTHONPATH=. python -m pytest tests -q` (parser/manifest unit tests pass);
   set `NEO4J_URI/NEO4J_USER/NEO4J_PASSWORD` from Secret Manager (env, never a flag);
   `python -m seed_loader.cli load --seed-dir ../seed --manifest ../seed/manifest.json --now <ISO>`.
   The DB-enforced constraints reject any malformed node at write — a load failure here is
   a real conformance signal, not a nuisance. Record the manifest digest. STOP.
6. **Acceptance — conformance 1a.** First make the `conformance` package importable —
   it is a SEPARATE install from `tools` (`pip install -e .` at the repo root / conformance
   package, or `PYTHONPATH=<repo-root>`). Then `python run_conformance_1a.py` (env pointed
   at the seeded instance). The runner now **fails loud** (exit 2, RESULT: NOT GREEN) if any
   assertion module fails to import or if zero assertions run — so a swallowed import can no
   longer read as green; if you see that, fix the import path, do not proceed.
   **Confirm the introspected assertion set against `conformance/assertions/` on disk**
   (fresh-fetch — don't trust the runner's module list from memory). RESULT must be
   **GREEN** (zero violations). 1b contracts stay xfail (RBT-15's flip, not here). STOP.

## Acceptance gate (RBT-58 closure — all four, then hand back to Tad)

- Instance up (StatefulSet Ready, bolt reachable).
- DDR-002 §7 DB-enforced set applied **and verified** (`SHOW CONSTRAINTS` matches §7;
  existence constraints present ⇒ Enterprise confirmed).
- Seed loaded; content-addressed manifest written; digest recorded.
- Conformance 1a **GREEN** against the seeded instance.

Write the seeded state in **earned tense**: provisioned and populated, DB-enforced set
verified, 1a green — **the DDR-004 n>0 empirical clock is NOT started** (seed data is
fixture ground truth, not capture traffic; out of scope per the ticket, DDR-004
calibration territory if it ever matters).

**Do not commit or merge.** Produce a report of what ran, the verification outputs, and
any deviations; Tad reviews against ground truth and owns the git transaction.
