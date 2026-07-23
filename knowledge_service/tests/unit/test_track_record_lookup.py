##############################################################################
# Module: test_track_record_lookup.py
# Service: knowledge-service
# Author: Haffey Enterprises LLC
# Created: 2026-07-23
# Revised: 2026-07-23
# Description: Unit tests for the track-record-lookup operation (app/domain/
#   retrieval/track_record_lookup.py, SDD-001 §3.3.3) — the port call, the
#   CandidateNode mapping (fixed read-discipline flags: ObservedPattern is
#   always origin_mechanism: derived, never promoted, so proposal_pending/
#   retracted/applicability_state/conditions are structurally constant), the
#   uncomposed node/edge confidence pair, and the ReadResult the R2 core
#   returns. Runs against the in-memory double — no live Neo4j (SDD-001 §6).
##############################################################################

from app.adapters.in_memory_graph import InMemoryGraphStore
from app.domain.retrieval.track_record_lookup import track_record_lookup
from app.domain.retrieval.types import ConsumingContext
from app.domain.shared.predicate_evaluators import FailClosedPredicateEvaluator
from app.models import ConditionalAdmissionStatus
from app.ports.graph_store import TargetEntityRef, TrackRecordCandidateRecord

_CONTEXT = ConsumingContext(environment_class="production", data_classification="internal")


class _NeverCalledPredicateEvaluator:
    """A predicate port that fails the test if ever invoked.

    track-record-lookup's candidates are always unconditional (ObservedPattern
    never carries HAS_CONDITION) — the predicate port must never be reached.
    """

    async def evaluate(self, predicate: object, context: object) -> bool:
        raise AssertionError("evaluate() must not be called for an ObservedPattern candidate")


def _candidate_record(
    *,
    node_id: str = "op-1",
    origin_mechanism: str = "derived",
    derivation_class: str | None = "distilled",
    node_confidence: float | None = 0.8,
    edge_confidence: float | None = 0.6,
    first_observed_at: str | None = "2026-01-01T00:00:00Z",
    last_observed_at: str | None = "2026-06-01T00:00:00Z",
) -> TrackRecordCandidateRecord:
    return TrackRecordCandidateRecord(
        node_id=node_id,
        origin_mechanism=origin_mechanism,
        derivation_class=derivation_class,
        node_confidence=node_confidence,
        edge_confidence=edge_confidence,
        first_observed_at=first_observed_at,
        last_observed_at=last_observed_at,
    )


class TestTrackRecordLookupForwardsTheRequest:
    """The operation forwards the caller's target refs to the port unchanged."""

    async def test_track_record_lookup_forwards_target_refs_to_the_graph_store(self) -> None:
        # Arrange
        graph_store = InMemoryGraphStore()
        refs = [TargetEntityRef(entity_kind="Technology", entity_id="tech-1")]

        # Act
        await track_record_lookup(refs, _CONTEXT, graph_store, FailClosedPredicateEvaluator())

        # Assert
        assert graph_store.find_track_record_calls == [refs]


class TestTrackRecordLookupCandidateMapping:
    """Each record becomes a CandidateNode with fixed, structural flags."""

    async def test_admits_a_candidate_without_ever_reaching_the_predicate_port(self) -> None:
        # Arrange — proves the flags are unconditional/clean by construction,
        # not merely by coincidence of a permissive evaluator.
        graph_store = InMemoryGraphStore()
        graph_store.set_track_record_candidates([_candidate_record()])

        # Act
        result = await track_record_lookup(
            [TargetEntityRef(entity_kind="Technology", entity_id="tech-1")],
            _CONTEXT,
            graph_store,
            _NeverCalledPredicateEvaluator(),
        )

        # Assert
        assert result.disclosures == []
        assert len(result.admitted) == 1

    async def test_admitted_envelope_carries_identity_and_plane(self) -> None:
        # Arrange
        graph_store = InMemoryGraphStore()
        graph_store.set_track_record_candidates([_candidate_record(node_id="op-42")])

        # Act
        result = await track_record_lookup(
            [TargetEntityRef(entity_kind="Technology", entity_id="tech-1")],
            _CONTEXT,
            graph_store,
            FailClosedPredicateEvaluator(),
        )

        # Assert
        envelope = result.admitted[0]
        assert envelope.node_id == "op-42"
        assert envelope.node_kind == "ObservedPattern"
        assert envelope.plane_labels == ["Operational"]
        assert (
            envelope.applicability.conditional_admission == ConditionalAdmissionStatus.UNCONDITIONAL
        )

    async def test_admitted_envelope_carries_origin_and_derivation_from_the_record(self) -> None:
        # Arrange
        graph_store = InMemoryGraphStore()
        graph_store.set_track_record_candidates(
            [_candidate_record(origin_mechanism="derived", derivation_class="distilled")]
        )

        # Act
        result = await track_record_lookup(
            [TargetEntityRef(entity_kind="Technology", entity_id="tech-1")],
            _CONTEXT,
            graph_store,
            FailClosedPredicateEvaluator(),
        )

        # Assert
        envelope = result.admitted[0]
        assert envelope.origin_mechanism == "derived"
        assert envelope.derivation_class == "distilled"

    async def test_admitted_envelope_has_no_version_or_version_pin(self) -> None:
        # Arrange — ObservedPattern is update-in-place (DDR-002 §2.3/§6); it
        # carries no version property, so the envelope must not fabricate one.
        graph_store = InMemoryGraphStore()
        graph_store.set_track_record_candidates([_candidate_record()])

        # Act
        result = await track_record_lookup(
            [TargetEntityRef(entity_kind="Technology", entity_id="tech-1")],
            _CONTEXT,
            graph_store,
            FailClosedPredicateEvaluator(),
        )

        # Assert
        envelope = result.admitted[0]
        assert envelope.version is None
        assert envelope.version_pin is None

    async def test_admitted_envelope_maps_the_observation_window_to_the_effective_window(
        self,
    ) -> None:
        # Arrange
        graph_store = InMemoryGraphStore()
        graph_store.set_track_record_candidates(
            [
                _candidate_record(
                    first_observed_at="2026-01-01T00:00:00Z",
                    last_observed_at="2026-06-01T00:00:00Z",
                )
            ]
        )

        # Act
        result = await track_record_lookup(
            [TargetEntityRef(entity_kind="Technology", entity_id="tech-1")],
            _CONTEXT,
            graph_store,
            FailClosedPredicateEvaluator(),
        )

        # Assert
        envelope = result.admitted[0]
        assert envelope.effective_from == "2026-01-01T00:00:00Z"
        assert envelope.effective_to == "2026-06-01T00:00:00Z"

    async def test_admitted_envelope_carries_node_and_edge_confidence_uncomposed(self) -> None:
        # Arrange — SDD-001 §3.3.3: composing here would author a reasoning
        # weight this gateway holds no authority to fix.
        graph_store = InMemoryGraphStore()
        graph_store.set_track_record_candidates(
            [_candidate_record(node_confidence=0.9, edge_confidence=0.3)]
        )

        # Act
        result = await track_record_lookup(
            [TargetEntityRef(entity_kind="Technology", entity_id="tech-1")],
            _CONTEXT,
            graph_store,
            FailClosedPredicateEvaluator(),
        )

        # Assert — node confidence first, edge (OBSERVED_IN) confidence second;
        # neither averaged, summed, nor otherwise rolled up.
        envelope = result.admitted[0]
        assert envelope.confidences == [0.9, 0.3]

    async def test_admitted_envelope_catalog_eligibility_is_the_forward_slot(self) -> None:
        # Arrange — Operational plane; catalog-eligibility is not this op's job.
        graph_store = InMemoryGraphStore()
        graph_store.set_track_record_candidates([_candidate_record()])

        # Act
        result = await track_record_lookup(
            [TargetEntityRef(entity_kind="Technology", entity_id="tech-1")],
            _CONTEXT,
            graph_store,
            FailClosedPredicateEvaluator(),
        )

        # Assert
        assert result.admitted[0].applicability.catalog_eligibility is None


class TestTrackRecordLookupMultipleCandidates:
    """Multiple ObservedPattern x target matches all compose into one result."""

    async def test_multiple_candidates_are_all_admitted_in_order(self) -> None:
        # Arrange
        graph_store = InMemoryGraphStore()
        graph_store.set_track_record_candidates(
            [_candidate_record(node_id="op-1"), _candidate_record(node_id="op-2")]
        )

        # Act
        result = await track_record_lookup(
            [TargetEntityRef(entity_kind="Technology", entity_id="tech-1")],
            _CONTEXT,
            graph_store,
            FailClosedPredicateEvaluator(),
        )

        # Assert
        assert [e.node_id for e in result.admitted] == ["op-1", "op-2"]


class TestTrackRecordLookupNoMatches:
    """No matching ObservedPattern yields an empty ReadResult."""

    async def test_no_candidates_yields_an_empty_read_result(self) -> None:
        # Arrange
        graph_store = InMemoryGraphStore()

        # Act
        result = await track_record_lookup(
            [TargetEntityRef(entity_kind="Technology", entity_id="tech-1")],
            _CONTEXT,
            graph_store,
            FailClosedPredicateEvaluator(),
        )

        # Assert
        assert result.admitted == []
        assert result.disclosures == []


class TestTrackRecordLookupOriginMechanismGuard:
    """R3a review finding: fail closed when a record violates the fixed-flags
    invariant, rather than blind-admitting on hardcoded flags that no longer
    hold.
    """

    async def test_a_non_derived_record_is_excluded_and_never_reaches_the_predicate_port(
        self,
    ) -> None:
        # Arrange — a record whose origin_mechanism disagrees with the
        # invariant _to_candidate's fixed flags rely on. The evaluator fails
        # the test if reached at all: the record never becomes a candidate.
        graph_store = InMemoryGraphStore()
        graph_store.set_track_record_candidates([_candidate_record(origin_mechanism="promoted")])

        # Act
        result = await track_record_lookup(
            [TargetEntityRef(entity_kind="Technology", entity_id="tech-1")],
            _CONTEXT,
            graph_store,
            _NeverCalledPredicateEvaluator(),
        )

        # Assert — excluded silently: not admitted, not disclosed (this is not
        # one of the §3.2 closed disclosure reasons; it is a data-integrity
        # guard, not a read-discipline exclusion).
        assert result.admitted == []
        assert result.disclosures == []

    async def test_a_mixed_batch_excludes_only_the_non_derived_record(self) -> None:
        # Arrange
        graph_store = InMemoryGraphStore()
        graph_store.set_track_record_candidates(
            [
                _candidate_record(node_id="op-good", origin_mechanism="derived"),
                _candidate_record(node_id="op-bad", origin_mechanism="promoted"),
            ]
        )

        # Act
        result = await track_record_lookup(
            [TargetEntityRef(entity_kind="Technology", entity_id="tech-1")],
            _CONTEXT,
            graph_store,
            FailClosedPredicateEvaluator(),
        )

        # Assert
        assert [e.node_id for e in result.admitted] == ["op-good"]
        assert result.disclosures == []


class TestTrackRecordLookupNullConfidence:
    """R3a review finding: a null confidence is carried honestly, not a crash.

    Neither ObservedPattern.confidence nor OBSERVED_IN.confidence is
    DDR-002-guaranteed non-null (both are T2; no CI check covers them, unlike
    Evidence.confidence's check #28) — so a null must map through the envelope
    rather than raising a validation error.
    """

    async def test_a_null_node_confidence_maps_through_without_raising(self) -> None:
        # Arrange
        graph_store = InMemoryGraphStore()
        graph_store.set_track_record_candidates(
            [_candidate_record(node_confidence=None, edge_confidence=0.6)]
        )

        # Act
        result = await track_record_lookup(
            [TargetEntityRef(entity_kind="Technology", entity_id="tech-1")],
            _CONTEXT,
            graph_store,
            FailClosedPredicateEvaluator(),
        )

        # Assert
        assert result.admitted[0].confidences == [None, 0.6]

    async def test_a_null_edge_confidence_maps_through_without_raising(self) -> None:
        # Arrange
        graph_store = InMemoryGraphStore()
        graph_store.set_track_record_candidates(
            [_candidate_record(node_confidence=0.9, edge_confidence=None)]
        )

        # Act
        result = await track_record_lookup(
            [TargetEntityRef(entity_kind="Technology", entity_id="tech-1")],
            _CONTEXT,
            graph_store,
            FailClosedPredicateEvaluator(),
        )

        # Assert
        assert result.admitted[0].confidences == [0.9, None]
