##############################################################################
# Module: seed_loader/parser.py
# Author: Haffey Enterprises LLC
# Created: 2026-07-14 / Revised: 2026-07-14
# Description: Parse a seed .md source file into a SeedDoc — YAML frontmatter +
#   the single fenced ```yaml graph payload (nodes + edges). Pure functions, no
#   Neo4j; unit-tested in tools/tests/test_parser.py.
##############################################################################

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml

_FRONTMATTER = re.compile(r"^---\n(.*?)\n---\n", re.DOTALL)
# The first fenced ```yaml ... ``` block (the graph payload contract).
_YAML_BLOCK = re.compile(r"```yaml\n(.*?)\n```", re.DOTALL)


@dataclass(frozen=True)
class SeedDoc:
    """One parsed seed .md file."""

    path: Path
    frontmatter: dict[str, Any]
    nodes: list[dict[str, Any]] = field(default_factory=list)
    edges: list[dict[str, Any]] = field(default_factory=list)

    @property
    def load_order(self) -> int:
        return int(self.frontmatter.get("load_order", 0))


def parse_text(text: str, path: Path) -> SeedDoc:
    """Parse seed-.md text into a SeedDoc. Raises ValueError on a malformed file
    (missing frontmatter or missing/!dict payload) — never silently degrades."""
    fm_match = _FRONTMATTER.match(text)
    if fm_match is None:
        raise ValueError(f"{path}: missing YAML frontmatter")
    frontmatter = yaml.safe_load(fm_match.group(1)) or {}

    block = _YAML_BLOCK.search(text)
    if block is None:
        raise ValueError(f"{path}: missing fenced ```yaml graph payload")
    payload = yaml.safe_load(block.group(1)) or {}
    if not isinstance(payload, dict):
        raise ValueError(f"{path}: graph payload is not a mapping")

    return SeedDoc(
        path=path,
        frontmatter=frontmatter,
        nodes=list(payload.get("nodes", [])),
        edges=list(payload.get("edges", [])),
    )


def parse_file(path: Path) -> SeedDoc:
    return parse_text(path.read_text(encoding="utf-8"), path)


def load_seed_dir(seed_dir: Path) -> list[SeedDoc]:
    """Parse every seed/*.md, ordered by load_order (Catalog first). The filename
    prefix and the frontmatter load_order must agree; load_order is authoritative."""
    # Scopes to the numbered seed-data files; non-numbered .md (README/notes) is
    # documentation, not seed data. A malformed NUMBERED file still fails loud
    # (discipline preserved for actual seed files).
    docs = [parse_file(p) for p in sorted(seed_dir.glob("[0-9]*.md"))]
    return sorted(docs, key=lambda d: d.load_order)
