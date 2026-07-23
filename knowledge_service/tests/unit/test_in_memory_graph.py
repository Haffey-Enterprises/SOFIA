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
#   testable in both directions, and its controllable candidate-record lists
#   (RBT-78/R3a track-record, R3b resolve-technology) are what make
#   read-discipline exercisable without modelling graph internals (§4.2 A3).
##############################################################################

from app.adapters.in_memory_graph import InMemoryGraphStore
from app.ports.graph_store import (
    GraphStoragePort,
    ResolveTechnologyCandidateRecord,
    TargetEntityRef,
    TrackRecordCandidateRecord,
)


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


class TestInMemoryGraphStoreFindTrackRecord:
    """The controllable candidate-record store (§4.2 A3)."""

    async def test_find_track_record_with_no_candidates_set_returns_empty(self) -> None:
        # Arrange
        store = InMemoryGraphStore()

        # Act
        result = await store.find_track_record(
            [TargetEntityRef(entity_kind="Technology", entity_id="t")]
        )

        # Assert
        assert result == []

    async def test_find_track_record_returns_the_configured_candidates(self) -> None:
        # Arrange
        store = InMemoryGraphStore()
        candidate = TrackRecordCandidateRecord(
            node_id="op-1",
            origin_mechanism="derived",
            derivation_class="distilled",
            node_confidence=0.8,
            edge_confidence=0.6,
            first_observed_at="2026-01-01T00:00:00Z",
            last_observed_at="2026-06-01T00:00:00Z",
        )
        store.set_track_record_candidates([candidate])

        # Act
        result = await store.find_track_record(
            [TargetEntityRef(entity_kind="Technology", entity_id="t")]
        )

        # Assert
        assert result == [candidate]

    async def test_find_track_record_records_the_requested_target_refs(self) -> None:
        # Arrange
        store = InMemoryGraphStore()
        refs = [TargetEntityRef(entity_kind="Pattern", entity_id="p-1")]

        # Act
        await store.find_track_record(refs)

        # Assert — lets a test prove the operation forwarded the caller's
        # target entities rather than dropping or substituting them.
        assert store.find_track_record_calls == [refs]


class TestInMemoryGraphStoreResolveTechnologyOptions:
    """The controllable candidate-record store (§4.2 A3)."""

    async def test_resolve_technology_options_with_no_candidates_set_returns_empty(
        self,
    ) -> None:
        # Arrange
        store = InMemoryGraphStore()

        # Act
        result = await store.resolve_technology_options("cap-1")

        # Assert
        assert result == []

    async def test_resolve_technology_options_returns_the_configured_candidates(
        self,
    ) -> None:
        # Arrange
        store = InMemoryGraphStore()
        candidate = ResolveTechnologyCandidateRecord(
            node_id="tech-1",
            version="1",
            origin_mechanism="ingested",
            derivation_class="primary",
            tier_applicability=("production",),
            approved_data_classifications=("internal",),
            applicability_state="unconditional",
            retracted=False,
            conditions=(),
        )
        store.set_technology_option_candidates([candidate])

        # Act
        result = await store.resolve_technology_options("cap-1")

        # Assert
        assert result == [candidate]

    async def test_resolve_technology_options_records_the_requested_capability_id(
        self,
    ) -> None:
        # Arrange
        store = InMemoryGraphStore()

        # Act
        await store.resolve_technology_options("cap-42")

        # Assert — lets a test prove the operation forwarded the caller's
        # capability id rather than dropping or substituting it.
        assert store.resolve_technology_options_calls == ["cap-42"]
