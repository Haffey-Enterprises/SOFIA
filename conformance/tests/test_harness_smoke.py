##############################################################################
# Module: test_harness_smoke.py
# Service: conformance (RBT-33)
# Author: Haffey Enterprises LLC
# Created: 2026-06-22
# Revised: 2026-06-22
# Description: Phase-1 green-harness dry-run gate (BUILD prompt §3). Proves the
#   ephemeral-Neo4j harness end to end — container up, seeded via the raw-CREATE
#   helper, one Cypher round-trip read back — before Phase 2 builds any
#   assertion against it. This is the diagnose-first hotspot proof.
# Standards: ENG-STD-001 v3.2.0
##############################################################################
"""Smoke test: the ephemeral-Neo4j fixture harness round-trips correctly."""

from neo4j import Driver

from conformance.fixtures.seeding import seed


def test_harness_round_trips_a_seeded_node(graph: Driver) -> None:
    """A raw-CREATE seed is readable back through the same driver."""
    seed(graph, ["CREATE (:SmokeProbe {value: 42})"])

    with graph.session() as session:
        record = session.run("MATCH (p:SmokeProbe) RETURN p.value AS value").single()

    assert record is not None
    assert record["value"] == 42


def test_graph_fixture_starts_empty(graph: Driver) -> None:
    """The graph fixture resets state, so each test starts from an empty graph."""
    with graph.session() as session:
        count = session.run("MATCH (n) RETURN count(n) AS n").single()

    assert count is not None
    assert count["n"] == 0
