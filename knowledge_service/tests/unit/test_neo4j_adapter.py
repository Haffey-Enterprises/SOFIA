##############################################################################
# Module: test_neo4j_adapter.py
# Service: knowledge-service
# Author: Haffey Enterprises LLC
# Created: 2026-07-21
# Revised: 2026-07-21
# Description: Unit tests for Neo4jAdapter's driver lifecycle (SDD-001 §4.2,
#   §4.7) — construction from Settings, connect/verify/close, and translation
#   of driver-level failure into the port's boolean verdict — plus (RBT-78/R3a)
#   find_track_record: the one-Cypher-call track-record-lookup traversal
#   (SDD-001 §3.3.3, ADR-002 §6 check 4). The driver is mocked at the adapter
#   boundary; no test here touches a live Neo4j — the real graph behavior is
#   conformance's (RBT-80).
##############################################################################

from collections.abc import Iterator
from types import SimpleNamespace
from typing import Any
from unittest.mock import AsyncMock, MagicMock

import pytest
from neo4j import RoutingControl
from neo4j.exceptions import AuthError, ServiceUnavailable

from app.adapters.neo4j_adapter import Neo4jAdapter
from app.config import Settings
from app.ports.graph_store import GraphStoragePort, TargetEntityRef

# mypy note: pydantic-settings accepts `_env_file` at runtime, but the model's
# generated __init__ signature does not declare it, so `--strict` flags every
# call. The argument is load-bearing here: it isolates the suite from a
# developer's local .env. Hence the narrow, coded ignores below.


@pytest.fixture
def settings(monkeypatch: pytest.MonkeyPatch) -> Iterator[Settings]:
    """Settings pinned to known Neo4j values, isolated from the ambient env."""
    monkeypatch.setenv("KS_NEO4J_URI", "neo4j+s://graph.example.internal:7687")
    monkeypatch.setenv("KS_NEO4J_DATABASE", "sofia")
    monkeypatch.setenv("KS_NEO4J_USERNAME", "gateway")
    monkeypatch.setenv("KS_NEO4J_PASSWORD", "unit-test-secret")
    monkeypatch.setenv("KS_NEO4J_MAX_CONNECTION_POOL_SIZE", "23")
    monkeypatch.setenv("KS_NEO4J_CONNECTION_ACQUISITION_TIMEOUT_SECONDS", "12.5")
    yield Settings(_env_file=None)  # type: ignore[call-arg]


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
        # neo4j ships no annotations on its exception constructors.
        unreachable = ServiceUnavailable("no route to host")  # type: ignore[no-untyped-call]
        driver.verify_connectivity.side_effect = unreachable
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


class TestNeo4jAdapterFindTrackRecord:
    """The track-record-lookup traversal (SDD-001 §3.3.3) — one Cypher call."""

    async def test_find_track_record_resolves_id_properties_per_target_kind(
        self, settings: Settings, driver_factory: MagicMock, driver: AsyncMock
    ) -> None:
        # Arrange — each target kind has its own PK property (DDR-002 §2.1/§2.2).
        driver.execute_query.return_value = SimpleNamespace(records=[])
        adapter = Neo4jAdapter(settings, driver_factory=driver_factory)
        await adapter.connect()
        refs = [
            TargetEntityRef(entity_kind="Technology", entity_id="tech-1"),
            TargetEntityRef(entity_kind="Pattern", entity_id="pattern-1"),
            TargetEntityRef(entity_kind="Capability", entity_id="cap-1"),
            TargetEntityRef(entity_kind="DeploymentEnvironment", entity_id="env-1"),
        ]

        # Act
        await adapter.find_track_record(refs)

        # Assert
        params = driver.execute_query.call_args.args[1]["target_refs"]
        assert params == [
            {"entity_kind": "Technology", "id_property": "technology_id", "entity_id": "tech-1"},
            {"entity_kind": "Pattern", "id_property": "pattern_id", "entity_id": "pattern-1"},
            {"entity_kind": "Capability", "id_property": "capability_id", "entity_id": "cap-1"},
            {
                "entity_kind": "DeploymentEnvironment",
                "id_property": "environment_id",
                "entity_id": "env-1",
            },
        ]

    async def test_find_track_record_routes_read_and_targets_the_configured_database(
        self, settings: Settings, driver_factory: MagicMock, driver: AsyncMock
    ) -> None:
        # Arrange
        driver.execute_query.return_value = SimpleNamespace(records=[])
        adapter = Neo4jAdapter(settings, driver_factory=driver_factory)
        await adapter.connect()

        # Act
        await adapter.find_track_record([TargetEntityRef(entity_kind="Technology", entity_id="t")])

        # Assert — a read traversal routes read, not the write default.
        kwargs = driver.execute_query.call_args.kwargs
        assert kwargs["routing_"] is RoutingControl.READ
        assert kwargs["database_"] == "sofia"

    async def test_find_track_record_query_matches_observed_in_on_active_patterns(
        self, settings: Settings, driver_factory: MagicMock, driver: AsyncMock
    ) -> None:
        # Arrange
        driver.execute_query.return_value = SimpleNamespace(records=[])
        adapter = Neo4jAdapter(settings, driver_factory=driver_factory)
        await adapter.connect()

        # Act
        await adapter.find_track_record([TargetEntityRef(entity_kind="Technology", entity_id="t")])

        # Assert — the single-store traversal (ADR-002 §6 check 4): ObservedPattern
        # OBSERVED_IN the target, active patterns only.
        query = driver.execute_query.call_args.args[0]
        assert "ObservedPattern" in query
        assert "OBSERVED_IN" in query
        assert "active" in query

    async def test_find_track_record_maps_each_record_to_a_candidate_record(
        self, settings: Settings, driver_factory: MagicMock, driver: AsyncMock
    ) -> None:
        # Arrange
        driver.execute_query.return_value = SimpleNamespace(
            records=[
                {
                    "node_id": "op-1",
                    "origin_mechanism": "derived",
                    "derivation_class": "distilled",
                    "node_confidence": 0.8,
                    "edge_confidence": 0.6,
                    "first_observed_at": "2026-01-01T00:00:00Z",
                    "last_observed_at": "2026-06-01T00:00:00Z",
                }
            ]
        )
        adapter = Neo4jAdapter(settings, driver_factory=driver_factory)
        await adapter.connect()

        # Act
        results = await adapter.find_track_record(
            [TargetEntityRef(entity_kind="Technology", entity_id="t")]
        )

        # Assert — uncomposed: node reliability and edge certainty both carried,
        # never combined (SDD-001 §3.3.3).
        assert len(results) == 1
        record = results[0]
        assert record.node_id == "op-1"
        assert record.origin_mechanism == "derived"
        assert record.derivation_class == "distilled"
        assert record.node_confidence == 0.8
        assert record.edge_confidence == 0.6
        assert record.first_observed_at == "2026-01-01T00:00:00Z"
        assert record.last_observed_at == "2026-06-01T00:00:00Z"

    async def test_find_track_record_maps_a_null_confidence_through_honestly(
        self, settings: Settings, driver_factory: MagicMock, driver: AsyncMock
    ) -> None:
        # Arrange — confidence is T2 on both surfaces (DDR-002 §7); no DB
        # constraint or CI check guarantees its presence, so a null must map
        # through rather than being defaulted or rejected.
        driver.execute_query.return_value = SimpleNamespace(
            records=[
                {
                    "node_id": "op-1",
                    "origin_mechanism": "derived",
                    "derivation_class": "distilled",
                    "node_confidence": None,
                    "edge_confidence": None,
                    "first_observed_at": None,
                    "last_observed_at": None,
                }
            ]
        )
        adapter = Neo4jAdapter(settings, driver_factory=driver_factory)
        await adapter.connect()

        # Act
        results = await adapter.find_track_record(
            [TargetEntityRef(entity_kind="Technology", entity_id="t")]
        )

        # Assert
        assert results[0].node_confidence is None
        assert results[0].edge_confidence is None

    async def test_find_track_record_with_no_matches_returns_empty(
        self, settings: Settings, driver_factory: MagicMock, driver: AsyncMock
    ) -> None:
        # Arrange
        driver.execute_query.return_value = SimpleNamespace(records=[])
        adapter = Neo4jAdapter(settings, driver_factory=driver_factory)
        await adapter.connect()

        # Act
        results = await adapter.find_track_record(
            [TargetEntityRef(entity_kind="Technology", entity_id="t")]
        )

        # Assert
        assert results == []

    async def test_find_track_record_before_connect_raises_runtime_error(
        self, settings: Settings, driver_factory: MagicMock
    ) -> None:
        # Arrange — a data operation with no open driver must fail loud, never
        # silently return an empty (and misleading) track record.
        adapter = Neo4jAdapter(settings, driver_factory=driver_factory)

        # Act / Assert
        with pytest.raises(RuntimeError, match="driver"):
            await adapter.find_track_record(
                [TargetEntityRef(entity_kind="Technology", entity_id="t")]
            )
