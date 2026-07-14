##############################################################################
# Module: tests/test_manifest.py
# Author: Haffey Enterprises LLC
# Created: 2026-07-14 / Revised: 2026-07-14
# Description: Unit tests for the content-addressed manifest — build, verify
#   round-trip, and drift detection (pure, no Neo4j).
##############################################################################

from pathlib import Path

from seed_loader.manifest import build_manifest, verify_manifest, write_manifest

_DOC = """---
doctype: kg-seed
plane: Catalog
load_order: 10
authority: DDR-002 v1.3.0
---

# Catalog

## Graph payload

```yaml
nodes:
  - labels: [Catalog, Pattern]
    properties: { pattern_id: PAT-001, version: "1.0.0" }
edges: []
```
"""


def _seed_dir(tmp_path: Path) -> Path:
    seed = tmp_path / "seed"
    seed.mkdir()
    (seed / "10-catalog.md").write_text(_DOC, encoding="utf-8")
    return seed


def test_build_and_verify_roundtrip(tmp_path: Path):
    seed = _seed_dir(tmp_path)
    manifest_path = tmp_path / "manifest.json"
    manifest = write_manifest(seed, manifest_path)

    assert manifest["files"][0]["node_count"] == 1
    assert manifest["files"][0]["path"] == "10-catalog.md"
    assert verify_manifest(seed, manifest_path) == []


def test_drift_detected(tmp_path: Path):
    seed = _seed_dir(tmp_path)
    manifest_path = tmp_path / "manifest.json"
    write_manifest(seed, manifest_path)

    # Mutate the payload after pinning — verify must flag it.
    (seed / "10-catalog.md").write_text(_DOC.replace("PAT-001", "PAT-999"), encoding="utf-8")
    problems = verify_manifest(seed, manifest_path)
    assert problems
    assert any("hash drift" in p or "digest mismatch" in p for p in problems)


def test_payload_hash_ignores_prose_edits(tmp_path: Path):
    seed = _seed_dir(tmp_path)
    baseline = build_manifest(seed)

    # Editing only the prose (not the yaml payload) must not move payload_sha256.
    (seed / "10-catalog.md").write_text(
        _DOC.replace("# Catalog", "# Catalog (Haffey Enterprises)"), encoding="utf-8"
    )
    after = build_manifest(seed)
    assert baseline["files"][0]["payload_sha256"] == after["files"][0]["payload_sha256"]
    # ...but the source hash DID move (drift is still visible at the source layer).
    assert baseline["files"][0]["source_sha256"] != after["files"][0]["source_sha256"]
