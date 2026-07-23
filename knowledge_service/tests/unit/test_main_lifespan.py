##############################################################################
# Module: test_main_lifespan.py
# Service: knowledge-service
# Author: Haffey Enterprises LLC
# Created: 2026-07-21
# Revised: 2026-07-23
# Description: Unit tests for the application wiring in main.py — the lifespan
#   (which opens exactly one driver and loads the in-process schema-metadata
#   registry, ADR-002 §2.5 / SDD-001 §3.1), the graph-store and schema-registry
#   dependencies, and the SDD-001 §3.2 typed-error handler that maps a
#   GatewayError to the error envelope. The adapter is doubled; no driver is
#   opened and no Neo4j is contacted.
##############################################################################

import json
from types import SimpleNamespace
from typing import Any
from unittest.mock import AsyncMock, MagicMock

import pytest
from fastapi import FastAPI

import app.main as main_module
from app.adapters.in_memory_graph import InMemoryGraphStore
from app.domain.exceptions import GatewayError
from app.domain.shared.schema_metadata import SchemaRegistry
from app.main import (
    get_graph_store,
    get_schema_registry,
    handle_gateway_error,
    lifespan,
)
from app.models import ErrorType


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
    """Startup opens exactly one driver and publishes the store and registry."""

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

    async def test_lifespan_publishes_a_ready_schema_registry(
        self, adapter_class: MagicMock, fake_adapter: AsyncMock
    ) -> None:
        # Arrange
        test_app = FastAPI()

        # Act — the registry loads in-process from the declared descriptor, so
        # it is ready without any graph.
        async with lifespan(test_app):
            registry = test_app.state.schema_registry

        # Assert
        assert registry.is_ready() is True

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
    """Shutdown disposes the driver and clears the published state."""

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

    async def test_lifespan_clears_the_schema_registry_on_shutdown(
        self, adapter_class: MagicMock, fake_adapter: AsyncMock
    ) -> None:
        # Arrange
        test_app = FastAPI()

        # Act
        async with lifespan(test_app):
            pass

        # Assert
        assert test_app.state.schema_registry is None

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


class TestGetSchemaRegistryDependency:
    """Readiness reaches the registry only through the lifespan-owned state."""

    def test_get_schema_registry_returns_the_registry_published_by_lifespan(self) -> None:
        # Arrange
        registry = SchemaRegistry(core_plane_bases={}, authority="a", ready=True)
        request = MagicMock()
        request.app.state.schema_registry = registry

        # Act
        result = get_schema_registry(request)

        # Assert
        assert result is registry

    def test_get_schema_registry_before_startup_raises_runtime_error(self) -> None:
        # Arrange — a readiness check that cannot find the registry is a startup
        # fault, not a 503.
        request = MagicMock()
        request.app.state = _StateWithoutStore()

        # Act / Assert
        with pytest.raises(RuntimeError, match="schema registry"):
            get_schema_registry(request)


class TestGatewayErrorHandler:
    """The §3.2 handler maps a GatewayError to the error envelope over HTTP."""

    async def test_handle_gateway_error_renders_the_envelope_at_the_resolved_status(
        self,
    ) -> None:
        # Arrange
        request = MagicMock()
        request.state = SimpleNamespace(correlation_id="cid-9")
        exc = GatewayError(ErrorType.TARGET_NOT_FOUND, "no such node", detail="version_id=v-1")

        # Act
        response = await handle_gateway_error(request, exc)

        # Assert
        assert response.status_code == 404
        body = json.loads(bytes(response.body))
        assert body["success"] is False
        assert body["error_code"] == "TARGET_NOT_FOUND"
        assert body["message"] == "no such node"
        assert body["detail"] == "version_id=v-1"
        assert body["correlation_id"] == "cid-9"

    async def test_handle_gateway_error_unmapped_type_resolves_to_500(self) -> None:
        # Arrange — a type with no status mapping is a build defect; fail loud.
        request = MagicMock()
        request.state = SimpleNamespace(correlation_id="cid-1")
        exc = GatewayError(ErrorType.AUTHOR_VIOLATION, "not wired yet")

        # Act
        response = await handle_gateway_error(request, exc)

        # Assert
        assert response.status_code == 500

    async def test_handle_gateway_error_without_a_correlation_id_sets_null(self) -> None:
        # Arrange — no correlation ID bound on state.
        request = MagicMock()
        request.state = SimpleNamespace()
        exc = GatewayError(ErrorType.TARGET_NOT_FOUND, "x")

        # Act
        response = await handle_gateway_error(request, exc)

        # Assert
        assert json.loads(bytes(response.body))["correlation_id"] is None


class _StateWithoutStore:
    """Stands in for app.state before the lifespan has published its state."""

    def __getattr__(self, name: str) -> Any:
        raise AttributeError(name)
