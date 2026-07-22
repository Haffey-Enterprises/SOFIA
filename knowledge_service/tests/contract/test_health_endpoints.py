##############################################################################
# Module: test_health_endpoints.py
# Service: knowledge-service
# Author: Haffey Enterprises LLC
# Created: 2026-07-21
# Revised: 2026-07-21
# Description: Contract tests for the SDD-001 §3.1 health and readiness
#   endpoints — the liveness shape, the readiness shape in both directions, and
#   the rule that readiness genuinely consumes the GraphStoragePort rather than
#   asserting health it did not check.
##############################################################################

from httpx import AsyncClient

from app.adapters.in_memory_graph import InMemoryGraphStore


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
    """Readiness: 200 when every check passes, 503 otherwise."""

    async def test_readyz_when_graph_reachable_returns_200_and_ok_checks(
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

    async def test_readyz_actually_consumes_the_graph_storage_port(
        self, async_client: AsyncClient, graph_store: InMemoryGraphStore
    ) -> None:
        # Act
        await async_client.get("/readyz")

        # Assert — the check is real, not a hard-coded "ok".
        assert graph_store.check_connectivity_calls == 1

    async def test_readyz_reports_only_the_checks_it_actually_performed(
        self, async_client: AsyncClient
    ) -> None:
        # Act
        response = await async_client.get("/readyz")

        # Assert — SDD-001 §3.1 check 2 (schema metadata loaded) lands with
        # RBT-78. It is staged, not faked: until it exists, readiness must not
        # claim it. A green /readyz today attests check 1 only.
        assert set(response.json()["checks"]) == {"neo4j_connectivity"}
