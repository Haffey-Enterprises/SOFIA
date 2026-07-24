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
#   (RBT-78/R3a track-record, R3b resolve-technology, R3c select-patterns) are
#   what make read-discipline exercisable without modelling graph internals
#   (§4.2 A3).
##############################################################################

from app.adapters.in_memory_graph import InMemoryGraphStore
from app.ports.graph_store import (
    FindPrecedentsCandidateRecord,
    FindPrecedentsCriteria,
    GraphStoragePort,
    ObligationCandidateRecord,
    ReadAsOfResolvedRecord,
    ResolveTechnologyCandidateRecord,
    SelectPatternsCandidateRecord,
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


class TestInMemoryGraphStoreSelectPatterns:
    """The controllable candidate-record store (§4.2 A3)."""

    async def test_select_patterns_with_no_candidates_set_returns_empty(self) -> None:
        # Arrange
        store = InMemoryGraphStore()

        # Act
        result = await store.select_patterns(["cap-1"])

        # Assert
        assert result == []

    async def test_select_patterns_returns_the_configured_candidates(self) -> None:
        # Arrange
        store = InMemoryGraphStore()
        candidate = SelectPatternsCandidateRecord(
            node_id="pattern-1",
            version="1",
            origin_mechanism="ingested",
            derivation_class="primary",
            applicability_state="unconditional",
            retracted=False,
            conditions=(),
            capabilities=(),
            preferred_over=(),
        )
        store.set_pattern_candidates([candidate])

        # Act
        result = await store.select_patterns(["cap-1"])

        # Assert
        assert result == [candidate]

    async def test_select_patterns_records_the_requested_capability_ids(self) -> None:
        # Arrange
        store = InMemoryGraphStore()

        # Act
        await store.select_patterns(["cap-a", "cap-b"])

        # Assert — lets a test prove the operation forwarded the caller's
        # required capabilities rather than dropping or substituting them.
        assert store.select_patterns_calls == [["cap-a", "cap-b"]]


class TestInMemoryGraphStoreObligationContext:
    """The controllable candidate-record store (§4.2 A3)."""

    async def test_obligation_context_with_no_candidates_set_returns_empty(self) -> None:
        # Arrange
        store = InMemoryGraphStore()

        # Act
        result = await store.obligation_context("sol-1")

        # Assert
        assert result == []

    async def test_obligation_context_returns_the_configured_candidates(self) -> None:
        # Arrange
        store = InMemoryGraphStore()
        candidate = ObligationCandidateRecord(
            node_id="rule-1",
            version="1",
            origin_mechanism="ingested",
            derivation_class="primary",
            applicability_state="unconditional",
            retracted=False,
            conditions=(),
            statement="Data at rest must be encrypted.",
            rule_definition="IF classification == 'restricted' THEN require(encryption)",
            dependency_manifest=("Technology",),
            enforcement_level="hard",
            enforced_at_gate="architecture_review",
            domain="security",
        )
        store.set_obligation_candidates([candidate])

        # Act
        result = await store.obligation_context("sol-1")

        # Assert
        assert result == [candidate]

    async def test_obligation_context_records_the_requested_solution_id(self) -> None:
        # Arrange
        store = InMemoryGraphStore()

        # Act
        await store.obligation_context("sol-42")

        # Assert — lets a test prove the operation forwarded the caller's
        # solution id rather than dropping or substituting it.
        assert store.obligation_context_calls == ["sol-42"]


class TestInMemoryGraphStoreFindPrecedents:
    """The controllable candidate-record store (§4.2 A3)."""

    async def test_find_precedents_with_no_candidates_set_returns_empty(self) -> None:
        # Arrange
        store = InMemoryGraphStore()
        criteria = FindPrecedentsCriteria(
            capability_ids=(),
            pattern_ids=(),
            technology_ids=("tech-1",),
            target_environment=None,
            gate_outcome=None,
        )

        # Act
        result = await store.find_precedents(criteria)

        # Assert
        assert result == []

    async def test_find_precedents_returns_the_configured_candidates(self) -> None:
        # Arrange
        store = InMemoryGraphStore()
        candidate = FindPrecedentsCandidateRecord(
            node_id="sol-1",
            version="1",
            origin_mechanism="authored",
            target_environment="production",
            gate_decisions=(),
        )
        store.set_precedent_candidates([candidate])
        criteria = FindPrecedentsCriteria(
            capability_ids=(),
            pattern_ids=(),
            technology_ids=("tech-1",),
            target_environment=None,
            gate_outcome=None,
        )

        # Act
        result = await store.find_precedents(criteria)

        # Assert
        assert result == [candidate]

    async def test_find_precedents_records_the_requested_criteria(self) -> None:
        # Arrange
        store = InMemoryGraphStore()
        criteria = FindPrecedentsCriteria(
            capability_ids=("cap-1",),
            pattern_ids=(),
            technology_ids=(),
            target_environment="production",
            gate_outcome="approved",
        )

        # Act
        await store.find_precedents(criteria)

        # Assert — lets a test prove the operation forwarded the caller's
        # criteria rather than dropping or substituting them.
        assert store.find_precedents_calls == [criteria]


class TestInMemoryGraphStoreReadAsOf:
    """The controllable single-record store (§4.2 A3)."""

    async def test_read_as_of_with_no_result_set_returns_none(self) -> None:
        # Arrange — a resolution miss.
        store = InMemoryGraphStore()

        # Act
        result = await store.read_as_of("Technology", "tech-1", "1")

        # Assert
        assert result is None

    async def test_read_as_of_returns_the_configured_record(self) -> None:
        # Arrange
        store = InMemoryGraphStore()
        record = ReadAsOfResolvedRecord(
            node_id="tech-1",
            plane_labels=("Catalog",),
            version="3",
            origin_mechanism="ingested",
            derivation_class="primary",
            effective_from=None,
            effective_to=None,
            applicability_state="unconditional",
            retracted=False,
            conditions=(),
        )
        store.set_read_as_of_result(record)

        # Act
        result = await store.read_as_of("Technology", "tech-1", "3")

        # Assert
        assert result == record

    async def test_read_as_of_records_the_requested_pin(self) -> None:
        # Arrange
        store = InMemoryGraphStore()

        # Act
        await store.read_as_of("Technology", "tech-42", "2")

        # Assert — lets a test prove the operation forwarded the caller's
        # pin rather than dropping or substituting it.
        assert store.read_as_of_calls == [("Technology", "tech-42", "2")]
