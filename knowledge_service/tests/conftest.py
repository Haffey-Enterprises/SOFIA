##############################################################################
# Module: conftest.py
# Service: knowledge-service
# Author: Haffey Enterprises LLC
# Created: 2026-07-21
# Revised: 2026-07-23
# Description: Shared fixtures for the knowledge-service suite. The application
#   is driven over httpx.AsyncClient with the graph-store AND schema-registry
#   dependencies overridden by test doubles, so every test in this suite runs
#   without a live Neo4j and without the lifespan loader (SDD-001 §6). No
#   telemetry exporter is configured in this service yet — there is nothing to
#   disable ahead of application import; when OpenTelemetry lands, the house
#   rule (direct assignment before any app import, never setdefault) applies
#   here.
##############################################################################

from collections.abc import AsyncIterator

import pytest
from httpx import ASGITransport, AsyncClient

from app.adapters.in_memory_graph import InMemoryGraphStore
from app.domain.shared.schema_metadata import SchemaRegistry, load_core_registry
from app.main import app, get_graph_store, get_schema_registry


@pytest.fixture
def graph_store() -> InMemoryGraphStore:
    """A healthy in-memory graph store the test can flip to failing."""
    return InMemoryGraphStore()


@pytest.fixture
def schema_registry() -> SchemaRegistry:
    """A ready schema-metadata registry loaded from the declared descriptor."""
    return load_core_registry()


@pytest.fixture
async def async_client(
    graph_store: InMemoryGraphStore, schema_registry: SchemaRegistry
) -> AsyncIterator[AsyncClient]:
    """The real application, with the graph store and schema registry doubled.

    The ASGI transport does not run lifespan events, so no driver is opened and
    no connection to Neo4j is attempted, and the registry is supplied by the
    override rather than the lifespan loader. Overrides are cleared on teardown
    so no test inherits another's wiring.
    """
    app.dependency_overrides[get_graph_store] = lambda: graph_store
    app.dependency_overrides[get_schema_registry] = lambda: schema_registry
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        yield client
    app.dependency_overrides.clear()
