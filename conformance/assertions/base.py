##############################################################################
# Module: base.py
# Service: conformance (RBT-33)
# Author: Haffey Enterprises LLC
# Created: 2026-06-22
# Revised: 2026-06-22
# Description: Shared assertion primitives. Graph-state assertions return a list
#   of Violation records (empty == conformant); a non-empty result is the caught
#   violation. Returning rather than raising lets a CI runner aggregate across
#   assertions and lets each assertion be tested against conformant + violation
#   fixtures (DDR-002 §4.3 — validator correctness against fixtures).
# Standards: ENG-STD-001 v3.2.0
##############################################################################
"""Shared types and helpers for graph-state conformance assertions."""

from collections.abc import Mapping
from dataclasses import dataclass
from typing import Any

from neo4j import Driver


@dataclass(frozen=True)
class Violation:
    """A single conformance-invariant violation found in the graph.

    Attributes:
        invariant: The invariant identifier (e.g. ``"DDR-002 §7 #1"``).
        identity: The business key / id of the offending node, for triage.
        detail: A human-readable description of what failed.
    """

    invariant: str
    identity: str
    detail: str


def query_rows(
    driver: Driver, cypher: str, parameters: Mapping[str, Any] | None = None
) -> list[dict[str, Any]]:
    """Run a read query and return its rows as dictionaries.

    Args:
        driver: An open Neo4j driver.
        cypher: The Cypher read query.
        parameters: Optional query parameters.

    Returns:
        The result rows, each as a ``dict`` keyed by return alias.
    """
    with driver.session() as session:
        return [record.data() for record in session.run(cypher, dict(parameters or {}))]
