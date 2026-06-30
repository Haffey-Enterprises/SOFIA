##############################################################################
# Module: conftest.py
# Service: conformance (RBT-33)
# Author: Haffey Enterprises LLC
# Created: 2026-06-22
# Revised: 2026-06-22
# Description: Fixtures for the 1b gateway-behavioral contracts. Provides the
#   bare-seam gateway. The return annotation is the GraphGateway Protocol, so
#   mypy --strict verifies the stub structurally conforms to the seam (the seam
#   is the contract RBT-15's gateway must satisfy). These contracts need no
#   Neo4j — they bind to the seam, not a graph.
# Standards: ENG-STD-001 v3.2.0
##############################################################################
"""Pytest fixtures for the gateway-behavioral contract suite."""

import pytest

from conformance.contracts.gateway_seam import GraphGateway, UnimplementedGraphGateway


@pytest.fixture
def gateway() -> GraphGateway:
    """The bare (unimplemented) GraphGateway seam the 1b contracts bind to."""
    return UnimplementedGraphGateway()
