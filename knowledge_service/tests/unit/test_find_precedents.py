##############################################################################
# Module: test_find_precedents.py
# Service: knowledge-service
# Author: Haffey Enterprises LLC
# Created: 2026-07-23
# Revised: 2026-07-23
# Description: Unit tests for the find-precedents operation (app/domain/
#   retrieval/find_precedents.py, SDD-001 §3.3.5) — the port call, the
#   CandidateNode mapping (fixed read-discipline flags: a Solution is always
#   origin_mechanism: authored, never a promotion/conditional/retraction
#   subject, so proposal_pending/retracted/applicability_state/conditions are
#   structurally constant), the envelope shape (node_kind="Solution",
#   plane_labels=() — an Artifact carries no KG plane label), the
#   target_environment + gate_decisions context, the origin-guard exclusion,
#   and the at-least-one-linkage empty-never-error guard. AND-across/OR-
#   within linkage matching is a graph-traversal concern (the Neo4j adapter's
#   Cypher query, verified via query-text-lock in test_neo4j_adapter.py) —
#   this operation is blind to which linkage dimension (technology/pattern/
#   capability) resolved a given record, exactly as it is blind to which
#   traversal path resolved any other operation's candidates; records
#   standing in for different dimensions below exercise that indifference.
#   Runs against the in-memory double — no live Neo4j (SDD-001 §6).
##############################################################################

from app.adapters.in_memory_graph import InMemoryGraphStore
from app.domain.retrieval.find_precedents import find_precedents
from app.domain.retrieval.types import ConsumingContext
from app.domain.shared.predicate_evaluators import FailClosedPredicateEvaluator
from app.models import ConditionalAdmissionStatus
from app.ports.graph_store import (
    FindPrecedentsCandidateRecord,
    FindPrecedentsCriteria,
    GateDecisionRecord,
)

_CONTEXT = ConsumingContext(environment_class="production", data_classification="internal")


class _NeverCalledPredicateEvaluator:
    """A predicate port that fails the test if ever invoked.

    find-precedents' candidates are always unconditional (a Solution never
    carries HAS_CONDITION) — the predicate port must never be reached.
    """

    async def evaluate(self, predicate: object, context: object) -> bool:
        raise AssertionError("evaluate() must not be called for a Solution candidate")


def _criteria(
    *,
    capability_ids: tuple[str, ...] = (),
    pattern_ids: tuple[str, ...] = (),
    technology_ids: tuple[str, ...] = (),
    target_environment: str | None = None,
    gate_outcome: str | None = None,
) -> FindPrecedentsCriteria:
    return FindPrecedentsCriteria(
        capability_ids=capability_ids,
        pattern_ids=pattern_ids,
        technology_ids=technology_ids,
        target_environment=target_environment,
        gate_outcome=gate_outcome,
    )


def _candidate_record(
    *,
    node_id: str = "sol-1",
    version: str = "1",
    origin_mechanism: str = "authored",
    target_environment: str | None = "production",
    gate_decisions: tuple[GateDecisionRecord, ...] = (),
) -> FindPrecedentsCandidateRecord:
    return FindPrecedentsCandidateRecord(
        node_id=node_id,
        version=version,
        origin_mechanism=origin_mechanism,
        target_environment=target_environment,
        gate_decisions=gate_decisions,
    )


class TestFindPrecedentsForwardsTheRequest:
    """The operation forwards the caller's criteria to the port unchanged."""

    async def test_find_precedents_forwards_criteria_to_the_graph_store(self) -> None:
        # Arrange
        graph_store = InMemoryGraphStore()
        criteria = _criteria(technology_ids=("tech-1",))

        # Act
        await find_precedents(criteria, _CONTEXT, graph_store, FailClosedPredicateEvaluator())

        # Assert
        assert graph_store.find_precedents_calls == [criteria]


class TestFindPrecedentsCandidateMapping:
    """Each record becomes a CandidateNode with fixed, structural flags."""

    async def test_admits_a_candidate_without_ever_reaching_the_predicate_port(self) -> None:
        # Arrange — proves the flags are unconditional/clean by construction,
        # not merely by coincidence of a permissive evaluator.
        graph_store = InMemoryGraphStore()
        graph_store.set_precedent_candidates([_candidate_record()])

        # Act
        result = await find_precedents(
            _criteria(technology_ids=("tech-1",)),
            _CONTEXT,
            graph_store,
            _NeverCalledPredicateEvaluator(),
        )

        # Assert
        assert len(result.precedents) == 1
        entry = result.precedents[0]
        assert entry.envelope.node_id == "sol-1"
        assert entry.envelope.node_kind == "Solution"
        assert entry.envelope.plane_labels == []
        assert entry.envelope.origin_mechanism == "authored"
        assert (
            entry.envelope.applicability.conditional_admission
            == ConditionalAdmissionStatus.UNCONDITIONAL
        )

    async def test_precedent_envelope_never_carries_catalog_eligibility_or_deprecation(
        self,
    ) -> None:
        # Arrange — Technology-only surfaces; a Solution carries neither.
        graph_store = InMemoryGraphStore()
        graph_store.set_precedent_candidates([_candidate_record()])

        # Act
        result = await find_precedents(
            _criteria(technology_ids=("tech-1",)),
            _CONTEXT,
            graph_store,
            _NeverCalledPredicateEvaluator(),
        )

        # Assert
        applicability = result.precedents[0].envelope.applicability
        assert applicability.catalog_eligibility is None
        assert applicability.deprecation is None

    async def test_precedent_carries_the_target_environment(self) -> None:
        # Arrange
        graph_store = InMemoryGraphStore()
        graph_store.set_precedent_candidates([_candidate_record(target_environment="staging")])

        # Act
        result = await find_precedents(
            _criteria(technology_ids=("tech-1",)),
            _CONTEXT,
            graph_store,
            _NeverCalledPredicateEvaluator(),
        )

        # Assert
        assert result.precedents[0].target_environment == "staging"

    async def test_precedent_carries_every_gate_decision(self) -> None:
        # Arrange — multiple gate decisions on one Solution surface all of
        # them, uncomposed, no pick.
        graph_store = InMemoryGraphStore()
        graph_store.set_precedent_candidates(
            [
                _candidate_record(
                    gate_decisions=(
                        GateDecisionRecord(outcome="approved", gate="gate_1", decision_id="gd-1"),
                        GateDecisionRecord(outcome="rejected", gate="gate_0", decision_id="gd-0"),
                    )
                )
            ]
        )

        # Act
        result = await find_precedents(
            _criteria(technology_ids=("tech-1",)),
            _CONTEXT,
            graph_store,
            _NeverCalledPredicateEvaluator(),
        )

        # Assert
        gate_decisions = result.precedents[0].gate_decisions
        assert len(gate_decisions) == 2
        outcomes = {gd.outcome for gd in gate_decisions}
        assert outcomes == {"approved", "rejected"}
        assert gate_decisions[0].decision_id == "gd-1"
        assert gate_decisions[1].decision_id == "gd-0"

    async def test_result_carries_no_disclosure_field(self) -> None:
        # Arrange — a Solution is never conditionally excluded; the result
        # type itself carries no disclosure channel (F4).
        graph_store = InMemoryGraphStore()
        graph_store.set_precedent_candidates([_candidate_record()])

        # Act
        result = await find_precedents(
            _criteria(technology_ids=("tech-1",)),
            _CONTEXT,
            graph_store,
            _NeverCalledPredicateEvaluator(),
        )

        # Assert
        assert not hasattr(result, "disclosures")


class TestFindPrecedentsLinkageDimensions:
    """The operation is agnostic to which linkage dimension resolved a
    record — technology-linked, pattern-linked, and capability-linked
    precedents are all mapped identically."""

    async def test_multiple_precedents_across_distinct_linkage_dimensions_are_all_admitted(
        self,
    ) -> None:
        # Arrange — one record standing in for each of the three linkage
        # dimensions the adapter's query resolves (technology via USES,
        # pattern via FOLLOWS, capability via FOLLOWS ∘ REQUIRES_CAPABILITY).
        graph_store = InMemoryGraphStore()
        graph_store.set_precedent_candidates(
            [
                _candidate_record(node_id="sol-tech-linked"),
                _candidate_record(node_id="sol-pattern-linked"),
                _candidate_record(node_id="sol-capability-linked"),
            ]
        )

        # Act
        result = await find_precedents(
            _criteria(
                technology_ids=("tech-1",),
                pattern_ids=("pattern-1",),
                capability_ids=("cap-1",),
            ),
            _CONTEXT,
            graph_store,
            _NeverCalledPredicateEvaluator(),
        )

        # Assert
        node_ids = {entry.envelope.node_id for entry in result.precedents}
        assert node_ids == {"sol-tech-linked", "sol-pattern-linked", "sol-capability-linked"}


class TestFindPrecedentsOriginGuard:
    """A non-authored origin is excluded fail-closed (the Solution invariant)."""

    async def test_non_authored_origin_is_excluded_fail_closed(self) -> None:
        # Arrange
        graph_store = InMemoryGraphStore()
        graph_store.set_precedent_candidates([_candidate_record(origin_mechanism="ingested")])

        # Act
        result = await find_precedents(
            _criteria(technology_ids=("tech-1",)),
            _CONTEXT,
            graph_store,
            _NeverCalledPredicateEvaluator(),
        )

        # Assert
        assert result.precedents == []


class TestFindPrecedentsEmptyInputs:
    """Empty inputs and empty resolutions yield empty lists, never an error."""

    async def test_all_empty_linkage_criteria_yields_empty_without_querying(self) -> None:
        # Arrange — F4: at least one linkage criterion is required.
        graph_store = InMemoryGraphStore()

        # Act
        result = await find_precedents(
            _criteria(), _CONTEXT, graph_store, FailClosedPredicateEvaluator()
        )

        # Assert
        assert result.precedents == []
        assert graph_store.find_precedents_calls == []

    async def test_target_environment_and_gate_outcome_alone_do_not_satisfy_the_guard(
        self,
    ) -> None:
        # Arrange — F4: target_environment/gate_outcome are not linkage
        # criteria; at least one of capability/pattern/technology ids is
        # still required.
        graph_store = InMemoryGraphStore()

        # Act
        result = await find_precedents(
            _criteria(target_environment="production", gate_outcome="approved"),
            _CONTEXT,
            graph_store,
            FailClosedPredicateEvaluator(),
        )

        # Assert
        assert result.precedents == []
        assert graph_store.find_precedents_calls == []

    async def test_no_matching_precedents_yields_an_empty_result(self) -> None:
        # Arrange
        graph_store = InMemoryGraphStore()

        # Act
        result = await find_precedents(
            _criteria(technology_ids=("tech-nonexistent",)),
            _CONTEXT,
            graph_store,
            FailClosedPredicateEvaluator(),
        )

        # Assert
        assert result.precedents == []
