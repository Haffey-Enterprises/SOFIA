##############################################################################
# Module: seed_loader/manifest.py
# Author: Haffey Enterprises LLC
# Created: 2026-07-14 / Revised: 2026-07-14
# Description: Content-addressed manifest for the seed set — the same discipline
#   the run substrates and conformance/schema_constants.py authority-pin use, so
#   the seeded state is verifiable substrate. Per file: sha256 of the source
#   bytes AND of the canonicalised graph payload; a top-level digest over the
#   sorted per-file hashes; the DDR-002 authority pin the payload conforms to.
#   Pure functions, no Neo4j; unit-tested.
##############################################################################

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from seed_loader.parser import SeedDoc, load_seed_dir


def _sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _canonical_payload(doc: SeedDoc) -> bytes:
    """Deterministic bytes for the graph payload — sorted keys, stable separators,
    so the payload hash is stable across formatting-only edits to the prose."""
    payload = {"nodes": doc.nodes, "edges": doc.edges}
    return json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")


def _labels_in(doc: SeedDoc) -> list[str]:
    seen: set[str] = set()
    for node in doc.nodes:
        seen.update(node.get("labels", []))
    return sorted(seen)


def build_manifest(seed_dir: Path) -> dict[str, Any]:
    """Build the content-addressed manifest for a seed directory."""
    docs = load_seed_dir(seed_dir)
    authority = docs[0].frontmatter.get("authority") if docs else None

    files: list[dict[str, Any]] = []
    for doc in docs:
        files.append(
            {
                "path": doc.path.name,
                "load_order": doc.load_order,
                "plane": doc.frontmatter.get("plane"),
                "source_sha256": _sha256_bytes(doc.path.read_bytes()),
                "payload_sha256": _sha256_bytes(_canonical_payload(doc)),
                "node_count": len(doc.nodes),
                "edge_count": len(doc.edges),
                "labels": _labels_in(doc),
            }
        )

    digest_material = "".join(
        f"{f['path']}:{f['source_sha256']}:{f['payload_sha256']}" for f in files
    ).encode("utf-8")

    return {
        "schema": "rbt-58-seed-manifest/v1",
        "authority": authority,
        "files": files,
        "manifest_digest": _sha256_bytes(digest_material),
    }


def write_manifest(seed_dir: Path, out_path: Path) -> dict[str, Any]:
    manifest = build_manifest(seed_dir)
    out_path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return manifest


def verify_manifest(seed_dir: Path, manifest_path: Path) -> list[str]:
    """Re-hash the seed dir and compare to a stored manifest. Returns a list of
    human-readable discrepancies (empty == verified in sync)."""
    stored = json.loads(manifest_path.read_text(encoding="utf-8"))
    current = build_manifest(seed_dir)
    problems: list[str] = []

    if stored.get("manifest_digest") != current["manifest_digest"]:
        problems.append(
            f"manifest_digest mismatch: stored {stored.get('manifest_digest')} "
            f"!= current {current['manifest_digest']}"
        )

    stored_by_path = {f["path"]: f for f in stored.get("files", [])}
    current_by_path = {f["path"]: f for f in current["files"]}
    for path in sorted(set(stored_by_path) | set(current_by_path)):
        s = stored_by_path.get(path)
        c = current_by_path.get(path)
        if s is None:
            problems.append(f"{path}: present now, absent in stored manifest")
        elif c is None:
            problems.append(f"{path}: in stored manifest, absent now")
        elif s["source_sha256"] != c["source_sha256"]:
            problems.append(f"{path}: source hash drift")
        elif s["payload_sha256"] != c["payload_sha256"]:
            problems.append(f"{path}: payload hash drift")

    return problems
