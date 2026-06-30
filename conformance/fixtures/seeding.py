##############################################################################
# Module: seeding.py
# Service: conformance (RBT-33)
# Author: Haffey Enterprises LLC
# Created: 2026-06-22
# Revised: 2026-06-22
# Description: Fixture-seeding helper. Graph-state fixtures are raw Cypher CREATE
#   statements that construct conformant / violation graph patterns directly
#   (DDR-002 §4.2.1 convention). Raw CREATEs are sufficient for assertion-
#   correctness: each fixture answers "does the assertion flag this violation /
#   pass this clean case," which needs only the graph shape. The native-
#   constraint DB-half is intentionally NOT installed here (it is the real
#   schema's job, RBT-15-adjacent / deploy-time).
# Standards: ENG-STD-001 v3.2.0
##############################################################################
"""Seed an ephemeral Neo4j database from raw Cypher CREATE statements."""

from collections.abc import Iterable, Sequence

from neo4j import Driver


def reset(driver: Driver) -> None:
    """Delete every node and relationship, returning a clean graph.

    Args:
        driver: An open Neo4j driver for the ephemeral fixture database.
    """
    with driver.session() as session:
        session.run("MATCH (n) DETACH DELETE n").consume()


def seed(driver: Driver, statements: Sequence[str] | Iterable[str]) -> None:
    """Apply raw Cypher CREATE statements to construct a fixture graph.

    Each statement is executed in its own auto-commit transaction, in order.
    No native constraints are installed (DDR-002 §4.2.1 — the DB-half is the
    real schema's job).

    Args:
        driver: An open Neo4j driver for the ephemeral fixture database.
        statements: Raw Cypher statements (typically CREATE) to apply in order.
    """
    with driver.session() as session:
        for statement in statements:
            session.run(statement).consume()
