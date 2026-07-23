##############################################################################
# Module: test_technology_candidate.py
# Service: knowledge-service
# Author: Haffey Enterprises LLC
# Created: 2026-07-23
# Revised: 2026-07-23
# Description: Unit tests for the shared Technology -> CandidateNode mapper
#   (app/domain/retrieval/technology_candidate.py, SDD-001 §3.3.1/§3.3.2) —
#   the Catalog-eligibility annotation (never exclusion), the deprecation
#   notice (marker-presence, v1.7.0), the promoted-only-state contradiction
#   guard, and the real read-discipline flags carried through onto the
#   returned CandidateNode. Promoted here (RBT-78 R3c review finding (a)) from
#   resolve_technology's former private _to_candidate so the mapper has its
#   own direct test coverage rather than only being exercised indirectly
#   through resolve_technology/select_patterns.
##############################################################################

from app.domain.retrieval.technology_candidate import to_technology_candidate
from app.domain.retrieval.types import ConsumingContext
from app.ports.graph_store import ResolvedConditionRecord, ResolveTechnologyCandidateRecord

_CONTEXT = ConsumingContext(
    environment_class="production",
    data_classification="internal",
    declared_fields={"tier": "gold"},
)


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


class TestToTechnologyCandidateShape:
    """The attribution/candidate fields a Technology mapping always carries."""

    def test_node_kind_and_plane_label_are_fixed(self) -> None:
        # Arrange
        record = _tech_record()

        # Act
        candidate = to_technology_candidate(record, _CONTEXT)

        # Assert
        assert candidate is not None
        assert candidate.attribution.node_kind == "Technology"
        assert candidate.attribution.plane_labels == ("Catalog",)

    def test_proposal_pending_is_always_false(self) -> None:
        # Arrange
        record = _tech_record()

        # Act
        candidate = to_technology_candidate(record, _CONTEXT)

        # Assert
        assert candidate is not None
        assert candidate.proposal_pending is False

    def test_version_and_version_pin_are_set_from_the_record(self) -> None:
        # Arrange
        record = _tech_record(version="3")

        # Act
        candidate = to_technology_candidate(record, _CONTEXT)

        # Assert
        assert candidate is not None
        assert candidate.attribution.version == "3"
        assert candidate.attribution.version_pin == "3"


class TestToTechnologyCandidateCatalogEligibility:
    """The eligibility verdict is always computed and never excludes."""

    def test_eligible_record_carries_an_eligible_verdict(self) -> None:
        # Arrange
        record = _tech_record(
            tier_applicability=("production",),
            approved_data_classifications=("internal",),
        )

        # Act
        candidate = to_technology_candidate(record, _CONTEXT)

        # Assert
        assert candidate is not None
        assert candidate.attribution.catalog_eligibility is not None
        assert candidate.attribution.catalog_eligibility.eligible is True

    def test_ineligible_record_is_still_admitted_with_an_ineligible_verdict(self) -> None:
        # Arrange — wrong tier: annotation, never exclusion (§4.4).
        record = _tech_record(
            tier_applicability=("staging",),
            approved_data_classifications=("internal",),
        )

        # Act
        candidate = to_technology_candidate(record, _CONTEXT)

        # Assert
        assert candidate is not None
        assert candidate.attribution.catalog_eligibility is not None
        assert candidate.attribution.catalog_eligibility.eligible is False


class TestToTechnologyCandidateDeprecationNotice:
    """`deprecated` is marker-presence, never a read-clock comparison."""

    def test_absent_deprecation_date_yields_not_deprecated(self) -> None:
        # Arrange
        record = _tech_record(deprecation_date=None)

        # Act
        candidate = to_technology_candidate(record, _CONTEXT)

        # Assert
        assert candidate is not None
        assert candidate.attribution.deprecation is not None
        assert candidate.attribution.deprecation.deprecated is False
        assert candidate.attribution.deprecation.deprecation_date is None

    def test_present_deprecation_date_yields_deprecated_regardless_of_date_value(
        self,
    ) -> None:
        # Arrange — a future date still marks deprecated=True: presence, not
        # a clock comparison.
        record = _tech_record(deprecation_date="2099-01-01")

        # Act
        candidate = to_technology_candidate(record, _CONTEXT)

        # Assert
        assert candidate is not None
        assert candidate.attribution.deprecation is not None
        assert candidate.attribution.deprecation.deprecated is True
        assert candidate.attribution.deprecation.deprecation_date == "2099-01-01"


class TestToTechnologyCandidatePromotedOnlyStateGuard:
    """A non-promoted origin claiming a promoted-only surface is excluded."""

    def test_ingested_and_retracted_is_excluded(self) -> None:
        # Arrange
        record = _tech_record(origin_mechanism="ingested", retracted=True)

        # Act
        candidate = to_technology_candidate(record, _CONTEXT)

        # Assert
        assert candidate is None

    def test_ingested_and_conditional_is_excluded(self) -> None:
        # Arrange
        record = _tech_record(origin_mechanism="ingested", applicability_state="conditional")

        # Act
        candidate = to_technology_candidate(record, _CONTEXT)

        # Assert
        assert candidate is None

    def test_promoted_and_retracted_is_admitted(self) -> None:
        # Arrange
        record = _tech_record(origin_mechanism="promoted", retracted=True)

        # Act
        candidate = to_technology_candidate(record, _CONTEXT)

        # Assert
        assert candidate is not None
        assert candidate.retracted is True


class TestToTechnologyCandidateReadDisciplineFlagsPassThrough:
    """The real per-node flags the traversal resolved survive onto the node."""

    def test_retracted_flag_passes_through(self) -> None:
        # Arrange
        record = _tech_record(origin_mechanism="promoted", retracted=True)

        # Act
        candidate = to_technology_candidate(record, _CONTEXT)

        # Assert
        assert candidate is not None
        assert candidate.retracted is True

    def test_applicability_state_passes_through(self) -> None:
        # Arrange
        record = _tech_record(origin_mechanism="promoted", applicability_state="conditional")

        # Act
        candidate = to_technology_candidate(record, _CONTEXT)

        # Assert
        assert candidate is not None
        assert candidate.applicability_state == "conditional"

    def test_conditions_pass_through_as_condition_refs(self) -> None:
        # Arrange
        condition = ResolvedConditionRecord(
            predicate={"op": "eq"}, required_context_fields=frozenset({"tier"})
        )
        record = _tech_record(
            origin_mechanism="promoted",
            applicability_state="conditional",
            conditions=(condition,),
        )

        # Act
        candidate = to_technology_candidate(record, _CONTEXT)

        # Assert
        assert candidate is not None
        assert len(candidate.conditions) == 1
        assert candidate.conditions[0].predicate == {"op": "eq"}
        assert candidate.conditions[0].required_context_fields == frozenset({"tier"})
