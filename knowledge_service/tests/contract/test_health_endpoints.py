##############################################################################
# Module: test_health_endpoints.py
# Service: knowledge-service
# Author: Haffey Enterprises LLC
# Created: 2026-07-21
# Revised: 2026-07-23
# Description: Contract tests for the SDD-001 §3.1 health and readiness
#   endpoints — the liveness shape, the readiness shape in both directions, the
#   two ordered checks (Neo4j connectivity and schema metadata) each answering
#   503 on its own failure, and the rule that readiness genuinely consumes the
#   GraphStoragePort rather than asserting health it did not check. RBT-78 lands
#   check 2 (schema metadata loaded).
##############################################################################

from httpx import AsyncClient

from app.adapters.in_memory_graph import InMemoryGraphStore
from app.domain.shared.schema_metadata import SchemaRegistry
from app.main import app, get_schema_registry


class TestHealthzContract:
    """Liveness: 200 {status, service}, no I/O, unconditional."""

    async def test_healthz_returns_200_with_status_and_service(
        self, async_client: AsyncClient
    ) -> None:
        # Act
        response = await async_client.get("/healthz")

        # Assert
        assert response.status_code == 200
        assert response.json() == {"status": "ok", "service": "knowledge-service"}

    async def test_healthz_stays_200_when_the_graph_store_is_unavailable(
        self, async_client: AsyncClient, graph_store: InMemoryGraphStore
    ) -> None:
        # Arrange — liveness must not track dependency state, or a graph
        # outage would get healthy containers killed.
        graph_store.set_connectivity(healthy=False)

        # Act
        response = await async_client.get("/healthz")

        # Assert
        assert response.status_code == 200
        assert graph_store.check_connectivity_calls == 0


class TestReadyzContract:
    """Readiness: 200 when every check passes, 503 otherwise (SDD-001 §3.1)."""

    async def test_readyz_when_all_checks_pass_returns_200_and_ok_checks(
        self, async_client: AsyncClient
    ) -> None:
        # Act
        response = await async_client.get("/readyz")

        # Assert
        assert response.status_code == 200
        body = response.json()
        assert body["status"] == "ok"
        assert body["service"] == "knowledge-service"
        assert body["checks"]["neo4j_connectivity"] == "ok"
        assert body["checks"]["schema_metadata"] == "ok"

    async def test_readyz_when_graph_unavailable_returns_503_and_names_the_failure(
        self, async_client: AsyncClient, graph_store: InMemoryGraphStore
    ) -> None:
        # Arrange
        graph_store.set_connectivity(healthy=False)

        # Act
        response = await async_client.get("/readyz")

        # Assert
        assert response.status_code == 503
        body = response.json()
        assert body["status"] == "unavailable"
        assert body["checks"]["neo4j_connectivity"] == "unavailable"
        # Check 2 is independent and still evaluated (SDD-001 §3.1: each check
        # runs; any failure answers 503).
        assert body["checks"]["schema_metadata"] == "ok"

    async def test_readyz_when_schema_metadata_unavailable_returns_503_and_names_it(
        self, async_client: AsyncClient
    ) -> None:
        # Arrange — a not-ready registry (load-verify failed): /readyz must
        # answer 503 rather than serve writes the gateway cannot validate.
        not_ready = SchemaRegistry(core_plane_bases={}, authority="unverified", ready=False)
        app.dependency_overrides[get_schema_registry] = lambda: not_ready

        # Act
        response = await async_client.get("/readyz")

        # Assert
        assert response.status_code == 503
        body = response.json()
        assert body["status"] == "unavailable"
        assert body["checks"]["schema_metadata"] == "unavailable"
        assert body["checks"]["neo4j_connectivity"] == "ok"

    async def test_readyz_actually_consumes_the_graph_storage_port(
        self, async_client: AsyncClient, graph_store: InMemoryGraphStore
    ) -> None:
        # Act
        await async_client.get("/readyz")

        # Assert — the check is real, not a hard-coded "ok".
        assert graph_store.check_connectivity_calls == 1

    async def test_readyz_reports_exactly_the_two_ordered_checks(
        self, async_client: AsyncClient
    ) -> None:
        # Act
        response = await async_client.get("/readyz")

        # Assert — SDD-001 §3.1 fixes exactly two checks; RBT-78 lands check 2,
        # so readiness now reports both and no others.
        assert set(response.json()["checks"]) == {"neo4j_connectivity", "schema_metadata"}
