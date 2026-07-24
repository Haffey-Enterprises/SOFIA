##############################################################################
# Module: test_main_lifespan.py
# Service: knowledge-service
# Author: Haffey Enterprises LLC
# Created: 2026-07-21
# Revised: 2026-07-21
# Description: Unit tests for the application lifespan and the graph-store
#   dependency — the wiring that makes this service the sole holder of the
#   Neo4j driver (ADR-002 §2.5). Startup configures structured logging and
#   opens exactly one driver; shutdown disposes it; handlers reach it only
#   through the injected port. The adapter is doubled; no driver is opened.
##############################################################################

from typing import Any
from unittest.mock import AsyncMock, MagicMock

import pytest
from fastapi import FastAPI

import app.main as main_module
from app.adapters.in_memory_graph import InMemoryGraphStore
from app.main import get_graph_store, lifespan


@pytest.fixture
def fake_adapter() -> AsyncMock:
    """A stand-in for Neo4jAdapter with the lifecycle surface stubbed."""
    return AsyncMock()


@pytest.fixture
def adapter_class(monkeypatch: pytest.MonkeyPatch, fake_adapter: AsyncMock) -> MagicMock:
    """Replace the adapter class the lifespan constructs."""
    factory = MagicMock(return_value=fake_adapter)
    monkeypatch.setattr(main_module, "Neo4jAdapter", factory)
    return factory


class TestLifespanStartup:
    """Startup opens exactly one driver and publishes it on app state."""

    async def test_lifespan_opens_the_driver_and_publishes_the_store(
        self, adapter_class: MagicMock, fake_adapter: AsyncMock
    ) -> None:
        # Arrange
        test_app = FastAPI()

        # Act
        async with lifespan(test_app):
            published = test_app.state.graph_store

        # Assert
        adapter_class.assert_called_once()
        fake_adapter.connect.assert_awaited_once()
        assert published is fake_adapter

    async def test_lifespan_configures_logging_at_the_settings_level(
        self, adapter_class: MagicMock, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        # Arrange
        recorded: list[str] = []
        monkeypatch.setattr(main_module, "configure_logging", lambda level: recorded.append(level))
        test_app = FastAPI()

        # Act
        async with lifespan(test_app):
            pass

        # Assert
        assert recorded == ["INFO"]


class TestLifespanShutdown:
    """Shutdown disposes the driver and clears the published store."""

    async def test_lifespan_closes_the_driver_on_shutdown(
        self, adapter_class: MagicMock, fake_adapter: AsyncMock
    ) -> None:
        # Arrange
        test_app = FastAPI()

        # Act
        async with lifespan(test_app):
            pass

        # Assert
        fake_adapter.close.assert_awaited_once()

    async def test_lifespan_closes_the_driver_even_when_the_app_body_raises(
        self, adapter_class: MagicMock, fake_adapter: AsyncMock
    ) -> None:
        # Arrange
        test_app = FastAPI()

        # Act
        with pytest.raises(RuntimeError):
            async with lifespan(test_app):
                raise RuntimeError("serving blew up")

        # Assert — a driver leaked on an abnormal shutdown is a pool leak.
        fake_adapter.close.assert_awaited_once()


class TestGetGraphStoreDependency:
    """Handlers reach the store only through the lifespan-owned state."""

    def test_get_graph_store_returns_the_store_published_by_lifespan(self) -> None:
        # Arrange
        store = InMemoryGraphStore()
        request = MagicMock()
        request.app.state.graph_store = store

        # Act
        result = get_graph_store(request)

        # Assert
        assert result is store

    def test_get_graph_store_before_startup_raises_runtime_error(self) -> None:
        # Arrange — a handler must never silently serve without a graph store.
        request = MagicMock()
        request.app.state = _StateWithoutStore()

        # Act / Assert
        # `match` matters: NotImplementedError subclasses RuntimeError, so a
        # bare raises() would pass against an unimplemented dependency.
        with pytest.raises(RuntimeError, match="graph store"):
            get_graph_store(request)


class _StateWithoutStore:
    """Stands in for app.state before the lifespan has published a store."""

    def __getattr__(self, name: str) -> Any:
        raise AttributeError(name)
