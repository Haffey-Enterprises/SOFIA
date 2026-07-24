##############################################################################
# Module: test_read_as_of.py
# Service: knowledge-service
# Author: Haffey Enterprises LLC
# Created: 2026-07-24
# Revised: 2026-07-24
# Description: Unit tests for the read-as-of operation (app/domain/retrieval/
#   read_as_of.py, SDD-001 §3.3.6), pin-mode only — the single-subject
#   resolution shape, the real read-discipline trio enforced at read time
#   even on a resolved pin (a currently-retracted pinned version is excluded
#   despite resolving), the TARGET_NOT_FOUND raise on a resolution miss (the
#   first read op that raises), the origin-guard contradiction, and both a
#   Catalog and a Standards node_kind. Runs against the in-memory double — no
#   live Neo4j (SDD-001 §6).
##############################################################################

from collections.abc import Mapping

import pytest

from app.adapters.in_memory_graph import InMemoryGraphStore
from app.domain.exceptions import GatewayError
from app.domain.retrieval.read_as_of import read_as_of
from app.domain.retrieval.types import ConsumingContext
from app.domain.shared.predicate_evaluators import FailClosedPredicateEvaluator
from app.models import ConditionalAdmissionStatus, DisclosureReason, ErrorType
from app.ports.graph_store import ReadAsOfResolvedRecord, ResolvedConditionRecord
from app.ports.predicate_eval import PredicateUnevaluable

_CONTEXT = ConsumingContext(
    environment_class="production",
    data_classification="internal",
    declared_fields={"tier": "gold"},
)


class ControllablePredicateEvaluator:
    """Test-only double: admits, refuses, or raises unevaluable on demand."""

    def __init__(self, *, verdict: bool | None = None) -> None:
        self._verdict = verdict

    async def evaluate(
        self, predicate: Mapping[str, object], context: Mapping[str, object]
    ) -> bool:
        if self._verdict is None:
            raise PredicateUnevaluable("test double: configured to raise")
        return self._verdict


class NeverCalledPredicateEvaluator:
    """Test-only double that fails the test if `evaluate` is ever invoked."""

    async def evaluate(
        self, predicate: Mapping[str, object], context: Mapping[str, object]
    ) -> bool:
        raise AssertionError("evaluate() must not be called for this candidate")


def _resolved_record(
    *,
    node_id: str = "tech-1",
    plane_labels: tuple[str, ...] = ("Catalog",),
    version: str = "3",
    origin_mechanism: str = "ingested",
    derivation_class: str | None = "primary",
    effective_from: str | None = None,
    effective_to: str | None = None,
    applicability_state: str = "unconditional",
    retracted: bool = False,
    conditions: tuple[ResolvedConditionRecord, ...] = (),
) -> ReadAsOfResolvedRecord:
    return ReadAsOfResolvedRecord(
        node_id=node_id,
        plane_labels=plane_labels,
        version=version,
        origin_mechanism=origin_mechanism,
        derivation_class=derivation_class,
        effective_from=effective_from,
        effective_to=effective_to,
        applicability_state=applicability_state,  # type: ignore[arg-type]
        retracted=retracted,
        conditions=conditions,
    )


_ONE_CONDITION = (
    ResolvedConditionRecord(predicate={"op": "eq"}, required_context_fields=frozenset({"tier"})),
)


class TestReadAsOfForwardsTheRequest:
    """The operation forwards the caller's pin to the port unchanged."""

    async def test_read_as_of_forwards_node_kind_business_key_version_to_the_graph_store(
        self,
    ) -> None:
        # Arrange
        graph_store = InMemoryGraphStore()
        graph_store.set_read_as_of_result(_resolved_record())

        # Act
        await read_as_of(
            "Technology", "tech-1", "3", _CONTEXT, graph_store, FailClosedPredicateEvaluator()
        )

        # Assert
        assert graph_store.read_as_of_calls == [("Technology", "tech-1", "3")]


class TestReadAsOfAdmittedPin:
    """A resolved, unconditional pin is admitted with its envelope."""

    async def test_admitted_pin_carries_the_envelope(self) -> None:
        # Arrange
        graph_store = InMemoryGraphStore()
        graph_store.set_read_as_of_result(_resolved_record(node_id="tech-1", version="3"))

        # Act
        result = await read_as_of(
            "Technology",
            "tech-1",
            "3",
            _CONTEXT,
            graph_store,
            NeverCalledPredicateEvaluator(),
        )

        # Assert
        assert result.disclosures == []
        assert len(result.admitted) == 1
        envelope = result.admitted[0]
        assert envelope.node_id == "tech-1"
        assert envelope.node_kind == "Technology"
        assert envelope.plane_labels == ["Catalog"]
        assert envelope.version == "3"
        assert envelope.version_pin == "3"
        assert (
            envelope.applicability.conditional_admission == ConditionalAdmissionStatus.UNCONDITIONAL
        )

    async def test_admitted_pin_never_carries_catalog_eligibility_or_deprecation(self) -> None:
        # Arrange — read-as-of is a resolution primitive, not a selection op.
        graph_store = InMemoryGraphStore()
        graph_store.set_read_as_of_result(_resolved_record())

        # Act
        result = await read_as_of(
            "Technology",
            "tech-1",
            "3",
            _CONTEXT,
            graph_store,
            NeverCalledPredicateEvaluator(),
        )

        # Assert
        applicability = result.admitted[0].applicability
        assert applicability.catalog_eligibility is None
        assert applicability.deprecation is None

    async def test_standards_node_kind_carries_the_standards_plane_label(self) -> None:
        # Arrange
        graph_store = InMemoryGraphStore()
        graph_store.set_read_as_of_result(
            _resolved_record(node_id="rule-1", plane_labels=("Standards",))
        )

        # Act
        result = await read_as_of(
            "PolicyRule",
            "rule-1",
            "1",
            _CONTEXT,
            graph_store,
            NeverCalledPredicateEvaluator(),
        )

        # Assert
        envelope = result.admitted[0]
        assert envelope.node_kind == "PolicyRule"
        assert envelope.plane_labels == ["Standards"]


class TestReadAsOfResolutionMiss:
    """A resolution miss raises TARGET_NOT_FOUND — the first read op that raises."""

    async def test_resolution_miss_raises_target_not_found(self) -> None:
        # Arrange — the double reports no configured result: a resolution miss.
        graph_store = InMemoryGraphStore()

        # Act / Assert
        with pytest.raises(GatewayError) as exc_info:
            await read_as_of(
                "Technology",
                "tech-nonexistent",
                "1",
                _CONTEXT,
                graph_store,
                FailClosedPredicateEvaluator(),
            )
        assert exc_info.value.error_type == ErrorType.TARGET_NOT_FOUND


class TestReadAsOfReadDiscipline:
    """A resolution HIT still runs the full §4.4 trio at read time."""

    async def test_resolved_but_retracted_pin_is_silently_admitted_as_empty(self) -> None:
        # Arrange — the node exists (the pin resolves) but is currently
        # retracted: silent exclusion, never TARGET_NOT_FOUND (D2).
        graph_store = InMemoryGraphStore()
        graph_store.set_read_as_of_result(
            _resolved_record(origin_mechanism="promoted", retracted=True)
        )

        # Act
        result = await read_as_of(
            "Technology",
            "tech-1",
            "3",
            _CONTEXT,
            graph_store,
            NeverCalledPredicateEvaluator(),
        )

        # Assert
        assert result.admitted == []
        assert result.disclosures == []

    async def test_resolved_but_conditional_unsatisfied_yields_one_disclosure(self) -> None:
        # Arrange
        graph_store = InMemoryGraphStore()
        graph_store.set_read_as_of_result(
            _resolved_record(
                node_id="tech-cond",
                origin_mechanism="promoted",
                applicability_state="conditional",
                conditions=_ONE_CONDITION,
            )
        )

        # Act — the fail-closed evaluator: no vocabulary exists yet.
        result = await read_as_of(
            "Technology",
            "tech-cond",
            "1",
            _CONTEXT,
            graph_store,
            FailClosedPredicateEvaluator(),
        )

        # Assert
        assert result.admitted == []
        assert len(result.disclosures) == 1
        assert result.disclosures[0].node_id == "tech-cond"
        assert result.disclosures[0].reason == DisclosureReason.CONDITION_UNEVALUABLE

    async def test_resolved_and_conditional_satisfied_is_admitted(self) -> None:
        # Arrange
        graph_store = InMemoryGraphStore()
        graph_store.set_read_as_of_result(
            _resolved_record(
                origin_mechanism="promoted",
                applicability_state="conditional",
                conditions=_ONE_CONDITION,
            )
        )

        # Act
        result = await read_as_of(
            "Technology",
            "tech-1",
            "3",
            _CONTEXT,
            graph_store,
            ControllablePredicateEvaluator(verdict=True),
        )

        # Assert
        assert result.disclosures == []
        assert len(result.admitted) == 1
        assert (
            result.admitted[0].applicability.conditional_admission
            == ConditionalAdmissionStatus.CONDITIONALLY_ADMITTED
        )


class TestReadAsOfOriginGuard:
    """A non-promoted origin claiming a promoted-only surface is excluded."""

    async def test_ingested_and_retracted_pin_is_excluded_fail_closed(self) -> None:
        # Arrange
        graph_store = InMemoryGraphStore()
        graph_store.set_read_as_of_result(
            _resolved_record(origin_mechanism="ingested", retracted=True)
        )

        # Act
        result = await read_as_of(
            "Technology",
            "tech-1",
            "3",
            _CONTEXT,
            graph_store,
            NeverCalledPredicateEvaluator(),
        )

        # Assert
        assert result.admitted == []
        assert result.disclosures == []

    async def test_ingested_and_conditional_pin_is_excluded_fail_closed(self) -> None:
        # Arrange
        graph_store = InMemoryGraphStore()
        graph_store.set_read_as_of_result(
            _resolved_record(
                origin_mechanism="ingested",
                applicability_state="conditional",
                conditions=_ONE_CONDITION,
            )
        )

        # Act
        result = await read_as_of(
            "Technology",
            "tech-1",
            "3",
            _CONTEXT,
            graph_store,
            NeverCalledPredicateEvaluator(),
        )

        # Assert
        assert result.admitted == []
        assert result.disclosures == []
