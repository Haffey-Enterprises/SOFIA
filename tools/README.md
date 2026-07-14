# RBT-58 — seed loader + conformance runner (Batch D)

The executable glue that turns the Batch-C `.md` source set into a verified, seeded
Neo4j Enterprise instance, and the Code execution prompt that drives the whole RBT-58
build on Tad's side.

## Contents

```
tools/
  seed_loader/
    parser.py     # .md (frontmatter + fenced yaml payload) -> SeedDoc
    schema.py     # label->PK map + versioned-ground-truth set (DDR-002 §2/§6)
    loader.py     # MERGE nodes/edges; dict-props -> JSON strings; §6 supersession-marking
    manifest.py   # content-addressed manifest (build / write / verify)
    cli.py        # `seed-loader load|manifest|verify`
  run_conformance_1a.py   # run 1a graph-state assertions vs the SEEDED instance
  tests/          # parser + manifest unit tests (pure; run in CI + pre-load)
RBT-58-code-execution-prompt.md   # the two-surface hand-off to Claude Code
```

## The design-over-code boundary (read this)

This loader is a **provisioning-era** tool that **precedes** the knowledge-service
gateway (ADR-002 §2.5). It is the bootstrap update pipeline (Tad's `.md`→load model);
once the gateway exists, `.md` updates route through the SDD-001 §3.6 `ingest` port. The
loader therefore **marks** predecessor versions superseded (§6) but does **not**
reimplement the gateway's owned atomic supersession-with-edge-repointing — that is
flagged, not duplicated. A direct-Cypher bootstrap load is a one-time provisioning act,
not a second runtime driver; it does not breach the sole-owner invariant, which governs
running-system access.

## Usage

```bash
cd tools && pip install -e . && pip install -r requirements.txt
PYTHONPATH=. python -m pytest tests -q                       # parser/manifest unit tests

# after constraints (Batch A) are applied to the instance:
export NEO4J_URI=... NEO4J_USER=... NEO4J_PASSWORD=...        # from Secret Manager, never a flag
python -m seed_loader.cli load --seed-dir ../seed --manifest ../seed/manifest.json --now 2026-07-14T00:00:00Z
python run_conformance_1a.py                                  # acceptance: must be GREEN
```

## Verified on the design surface

Parser + manifest unit tests pass (6/6); the Batch-C seed parses to 24 nodes / 25 edges,
every node resolves a PK, dict-properties serialize to JSON strings, and the cost
`PlaneDefinition`'s `confidence_basis`/`property_schema` key-sets are equal (§7 #26). The
live Neo4j load + 1a run execute on Tad's side against the provisioned instance.
