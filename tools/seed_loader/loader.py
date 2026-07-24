##############################################################################
# Module: seed_loader/loader.py
# Author: Haffey Enterprises LLC
# Created: 2026-07-14 / Revised: 2026-07-14
# Description: Load parsed SeedDocs into Neo4j via idempotent MERGE. Nodes MERGE
#   on their PK with the full label set; dict-valued properties are serialized to
#   JSON strings on write (DDR-002 §2.6 declarations-not-edges — confidence_basis
#   / property_schema / source_record_ref / rates; Neo4j properties cannot nest).
#   Edges MERGE by matching endpoints on their PK.
#
#   The DB-enforced constraints (deploy/neo4j/schema/01-constraints.cypher) MUST
#   be applied BEFORE this loader runs — they are what reject a malformed seed
#   node at write. This loader assumes they are in place.
#
#   Supersession (§6): apply_supersession marks a prior active version superseded
#   when a new version of the same business_key arrives (the bootstrap-era update
#   path — Tad's #1). It does NOT re-point rebind:current edges — that atomic
#   mechanic is the knowledge-service gateway's owned responsibility (§6; ADR-002
#   §2.5) and is flagged, not reimplemented here. On the initial seed load nothing
#   pre-exists, so only the create path runs.
##############################################################################

from __future__ import annotations

import json
from typing import Any

from neo4j import Driver, ManagedTransaction

from seed_loader.parser import SeedDoc
from seed_loader.schema import VERSIONED_GROUND_TRUTH, pk_for


def _serialize(value: Any) -> Any:
    """dict, or list-containing-dict -> JSON string (Neo4j can't nest maps).
    Primitives and primitive arrays pass through unchanged."""
    if isinstance(value, dict):
        return json.dumps(value, sort_keys=True)
    if isinstance(value, list) and any(isinstance(item, dict) for item in value):
        return json.dumps(value, sort_keys=True)
    return value


def _serialize_props(props: dict[str, Any]) -> dict[str, Any]:
    return {key: _serialize(val) for key, val in props.items()}


def apply_supersession(
    tx: ManagedTransaction, entity_label: str, props: dict[str, Any], now: str
) -> None:
    """Mark any prior ACTIVE version of this business_key superseded (§6). Bootstrap
    marking only — rebind:current edge re-point is gateway-owned, NOT done here."""
    business_key = props.get("business_key")
    new_version = props.get("version")
    if business_key is None or new_version is None:
        return
    tx.run(
        f"MATCH (old:{entity_label} {{business_key: $bk}}) "
        "WHERE old.version <> $ver AND old.status = 'active' "
        "SET old.status = 'superseded', old.superseded_by = $ver, old.effective_to = $now",
        bk=business_key,
        ver=new_version,
        now=now,
    )


def _merge_node(tx: ManagedTransaction, node: dict[str, Any], now: str) -> None:
    labels: list[str] = node["labels"]
    entity_label, pk_prop = pk_for(labels)
    props = _serialize_props(node["properties"])
    pk_value = props[pk_prop]

    if entity_label in VERSIONED_GROUND_TRUTH:
        apply_supersession(tx, entity_label, node["properties"], now)

    label_expr = ":".join(labels)
    tx.run(
        f"MERGE (n:{label_expr} {{{pk_prop}: $pk}}) SET n += $props",
        pk=pk_value,
        props=props,
    )


def _merge_edge(tx: ManagedTransaction, edge: dict[str, Any]) -> None:
    (from_prop, from_val), = edge["from"].items()
    (to_prop, to_val), = edge["to"].items()
    props = _serialize_props(edge.get("properties", {}) or {})
    # RETURN count(r): if either endpoint MATCH is empty (a missing/mistyped PK),
    # MERGE binds nothing and count is 0 — fail loud rather than silently drop the
    # edge. On a re-run the existing edge is matched (count 1), so this stays idempotent.
    result = tx.run(
        f"MATCH (a {{{from_prop}: $from_val}}), (b {{{to_prop}: $to_val}}) "
        f"MERGE (a)-[r:{edge['type']}]->(b) SET r += $props "
        "RETURN count(r) AS n",
        from_val=from_val,
        to_val=to_val,
        props=props,
    )
    if result.single()["n"] == 0:
        raise ValueError(
            f"edge {edge['type']} endpoints unresolved: "
            f"{from_prop}={from_val!r} -> {to_prop}={to_val!r} (an endpoint node is missing)"
        )


def load_docs(driver: Driver, docs: list[SeedDoc], now: str) -> dict[str, int]:
    """Load nodes first (all docs), then edges (all docs), so a later plane's edge
    to an earlier plane's node always resolves. `now` is caller-supplied (an ISO
    timestamp) — never clock-derived here, so a load is reproducible."""
    counts = {"nodes": 0, "edges": 0}
    with driver.session() as session:
        for doc in docs:
            for node in doc.nodes:
                session.execute_write(_merge_node, node, now)
                counts["nodes"] += 1
        for doc in docs:
            for edge in doc.edges:
                session.execute_write(_merge_edge, edge)
                counts["edges"] += 1
    return counts
