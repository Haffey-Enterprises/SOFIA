##############################################################################
# Module: tests/test_parser.py
# Author: Haffey Enterprises LLC
# Created: 2026-07-14 / Revised: 2026-07-14
# Description: Unit tests for the seed .md parser (pure, no Neo4j).
##############################################################################

from pathlib import Path

import pytest

from seed_loader.parser import load_seed_dir, parse_text

_SAMPLE = """---
doctype: kg-seed
plane: Catalog
load_order: 10
authority: DDR-002 v1.3.0
---

# Catalog

Some prose.

## Graph payload

```yaml
nodes:
  - labels: [Catalog, Pattern]
    properties:
      pattern_id: PAT-001
      version: "1.0.0"
edges:
  - type: REQUIRES_CAPABILITY
    from: { pattern_id: PAT-001 }
    to: { capability_id: CAP-001 }
    properties: { required: true }
```
"""


def test_parses_frontmatter_nodes_edges():
    doc = parse_text(_SAMPLE, Path("10-catalog.md"))
    assert doc.frontmatter["plane"] == "Catalog"
    assert doc.load_order == 10
    assert len(doc.nodes) == 1
    assert doc.nodes[0]["properties"]["pattern_id"] == "PAT-001"
    assert doc.edges[0]["type"] == "REQUIRES_CAPABILITY"
    assert doc.edges[0]["from"] == {"pattern_id": "PAT-001"}


def test_missing_frontmatter_raises():
    with pytest.raises(ValueError):
        parse_text("# no frontmatter\n", Path("bad.md"))


def test_missing_payload_raises():
    text = "---\nplane: Catalog\n---\n\n# no payload block\n"
    with pytest.raises(ValueError):
        parse_text(text, Path("bad.md"))


def test_load_seed_dir_ignores_non_numbered_readme(tmp_path):
    """A README.md (no frontmatter) in the seed dir is documentation, not seed
    data — load_seed_dir scopes to numbered files and must not parse it."""
    (tmp_path / "10-catalog.md").write_text(_SAMPLE, encoding="utf-8")
    (tmp_path / "README.md").write_text(
        "# RBT-58 — KG seed dataset\n\nNo frontmatter here.\n", encoding="utf-8"
    )
    docs = load_seed_dir(tmp_path)  # must not raise on README.md
    assert [d.load_order for d in docs] == [10]
    assert all("README" not in str(d.path) for d in docs)
