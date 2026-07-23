##############################################################################
# Module: test_resolve_technology.py
# Service: knowledge-service
# Author: Haffey Enterprises LLC
# Created: 2026-07-23
# Revised: 2026-07-23
# Description: Unit tests for the resolve-technology operation (app/domain/
#   retrieval/resolve_technology.py, SDD-001 §3.3.2) — the port call, the
#   Catalog-eligibility annotation (never exclusion), the REAL read-discipline
#   flags (a Technology can genuinely be retracted or promoted-conditional,
#   unlike track-record-lookup's fixed constants), the ingested-origin
#   contradiction guard, the deprecation notice (v1.7.0 — marker-presence,
#   never a read-clock comparison, never affecting admission), and the
#   ReadResult the R2 core returns. Runs against the in-memory double — no
#   live Neo4j (SDD-001 §6).
##############################################################################

from collections.abc import Mapping

from app.adapters.in_memory_graph import InMemoryGraphStore
from app.domain.retrieval.resolve_technology import resolve_technology
from app.domain.retrieval.types import ConsumingContext
from app.domain.shared.predicate_evaluators import FailClosedPredicateEvaluator
from app.models import ConditionalAdmissionStatus, DisclosureReason
from app.ports.graph_store import ResolvedConditionRecord, ResolveTechnologyCandidateRecord
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


def _tech_record(
    *,
    node_id: str = "tech-1",
    version: str = "1",
    origin_mechanism: str = "ingested",
    derivation_class: str | None = "primary",
    tier_applicability: tuple[str, ...] = ("production",),
    approved_data_classifications: tuple[str, ...] = ("internal",),
    applicability_state: str = "unconditional",
    retracted: bool = False,
    conditions: tuple[ResolvedConditionRecord, ...] = (),
    deprecation_date: str | None = None,
) -> ResolveTechnologyCandidateRecord:
    return ResolveTechnologyCandidateRecord(
        node_id=node_id,
        version=version,
        origin_mechanism=origin_mechanism,
        derivation_class=derivation_class,
        tier_applicability=tier_applicability,
        approved_data_classifications=approved_data_classifications,
        applicability_state=applicability_state,  # type: ignore[arg-type]
        retracted=retracted,
        conditions=conditions,
        deprecation_date=deprecation_date,
    )


_ONE_CONDITION = (
    ResolvedConditionRecord(predicate={"op": "eq"}, required_context_fields=frozenset({"tier"})),
)
_TWO_CONDITIONS = (
    ResolvedConditionRecord(predicate={"op": "eq"}, required_context_fields=frozenset({"tier"})),
    ResolvedConditionRecord(predicate={"op": "ne"}, required_context_fields=frozenset({"tier"})),
)


class TestResolveTechnologyForwardsTheRequest:
    """The operation forwards the caller's capability id to the port unchanged."""

    async def test_resolve_technology_forwards_capability_id_to_the_graph_store(self) -> None:
        # Arrange
        graph_store = InMemoryGraphStore()

        # Act
        await resolve_technology("cap-1", _CONTEXT, graph_store, FailClosedPredicateEvaluator())

        # Assert
        assert graph_store.resolve_technology_options_calls == ["cap-1"]


class TestResolveTechnologyCatalogEligibility:
    """Ineligible is annotated, never excluded (SDD-001 §4.4)."""

    async def test_eligible_technology_is_admitted_and_annotated_eligible(self) -> None:
        # Arrange
        graph_store = InMemoryGraphStore()
        graph_store.set_technology_option_candidates(
            [
                _tech_record(
                    tier_applicability=("production",),
                    approved_data_classifications=("internal",),
                )
            ]
        )

        # Act
        result = await resolve_technology(
            "cap-1", _CONTEXT, graph_store, NeverCalledPredicateEvaluator()
        )

        # Assert
        assert len(result.admitted) == 1
        eligibility = result.admitted[0].applicability.catalog_eligibility
        assert eligibility is not None
        assert eligibility.eligible is True
        assert eligibility.failing_fields == []

    async def test_ineligible_technology_is_still_admitted_annotated_ineligible(self) -> None:
        # Arrange — SDD-001 §4.4: annotation, never exclusion. The gap-vs-
        # ineligible distinction is load-bearing.
        graph_store = InMemoryGraphStore()
        graph_store.set_technology_option_candidates(
            [
                _tech_record(
                    tier_applicability=("staging",),
                    approved_data_classifications=("restricted",),
                )
            ]
        )

        # Act
        result = await resolve_technology(
            "cap-1", _CONTEXT, graph_store, NeverCalledPredicateEvaluator()
        )

        # Assert — NOT excluded; still admitted.
        assert result.disclosures == []
        assert len(result.admitted) == 1
        eligibility = result.admitted[0].applicability.catalog_eligibility
        assert eligibility is not None
        assert eligibility.eligible is False
        assert eligibility.failing_fields == ["tier_applicability", "approved_data_classifications"]

    async def test_tier_only_failure_names_only_tier_applicability(self) -> None:
        # Arrange
        graph_store = InMemoryGraphStore()
        graph_store.set_technology_option_candidates(
            [
                _tech_record(
                    tier_applicability=("staging",),
                    approved_data_classifications=("internal",),
                )
            ]
        )

        # Act
        result = await resolve_technology(
            "cap-1", _CONTEXT, graph_store, NeverCalledPredicateEvaluator()
        )

        # Assert
        eligibility = result.admitted[0].applicability.catalog_eligibility
        assert eligibility is not None
        assert eligibility.failing_fields == ["tier_applicability"]

    async def test_classification_only_failure_names_only_that_field(self) -> None:
        # Arrange
        graph_store = InMemoryGraphStore()
        graph_store.set_technology_option_candidates(
            [
                _tech_record(
                    tier_applicability=("production",),
                    approved_data_classifications=("restricted",),
                )
            ]
        )

        # Act
        result = await resolve_technology(
            "cap-1", _CONTEXT, graph_store, NeverCalledPredicateEvaluator()
        )

        # Assert
        eligibility = result.admitted[0].applicability.catalog_eligibility
        assert eligibility is not None
        assert eligibility.failing_fields == ["approved_data_classifications"]


class TestResolveTechnologyDeprecationNotice:
    """The deprecation notice (SDD-001 §3.2 v1.7.0) — marker-presence, never
    a read-clock comparison, and never affecting admission.
    """

    async def test_deprecated_technology_is_still_admitted_and_annotated(self) -> None:
        # Arrange
        graph_store = InMemoryGraphStore()
        graph_store.set_technology_option_candidates([_tech_record(deprecation_date="2026-01-01")])

        # Act
        result = await resolve_technology(
            "cap-1", _CONTEXT, graph_store, NeverCalledPredicateEvaluator()
        )

        # Assert — annotation, never exclusion (same footing as eligibility).
        assert len(result.admitted) == 1
        deprecation = result.admitted[0].applicability.deprecation
        assert deprecation is not None
        assert deprecation.deprecated is True
        assert deprecation.deprecation_date == "2026-01-01"

    async def test_non_deprecated_technology_reads_deprecated_false(self) -> None:
        # Arrange — no deprecation_date on the record. Model choice: a notice
        # is always built (not None) so `deprecated`/`deprecation_date` are
        # uniformly readable without a None-check on the notice itself.
        graph_store = InMemoryGraphStore()
        graph_store.set_technology_option_candidates([_tech_record(deprecation_date=None)])

        # Act
        result = await resolve_technology(
            "cap-1", _CONTEXT, graph_store, NeverCalledPredicateEvaluator()
        )

        # Assert
        deprecation = result.admitted[0].applicability.deprecation
        assert deprecation is not None
        assert deprecation.deprecated is False
        assert deprecation.deprecation_date is None

    async def test_a_future_deprecation_date_still_reads_deprecated_true(self) -> None:
        # Arrange — proves no read-clock comparison crept in: marker-presence
        # only, regardless of whether the date is past or future.
        graph_store = InMemoryGraphStore()
        graph_store.set_technology_option_candidates([_tech_record(deprecation_date="2099-01-01")])

        # Act
        result = await resolve_technology(
            "cap-1", _CONTEXT, graph_store, NeverCalledPredicateEvaluator()
        )

        # Assert
        deprecation = result.admitted[0].applicability.deprecation
        assert deprecation is not None
        assert deprecation.deprecated is True
        assert deprecation.deprecation_date == "2099-01-01"

    async def test_deprecation_state_does_not_change_admission(self) -> None:
        # Arrange — a retracted-and-deprecated candidate is excluded solely by
        # the read-discipline trio (retraction, #21); deprecation is inert to
        # that decision, one way or the other.
        graph_store = InMemoryGraphStore()
        graph_store.set_technology_option_candidates(
            [
                _tech_record(
                    node_id="retracted-and-deprecated",
                    origin_mechanism="promoted",
                    retracted=True,
                    deprecation_date="2026-01-01",
                ),
                _tech_record(
                    node_id="clean-and-deprecated",
                    origin_mechanism="ingested",
                    retracted=False,
                    deprecation_date="2026-01-01",
                ),
            ]
        )

        # Act
        result = await resolve_technology(
            "cap-1", _CONTEXT, graph_store, NeverCalledPredicateEvaluator()
        )

        # Assert — the retracted one is excluded (silent), the clean one
        # admitted — deprecation on both, admission driven by retraction alone.
        assert [e.node_id for e in result.admitted] == ["clean-and-deprecated"]
        assert result.disclosures == []
        assert result.admitted[0].applicability.deprecation is not None
        assert result.admitted[0].applicability.deprecation.deprecated is True


class TestResolveTechnologyRealReadDiscipline:
    """A Technology can genuinely be retracted or conditional (D1)."""

    async def test_retracted_technology_is_silently_excluded(self) -> None:
        # Arrange
        graph_store = InMemoryGraphStore()
        graph_store.set_technology_option_candidates(
            [_tech_record(origin_mechanism="promoted", retracted=True)]
        )

        # Act
        result = await resolve_technology(
            "cap-1", _CONTEXT, graph_store, NeverCalledPredicateEvaluator()
        )

        # Assert — silent: not admitted, not disclosed.
        assert result.admitted == []
        assert result.disclosures == []

    async def test_conditional_technology_excluded_unevaluable_under_fail_closed_evaluator(
        self,
    ) -> None:
        # Arrange — the production evaluator: no vocabulary exists yet.
        graph_store = InMemoryGraphStore()
        graph_store.set_technology_option_candidates(
            [
                _tech_record(
                    origin_mechanism="promoted",
                    applicability_state="conditional",
                    conditions=_ONE_CONDITION,
                )
            ]
        )

        # Act
        result = await resolve_technology(
            "cap-1", _CONTEXT, graph_store, FailClosedPredicateEvaluator()
        )

        # Assert
        assert result.admitted == []
        assert len(result.disclosures) == 1
        assert result.disclosures[0].reason == DisclosureReason.CONDITION_UNEVALUABLE

    async def test_conditional_technology_admitted_when_the_predicate_is_satisfied(self) -> None:
        # Arrange — a controllable double proves the admit path is reachable.
        graph_store = InMemoryGraphStore()
        graph_store.set_technology_option_candidates(
            [
                _tech_record(
                    origin_mechanism="promoted",
                    applicability_state="conditional",
                    conditions=_ONE_CONDITION,
                )
            ]
        )

        # Act
        result = await resolve_technology(
            "cap-1", _CONTEXT, graph_store, ControllablePredicateEvaluator(verdict=True)
        )

        # Assert
        assert result.disclosures == []
        assert len(result.admitted) == 1
        assert (
            result.admitted[0].applicability.conditional_admission
            == ConditionalAdmissionStatus.CONDITIONALLY_ADMITTED
        )

    async def test_multi_condition_technology_is_surfaced_as_scope_conflict(self) -> None:
        # Arrange
        graph_store = InMemoryGraphStore()
        graph_store.set_technology_option_candidates(
            [
                _tech_record(
                    origin_mechanism="promoted",
                    applicability_state="conditional",
                    conditions=_TWO_CONDITIONS,
                )
            ]
        )

        # Act
        result = await resolve_technology(
            "cap-1", _CONTEXT, graph_store, NeverCalledPredicateEvaluator()
        )

        # Assert
        assert result.admitted == []
        assert len(result.disclosures) == 1
        assert result.disclosures[0].reason == DisclosureReason.MULTI_CONDITION_SCOPE_CONFLICT

    async def test_unconditional_unretracted_technology_is_admitted_unconditional(self) -> None:
        # Arrange
        graph_store = InMemoryGraphStore()
        graph_store.set_technology_option_candidates([_tech_record()])

        # Act
        result = await resolve_technology(
            "cap-1", _CONTEXT, graph_store, NeverCalledPredicateEvaluator()
        )

        # Assert
        assert len(result.admitted) == 1
        assert (
            result.admitted[0].applicability.conditional_admission
            == ConditionalAdmissionStatus.UNCONDITIONAL
        )


class TestResolveTechnologyOriginMechanismContradictionGuard:
    """An ingested-origin Technology cannot be retracted or conditional (D1).

    RETRACTS un-promotes a PROMOTED fact (§7 #21); applicability_state/
    Condition is exclusive to PROMOTES_TO_KNOWLEDGE-materialized nodes (§5).
    A record disagreeing with either is a data-integrity contradiction —
    excluded, fail-closed, rather than admitted (or silently trusted) on a
    broken assumption.
    """

    async def test_ingested_and_retracted_is_excluded_fail_closed(self) -> None:
        # Arrange
        graph_store = InMemoryGraphStore()
        graph_store.set_technology_option_candidates(
            [_tech_record(origin_mechanism="ingested", retracted=True)]
        )

        # Act
        result = await resolve_technology(
            "cap-1", _CONTEXT, graph_store, NeverCalledPredicateEvaluator()
        )

        # Assert
        assert result.admitted == []
        assert result.disclosures == []

    async def test_ingested_and_conditional_is_excluded_fail_closed(self) -> None:
        # Arrange
        graph_store = InMemoryGraphStore()
        graph_store.set_technology_option_candidates(
            [
                _tech_record(
                    origin_mechanism="ingested",
                    applicability_state="conditional",
                    conditions=_ONE_CONDITION,
                )
            ]
        )

        # Act
        result = await resolve_technology(
            "cap-1", _CONTEXT, graph_store, NeverCalledPredicateEvaluator()
        )

        # Assert — the evaluator must never be reached: the contradiction is
        # caught before conditional evaluation would even begin.
        assert result.admitted == []
        assert result.disclosures == []

    async def test_ingested_and_unconditional_unretracted_is_admitted_normally(self) -> None:
        # Arrange — the ordinary, non-contradictory ingested case still works.
        graph_store = InMemoryGraphStore()
        graph_store.set_technology_option_candidates(
            [_tech_record(origin_mechanism="ingested", retracted=False)]
        )

        # Act
        result = await resolve_technology(
            "cap-1", _CONTEXT, graph_store, NeverCalledPredicateEvaluator()
        )

        # Assert
        assert len(result.admitted) == 1
        assert result.disclosures == []


class TestResolveTechnologyMultipleCandidates:
    """Each candidate is evaluated independently; results compose in order."""

    async def test_mixed_batch_yields_the_expected_admitted_and_disclosed_sets(self) -> None:
        # Arrange
        graph_store = InMemoryGraphStore()
        graph_store.set_technology_option_candidates(
            [
                _tech_record(node_id="admit-me"),
                _tech_record(
                    node_id="hide-me-retracted", origin_mechanism="promoted", retracted=True
                ),
                _tech_record(
                    node_id="disclose-me",
                    origin_mechanism="promoted",
                    applicability_state="conditional",
                    conditions=_ONE_CONDITION,
                ),
            ]
        )

        # Act
        result = await resolve_technology(
            "cap-1", _CONTEXT, graph_store, FailClosedPredicateEvaluator()
        )

        # Assert
        assert [e.node_id for e in result.admitted] == ["admit-me"]
        assert [d.node_id for d in result.disclosures] == ["disclose-me"]


class TestResolveTechnologyNoMatches:
    """No approved options yields an empty ReadResult."""

    async def test_no_candidates_yields_an_empty_read_result(self) -> None:
        # Arrange
        graph_store = InMemoryGraphStore()

        # Act
        result = await resolve_technology(
            "cap-1", _CONTEXT, graph_store, FailClosedPredicateEvaluator()
        )

        # Assert
        assert result.admitted == []
        assert result.disclosures == []
