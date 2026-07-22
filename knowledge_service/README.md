# knowledge-service

The KG/RG graph gateway: the sole holder of the Neo4j driver and the single
graph-access boundary on the platform (ADR-002 §2.5, SDD-001). Every Knowledge
Graph, Reasoning Graph, and Artifact-family read and write flows through its
API. Its distinguishing commitment is that the API is *operation-shaped, not
graph-shaped* — each write endpoint is one schema-defined transactional shape
whose invariants are native to the operation, so the schema's safety-critical
integrity properties hold by construction rather than by policing. The gateway
executes every authoritative write and authors none.

**Design authority:** [SDD-001](../docs/sdd/SDD-001-knowledge-service.md)
(v1.6.0, ACCEPTED). Read it before changing anything here — the module tree,
port seams, and testing posture below are its §4.1, §4.2, and §6.

## Data classification

**Tier 2 — Internal.** The gateway handles architecture and reasoning
metadata: graph node/edge content, provenance stamps, decision records, and
operational events. **No PHI, by design** — the platform enforces
data-classification at intake/ingestion (CLAUDE.md operating constraints), and
this service's ingestion boundary is one of the enforcement points (SDD-001
§1). Tier 3/4 data is out of scope for the initial build; a PHI scope change is
its own ADR, not a code change.

Neo4j credentials are Tier 4 and arrive from GCP Secret Manager as environment
variables under Workload Identity Federation (SDD-001 §4.6). They never appear
in source, logs, error messages, or API responses. The log-channel ceiling is
Tier 2.

## Current scope

This service is at the scaffold stage (RBT-77). What exists today:

- `GET /healthz` — liveness only, no I/O.
- `GET /readyz` — readiness, `200` ready / `503` not ready.
- `GraphStoragePort` + the Neo4j adapter's driver lifecycle, and the in-memory
  double the tests run against.

The graph operations themselves (§3.3–§3.6 of SDD-001 — retrieval, capture,
promotion, ingestion) are not implemented yet; their packages exist as empty
homes so later stories land in the tree the SDD fixes rather than inventing one.

### Readiness checks — staged

SDD-001 §3.1 fixes two ordered readiness checks, both critical:

1. **Neo4j connectivity and authentication** — implemented.
2. **Schema-metadata loaded** — the `PlaneDefinition` registry and validation
   metadata the write paths enforce against. **Lands with RBT-78's
   `schema_metadata.py`.** It is staged by ruling, not omitted by accident: the
   gateway must not execute writes it cannot validate, and there is nothing to
   validate against until the registry exists. `/readyz` names it in a code
   comment and does not fake it — until RBT-78, a `200` from `/readyz` attests
   check 1 only.

## Local quickstart

Requires Python 3.11+.

```bash
cd knowledge_service
python3.11 -m venv .venv
./.venv/bin/pip install --require-hashes -r requirements-dev.txt
cp .env.example .env          # .env is git-ignored; fill in local values
```

Run the gates — all four must pass before a change is proposed:

```bash
./.venv/bin/ruff check . && ./.venv/bin/ruff format --check . && ./.venv/bin/mypy && ./.venv/bin/pytest
```

Run the service locally:

```bash
./.venv/bin/uvicorn app.main:app --reload --port 8080
```

No live Neo4j is needed for the test suite: every test runs against the
in-memory double (SDD-001 §6). Running the service itself does need a reachable
Neo4j for `/readyz` to report ready — `/healthz` answers regardless.

## Dependencies

Floors live in `requirements.in` / `requirements-dev.in`; the committed
`requirements*.txt` are hash-pinned output of
`pip-compile --generate-hashes`. Never hand-edit a lockfile and never
`pip freeze` one — production installs run `pip install --require-hashes`, and
an unhashed pin defeats it.
