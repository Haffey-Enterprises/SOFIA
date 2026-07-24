##############################################################################
# Module: test_neo4j_adapter.py
# Service: knowledge-service
# Author: Haffey Enterprises LLC
# Created: 2026-07-21
# Revised: 2026-07-21
# Description: Unit tests for Neo4jAdapter's driver lifecycle (SDD-001 §4.2,
#   §4.7) — construction from Settings, connect/verify/close, and translation
#   of driver-level failure into the port's boolean verdict — plus (RBT-78/R3a)
#   find_track_record and (R3b) resolve_technology_options: the one-Cypher-call
#   traversals per operation (ADR-002 §6 check 4). The driver is mocked at the
#   adapter boundary; no test here touches a live Neo4j — the real graph
#   behavior (including the R3b flag-determination Cypher's correctness) is
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
from app.ports.graph_store import FindPrecedentsCriteria, GraphStoragePort, TargetEntityRef

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


class TestNeo4jAdapterResolveTechnologyOptions:
    """The resolve-technology traversal (SDD-001 §3.3.2) — one Cypher call."""

    async def test_resolve_technology_options_queries_with_the_capability_id(
        self, settings: Settings, driver_factory: MagicMock, driver: AsyncMock
    ) -> None:
        # Arrange
        driver.execute_query.return_value = SimpleNamespace(records=[])
        adapter = Neo4jAdapter(settings, driver_factory=driver_factory)
        await adapter.connect()

        # Act
        await adapter.resolve_technology_options("cap-1")

        # Assert
        params = driver.execute_query.call_args.args[1]
        assert params == {"capability_id": "cap-1"}

    async def test_resolve_technology_options_routes_read_and_targets_the_database(
        self, settings: Settings, driver_factory: MagicMock, driver: AsyncMock
    ) -> None:
        # Arrange
        driver.execute_query.return_value = SimpleNamespace(records=[])
        adapter = Neo4jAdapter(settings, driver_factory=driver_factory)
        await adapter.connect()

        # Act
        await adapter.resolve_technology_options("cap-1")

        # Assert
        kwargs = driver.execute_query.call_args.kwargs
        assert kwargs["routing_"] is RoutingControl.READ
        assert kwargs["database_"] == "sofia"

    async def test_resolve_technology_options_query_matches_approved_option_for(
        self, settings: Settings, driver_factory: MagicMock, driver: AsyncMock
    ) -> None:
        # Arrange
        driver.execute_query.return_value = SimpleNamespace(records=[])
        adapter = Neo4jAdapter(settings, driver_factory=driver_factory)
        await adapter.connect()

        # Act
        await adapter.resolve_technology_options("cap-1")

        # Assert — the single-store traversal (ADR-002 §6 check 4): Technology
        # APPROVED_OPTION_FOR Capability, plus the real read-discipline
        # structure (RETRACTS/DECIDED_ON for retraction, PROMOTES_TO_KNOWLEDGE/
        # HAS_CONDITION for the resolved Condition set).
        query = driver.execute_query.call_args.args[0]
        assert "APPROVED_OPTION_FOR" in query
        assert "RETRACTS" in query
        assert "PROMOTES_TO_KNOWLEDGE" in query
        assert "HAS_CONDITION" in query

    async def test_retraction_is_existence_based_not_governance_based(
        self, settings: Settings, driver_factory: MagicMock, driver: AsyncMock
    ) -> None:
        # Arrange — review Fix A: DDR-002 §2.4 states #21 "traces to an
        # approving decision, not the governing one" — the opposite of #15's
        # promoted-origin rule. retracted must be an existence check over ANY
        # approving DECIDED_ON on a retraction candidate, never a
        # latest-decided_at "governing decision" selection — the prior
        # ORDER BY/collect[0] form for retraction is gone entirely.
        driver.execute_query.return_value = SimpleNamespace(records=[])
        adapter = Neo4jAdapter(settings, driver_factory=driver_factory)
        await adapter.connect()

        # Act
        await adapter.resolve_technology_options("cap-1")

        # Assert
        query = driver.execute_query.call_args.args[0]
        assert "EXISTS {" in query
        assert "governing_retraction_decision" not in query

    async def test_verdict_flip_a_later_non_approving_redecision_still_yields_retracted_true(
        self, settings: Settings, driver_factory: MagicMock, driver: AsyncMock
    ) -> None:
        # Arrange — review Fix A verdict-flip scenario: a retraction with an
        # approving DECIDED_ON followed by a LATER non-approving re-decision.
        # The Cypher's EXISTS{} existence check (verified structurally above)
        # is what makes this graph state resolve to retracted=true rather than
        # false; at the mocked-driver layer, the boundary this test can prove
        # is the mapping — the driver returns exactly the boolean such a graph
        # would produce, and the adapter must carry it through unchanged
        # rather than re-deriving or overriding it. The Cypher's real
        # existence-vs-governance behavior against a live graph is
        # conformance's to verify (RBT-80 #21).
        driver.execute_query.return_value = SimpleNamespace(
            records=[
                {
                    "node_id": "tech-flip",
                    "version": "1",
                    "origin_mechanism": "promoted",
                    "derivation_class": None,
                    "tier_applicability": [],
                    "approved_data_classifications": [],
                    "applicability_state": "unconditional",
                    "retracted": True,
                    "conditions": [],
                    "deprecation_date": None,
                }
            ]
        )
        adapter = Neo4jAdapter(settings, driver_factory=driver_factory)
        await adapter.connect()

        # Act
        results = await adapter.resolve_technology_options("cap-1")

        # Assert
        assert results[0].retracted is True

    async def test_resolve_technology_options_returns_one_record_per_technology(
        self, settings: Settings, driver_factory: MagicMock, driver: AsyncMock
    ) -> None:
        # Arrange — review Fix B: a technology with multiple retraction
        # proposals and/or decisions must not multiply rows. EXISTS{} is a
        # boolean subquery (cannot expand outer cardinality) and the
        # conditions CALL{} subquery resolves to exactly one aggregate row per
        # tech by construction — both verified structurally; here the driver
        # returns the single row the fixed query would produce for such a
        # tech, and the adapter must map it to exactly one candidate record,
        # never one per underlying retraction/decision.
        driver.execute_query.return_value = SimpleNamespace(
            records=[
                {
                    "node_id": "tech-multi-retraction",
                    "version": "1",
                    "origin_mechanism": "promoted",
                    "derivation_class": None,
                    "tier_applicability": [],
                    "approved_data_classifications": [],
                    "applicability_state": "unconditional",
                    "retracted": True,
                    "conditions": [],
                    "deprecation_date": None,
                }
            ]
        )
        adapter = Neo4jAdapter(settings, driver_factory=driver_factory)
        await adapter.connect()

        # Act
        results = await adapter.resolve_technology_options("cap-1")

        # Assert
        assert len(results) == 1

    async def test_conditions_are_scoped_to_the_governing_approving_decision(
        self, settings: Settings, driver_factory: MagicMock, driver: AsyncMock
    ) -> None:
        # Arrange — review Fix C: conditions must be collected only from the
        # decision that is both approving AND governing (latest decided_at
        # among approving decisions), never from any approving-or-not decision
        # unscoped. The CALL{} subquery filters to approving outcomes first,
        # then takes the single latest by decided_at, then collects only ITS
        # HAS_CONDITION set.
        driver.execute_query.return_value = SimpleNamespace(records=[])
        adapter = Neo4jAdapter(settings, driver_factory=driver_factory)
        await adapter.connect()

        # Act
        await adapter.resolve_technology_options("cap-1")

        # Assert
        query = driver.execute_query.call_args.args[0]
        assert "decided.outcome IN ['approved', 'approved_conditional']" in query
        assert "ORDER BY decision.decided_at DESC" in query
        assert "LIMIT 1" in query

    async def test_superseded_condition_does_not_leak_when_governing_decision_is_unconditional(
        self, settings: Settings, driver_factory: MagicMock, driver: AsyncMock
    ) -> None:
        # Arrange — review Fix C(a): an earlier approving decision carried a
        # condition; a later approving (governing) decision carries none. The
        # driver returns what the fixed query would compute for that graph
        # state — conditions=[] — and the adapter must map it through as an
        # empty tuple, not resurrect the superseded condition.
        driver.execute_query.return_value = SimpleNamespace(
            records=[
                {
                    "node_id": "tech-resuperseded",
                    "version": "1",
                    "origin_mechanism": "promoted",
                    "derivation_class": None,
                    "tier_applicability": [],
                    "approved_data_classifications": [],
                    "applicability_state": "unconditional",
                    "retracted": False,
                    "conditions": [],
                    "deprecation_date": None,
                }
            ]
        )
        adapter = Neo4jAdapter(settings, driver_factory=driver_factory)
        await adapter.connect()

        # Act
        results = await adapter.resolve_technology_options("cap-1")

        # Assert
        assert results[0].conditions == ()

    async def test_re_scoped_condition_reflects_only_the_new_governing_set(
        self, settings: Settings, driver_factory: MagicMock, driver: AsyncMock
    ) -> None:
        # Arrange — review Fix C(b): a later governing approving decision
        # carries a NEW condition set distinct from any earlier one. The
        # driver returns what the fixed query would compute — only the new
        # set — and the adapter must map exactly that through, nothing more.
        driver.execute_query.return_value = SimpleNamespace(
            records=[
                {
                    "node_id": "tech-rescoped",
                    "version": "1",
                    "origin_mechanism": "promoted",
                    "derivation_class": None,
                    "tier_applicability": [],
                    "approved_data_classifications": [],
                    "applicability_state": "conditional",
                    "retracted": False,
                    "conditions": [
                        {
                            "predicate": {"op": "eq", "field": "new_tier"},
                            "dependency_manifest": ["new_tier"],
                        }
                    ],
                    "deprecation_date": None,
                }
            ]
        )
        adapter = Neo4jAdapter(settings, driver_factory=driver_factory)
        await adapter.connect()

        # Act
        results = await adapter.resolve_technology_options("cap-1")

        # Assert
        assert len(results[0].conditions) == 1
        assert results[0].conditions[0].predicate == {"op": "eq", "field": "new_tier"}
        assert results[0].conditions[0].required_context_fields == frozenset({"new_tier"})

    async def test_resolve_technology_options_maps_an_unconditional_unretracted_record(
        self, settings: Settings, driver_factory: MagicMock, driver: AsyncMock
    ) -> None:
        # Arrange
        driver.execute_query.return_value = SimpleNamespace(
            records=[
                {
                    "node_id": "tech-1",
                    "version": "2",
                    "origin_mechanism": "ingested",
                    "derivation_class": "primary",
                    "tier_applicability": ["production", "staging"],
                    "approved_data_classifications": ["internal"],
                    "applicability_state": None,
                    "retracted": False,
                    "conditions": [],
                    "deprecation_date": None,
                }
            ]
        )
        adapter = Neo4jAdapter(settings, driver_factory=driver_factory)
        await adapter.connect()

        # Act
        results = await adapter.resolve_technology_options("cap-1")

        # Assert — a null applicability_state maps to the schema's own default.
        assert len(results) == 1
        record = results[0]
        assert record.node_id == "tech-1"
        assert record.version == "2"
        assert record.origin_mechanism == "ingested"
        assert record.derivation_class == "primary"
        assert record.tier_applicability == ("production", "staging")
        assert record.approved_data_classifications == ("internal",)
        assert record.applicability_state == "unconditional"
        assert record.retracted is False
        assert record.conditions == ()
        assert record.deprecation_date is None

    async def test_resolve_technology_options_maps_a_retracted_conditional_record(
        self, settings: Settings, driver_factory: MagicMock, driver: AsyncMock
    ) -> None:
        # Arrange
        driver.execute_query.return_value = SimpleNamespace(
            records=[
                {
                    "node_id": "tech-2",
                    "version": "1",
                    "origin_mechanism": "promoted",
                    "derivation_class": None,
                    "tier_applicability": [],
                    "approved_data_classifications": [],
                    "applicability_state": "conditional",
                    "retracted": True,
                    "conditions": [
                        {
                            "predicate": {"op": "eq", "field": "tier"},
                            "dependency_manifest": ["tier"],
                        }
                    ],
                    "deprecation_date": "2026-01-01",
                }
            ]
        )
        adapter = Neo4jAdapter(settings, driver_factory=driver_factory)
        await adapter.connect()

        # Act
        results = await adapter.resolve_technology_options("cap-1")

        # Assert
        record = results[0]
        assert record.applicability_state == "conditional"
        assert record.retracted is True
        assert len(record.conditions) == 1
        assert record.conditions[0].predicate == {"op": "eq", "field": "tier"}
        assert record.conditions[0].required_context_fields == frozenset({"tier"})
        assert record.deprecation_date == "2026-01-01"

    async def test_resolve_technology_options_with_no_matches_returns_empty(
        self, settings: Settings, driver_factory: MagicMock, driver: AsyncMock
    ) -> None:
        # Arrange
        driver.execute_query.return_value = SimpleNamespace(records=[])
        adapter = Neo4jAdapter(settings, driver_factory=driver_factory)
        await adapter.connect()

        # Act
        results = await adapter.resolve_technology_options("cap-1")

        # Assert
        assert results == []

    async def test_resolve_technology_options_before_connect_raises_runtime_error(
        self, settings: Settings, driver_factory: MagicMock
    ) -> None:
        # Arrange
        adapter = Neo4jAdapter(settings, driver_factory=driver_factory)

        # Act / Assert
        with pytest.raises(RuntimeError, match="driver"):
            await adapter.resolve_technology_options("cap-1")


class TestNeo4jAdapterSelectPatterns:
    """The select-patterns traversal (SDD-001 §3.3.1) — one Cypher call."""

    async def test_select_patterns_queries_with_the_capability_ids(
        self, settings: Settings, driver_factory: MagicMock, driver: AsyncMock
    ) -> None:
        # Arrange
        driver.execute_query.return_value = SimpleNamespace(records=[])
        adapter = Neo4jAdapter(settings, driver_factory=driver_factory)
        await adapter.connect()

        # Act
        await adapter.select_patterns(["cap-1", "cap-2"])

        # Assert
        params = driver.execute_query.call_args.args[1]
        assert params == {"capability_ids": ["cap-1", "cap-2"]}

    async def test_select_patterns_routes_read_and_targets_the_database(
        self, settings: Settings, driver_factory: MagicMock, driver: AsyncMock
    ) -> None:
        # Arrange
        driver.execute_query.return_value = SimpleNamespace(records=[])
        adapter = Neo4jAdapter(settings, driver_factory=driver_factory)
        await adapter.connect()

        # Act
        await adapter.select_patterns(["cap-1"])

        # Assert
        kwargs = driver.execute_query.call_args.kwargs
        assert kwargs["routing_"] is RoutingControl.READ
        assert kwargs["database_"] == "sofia"

    async def test_select_patterns_query_matches_the_selection_web_shape(
        self, settings: Settings, driver_factory: MagicMock, driver: AsyncMock
    ) -> None:
        # Arrange
        driver.execute_query.return_value = SimpleNamespace(records=[])
        adapter = Neo4jAdapter(settings, driver_factory=driver_factory)
        await adapter.connect()

        # Act
        await adapter.select_patterns(["cap-1"])

        # Assert — the single-store traversal (ADR-002 §6 check 4): Pattern
        # REQUIRES_CAPABILITY, Technology APPROVED_OPTION_FOR, PREFERRED_OVER,
        # plus the read-discipline structure at both the Pattern and Technology
        # levels (RETRACTS/DECIDED_ON existence, PROMOTES_TO_KNOWLEDGE/
        # HAS_CONDITION governing-decision resolution).
        query = driver.execute_query.call_args.args[0]
        assert "REQUIRES_CAPABILITY" in query
        assert "APPROVED_OPTION_FOR" in query
        assert "PREFERRED_OVER" in query
        assert "RETRACTS" in query
        assert "PROMOTES_TO_KNOWLEDGE" in query
        assert "HAS_CONDITION" in query
        assert "EXISTS {" in query

    async def test_select_patterns_with_empty_capability_ids_returns_empty_without_querying(
        self, settings: Settings, driver_factory: MagicMock, driver: AsyncMock
    ) -> None:
        # Arrange
        adapter = Neo4jAdapter(settings, driver_factory=driver_factory)
        await adapter.connect()

        # Act
        results = await adapter.select_patterns([])

        # Assert — empty-never-error (ruling #6); no wasted round-trip either.
        assert results == []
        driver.execute_query.assert_not_awaited()

    async def test_select_patterns_maps_a_single_capability_single_tech_row(
        self, settings: Settings, driver_factory: MagicMock, driver: AsyncMock
    ) -> None:
        # Arrange
        driver.execute_query.return_value = SimpleNamespace(
            records=[
                {
                    "node_id": "pattern-1",
                    "version": "2",
                    "origin_mechanism": "ingested",
                    "derivation_class": "primary",
                    "applicability_state": None,
                    "retracted": False,
                    "conditions": [],
                    "preferred_over": ["pattern-2"],
                    "capability_id": "cap-1",
                    "l1_taxonomy": "compute",
                    "l2_taxonomy": "serverless",
                    "l3_taxonomy": "functions",
                    "tech_node_id": "tech-1",
                    "tech_version": "1",
                    "tech_origin_mechanism": "ingested",
                    "tech_derivation_class": "primary",
                    "tech_tier_applicability": ["production"],
                    "tech_approved_data_classifications": ["internal"],
                    "tech_applicability_state": None,
                    "tech_deprecation_date": None,
                    "tech_retracted": False,
                    "tech_conditions": [],
                }
            ]
        )
        adapter = Neo4jAdapter(settings, driver_factory=driver_factory)
        await adapter.connect()

        # Act
        results = await adapter.select_patterns(["cap-1"])

        # Assert
        assert len(results) == 1
        pattern = results[0]
        assert pattern.node_id == "pattern-1"
        assert pattern.version == "2"
        assert pattern.origin_mechanism == "ingested"
        assert pattern.derivation_class == "primary"
        assert pattern.applicability_state == "unconditional"
        assert pattern.retracted is False
        assert pattern.conditions == ()
        assert pattern.preferred_over == ("pattern-2",)
        assert len(pattern.capabilities) == 1
        block = pattern.capabilities[0]
        assert block.capability_id == "cap-1"
        assert block.l1_taxonomy == "compute"
        assert block.l2_taxonomy == "serverless"
        assert block.l3_taxonomy == "functions"
        assert len(block.technology_options) == 1
        tech = block.technology_options[0]
        assert tech.node_id == "tech-1"
        assert tech.version == "1"
        assert tech.tier_applicability == ("production",)
        assert tech.approved_data_classifications == ("internal",)
        assert tech.applicability_state == "unconditional"
        assert tech.retracted is False
        assert tech.deprecation_date is None

    async def test_select_patterns_maps_a_capability_gap_row_as_no_tech_candidate(
        self, settings: Settings, driver_factory: MagicMock, driver: AsyncMock
    ) -> None:
        # Arrange — an OPTIONAL MATCH miss on Technology: every tech_* field is
        # null. This must map to an empty technology_options tuple, never a
        # phantom candidate.
        driver.execute_query.return_value = SimpleNamespace(
            records=[
                {
                    "node_id": "pattern-1",
                    "version": "1",
                    "origin_mechanism": "ingested",
                    "derivation_class": "primary",
                    "applicability_state": None,
                    "retracted": False,
                    "conditions": [],
                    "preferred_over": [],
                    "capability_id": "cap-gap",
                    "l1_taxonomy": None,
                    "l2_taxonomy": None,
                    "l3_taxonomy": None,
                    "tech_node_id": None,
                    "tech_version": None,
                    "tech_origin_mechanism": None,
                    "tech_derivation_class": None,
                    "tech_tier_applicability": None,
                    "tech_approved_data_classifications": None,
                    "tech_applicability_state": None,
                    "tech_deprecation_date": None,
                    "tech_retracted": False,
                    "tech_conditions": [],
                }
            ]
        )
        adapter = Neo4jAdapter(settings, driver_factory=driver_factory)
        await adapter.connect()

        # Act
        results = await adapter.select_patterns(["cap-gap"])

        # Assert
        assert len(results) == 1
        assert len(results[0].capabilities) == 1
        assert results[0].capabilities[0].technology_options == ()

    async def test_select_patterns_groups_multiple_capability_rows_under_one_pattern(
        self, settings: Settings, driver_factory: MagicMock, driver: AsyncMock
    ) -> None:
        # Arrange — two rows, same pattern, different capability.
        def _row(capability_id: str) -> dict[str, object]:
            return {
                "node_id": "pattern-1",
                "version": "1",
                "origin_mechanism": "ingested",
                "derivation_class": "primary",
                "applicability_state": None,
                "retracted": False,
                "conditions": [],
                "preferred_over": [],
                "capability_id": capability_id,
                "l1_taxonomy": None,
                "l2_taxonomy": None,
                "l3_taxonomy": None,
                "tech_node_id": None,
                "tech_version": None,
                "tech_origin_mechanism": None,
                "tech_derivation_class": None,
                "tech_tier_applicability": None,
                "tech_approved_data_classifications": None,
                "tech_applicability_state": None,
                "tech_deprecation_date": None,
                "tech_retracted": False,
                "tech_conditions": [],
            }

        driver.execute_query.return_value = SimpleNamespace(records=[_row("cap-a"), _row("cap-b")])
        adapter = Neo4jAdapter(settings, driver_factory=driver_factory)
        await adapter.connect()

        # Act
        results = await adapter.select_patterns(["cap-a", "cap-b"])

        # Assert — one pattern record, two capability blocks.
        assert len(results) == 1
        capability_ids = {block.capability_id for block in results[0].capabilities}
        assert capability_ids == {"cap-a", "cap-b"}

    async def test_select_patterns_groups_multiple_tech_rows_under_one_capability(
        self, settings: Settings, driver_factory: MagicMock, driver: AsyncMock
    ) -> None:
        # Arrange — two rows, same pattern + capability, different tech.
        def _row(tech_node_id: str) -> dict[str, object]:
            return {
                "node_id": "pattern-1",
                "version": "1",
                "origin_mechanism": "ingested",
                "derivation_class": "primary",
                "applicability_state": None,
                "retracted": False,
                "conditions": [],
                "preferred_over": [],
                "capability_id": "cap-1",
                "l1_taxonomy": None,
                "l2_taxonomy": None,
                "l3_taxonomy": None,
                "tech_node_id": tech_node_id,
                "tech_version": "1",
                "tech_origin_mechanism": "ingested",
                "tech_derivation_class": "primary",
                "tech_tier_applicability": [],
                "tech_approved_data_classifications": [],
                "tech_applicability_state": None,
                "tech_deprecation_date": None,
                "tech_retracted": False,
                "tech_conditions": [],
            }

        driver.execute_query.return_value = SimpleNamespace(
            records=[_row("tech-a"), _row("tech-b")]
        )
        adapter = Neo4jAdapter(settings, driver_factory=driver_factory)
        await adapter.connect()

        # Act
        results = await adapter.select_patterns(["cap-1"])

        # Assert — one pattern, one capability block, two tech options.
        assert len(results) == 1
        assert len(results[0].capabilities) == 1
        tech_ids = {tech.node_id for tech in results[0].capabilities[0].technology_options}
        assert tech_ids == {"tech-a", "tech-b"}

    async def test_select_patterns_maps_conditional_and_retracted_flags(
        self, settings: Settings, driver_factory: MagicMock, driver: AsyncMock
    ) -> None:
        # Arrange
        driver.execute_query.return_value = SimpleNamespace(
            records=[
                {
                    "node_id": "pattern-1",
                    "version": "1",
                    "origin_mechanism": "promoted",
                    "derivation_class": None,
                    "applicability_state": "conditional",
                    "retracted": True,
                    "conditions": [{"predicate": {"op": "eq"}, "dependency_manifest": ["tier"]}],
                    "preferred_over": [],
                    "capability_id": "cap-1",
                    "l1_taxonomy": None,
                    "l2_taxonomy": None,
                    "l3_taxonomy": None,
                    "tech_node_id": None,
                    "tech_version": None,
                    "tech_origin_mechanism": None,
                    "tech_derivation_class": None,
                    "tech_tier_applicability": None,
                    "tech_approved_data_classifications": None,
                    "tech_applicability_state": None,
                    "tech_deprecation_date": None,
                    "tech_retracted": False,
                    "tech_conditions": [],
                }
            ]
        )
        adapter = Neo4jAdapter(settings, driver_factory=driver_factory)
        await adapter.connect()

        # Act
        results = await adapter.select_patterns(["cap-1"])

        # Assert
        pattern = results[0]
        assert pattern.applicability_state == "conditional"
        assert pattern.retracted is True
        assert len(pattern.conditions) == 1
        assert pattern.conditions[0].required_context_fields == frozenset({"tier"})

    async def test_select_patterns_with_no_matches_returns_empty(
        self, settings: Settings, driver_factory: MagicMock, driver: AsyncMock
    ) -> None:
        # Arrange
        driver.execute_query.return_value = SimpleNamespace(records=[])
        adapter = Neo4jAdapter(settings, driver_factory=driver_factory)
        await adapter.connect()

        # Act
        results = await adapter.select_patterns(["cap-nonexistent"])

        # Assert
        assert results == []

    async def test_select_patterns_before_connect_raises_runtime_error(
        self, settings: Settings, driver_factory: MagicMock
    ) -> None:
        # Arrange
        adapter = Neo4jAdapter(settings, driver_factory=driver_factory)

        # Act / Assert
        with pytest.raises(RuntimeError, match="driver"):
            await adapter.select_patterns(["cap-1"])


class TestNeo4jAdapterObligationContext:
    """The obligation-context traversal (SDD-001 §3.3.4) — one Cypher call."""

    async def test_obligation_context_queries_with_the_solution_id(
        self, settings: Settings, driver_factory: MagicMock, driver: AsyncMock
    ) -> None:
        # Arrange
        driver.execute_query.return_value = SimpleNamespace(records=[])
        adapter = Neo4jAdapter(settings, driver_factory=driver_factory)
        await adapter.connect()

        # Act
        await adapter.obligation_context("sol-1")

        # Assert
        params = driver.execute_query.call_args.args[1]
        assert params == {"solution_id": "sol-1"}

    async def test_obligation_context_routes_read_and_targets_the_database(
        self, settings: Settings, driver_factory: MagicMock, driver: AsyncMock
    ) -> None:
        # Arrange
        driver.execute_query.return_value = SimpleNamespace(records=[])
        adapter = Neo4jAdapter(settings, driver_factory=driver_factory)
        await adapter.connect()

        # Act
        await adapter.obligation_context("sol-1")

        # Assert
        kwargs = driver.execute_query.call_args.kwargs
        assert kwargs["routing_"] is RoutingControl.READ
        assert kwargs["database_"] == "sofia"

    async def test_obligation_context_query_matches_the_traversal_shape(
        self, settings: Settings, driver_factory: MagicMock, driver: AsyncMock
    ) -> None:
        # Arrange
        driver.execute_query.return_value = SimpleNamespace(records=[])
        adapter = Neo4jAdapter(settings, driver_factory=driver_factory)
        await adapter.connect()

        # Act
        await adapter.obligation_context("sol-1")

        # Assert — the single-store traversal (ADR-002 §6 check 4): USES/
        # FOLLOWS entity resolution, GOVERNED_BY (entity to rule) and MANDATES
        # (rule to Technology, inbound), the current-version filter on the
        # resolved rule, plus the read-discipline structure (RETRACTS/
        # DECIDED_ON existence, PROMOTES_TO_KNOWLEDGE/HAS_CONDITION governing-
        # decision resolution).
        query = driver.execute_query.call_args.args[0]
        assert "USES" in query
        assert "FOLLOWS" in query
        assert "GOVERNED_BY" in query
        assert "MANDATES" in query
        assert "superseded_by IS NULL" in query
        assert "RETRACTS" in query
        assert "PROMOTES_TO_KNOWLEDGE" in query
        assert "HAS_CONDITION" in query
        assert "EXISTS {" in query

    async def test_obligation_context_maps_a_single_rule_row(
        self, settings: Settings, driver_factory: MagicMock, driver: AsyncMock
    ) -> None:
        # Arrange
        driver.execute_query.return_value = SimpleNamespace(
            records=[
                {
                    "node_id": "rule-1",
                    "version": "2",
                    "origin_mechanism": "ingested",
                    "derivation_class": "primary",
                    "applicability_state": None,
                    "retracted": False,
                    "conditions": [],
                    "statement": "Data at rest must be encrypted.",
                    "rule_definition": "IF classification == 'restricted' THEN require(encryption)",
                    "dependency_manifest": ["Technology"],
                    "enforcement_level": "hard",
                    "enforced_at_gate": "architecture_review",
                    "domain": "security",
                }
            ]
        )
        adapter = Neo4jAdapter(settings, driver_factory=driver_factory)
        await adapter.connect()

        # Act
        results = await adapter.obligation_context("sol-1")

        # Assert
        assert len(results) == 1
        rule = results[0]
        assert rule.node_id == "rule-1"
        assert rule.version == "2"
        assert rule.origin_mechanism == "ingested"
        assert rule.derivation_class == "primary"
        assert rule.applicability_state == "unconditional"
        assert rule.retracted is False
        assert rule.conditions == ()
        assert rule.statement == "Data at rest must be encrypted."
        assert rule.rule_definition == "IF classification == 'restricted' THEN require(encryption)"
        assert rule.dependency_manifest == ("Technology",)
        assert rule.enforcement_level == "hard"
        assert rule.enforced_at_gate == "architecture_review"
        assert rule.domain == "security"

    async def test_obligation_context_maps_multiple_distinct_rule_rows(
        self, settings: Settings, driver_factory: MagicMock, driver: AsyncMock
    ) -> None:
        # Arrange — one row standing in for a GOVERNED_BY-reached rule, one for
        # a MANDATES-reached rule.
        def _row(node_id: str) -> dict[str, object]:
            return {
                "node_id": node_id,
                "version": "1",
                "origin_mechanism": "ingested",
                "derivation_class": "primary",
                "applicability_state": None,
                "retracted": False,
                "conditions": [],
                "statement": None,
                "rule_definition": None,
                "dependency_manifest": [],
                "enforcement_level": None,
                "enforced_at_gate": None,
                "domain": None,
            }

        driver.execute_query.return_value = SimpleNamespace(
            records=[_row("rule-governed-by"), _row("rule-mandates")]
        )
        adapter = Neo4jAdapter(settings, driver_factory=driver_factory)
        await adapter.connect()

        # Act
        results = await adapter.obligation_context("sol-1")

        # Assert
        node_ids = {rule.node_id for rule in results}
        assert node_ids == {"rule-governed-by", "rule-mandates"}

    async def test_obligation_context_maps_conditional_and_retracted_flags(
        self, settings: Settings, driver_factory: MagicMock, driver: AsyncMock
    ) -> None:
        # Arrange
        driver.execute_query.return_value = SimpleNamespace(
            records=[
                {
                    "node_id": "rule-1",
                    "version": "1",
                    "origin_mechanism": "promoted",
                    "derivation_class": None,
                    "applicability_state": "conditional",
                    "retracted": True,
                    "conditions": [{"predicate": {"op": "eq"}, "dependency_manifest": ["tier"]}],
                    "statement": None,
                    "rule_definition": None,
                    "dependency_manifest": [],
                    "enforcement_level": None,
                    "enforced_at_gate": None,
                    "domain": None,
                }
            ]
        )
        adapter = Neo4jAdapter(settings, driver_factory=driver_factory)
        await adapter.connect()

        # Act
        results = await adapter.obligation_context("sol-1")

        # Assert
        rule = results[0]
        assert rule.applicability_state == "conditional"
        assert rule.retracted is True
        assert len(rule.conditions) == 1
        assert rule.conditions[0].required_context_fields == frozenset({"tier"})

    async def test_obligation_context_with_no_matches_returns_empty(
        self, settings: Settings, driver_factory: MagicMock, driver: AsyncMock
    ) -> None:
        # Arrange
        driver.execute_query.return_value = SimpleNamespace(records=[])
        adapter = Neo4jAdapter(settings, driver_factory=driver_factory)
        await adapter.connect()

        # Act
        results = await adapter.obligation_context("sol-nonexistent")

        # Assert
        assert results == []

    async def test_obligation_context_before_connect_raises_runtime_error(
        self, settings: Settings, driver_factory: MagicMock
    ) -> None:
        # Arrange
        adapter = Neo4jAdapter(settings, driver_factory=driver_factory)

        # Act / Assert
        with pytest.raises(RuntimeError, match="driver"):
            await adapter.obligation_context("sol-1")


class TestNeo4jAdapterFindPrecedents:
    """The find-precedents traversal (SDD-001 §3.3.5) — one Cypher call."""

    async def test_find_precedents_queries_with_the_criteria(
        self, settings: Settings, driver_factory: MagicMock, driver: AsyncMock
    ) -> None:
        # Arrange
        driver.execute_query.return_value = SimpleNamespace(records=[])
        adapter = Neo4jAdapter(settings, driver_factory=driver_factory)
        await adapter.connect()
        criteria = FindPrecedentsCriteria(
            capability_ids=("cap-1",),
            pattern_ids=("pattern-1",),
            technology_ids=("tech-1",),
            target_environment="production",
            gate_outcome="approved",
        )

        # Act
        await adapter.find_precedents(criteria)

        # Assert
        params = driver.execute_query.call_args.args[1]
        assert params == {
            "technology_ids": ["tech-1"],
            "pattern_ids": ["pattern-1"],
            "capability_ids": ["cap-1"],
            "target_environment": "production",
            "gate_outcome": "approved",
        }

    async def test_find_precedents_routes_read_and_targets_the_database(
        self, settings: Settings, driver_factory: MagicMock, driver: AsyncMock
    ) -> None:
        # Arrange
        driver.execute_query.return_value = SimpleNamespace(records=[])
        adapter = Neo4jAdapter(settings, driver_factory=driver_factory)
        await adapter.connect()

        # Act
        await adapter.find_precedents(
            FindPrecedentsCriteria(
                capability_ids=(),
                pattern_ids=(),
                technology_ids=("tech-1",),
                target_environment=None,
                gate_outcome=None,
            )
        )

        # Assert
        kwargs = driver.execute_query.call_args.kwargs
        assert kwargs["routing_"] is RoutingControl.READ
        assert kwargs["database_"] == "sofia"

    async def test_find_precedents_query_matches_the_traversal_shape(
        self, settings: Settings, driver_factory: MagicMock, driver: AsyncMock
    ) -> None:
        # Arrange
        driver.execute_query.return_value = SimpleNamespace(records=[])
        adapter = Neo4jAdapter(settings, driver_factory=driver_factory)
        await adapter.connect()

        # Act
        await adapter.find_precedents(
            FindPrecedentsCriteria(
                capability_ids=(),
                pattern_ids=(),
                technology_ids=("tech-1",),
                target_environment=None,
                gate_outcome=None,
            )
        )

        # Assert — the single-store traversal (ADR-002 §6 check 4): USES/
        # FOLLOWS entity resolution, the capability 2-hop FOLLOWS ->
        # REQUIRES_CAPABILITY path (never USES -> APPROVED_OPTION_FOR),
        # target_environment/gate_outcome filters, and every GateDecision via
        # DECIDED_ON.
        query = driver.execute_query.call_args.args[0]
        assert "Artifact:Solution" in query
        assert "[:USES]->(tech:Catalog:Technology)" in query
        assert "[:FOLLOWS]->(pat:Catalog:Pattern)" in query
        assert "[:FOLLOWS]->(:Catalog:Pattern)-[:REQUIRES_CAPABILITY]->" in query
        assert "target_environment" in query
        assert "DECIDED_ON" in query
        assert "GateDecision" in query
        assert "EXISTS {" in query
        # AND-across dimensions: every non-empty-dimension filter is joined
        # by AND in the WHERE clause, so a Solution failing any one is
        # excluded from the result set.
        assert query.count("AND (") >= 3

    async def test_find_precedents_with_empty_criteria_still_queries(
        self, settings: Settings, driver_factory: MagicMock, driver: AsyncMock
    ) -> None:
        # Arrange — the at-least-one-linkage guard is the OPERATION's job
        # (F4); the adapter has no opinion and queries whatever it is asked.
        driver.execute_query.return_value = SimpleNamespace(records=[])
        adapter = Neo4jAdapter(settings, driver_factory=driver_factory)
        await adapter.connect()

        # Act
        results = await adapter.find_precedents(
            FindPrecedentsCriteria(
                capability_ids=(),
                pattern_ids=(),
                technology_ids=(),
                target_environment=None,
                gate_outcome=None,
            )
        )

        # Assert
        assert results == []
        driver.execute_query.assert_awaited_once()

    async def test_find_precedents_maps_a_single_solution_row(
        self, settings: Settings, driver_factory: MagicMock, driver: AsyncMock
    ) -> None:
        # Arrange
        driver.execute_query.return_value = SimpleNamespace(
            records=[
                {
                    "node_id": "sol-1",
                    "version": "2",
                    "origin_mechanism": "authored",
                    "target_environment": "production",
                    "gate_decisions": [
                        {"outcome": "approved", "gate": "gate_1", "decision_id": "gd-1"}
                    ],
                }
            ]
        )
        adapter = Neo4jAdapter(settings, driver_factory=driver_factory)
        await adapter.connect()

        # Act
        results = await adapter.find_precedents(
            FindPrecedentsCriteria(
                capability_ids=(),
                pattern_ids=(),
                technology_ids=("tech-1",),
                target_environment=None,
                gate_outcome=None,
            )
        )

        # Assert
        assert len(results) == 1
        sol = results[0]
        assert sol.node_id == "sol-1"
        assert sol.version == "2"
        assert sol.origin_mechanism == "authored"
        assert sol.target_environment == "production"
        assert len(sol.gate_decisions) == 1
        gd = sol.gate_decisions[0]
        assert gd.outcome == "approved"
        assert gd.gate == "gate_1"
        assert gd.decision_id == "gd-1"

    async def test_find_precedents_maps_a_solution_with_no_gate_decisions(
        self, settings: Settings, driver_factory: MagicMock, driver: AsyncMock
    ) -> None:
        # Arrange — the CASE-guarded collect() must yield [], never one
        # all-null entry, when a Solution has no GateDecision at all.
        driver.execute_query.return_value = SimpleNamespace(
            records=[
                {
                    "node_id": "sol-1",
                    "version": "1",
                    "origin_mechanism": "authored",
                    "target_environment": None,
                    "gate_decisions": [],
                }
            ]
        )
        adapter = Neo4jAdapter(settings, driver_factory=driver_factory)
        await adapter.connect()

        # Act
        results = await adapter.find_precedents(
            FindPrecedentsCriteria(
                capability_ids=(),
                pattern_ids=(),
                technology_ids=("tech-1",),
                target_environment=None,
                gate_outcome=None,
            )
        )

        # Assert
        assert results[0].gate_decisions == ()

    async def test_find_precedents_maps_multiple_gate_decisions(
        self, settings: Settings, driver_factory: MagicMock, driver: AsyncMock
    ) -> None:
        # Arrange
        driver.execute_query.return_value = SimpleNamespace(
            records=[
                {
                    "node_id": "sol-1",
                    "version": "1",
                    "origin_mechanism": "authored",
                    "target_environment": "production",
                    "gate_decisions": [
                        {"outcome": "rejected", "gate": "gate_0", "decision_id": "gd-0"},
                        {"outcome": "approved", "gate": "gate_1", "decision_id": "gd-1"},
                    ],
                }
            ]
        )
        adapter = Neo4jAdapter(settings, driver_factory=driver_factory)
        await adapter.connect()

        # Act
        results = await adapter.find_precedents(
            FindPrecedentsCriteria(
                capability_ids=(),
                pattern_ids=(),
                technology_ids=("tech-1",),
                target_environment=None,
                gate_outcome=None,
            )
        )

        # Assert
        assert len(results[0].gate_decisions) == 2
        outcomes = {gd.outcome for gd in results[0].gate_decisions}
        assert outcomes == {"rejected", "approved"}

    async def test_find_precedents_with_no_matches_returns_empty(
        self, settings: Settings, driver_factory: MagicMock, driver: AsyncMock
    ) -> None:
        # Arrange
        driver.execute_query.return_value = SimpleNamespace(records=[])
        adapter = Neo4jAdapter(settings, driver_factory=driver_factory)
        await adapter.connect()

        # Act
        results = await adapter.find_precedents(
            FindPrecedentsCriteria(
                capability_ids=(),
                pattern_ids=(),
                technology_ids=("tech-nonexistent",),
                target_environment=None,
                gate_outcome=None,
            )
        )

        # Assert
        assert results == []

    async def test_find_precedents_before_connect_raises_runtime_error(
        self, settings: Settings, driver_factory: MagicMock
    ) -> None:
        # Arrange
        adapter = Neo4jAdapter(settings, driver_factory=driver_factory)

        # Act / Assert
        with pytest.raises(RuntimeError, match="driver"):
            await adapter.find_precedents(
                FindPrecedentsCriteria(
                    capability_ids=(),
                    pattern_ids=(),
                    technology_ids=("tech-1",),
                    target_environment=None,
                    gate_outcome=None,
                )
            )


class TestNeo4jAdapterReadAsOf:
    """The read-as-of traversal (SDD-001 §3.3.6), pin-mode — one Cypher call."""

    async def test_read_as_of_queries_with_business_key_and_version(
        self, settings: Settings, driver_factory: MagicMock, driver: AsyncMock
    ) -> None:
        # Arrange
        driver.execute_query.return_value = SimpleNamespace(records=[])
        adapter = Neo4jAdapter(settings, driver_factory=driver_factory)
        await adapter.connect()

        # Act
        await adapter.read_as_of("Technology", "tech-1", "3")

        # Assert
        params = driver.execute_query.call_args.args[1]
        assert params == {"business_key": "tech-1", "version": "3"}

    async def test_read_as_of_routes_read_and_targets_the_database(
        self, settings: Settings, driver_factory: MagicMock, driver: AsyncMock
    ) -> None:
        # Arrange
        driver.execute_query.return_value = SimpleNamespace(records=[])
        adapter = Neo4jAdapter(settings, driver_factory=driver_factory)
        await adapter.connect()

        # Act
        await adapter.read_as_of("Technology", "tech-1", "3")

        # Assert
        kwargs = driver.execute_query.call_args.kwargs
        assert kwargs["routing_"] is RoutingControl.READ
        assert kwargs["database_"] == "sofia"

    @pytest.mark.parametrize(
        ("node_kind", "label", "pk_property"),
        [
            ("Pattern", "Catalog:Pattern", "pattern_id"),
            ("Technology", "Catalog:Technology", "technology_id"),
            ("Capability", "Catalog:Capability", "capability_id"),
            ("IacTemplate", "Catalog:IacTemplate", "iac_template_id"),
            ("Standard", "Standards:Standard", "standard_id"),
            ("PolicyRule", "Standards:PolicyRule", "policy_rule_id"),
        ],
    )
    async def test_read_as_of_query_matches_the_per_label_mapping(
        self,
        node_kind: str,
        label: str,
        pk_property: str,
        settings: Settings,
        driver_factory: MagicMock,
        driver: AsyncMock,
    ) -> None:
        # Arrange
        driver.execute_query.return_value = SimpleNamespace(records=[])
        adapter = Neo4jAdapter(settings, driver_factory=driver_factory)
        await adapter.connect()

        # Act
        await adapter.read_as_of(node_kind, "key-1", "1")  # type: ignore[arg-type]

        # Assert — the single-store traversal (ADR-002 §6 check 4): the
        # correct label + PK property interpolated, no status/superseded_by
        # filter (a pin resolves the exact version even if superseded), plus
        # the read-discipline structure (RETRACTS/DECIDED_ON existence,
        # PROMOTES_TO_KNOWLEDGE/HAS_CONDITION governing-decision resolution).
        query = driver.execute_query.call_args.args[0]
        assert f"MATCH (n:{label} {{{pk_property}: $business_key, version: $version}})" in query
        assert f"n.{pk_property} AS node_id" in query
        assert "status" not in query
        assert "superseded_by" not in query
        assert "RETRACTS" in query
        assert "PROMOTES_TO_KNOWLEDGE" in query
        assert "HAS_CONDITION" in query
        assert "EXISTS {" in query

    async def test_read_as_of_maps_a_resolved_row(
        self, settings: Settings, driver_factory: MagicMock, driver: AsyncMock
    ) -> None:
        # Arrange
        driver.execute_query.return_value = SimpleNamespace(
            records=[
                {
                    "node_id": "tech-1",
                    "version": "3",
                    "origin_mechanism": "ingested",
                    "derivation_class": "primary",
                    "effective_from": None,
                    "applicability_state": None,
                    "retracted": False,
                    "conditions": [],
                }
            ]
        )
        adapter = Neo4jAdapter(settings, driver_factory=driver_factory)
        await adapter.connect()

        # Act
        record = await adapter.read_as_of("Technology", "tech-1", "3")

        # Assert
        assert record is not None
        assert record.node_id == "tech-1"
        assert record.plane_labels == ("Catalog",)
        assert record.version == "3"
        assert record.origin_mechanism == "ingested"
        assert record.derivation_class == "primary"
        assert record.effective_from is None
        assert record.effective_to is None
        assert record.applicability_state == "unconditional"
        assert record.retracted is False
        assert record.conditions == ()

    async def test_read_as_of_maps_effective_from_for_pattern(
        self, settings: Settings, driver_factory: MagicMock, driver: AsyncMock
    ) -> None:
        # Arrange — the one label DDR-002 §2.1 declares effective_from on.
        driver.execute_query.return_value = SimpleNamespace(
            records=[
                {
                    "node_id": "pattern-1",
                    "version": "1",
                    "origin_mechanism": "ingested",
                    "derivation_class": "primary",
                    "effective_from": "2026-01-01T00:00:00Z",
                    "applicability_state": None,
                    "retracted": False,
                    "conditions": [],
                }
            ]
        )
        adapter = Neo4jAdapter(settings, driver_factory=driver_factory)
        await adapter.connect()

        # Act
        record = await adapter.read_as_of("Pattern", "pattern-1", "1")

        # Assert
        assert record is not None
        assert record.effective_from == "2026-01-01T00:00:00Z"
        assert record.effective_to is None
        assert record.plane_labels == ("Catalog",)

    async def test_read_as_of_maps_a_standards_node_kind(
        self, settings: Settings, driver_factory: MagicMock, driver: AsyncMock
    ) -> None:
        # Arrange
        driver.execute_query.return_value = SimpleNamespace(
            records=[
                {
                    "node_id": "rule-1",
                    "version": "1",
                    "origin_mechanism": "ingested",
                    "derivation_class": "primary",
                    "effective_from": None,
                    "applicability_state": None,
                    "retracted": False,
                    "conditions": [],
                }
            ]
        )
        adapter = Neo4jAdapter(settings, driver_factory=driver_factory)
        await adapter.connect()

        # Act
        record = await adapter.read_as_of("PolicyRule", "rule-1", "1")

        # Assert
        assert record is not None
        assert record.plane_labels == ("Standards",)

    async def test_read_as_of_maps_conditional_and_retracted_flags(
        self, settings: Settings, driver_factory: MagicMock, driver: AsyncMock
    ) -> None:
        # Arrange
        driver.execute_query.return_value = SimpleNamespace(
            records=[
                {
                    "node_id": "tech-1",
                    "version": "1",
                    "origin_mechanism": "promoted",
                    "derivation_class": None,
                    "effective_from": None,
                    "applicability_state": "conditional",
                    "retracted": True,
                    "conditions": [{"predicate": {"op": "eq"}, "dependency_manifest": ["tier"]}],
                }
            ]
        )
        adapter = Neo4jAdapter(settings, driver_factory=driver_factory)
        await adapter.connect()

        # Act
        record = await adapter.read_as_of("Technology", "tech-1", "1")

        # Assert
        assert record is not None
        assert record.applicability_state == "conditional"
        assert record.retracted is True
        assert len(record.conditions) == 1
        assert record.conditions[0].required_context_fields == frozenset({"tier"})

    async def test_read_as_of_with_no_match_returns_none(
        self, settings: Settings, driver_factory: MagicMock, driver: AsyncMock
    ) -> None:
        # Arrange
        driver.execute_query.return_value = SimpleNamespace(records=[])
        adapter = Neo4jAdapter(settings, driver_factory=driver_factory)
        await adapter.connect()

        # Act
        record = await adapter.read_as_of("Technology", "tech-nonexistent", "1")

        # Assert
        assert record is None

    async def test_read_as_of_before_connect_raises_runtime_error(
        self, settings: Settings, driver_factory: MagicMock
    ) -> None:
        # Arrange
        adapter = Neo4jAdapter(settings, driver_factory=driver_factory)

        # Act / Assert
        with pytest.raises(RuntimeError, match="driver"):
            await adapter.read_as_of("Technology", "tech-1", "1")


def _row(**overrides: object) -> dict[str, object]:
    """One `RETURN` row for the citation-lookup query, entry_found + empty by
    default — tests override only what they exercise."""
    base: dict[str, object] = {
        "entry_found": True,
        "entry_statuses": [],
        "citation_rows": [],
    }
    base.update(overrides)
    return base


class TestNeo4jAdapterCitationLookup:
    """The citation-lookup traversal (SDD-001 §3.3.7) — one Cypher call, the
    audit posture (no read-discipline resolution beyond the raw marker
    facts), and keyset pagination via a limit+1 fetch."""

    async def test_citation_lookup_queries_with_the_full_parameter_set(
        self, settings: Settings, driver_factory: MagicMock, driver: AsyncMock
    ) -> None:
        # Arrange
        driver.execute_query.return_value = SimpleNamespace(records=[_row()])
        adapter = Neo4jAdapter(settings, driver_factory=driver_factory)
        await adapter.connect()

        # Act
        await adapter.citation_lookup(
            "Technology", "tech-1", "3", "per_version", "ev-5", 25
        )

        # Assert — fetch_limit is limit+1, the has-more probe.
        params = driver.execute_query.call_args.args[1]
        assert params == {
            "business_key": "tech-1",
            "version": "3",
            "after_evidence_id": "ev-5",
            "fetch_limit": 26,
        }

    async def test_citation_lookup_business_key_wide_passes_no_version(
        self, settings: Settings, driver_factory: MagicMock, driver: AsyncMock
    ) -> None:
        # Arrange
        driver.execute_query.return_value = SimpleNamespace(records=[_row()])
        adapter = Neo4jAdapter(settings, driver_factory=driver_factory)
        await adapter.connect()

        # Act
        await adapter.citation_lookup(
            "Technology", "tech-1", None, "business_key_wide", None, 50
        )

        # Assert
        params = driver.execute_query.call_args.args[1]
        assert params["version"] is None
        assert params["after_evidence_id"] is None

    async def test_citation_lookup_routes_read_and_targets_the_database(
        self, settings: Settings, driver_factory: MagicMock, driver: AsyncMock
    ) -> None:
        # Arrange
        driver.execute_query.return_value = SimpleNamespace(records=[_row()])
        adapter = Neo4jAdapter(settings, driver_factory=driver_factory)
        await adapter.connect()

        # Act
        await adapter.citation_lookup("Technology", "tech-1", "3", "per_version", None, 50)

        # Assert
        kwargs = driver.execute_query.call_args.kwargs
        assert kwargs["routing_"] is RoutingControl.READ
        assert kwargs["database_"] == "sofia"

    @pytest.mark.parametrize(
        ("node_kind", "label", "pk_property"),
        [
            ("Pattern", "Catalog:Pattern", "pattern_id"),
            ("Technology", "Catalog:Technology", "technology_id"),
            ("Capability", "Catalog:Capability", "capability_id"),
            ("IacTemplate", "Catalog:IacTemplate", "iac_template_id"),
            ("Standard", "Standards:Standard", "standard_id"),
            ("PolicyRule", "Standards:PolicyRule", "policy_rule_id"),
        ],
    )
    async def test_citation_lookup_query_matches_the_per_label_mapping_and_traversal_shape(
        self,
        node_kind: str,
        label: str,
        pk_property: str,
        settings: Settings,
        driver_factory: MagicMock,
        driver: AsyncMock,
    ) -> None:
        # Arrange
        driver.execute_query.return_value = SimpleNamespace(records=[_row()])
        adapter = Neo4jAdapter(settings, driver_factory=driver_factory)
        await adapter.connect()

        # Act
        await adapter.citation_lookup(node_kind, "key-1", "1", "per_version", None, 50)  # type: ignore[arg-type]

        # Assert — the reuse of the read-as-of label/PK map (no second map),
        # the reverse SOURCED_FROM/SUPPORTED_BY/CONTAINS traversal (no new
        # index — DDR-002 §7's reverse-lookup note, SDD-001 §3.3.7), and the
        # audit posture: RETRACTS/DECIDED_ON existence for the marker facts,
        # but no HAS_CONDITION resolution (no Condition set is built).
        query = driver.execute_query.call_args.args[0]
        assert f"MATCH (n:{label} {{{pk_property}: $business_key}})" in query
        assert "SOURCED_FROM" in query
        assert "SUPPORTED_BY" in query
        assert "CONTAINS" in query
        assert "RETRACTS" in query
        assert "HAS_CONDITION" not in query

    async def test_citation_lookup_maps_entry_found_false(
        self, settings: Settings, driver_factory: MagicMock, driver: AsyncMock
    ) -> None:
        # Arrange — a truly-absent entry.
        driver.execute_query.return_value = SimpleNamespace(
            records=[_row(entry_found=False)]
        )
        adapter = Neo4jAdapter(settings, driver_factory=driver_factory)
        await adapter.connect()

        # Act
        page = await adapter.citation_lookup(
            "Technology", "tech-x", "1", "per_version", None, 50
        )

        # Assert
        assert page.entry_found is False
        assert page.citations == ()
        assert page.entry_statuses == ()

    async def test_citation_lookup_maps_entry_statuses(
        self, settings: Settings, driver_factory: MagicMock, driver: AsyncMock
    ) -> None:
        # Arrange
        driver.execute_query.return_value = SimpleNamespace(
            records=[
                _row(
                    entry_statuses=[
                        {
                            "version": "2",
                            "is_superseded": True,
                            "is_retracted": False,
                            "is_conditional": True,
                        }
                    ]
                )
            ]
        )
        adapter = Neo4jAdapter(settings, driver_factory=driver_factory)
        await adapter.connect()

        # Act
        page = await adapter.citation_lookup(
            "Technology", "tech-1", "2", "per_version", None, 50
        )

        # Assert
        assert len(page.entry_statuses) == 1
        status = page.entry_statuses[0]
        assert status.version == "2"
        assert status.is_superseded is True
        assert status.is_retracted is False
        assert status.is_conditional is True

    async def test_citation_lookup_maps_citations_with_owners(
        self, settings: Settings, driver_factory: MagicMock, driver: AsyncMock
    ) -> None:
        # Arrange
        driver.execute_query.return_value = SimpleNamespace(
            records=[
                _row(
                    citation_rows=[
                        {
                            "evidence_id": "ev-1",
                            "fact_summary": "a fact",
                            "confidence": 0.8,
                            "weight": 1.0,
                            "source_node_version": "1",
                            "observed_at": "2026-07-24T00:00:00Z",
                            "owners": [
                                {
                                    "progress_id": "prog-1",
                                    "conclusion_type": "TechnologySelection",
                                    "reasoner_category": "encoded_reasoning",
                                    "authoritative": True,
                                    "confidence": 0.9,
                                    "session_id": "sess-1",
                                },
                                {
                                    "progress_id": "prog-2",
                                    "conclusion_type": "RiskSignal",
                                    "reasoner_category": "llm_advisory",
                                    "authoritative": False,
                                    "confidence": None,
                                    "session_id": "sess-2",
                                },
                            ],
                        }
                    ]
                )
            ]
        )
        adapter = Neo4jAdapter(settings, driver_factory=driver_factory)
        await adapter.connect()

        # Act
        page = await adapter.citation_lookup(
            "Technology", "tech-1", "1", "per_version", None, 50
        )

        # Assert
        assert len(page.citations) == 1
        citation = page.citations[0]
        assert citation.evidence_id == "ev-1"
        assert citation.fact_summary == "a fact"
        assert len(citation.owners) == 2
        assert {owner.progress_id for owner in citation.owners} == {"prog-1", "prog-2"}

    async def test_citation_lookup_page_at_the_limit_has_no_next_cursor(
        self, settings: Settings, driver_factory: MagicMock, driver: AsyncMock
    ) -> None:
        # Arrange — fetch_limit rows returned == limit + 1 NOT reached: no more.
        driver.execute_query.return_value = SimpleNamespace(
            records=[
                _row(
                    citation_rows=[
                        {
                            "evidence_id": eid,
                            "fact_summary": None,
                            "confidence": None,
                            "weight": None,
                            "source_node_version": None,
                            "observed_at": None,
                            "owners": [],
                        }
                        for eid in ["ev-1", "ev-2"]
                    ]
                )
            ]
        )
        adapter = Neo4jAdapter(settings, driver_factory=driver_factory)
        await adapter.connect()

        # Act
        page = await adapter.citation_lookup(
            "Technology", "tech-1", "1", "per_version", None, 2
        )

        # Assert
        assert [c.evidence_id for c in page.citations] == ["ev-1", "ev-2"]
        assert page.next_cursor is None

    async def test_citation_lookup_page_over_the_limit_sets_next_cursor(
        self, settings: Settings, driver_factory: MagicMock, driver: AsyncMock
    ) -> None:
        # Arrange — 3 rows returned for limit=2 (fetch_limit=3): one more page.
        driver.execute_query.return_value = SimpleNamespace(
            records=[
                _row(
                    citation_rows=[
                        {
                            "evidence_id": eid,
                            "fact_summary": None,
                            "confidence": None,
                            "weight": None,
                            "source_node_version": None,
                            "observed_at": None,
                            "owners": [],
                        }
                        for eid in ["ev-1", "ev-2", "ev-3"]
                    ]
                )
            ]
        )
        adapter = Neo4jAdapter(settings, driver_factory=driver_factory)
        await adapter.connect()

        # Act
        page = await adapter.citation_lookup(
            "Technology", "tech-1", "1", "per_version", None, 2
        )

        # Assert — the 3rd row is truncated off the page, never surfaced.
        assert [c.evidence_id for c in page.citations] == ["ev-1", "ev-2"]
        assert page.next_cursor == "ev-2"

    async def test_citation_lookup_before_connect_raises_runtime_error(
        self, settings: Settings, driver_factory: MagicMock
    ) -> None:
        # Arrange
        adapter = Neo4jAdapter(settings, driver_factory=driver_factory)

        # Act / Assert
        with pytest.raises(RuntimeError, match="driver"):
            await adapter.citation_lookup(
                "Technology", "tech-1", "1", "per_version", None, 50
            )


def _provenance_row(**overrides: object) -> dict[str, object]:
    """One `RETURN` row for the provenance-of query, entry_found + promoted +
    a minimal candidate/decision by default; empty frozen entries."""
    base: dict[str, object] = {
        "entry_found": True,
        "is_promoted": True,
        "origin_mechanism": "promoted",
        "candidate": {
            "candidate_id": "cand-1",
            "proposal_kind": "promotion",
            "status": "promoted",
        },
        "is_superseded": False,
        "is_retracted": False,
        "is_conditional": False,
        "governing_decision": {
            "decision_id": "dec-1",
            "outcome": "approved",
            "decided_at": "2026-07-01T00:00:00Z",
        },
        "provenance_summary_id": "summary-1",
        "frozen_layer_present": True,
        "frozen_entries": [],
    }
    base.update(overrides)
    return base


class TestNeo4jAdapterProvenanceOf:
    """The provenance-of traversal (SDD-001 §3.3.8) — one Cypher call, the
    audit posture, single-subject and unpaginated."""

    async def test_provenance_of_queries_with_business_key_and_version(
        self, settings: Settings, driver_factory: MagicMock, driver: AsyncMock
    ) -> None:
        # Arrange
        driver.execute_query.return_value = SimpleNamespace(records=[_provenance_row()])
        adapter = Neo4jAdapter(settings, driver_factory=driver_factory)
        await adapter.connect()

        # Act
        await adapter.provenance_of("Technology", "tech-1", "3")

        # Assert
        params = driver.execute_query.call_args.args[1]
        assert params == {"business_key": "tech-1", "version": "3"}

    async def test_provenance_of_routes_read_and_targets_the_database(
        self, settings: Settings, driver_factory: MagicMock, driver: AsyncMock
    ) -> None:
        # Arrange
        driver.execute_query.return_value = SimpleNamespace(records=[_provenance_row()])
        adapter = Neo4jAdapter(settings, driver_factory=driver_factory)
        await adapter.connect()

        # Act
        await adapter.provenance_of("Technology", "tech-1", "3")

        # Assert
        kwargs = driver.execute_query.call_args.kwargs
        assert kwargs["routing_"] is RoutingControl.READ
        assert kwargs["database_"] == "sofia"

    @pytest.mark.parametrize(
        ("node_kind", "label", "pk_property"),
        [
            ("Pattern", "Catalog:Pattern", "pattern_id"),
            ("Technology", "Catalog:Technology", "technology_id"),
            ("Capability", "Catalog:Capability", "capability_id"),
            ("IacTemplate", "Catalog:IacTemplate", "iac_template_id"),
            ("Standard", "Standards:Standard", "standard_id"),
            ("PolicyRule", "Standards:PolicyRule", "policy_rule_id"),
        ],
    )
    async def test_provenance_of_query_matches_the_per_label_mapping_and_traversal_shape(
        self,
        node_kind: str,
        label: str,
        pk_property: str,
        settings: Settings,
        driver_factory: MagicMock,
        driver: AsyncMock,
    ) -> None:
        # Arrange
        driver.execute_query.return_value = SimpleNamespace(records=[_provenance_row()])
        adapter = Neo4jAdapter(settings, driver_factory=driver_factory)
        await adapter.connect()

        # Act
        await adapter.provenance_of(node_kind, "key-1", "1")  # type: ignore[arg-type]

        # Assert — the reuse of the read-as-of label/PK map (no second map),
        # the promotion/governing-decision/frozen-summary traversal, and NO
        # re-traversal to owning reasoning (SUPPORTED_BY/CONTAINS absent —
        # that is citation-lookup's job, not this op's).
        query = driver.execute_query.call_args.args[0]
        assert f"MATCH (n:{label} {{{pk_property}: $business_key, version: $version}})" in query
        assert "PROMOTES_TO_KNOWLEDGE" in query
        assert "MATERIALIZES_PROVENANCE_OF" in query
        assert "DECIDED_ON" in query
        assert "frozen_evidence_ids" in query
        assert "RETRACTS" in query
        assert "SUPPORTED_BY" not in query
        assert "CONTAINS" not in query
        assert "HAS_CONDITION" not in query

    async def test_provenance_of_maps_entry_found_false(
        self, settings: Settings, driver_factory: MagicMock, driver: AsyncMock
    ) -> None:
        # Arrange — a truly-absent entry.
        driver.execute_query.return_value = SimpleNamespace(
            records=[
                _provenance_row(
                    entry_found=False,
                    is_promoted=False,
                    origin_mechanism=None,
                    candidate=None,
                    governing_decision=None,
                    provenance_summary_id=None,
                    frozen_layer_present=False,
                )
            ]
        )
        adapter = Neo4jAdapter(settings, driver_factory=driver_factory)
        await adapter.connect()

        # Act
        page = await adapter.provenance_of("Technology", "tech-x", "1")

        # Assert
        assert page.entry_found is False
        assert page.is_promoted is False
        assert page.candidate is None
        assert page.governing_decision is None

    async def test_provenance_of_maps_existing_but_not_promoted(
        self, settings: Settings, driver_factory: MagicMock, driver: AsyncMock
    ) -> None:
        # Arrange — the node exists (e.g. ingested) but was never promoted.
        driver.execute_query.return_value = SimpleNamespace(
            records=[
                _provenance_row(
                    is_promoted=False,
                    origin_mechanism="ingested",
                    candidate=None,
                    governing_decision=None,
                    provenance_summary_id=None,
                    frozen_layer_present=False,
                )
            ]
        )
        adapter = Neo4jAdapter(settings, driver_factory=driver_factory)
        await adapter.connect()

        # Act
        page = await adapter.provenance_of("Technology", "tech-1", "1")

        # Assert
        assert page.entry_found is True
        assert page.is_promoted is False
        assert page.origin_mechanism == "ingested"

    async def test_provenance_of_maps_candidate_and_governing_decision(
        self, settings: Settings, driver_factory: MagicMock, driver: AsyncMock
    ) -> None:
        # Arrange
        driver.execute_query.return_value = SimpleNamespace(records=[_provenance_row()])
        adapter = Neo4jAdapter(settings, driver_factory=driver_factory)
        await adapter.connect()

        # Act
        page = await adapter.provenance_of("Technology", "tech-1", "3")

        # Assert
        assert page.candidate is not None
        assert page.candidate.candidate_id == "cand-1"
        assert page.candidate.proposal_kind == "promotion"
        assert page.candidate.status == "promoted"
        assert page.governing_decision is not None
        assert page.governing_decision.decision_id == "dec-1"
        assert page.governing_decision.outcome == "approved"
        assert page.governing_decision.decided_at == "2026-07-01T00:00:00Z"

    async def test_provenance_of_maps_entry_markers(
        self, settings: Settings, driver_factory: MagicMock, driver: AsyncMock
    ) -> None:
        # Arrange
        driver.execute_query.return_value = SimpleNamespace(
            records=[
                _provenance_row(is_superseded=True, is_retracted=True, is_conditional=True)
            ]
        )
        adapter = Neo4jAdapter(settings, driver_factory=driver_factory)
        await adapter.connect()

        # Act
        page = await adapter.provenance_of("Technology", "tech-1", "1")

        # Assert
        assert page.is_superseded is True
        assert page.is_retracted is True
        assert page.is_conditional is True

    async def test_provenance_of_maps_frozen_layer_present_false(
        self, settings: Settings, driver_factory: MagicMock, driver: AsyncMock
    ) -> None:
        # Arrange — the candidate resolves but no ProvenanceSummary exists.
        driver.execute_query.return_value = SimpleNamespace(
            records=[
                _provenance_row(frozen_layer_present=False, provenance_summary_id=None)
            ]
        )
        adapter = Neo4jAdapter(settings, driver_factory=driver_factory)
        await adapter.connect()

        # Act
        page = await adapter.provenance_of("Technology", "tech-1", "1")

        # Assert — never raises; candidate/governing_decision untouched.
        assert page.frozen_layer_present is False
        assert page.provenance_summary_id is None
        assert page.candidate is not None

    async def test_provenance_of_maps_frozen_entries_with_live_overlay(
        self, settings: Settings, driver_factory: MagicMock, driver: AsyncMock
    ) -> None:
        # Arrange
        driver.execute_query.return_value = SimpleNamespace(
            records=[
                _provenance_row(
                    frozen_entries=[
                        {
                            "evidence_id": "ev-1",
                            "frozen_fact_summary": "frozen fact",
                            "frozen_source_version_pin": "1",
                            "frozen_source_node_ref": "tech-1",
                            "is_live": True,
                            "live_fact_summary": "live fact",
                            "live_confidence": 0.9,
                            "live_weight": 1.0,
                            "live_source_node_version": "2",
                            "live_observed_at": "2026-07-20T00:00:00Z",
                        }
                    ]
                )
            ]
        )
        adapter = Neo4jAdapter(settings, driver_factory=driver_factory)
        await adapter.connect()

        # Act
        page = await adapter.provenance_of("Technology", "tech-1", "1")

        # Assert
        assert len(page.entries) == 1
        entry = page.entries[0]
        assert entry.evidence_id == "ev-1"
        assert entry.frozen_source_version_pin == "1"
        assert entry.is_live is True
        assert entry.live_source_node_version == "2"

    async def test_provenance_of_maps_frozen_only_entries(
        self, settings: Settings, driver_factory: MagicMock, driver: AsyncMock
    ) -> None:
        # Arrange — the originating Evidence has expired out of retention.
        driver.execute_query.return_value = SimpleNamespace(
            records=[
                _provenance_row(
                    frozen_entries=[
                        {
                            "evidence_id": "ev-1",
                            "frozen_fact_summary": "frozen fact",
                            "frozen_source_version_pin": "1",
                            "frozen_source_node_ref": "tech-1",
                            "is_live": False,
                            "live_fact_summary": None,
                            "live_confidence": None,
                            "live_weight": None,
                            "live_source_node_version": None,
                            "live_observed_at": None,
                        }
                    ]
                )
            ]
        )
        adapter = Neo4jAdapter(settings, driver_factory=driver_factory)
        await adapter.connect()

        # Act
        page = await adapter.provenance_of("Technology", "tech-1", "1")

        # Assert
        assert len(page.entries) == 1
        entry = page.entries[0]
        assert entry.is_live is False
        assert entry.live_source_node_version is None

    async def test_provenance_of_before_connect_raises_runtime_error(
        self, settings: Settings, driver_factory: MagicMock
    ) -> None:
        # Arrange
        adapter = Neo4jAdapter(settings, driver_factory=driver_factory)

        # Act / Assert
        with pytest.raises(RuntimeError, match="driver"):
            await adapter.provenance_of("Technology", "tech-1", "1")


def _cited_node_row(**overrides: object) -> dict[str, object]:
    """One `resolved_pin`/`would_have_used` entry map for the session-trace
    query, a mapped-label citation by default."""
    base: dict[str, object] = {
        "node_kind": "Technology",
        "node_id": "tech-1",
        "version": "1",
        "is_superseded": False,
        "is_retracted": False,
        "is_conditional": False,
    }
    base.update(overrides)
    return base


def _evidence_row(**overrides: object) -> dict[str, object]:
    base: dict[str, object] = {
        "evidence_id": "ev-1",
        "fact_summary": "a fact",
        "confidence": 0.8,
        "weight": 1.0,
        "source_node_version": "1",
        "observed_at": "2026-07-01T00:00:00Z",
        "resolved_pin": _cited_node_row(),
    }
    base.update(overrides)
    return base


def _rejected_row(**overrides: object) -> dict[str, object]:
    base: dict[str, object] = {
        "rejected_id": "rej-1",
        "candidate_type": "Technology",
        "rejection_reason": "cost",
        "score_delta": -0.2,
        "human_accepted": False,
        "would_have_used": [],
    }
    base.update(overrides)
    return base


def _conclusion_row(**overrides: object) -> dict[str, object]:
    base: dict[str, object] = {
        "progress_id": "prog-1",
        "conclusion_type": "TechnologySelection",
        "reasoner_category": "encoded_reasoning",
        "authoritative": True,
        "confidence": 0.9,
        "overridden_by_human": False,
        "created_at": "2026-07-01T00:00:00Z",
        "evidence": [_evidence_row()],
        "rejected_alternatives": [_rejected_row()],
    }
    base.update(overrides)
    return base


def _session_row(**overrides: object) -> dict[str, object]:
    base: dict[str, object] = {
        "session_found": True,
        "conclusion_rows": [_conclusion_row()],
        "led_to_rows": [{"from_progress_id": "prog-1", "to_progress_id": "prog-2"}],
    }
    base.update(overrides)
    return base


class TestNeo4jAdapterSessionTrace:
    """The session-trace traversal (SDD-001 §3.3.9) — one Cypher call, the
    RG explainability traversal, and the scoped cited-node PK map (relay
    delta resolution)."""

    async def test_session_trace_queries_with_session_id(
        self, settings: Settings, driver_factory: MagicMock, driver: AsyncMock
    ) -> None:
        # Arrange
        driver.execute_query.return_value = SimpleNamespace(records=[_session_row()])
        adapter = Neo4jAdapter(settings, driver_factory=driver_factory)
        await adapter.connect()

        # Act
        await adapter.session_trace("sess-1")

        # Assert
        params = driver.execute_query.call_args.args[1]
        assert params == {"session_id": "sess-1"}

    async def test_session_trace_routes_read_and_targets_the_database(
        self, settings: Settings, driver_factory: MagicMock, driver: AsyncMock
    ) -> None:
        # Arrange
        driver.execute_query.return_value = SimpleNamespace(records=[_session_row()])
        adapter = Neo4jAdapter(settings, driver_factory=driver_factory)
        await adapter.connect()

        # Act
        await adapter.session_trace("sess-1")

        # Assert
        kwargs = driver.execute_query.call_args.kwargs
        assert kwargs["routing_"] is RoutingControl.READ
        assert kwargs["database_"] == "sofia"

    async def test_session_trace_query_matches_the_rg_traversal_shape(
        self, settings: Settings, driver_factory: MagicMock, driver: AsyncMock
    ) -> None:
        # Arrange
        driver.execute_query.return_value = SimpleNamespace(records=[_session_row()])
        adapter = Neo4jAdapter(settings, driver_factory=driver_factory)
        await adapter.connect()

        # Act
        await adapter.session_trace("sess-1")

        # Assert — the full RG traversal (ST-D2), no read-discipline
        # resolution (no HAS_CONDITION — trio-free by inapplicability).
        query = driver.execute_query.call_args.args[0]
        assert "ReasoningSession {session_id: $session_id}" in query
        assert "CONTAINS" in query
        assert "SUPPORTED_BY" in query
        assert "SOURCED_FROM" in query
        assert "REJECTED" in query
        assert "WOULD_HAVE_USED" in query
        assert "LED_TO" in query
        assert "HAS_CONDITION" not in query

    async def test_session_trace_query_embeds_the_scoped_cited_node_pk_map(
        self, settings: Settings, driver_factory: MagicMock, driver: AsyncMock
    ) -> None:
        # Arrange
        driver.execute_query.return_value = SimpleNamespace(records=[_session_row()])
        adapter = Neo4jAdapter(settings, driver_factory=driver_factory)
        await adapter.connect()

        # Act
        await adapter.session_trace("sess-1")

        # Assert — every relay-delta-scoped label's PK property is embedded,
        # confirming node_id resolution covers the full ratified scope
        # (Catalog/Standards/Environment/Operational/Cost citable labels).
        query = driver.execute_query.call_args.args[0]
        for pk_property in (
            "pattern_id",
            "technology_id",
            "capability_id",
            "iac_template_id",
            "standard_id",
            "policy_rule_id",
            "control_id",
            "deployed_service_id",
            "environment_id",
            "ci_id",
            "observed_pattern_id",
            "estimate_id",
        ):
            assert pk_property in query

    async def test_session_trace_maps_session_found_false(
        self, settings: Settings, driver_factory: MagicMock, driver: AsyncMock
    ) -> None:
        # Arrange — a truly-absent session.
        driver.execute_query.return_value = SimpleNamespace(
            records=[_session_row(session_found=False, conclusion_rows=[], led_to_rows=[])]
        )
        adapter = Neo4jAdapter(settings, driver_factory=driver_factory)
        await adapter.connect()

        # Act
        page = await adapter.session_trace("sess-x")

        # Assert
        assert page.session_found is False
        assert page.conclusions == ()
        assert page.led_to == ()

    async def test_session_trace_maps_a_full_conclusion_tree(
        self, settings: Settings, driver_factory: MagicMock, driver: AsyncMock
    ) -> None:
        # Arrange
        driver.execute_query.return_value = SimpleNamespace(records=[_session_row()])
        adapter = Neo4jAdapter(settings, driver_factory=driver_factory)
        await adapter.connect()

        # Act
        page = await adapter.session_trace("sess-1")

        # Assert
        assert page.session_found is True
        assert len(page.conclusions) == 1
        conclusion = page.conclusions[0]
        assert conclusion.progress_id == "prog-1"
        assert conclusion.conclusion_type == "TechnologySelection"
        assert len(conclusion.evidence) == 1
        evidence = conclusion.evidence[0]
        assert evidence.evidence_id == "ev-1"
        assert evidence.resolved_pin is not None
        assert evidence.resolved_pin.node_kind == "Technology"
        assert evidence.resolved_pin.node_id == "tech-1"
        assert len(conclusion.rejected_alternatives) == 1
        assert conclusion.rejected_alternatives[0].rejected_id == "rej-1"
        assert len(page.led_to) == 1
        assert page.led_to[0].from_progress_id == "prog-1"
        assert page.led_to[0].to_progress_id == "prog-2"

    async def test_session_trace_maps_resolved_pin_none_when_no_sourced_from(
        self, settings: Settings, driver_factory: MagicMock, driver: AsyncMock
    ) -> None:
        # Arrange
        driver.execute_query.return_value = SimpleNamespace(
            records=[
                _session_row(
                    conclusion_rows=[
                        _conclusion_row(evidence=[_evidence_row(resolved_pin=None)])
                    ]
                )
            ]
        )
        adapter = Neo4jAdapter(settings, driver_factory=driver_factory)
        await adapter.connect()

        # Act
        page = await adapter.session_trace("sess-1")

        # Assert
        assert page.conclusions[0].evidence[0].resolved_pin is None

    async def test_session_trace_maps_would_have_used_refs(
        self, settings: Settings, driver_factory: MagicMock, driver: AsyncMock
    ) -> None:
        # Arrange
        driver.execute_query.return_value = SimpleNamespace(
            records=[
                _session_row(
                    conclusion_rows=[
                        _conclusion_row(
                            rejected_alternatives=[
                                _rejected_row(
                                    would_have_used=[_cited_node_row(node_id="tech-2")]
                                )
                            ]
                        )
                    ]
                )
            ]
        )
        adapter = Neo4jAdapter(settings, driver_factory=driver_factory)
        await adapter.connect()

        # Act
        page = await adapter.session_trace("sess-1")

        # Assert
        would_have_used = page.conclusions[0].rejected_alternatives[0].would_have_used
        assert len(would_have_used) == 1
        assert would_have_used[0].node_id == "tech-2"

    async def test_session_trace_before_connect_raises_runtime_error(
        self, settings: Settings, driver_factory: MagicMock
    ) -> None:
        # Arrange
        adapter = Neo4jAdapter(settings, driver_factory=driver_factory)

        # Act / Assert
        with pytest.raises(RuntimeError, match="driver"):
            await adapter.session_trace("sess-1")
