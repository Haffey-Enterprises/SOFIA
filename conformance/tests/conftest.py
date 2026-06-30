##############################################################################
# Module: conftest.py
# Service: conformance (RBT-33)
# Author: Haffey Enterprises LLC
# Created: 2026-06-22
# Revised: 2026-06-22
# Description: Pytest harness for the conformance graph-state suite — a seeded
#   ephemeral Neo4j (testcontainers, Community 5.x; DDR-002 §4.2.1, no native
#   constraints installed). One container per test session; the graph is reset
#   to empty before each test so fixtures never bleed across cases.
# Standards: ENG-STD-001 v3.2.0
##############################################################################
"""Shared pytest fixtures for the ephemeral-Neo4j conformance harness."""

from collections.abc import Iterator

import pytest
from neo4j import Driver
from testcontainers.neo4j import Neo4jContainer

from conformance.fixtures.seeding import reset

# Community edition is sufficient: the assertion-correctness fixtures install no
# native constraints (DDR-002 §4.2.1). Pinned to the 5.x line for Cypher-dialect
# parity with the eventual Enterprise production graph (the edition difference +
# the fixture<->real-schema parity gap are RBT-15-inherited; see the working
# note). Bump deliberately, not implicitly.
NEO4J_IMAGE = "neo4j:5.26-community"


@pytest.fixture(scope="session")
def neo4j_driver() -> Iterator[Driver]:
    """Start one ephemeral Neo4j container for the session and yield a driver.

    Yields:
        An open, connectivity-verified Neo4j driver bound to the container.
    """
    with Neo4jContainer(image=NEO4J_IMAGE) as container:
        driver = container.get_driver()
        try:
            driver.verify_connectivity()
            yield driver
        finally:
            driver.close()


@pytest.fixture
def graph(neo4j_driver: Driver) -> Driver:
    """Yield a driver bound to an empty graph (reset before each test).

    Args:
        neo4j_driver: The session-scoped driver.

    Returns:
        The same driver, against a freshly emptied database.
    """
    reset(neo4j_driver)
    return neo4j_driver
