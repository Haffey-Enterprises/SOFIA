##############################################################################
# Module: test_neo4j_adapter.py
# Service: knowledge-service
# Author: Haffey Enterprises LLC
# Created: 2026-07-21
# Revised: 2026-07-21
# Description: Unit tests for Neo4jAdapter's driver lifecycle (SDD-001 §4.2,
#   §4.7) — construction from Settings, connect/verify/close, and translation
#   of driver-level failure into the port's boolean verdict. The driver is
#   mocked at the adapter boundary; no test here touches a live Neo4j.
##############################################################################

from collections.abc import Iterator
from typing import Any
from unittest.mock import AsyncMock, MagicMock

import pytest
from neo4j.exceptions import AuthError, ServiceUnavailable

from app.adapters.neo4j_adapter import Neo4jAdapter
from app.config import Settings
from app.ports.graph_store import GraphStoragePort


@pytest.fixture
def settings(monkeypatch: pytest.MonkeyPatch) -> Iterator[Settings]:
    """Settings pinned to known Neo4j values, isolated from the ambient env."""
    monkeypatch.setenv("KS_NEO4J_URI", "neo4j+s://graph.example.internal:7687")
    monkeypatch.setenv("KS_NEO4J_DATABASE", "sofia")
    monkeypatch.setenv("KS_NEO4J_USERNAME", "gateway")
    monkeypatch.setenv("KS_NEO4J_PASSWORD", "unit-test-secret")
    monkeypatch.setenv("KS_NEO4J_MAX_CONNECTION_POOL_SIZE", "23")
    monkeypatch.setenv("KS_NEO4J_CONNECTION_ACQUISITION_TIMEOUT_SECONDS", "12.5")
    yield Settings(_env_file=None)


@pytest.fixture
def driver() -> AsyncMock:
    """A stand-in for neo4j.AsyncDriver."""
    return AsyncMock()


@pytest.fixture
def driver_factory(driver: AsyncMock) -> MagicMock:
    """A stand-in for AsyncGraphDatabase.driver."""
    return MagicMock(return_value=driver)


class TestNeo4jAdapterSubstitutability:
    """The production adapter must satisfy the port it implements."""

    def test_neo4j_adapter_satisfies_the_graph_storage_port(
        self, settings: Settings, driver_factory: MagicMock
    ) -> None:
        # Arrange
        adapter = Neo4jAdapter(settings, driver_factory=driver_factory)

        # Act / Assert
        assert isinstance(adapter, GraphStoragePort)


class TestNeo4jAdapterConnect:
    """The driver is constructed from Settings and only once."""

    async def test_connect_builds_the_driver_from_settings(
        self, settings: Settings, driver_factory: MagicMock
    ) -> None:
        # Arrange
        adapter = Neo4jAdapter(settings, driver_factory=driver_factory)

        # Act
        await adapter.connect()

        # Assert
        driver_factory.assert_called_once_with(
            "neo4j+s://graph.example.internal:7687",
            auth=("gateway", "unit-test-secret"),
            max_connection_pool_size=23,
            connection_acquisition_timeout=12.5,
        )

    async def test_connect_does_not_construct_a_second_driver_when_called_twice(
        self, settings: Settings, driver_factory: MagicMock
    ) -> None:
        # Arrange
        adapter = Neo4jAdapter(settings, driver_factory=driver_factory)

        # Act
        await adapter.connect()
        await adapter.connect()

        # Assert
        assert driver_factory.call_count == 1

    def test_constructing_the_adapter_does_not_open_a_driver(
        self, settings: Settings, driver_factory: MagicMock
    ) -> None:
        # Arrange / Act
        Neo4jAdapter(settings, driver_factory=driver_factory)

        # Assert — construction is inert; the connection is a lifespan act.
        driver_factory.assert_not_called()


class TestNeo4jAdapterCheckConnectivity:
    """Driver-level failure becomes the port's boolean verdict, never an escape."""

    async def test_check_connectivity_when_driver_verifies_returns_true(
        self, settings: Settings, driver_factory: MagicMock, driver: AsyncMock
    ) -> None:
        # Arrange
        adapter = Neo4jAdapter(settings, driver_factory=driver_factory)
        await adapter.connect()

        # Act
        result = await adapter.check_connectivity()

        # Assert
        assert result is True
        driver.verify_connectivity.assert_awaited_once()

    async def test_check_connectivity_before_connect_returns_false(
        self, settings: Settings, driver_factory: MagicMock
    ) -> None:
        # Arrange
        adapter = Neo4jAdapter(settings, driver_factory=driver_factory)

        # Act
        result = await adapter.check_connectivity()

        # Assert
        assert result is False

    async def test_check_connectivity_when_store_unreachable_returns_false(
        self, settings: Settings, driver_factory: MagicMock, driver: AsyncMock
    ) -> None:
        # Arrange
        driver.verify_connectivity.side_effect = ServiceUnavailable("no route to host")
        adapter = Neo4jAdapter(settings, driver_factory=driver_factory)
        await adapter.connect()

        # Act
        result = await adapter.check_connectivity()

        # Assert
        assert result is False

    async def test_check_connectivity_when_credentials_rejected_returns_false(
        self, settings: Settings, driver_factory: MagicMock, driver: AsyncMock
    ) -> None:
        # Arrange — authentication failure is part of readiness check 1, not a
        # separate condition (SDD-001 §3.1).
        driver.verify_connectivity.side_effect = AuthError("credentials rejected")
        adapter = Neo4jAdapter(settings, driver_factory=driver_factory)
        await adapter.connect()

        # Act
        result = await adapter.check_connectivity()

        # Assert
        assert result is False

    async def test_check_connectivity_failure_does_not_log_the_credential(
        self,
        settings: Settings,
        driver_factory: MagicMock,
        driver: AsyncMock,
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        # Arrange
        driver.verify_connectivity.side_effect = AuthError("credentials rejected")
        adapter = Neo4jAdapter(settings, driver_factory=driver_factory)
        await adapter.connect()

        # Act
        await adapter.check_connectivity()

        # Assert — the Tier 4 value must not reach any log channel.
        captured = capsys.readouterr()
        assert "unit-test-secret" not in captured.out
        assert "unit-test-secret" not in captured.err


class TestNeo4jAdapterClose:
    """Disposal is graceful and idempotent."""

    async def test_close_disposes_the_driver(
        self, settings: Settings, driver_factory: MagicMock, driver: AsyncMock
    ) -> None:
        # Arrange
        adapter = Neo4jAdapter(settings, driver_factory=driver_factory)
        await adapter.connect()

        # Act
        await adapter.close()

        # Assert
        driver.close.assert_awaited_once()

    async def test_close_when_never_connected_is_a_no_op(
        self, settings: Settings, driver_factory: MagicMock, driver: AsyncMock
    ) -> None:
        # Arrange
        adapter = Neo4jAdapter(settings, driver_factory=driver_factory)

        # Act
        await adapter.close()

        # Assert
        driver.close.assert_not_awaited()

    async def test_connect_after_close_builds_a_fresh_driver(
        self, settings: Settings, driver_factory: MagicMock
    ) -> None:
        # Arrange
        adapter = Neo4jAdapter(settings, driver_factory=driver_factory)
        await adapter.connect()
        await adapter.close()

        # Act
        await adapter.connect()

        # Assert
        assert driver_factory.call_count == 2


class TestNeo4jAdapterDefaultFactory:
    """Without an injected factory the adapter binds the real driver builder."""

    async def test_adapter_defaults_to_the_neo4j_async_driver_factory(
        self, settings: Settings, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        # Arrange
        recorded: dict[str, Any] = {}

        def fake_driver(uri: str, **kwargs: Any) -> AsyncMock:
            recorded["uri"] = uri
            return AsyncMock()

        monkeypatch.setattr(
            "app.adapters.neo4j_adapter.AsyncGraphDatabase.driver",
            fake_driver,
        )
        adapter = Neo4jAdapter(settings)

        # Act
        await adapter.connect()

        # Assert — with no factory injected, the real neo4j builder is used.
        assert recorded["uri"] == "neo4j+s://graph.example.internal:7687"
