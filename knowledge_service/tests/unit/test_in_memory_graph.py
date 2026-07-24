##############################################################################
# Module: test_in_memory_graph.py
# Service: knowledge-service
# Author: Haffey Enterprises LLC
# Created: 2026-07-21
# Revised: 2026-07-21
# Description: Unit tests for InMemoryGraphStore — the GraphStoragePort double
#   every service test runs against (SDD-001 §6, no test depends on live
#   Neo4j). The double is real behavior and is covered as such: its
#   controllable connectivity verdict is what makes the §3.1 readiness check
#   testable in both directions.
##############################################################################

from app.adapters.in_memory_graph import InMemoryGraphStore
from app.ports.graph_store import GraphStoragePort


class TestInMemoryGraphStoreSubstitutability:
    """The double must satisfy the port it substitutes for."""

    def test_in_memory_store_satisfies_the_graph_storage_port(self) -> None:
        # Arrange
        store = InMemoryGraphStore()

        # Act / Assert
        assert isinstance(store, GraphStoragePort)


class TestInMemoryGraphStoreConnectivity:
    """Connectivity is controllable in both directions, and observable."""

    async def test_check_connectivity_when_store_is_healthy_returns_true(self) -> None:
        # Arrange
        store = InMemoryGraphStore()

        # Act
        result = await store.check_connectivity()

        # Assert
        assert result is True

    async def test_check_connectivity_when_constructed_unhealthy_returns_false(self) -> None:
        # Arrange
        store = InMemoryGraphStore(connectivity_healthy=False)

        # Act
        result = await store.check_connectivity()

        # Assert
        assert result is False

    async def test_set_connectivity_flips_the_reported_verdict(self) -> None:
        # Arrange
        store = InMemoryGraphStore()

        # Act
        store.set_connectivity(healthy=False)
        after_failure = await store.check_connectivity()
        store.set_connectivity(healthy=True)
        after_recovery = await store.check_connectivity()

        # Assert
        assert after_failure is False
        assert after_recovery is True

    async def test_check_connectivity_records_how_many_times_it_was_consumed(self) -> None:
        # Arrange
        store = InMemoryGraphStore()

        # Act
        await store.check_connectivity()
        await store.check_connectivity()

        # Assert — lets a readiness test prove the check was exercised, not
        # short-circuited around.
        assert store.check_connectivity_calls == 2
