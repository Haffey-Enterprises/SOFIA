##############################################################################
# Module: test_select_patterns.py
# Service: knowledge-service
# Author: Haffey Enterprises LLC
# Created: 2026-07-23
# Revised: 2026-07-23
# Description: Unit tests for the select-patterns operation (app/domain/
#   retrieval/select_patterns.py, SDD-001 §3.3.1) — the nested result shape
#   (ruling #1), per-node read-discipline at both the Pattern and per-capability
#   Technology levels (ruling #2), uncomposed PREFERRED_OVER (ruling #3),
#   Technology-only catalog-eligibility/deprecation (ruling #5), the gap signal
#   (ruling #6), per-capability taxonomy placement (ruling #8), and the shared
#   origin-guard contradiction excluding both a Pattern and a Technology option
#   fail-closed. Runs against the in-memory double — no live Neo4j (SDD-001 §6).
##############################################################################

from collections.abc import Mapping

from app.adapters.in_memory_graph import InMemoryGraphStore
from app.domain.retrieval.select_patterns import select_patterns
from app.domain.retrieval.types import ConsumingContext
from app.domain.shared.predicate_evaluators import FailClosedPredicateEvaluator
from app.models import ConditionalAdmissionStatus, DisclosureReason
from app.ports.graph_store import (
    CapabilityBlockRecord,
    ResolvedConditionRecord,
    ResolveTechnologyCandidateRecord,
    SelectPatternsCandidateRecord,
)
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


def _cap_block(
    *,
    capability_id: str = "cap-1",
    l1_taxonomy: str | None = "l1",
    l2_taxonomy: str | None = "l2",
    l3_taxonomy: str | None = "l3",
    technology_options: tuple[ResolveTechnologyCandidateRecord, ...] = (),
) -> CapabilityBlockRecord:
    return CapabilityBlockRecord(
        capability_id=capability_id,
        l1_taxonomy=l1_taxonomy,
        l2_taxonomy=l2_taxonomy,
        l3_taxonomy=l3_taxonomy,
        technology_options=technology_options,
    )


def _pattern_record(
    *,
    node_id: str = "pattern-1",
    version: str = "1",
    origin_mechanism: str = "ingested",
    derivation_class: str | None = "primary",
    applicability_state: str = "unconditional",
    retracted: bool = False,
    conditions: tuple[ResolvedConditionRecord, ...] = (),
    capabilities: tuple[CapabilityBlockRecord, ...] = (),
    preferred_over: tuple[str, ...] = (),
) -> SelectPatternsCandidateRecord:
    return SelectPatternsCandidateRecord(
        node_id=node_id,
        version=version,
        origin_mechanism=origin_mechanism,
        derivation_class=derivation_class,
        applicability_state=applicability_state,  # type: ignore[arg-type]
        retracted=retracted,
        conditions=conditions,
        capabilities=capabilities,
        preferred_over=preferred_over,
    )


_ONE_CONDITION = (
    ResolvedConditionRecord(predicate={"op": "eq"}, required_context_fields=frozenset({"tier"})),
)
_TWO_CONDITIONS = (
    ResolvedConditionRecord(predicate={"op": "eq"}, required_context_fields=frozenset({"tier"})),
    ResolvedConditionRecord(predicate={"op": "ne"}, required_context_fields=frozenset({"tier"})),
)


class TestSelectPatternsForwardsTheRequest:
    """The operation forwards the caller's capability ids to the port unchanged."""

    async def test_select_patterns_forwards_capability_ids_to_the_graph_store(self) -> None:
        # Arrange
        graph_store = InMemoryGraphStore()

        # Act
        await select_patterns(
            ["cap-1", "cap-2"], _CONTEXT, graph_store, FailClosedPredicateEvaluator()
        )

        # Assert
        assert graph_store.select_patterns_calls == [["cap-1", "cap-2"]]


class TestSelectPatternsAdmittedPattern:
    """An admitted pattern with nested capabilities and tech options."""

    async def test_admitted_pattern_carries_the_pattern_envelope(self) -> None:
        # Arrange
        graph_store = InMemoryGraphStore()
        graph_store.set_pattern_candidates(
            [_pattern_record(node_id="pattern-42", capabilities=(_cap_block(),))]
        )

        # Act
        result = await select_patterns(
            ["cap-1"], _CONTEXT, graph_store, NeverCalledPredicateEvaluator()
        )

        # Assert
        assert result.pattern_disclosures == []
        assert len(result.patterns) == 1
        candidate = result.patterns[0]
        assert candidate.envelope.node_id == "pattern-42"
        assert candidate.envelope.node_kind == "Pattern"
        assert candidate.envelope.plane_labels == ["Catalog"]
        assert (
            candidate.envelope.applicability.conditional_admission
            == ConditionalAdmissionStatus.UNCONDITIONAL
        )

    async def test_pattern_envelope_never_carries_catalog_eligibility_or_deprecation(
        self,
    ) -> None:
        # Arrange — ruling #5: Technology-only surfaces.
        graph_store = InMemoryGraphStore()
        graph_store.set_pattern_candidates([_pattern_record(capabilities=(_cap_block(),))])

        # Act
        result = await select_patterns(
            ["cap-1"], _CONTEXT, graph_store, NeverCalledPredicateEvaluator()
        )

        # Assert
        applicability = result.patterns[0].envelope.applicability
        assert applicability.catalog_eligibility is None
        assert applicability.deprecation is None

    async def test_admitted_pattern_carries_nested_capability_with_taxonomy(self) -> None:
        # Arrange
        graph_store = InMemoryGraphStore()
        graph_store.set_pattern_candidates(
            [
                _pattern_record(
                    capabilities=(
                        _cap_block(
                            capability_id="cap-9",
                            l1_taxonomy="compute",
                            l2_taxonomy="serverless",
                            l3_taxonomy="functions",
                        ),
                    )
                )
            ]
        )

        # Act
        result = await select_patterns(
            ["cap-9"], _CONTEXT, graph_store, NeverCalledPredicateEvaluator()
        )

        # Assert
        block = result.patterns[0].capabilities[0]
        assert block.capability_id == "cap-9"
        assert block.l1_taxonomy == "compute"
        assert block.l2_taxonomy == "serverless"
        assert block.l3_taxonomy == "functions"

    async def test_admitted_pattern_carries_admitted_technology_options(self) -> None:
        # Arrange
        graph_store = InMemoryGraphStore()
        graph_store.set_pattern_candidates(
            [_pattern_record(capabilities=(_cap_block(technology_options=(_tech_record(),)),))]
        )

        # Act
        result = await select_patterns(
            ["cap-1"], _CONTEXT, graph_store, NeverCalledPredicateEvaluator()
        )

        # Assert
        block = result.patterns[0].capabilities[0]
        assert block.technology_disclosures == []
        assert len(block.technology_options) == 1
        assert block.technology_options[0].node_id == "tech-1"
        assert block.technology_options[0].node_kind == "Technology"

    async def test_multi_capability_pattern_carries_every_matched_capability(self) -> None:
        # Arrange
        graph_store = InMemoryGraphStore()
        graph_store.set_pattern_candidates(
            [
                _pattern_record(
                    capabilities=(
                        _cap_block(capability_id="cap-a"),
                        _cap_block(capability_id="cap-b"),
                    )
                )
            ]
        )

        # Act
        result = await select_patterns(
            ["cap-a", "cap-b"], _CONTEXT, graph_store, NeverCalledPredicateEvaluator()
        )

        # Assert
        capability_ids = {block.capability_id for block in result.patterns[0].capabilities}
        assert capability_ids == {"cap-a", "cap-b"}

    async def test_preferred_over_is_surfaced_uncomposed(self) -> None:
        # Arrange — ruling #3: structural facts only, no ordering or pick.
        graph_store = InMemoryGraphStore()
        graph_store.set_pattern_candidates(
            [
                _pattern_record(
                    capabilities=(_cap_block(),),
                    preferred_over=("pattern-2", "pattern-3"),
                )
            ]
        )

        # Act
        result = await select_patterns(
            ["cap-1"], _CONTEXT, graph_store, NeverCalledPredicateEvaluator()
        )

        # Assert
        assert result.patterns[0].preferred_over == ["pattern-2", "pattern-3"]


class TestSelectPatternsGapSignal:
    """A capability with no approved technology yields empty, never an error."""

    async def test_capability_with_no_technology_options_is_the_gap_signal(self) -> None:
        # Arrange — ruling #6.
        graph_store = InMemoryGraphStore()
        graph_store.set_pattern_candidates(
            [_pattern_record(capabilities=(_cap_block(technology_options=()),))]
        )

        # Act
        result = await select_patterns(
            ["cap-1"], _CONTEXT, graph_store, NeverCalledPredicateEvaluator()
        )

        # Assert — empty lists, no error, no disclosure.
        block = result.patterns[0].capabilities[0]
        assert block.technology_options == []
        assert block.technology_disclosures == []


class TestSelectPatternsPatternReadDiscipline:
    """The Pattern node itself runs the full §4.4 trio (ruling #2)."""

    async def test_retracted_pattern_is_silently_dropped_with_its_subtree(self) -> None:
        # Arrange
        graph_store = InMemoryGraphStore()
        graph_store.set_pattern_candidates(
            [
                _pattern_record(
                    origin_mechanism="promoted",
                    retracted=True,
                    capabilities=(_cap_block(technology_options=(_tech_record(),)),),
                )
            ]
        )

        # Act
        result = await select_patterns(
            ["cap-1"], _CONTEXT, graph_store, NeverCalledPredicateEvaluator()
        )

        # Assert — silent: no pattern, no disclosure, subtree never resolved.
        assert result.patterns == []
        assert result.pattern_disclosures == []

    async def test_conditional_pattern_excluded_yields_one_pattern_disclosure(self) -> None:
        # Arrange
        graph_store = InMemoryGraphStore()
        graph_store.set_pattern_candidates(
            [
                _pattern_record(
                    node_id="pattern-cond",
                    origin_mechanism="promoted",
                    applicability_state="conditional",
                    conditions=_ONE_CONDITION,
                    capabilities=(_cap_block(technology_options=(_tech_record(),)),),
                )
            ]
        )

        # Act — the fail-closed evaluator: no vocabulary exists yet.
        result = await select_patterns(
            ["cap-1"], _CONTEXT, graph_store, FailClosedPredicateEvaluator()
        )

        # Assert — whole subtree gone, exactly one top-level disclosure.
        assert result.patterns == []
        assert len(result.pattern_disclosures) == 1
        assert result.pattern_disclosures[0].node_id == "pattern-cond"
        assert result.pattern_disclosures[0].reason == DisclosureReason.CONDITION_UNEVALUABLE

    async def test_multi_condition_pattern_is_surfaced_as_scope_conflict(self) -> None:
        # Arrange
        graph_store = InMemoryGraphStore()
        graph_store.set_pattern_candidates(
            [
                _pattern_record(
                    origin_mechanism="promoted",
                    applicability_state="conditional",
                    conditions=_TWO_CONDITIONS,
                    capabilities=(_cap_block(),),
                )
            ]
        )

        # Act
        result = await select_patterns(
            ["cap-1"], _CONTEXT, graph_store, NeverCalledPredicateEvaluator()
        )

        # Assert
        assert result.patterns == []
        assert len(result.pattern_disclosures) == 1
        disclosure_reason = result.pattern_disclosures[0].reason
        assert disclosure_reason == DisclosureReason.MULTI_CONDITION_SCOPE_CONFLICT

    async def test_conditional_pattern_admitted_when_predicate_satisfied(self) -> None:
        # Arrange
        graph_store = InMemoryGraphStore()
        graph_store.set_pattern_candidates(
            [
                _pattern_record(
                    origin_mechanism="promoted",
                    applicability_state="conditional",
                    conditions=_ONE_CONDITION,
                    capabilities=(_cap_block(),),
                )
            ]
        )

        # Act
        result = await select_patterns(
            ["cap-1"], _CONTEXT, graph_store, ControllablePredicateEvaluator(verdict=True)
        )

        # Assert
        assert result.pattern_disclosures == []
        assert len(result.patterns) == 1
        assert (
            result.patterns[0].envelope.applicability.conditional_admission
            == ConditionalAdmissionStatus.CONDITIONALLY_ADMITTED
        )


class TestSelectPatternsTechnologyReadDiscipline:
    """Each capability's Technology options independently run the trio."""

    async def test_ineligible_technology_is_annotated_not_excluded(self) -> None:
        # Arrange — Catalog-eligibility is annotation only, never exclusion.
        graph_store = InMemoryGraphStore()
        graph_store.set_pattern_candidates(
            [
                _pattern_record(
                    capabilities=(
                        _cap_block(
                            technology_options=(
                                _tech_record(
                                    tier_applicability=("staging",),
                                    approved_data_classifications=("restricted",),
                                ),
                            )
                        ),
                    )
                )
            ]
        )

        # Act
        result = await select_patterns(
            ["cap-1"], _CONTEXT, graph_store, NeverCalledPredicateEvaluator()
        )

        # Assert
        block = result.patterns[0].capabilities[0]
        assert block.technology_disclosures == []
        assert len(block.technology_options) == 1
        eligibility = block.technology_options[0].applicability.catalog_eligibility
        assert eligibility is not None
        assert eligibility.eligible is False
        assert eligibility.failing_fields == ["tier_applicability", "approved_data_classifications"]

    async def test_deprecated_technology_is_annotated_with_the_marker(self) -> None:
        # Arrange — marker-presence, never exclusion.
        graph_store = InMemoryGraphStore()
        graph_store.set_pattern_candidates(
            [
                _pattern_record(
                    capabilities=(
                        _cap_block(
                            technology_options=(_tech_record(deprecation_date="2026-01-01"),)
                        ),
                    )
                )
            ]
        )

        # Act
        result = await select_patterns(
            ["cap-1"], _CONTEXT, graph_store, NeverCalledPredicateEvaluator()
        )

        # Assert
        tech_option = result.patterns[0].capabilities[0].technology_options[0]
        deprecation = tech_option.applicability.deprecation
        assert deprecation is not None
        assert deprecation.deprecated is True
        assert deprecation.deprecation_date == "2026-01-01"

    async def test_retracted_technology_option_is_silently_dropped(self) -> None:
        # Arrange
        graph_store = InMemoryGraphStore()
        graph_store.set_pattern_candidates(
            [
                _pattern_record(
                    capabilities=(
                        _cap_block(
                            technology_options=(
                                _tech_record(origin_mechanism="promoted", retracted=True),
                            )
                        ),
                    )
                )
            ]
        )

        # Act
        result = await select_patterns(
            ["cap-1"], _CONTEXT, graph_store, NeverCalledPredicateEvaluator()
        )

        # Assert
        block = result.patterns[0].capabilities[0]
        assert block.technology_options == []
        assert block.technology_disclosures == []

    async def test_conditional_technology_option_yields_a_technology_disclosure(self) -> None:
        # Arrange
        graph_store = InMemoryGraphStore()
        graph_store.set_pattern_candidates(
            [
                _pattern_record(
                    capabilities=(
                        _cap_block(
                            capability_id="cap-cond",
                            technology_options=(
                                _tech_record(
                                    node_id="tech-cond",
                                    origin_mechanism="promoted",
                                    applicability_state="conditional",
                                    conditions=_ONE_CONDITION,
                                ),
                            ),
                        ),
                    )
                )
            ]
        )

        # Act — fail-closed evaluator.
        result = await select_patterns(
            ["cap-cond"], _CONTEXT, graph_store, FailClosedPredicateEvaluator()
        )

        # Assert — the PATTERN is still admitted; only the tech option is
        # disclosed, per-capability.
        assert len(result.patterns) == 1
        block = result.patterns[0].capabilities[0]
        assert block.technology_options == []
        assert len(block.technology_disclosures) == 1
        assert block.technology_disclosures[0].node_id == "tech-cond"
        assert block.technology_disclosures[0].reason == DisclosureReason.CONDITION_UNEVALUABLE


class TestSelectPatternsOriginGuard:
    """The shared contradiction guard excludes both a Pattern and a Technology."""

    async def test_ingested_and_retracted_pattern_is_excluded_fail_closed(self) -> None:
        # Arrange
        graph_store = InMemoryGraphStore()
        graph_store.set_pattern_candidates(
            [
                _pattern_record(
                    origin_mechanism="ingested",
                    retracted=True,
                    capabilities=(_cap_block(),),
                )
            ]
        )

        # Act
        result = await select_patterns(
            ["cap-1"], _CONTEXT, graph_store, NeverCalledPredicateEvaluator()
        )

        # Assert
        assert result.patterns == []
        assert result.pattern_disclosures == []

    async def test_ingested_and_retracted_technology_is_excluded_fail_closed(self) -> None:
        # Arrange
        graph_store = InMemoryGraphStore()
        graph_store.set_pattern_candidates(
            [
                _pattern_record(
                    capabilities=(
                        _cap_block(
                            technology_options=(
                                _tech_record(origin_mechanism="ingested", retracted=True),
                            )
                        ),
                    )
                )
            ]
        )

        # Act
        result = await select_patterns(
            ["cap-1"], _CONTEXT, graph_store, NeverCalledPredicateEvaluator()
        )

        # Assert
        block = result.patterns[0].capabilities[0]
        assert block.technology_options == []
        assert block.technology_disclosures == []


class TestSelectPatternsEmptyInputs:
    """Empty inputs and empty resolutions yield empty lists, never an error."""

    async def test_empty_capability_ids_yields_an_empty_result(self) -> None:
        # Arrange
        graph_store = InMemoryGraphStore()

        # Act
        result = await select_patterns([], _CONTEXT, graph_store, FailClosedPredicateEvaluator())

        # Assert
        assert result.patterns == []
        assert result.pattern_disclosures == []

    async def test_no_matching_patterns_yields_an_empty_result(self) -> None:
        # Arrange
        graph_store = InMemoryGraphStore()

        # Act
        result = await select_patterns(
            ["cap-nonexistent"], _CONTEXT, graph_store, FailClosedPredicateEvaluator()
        )

        # Assert
        assert result.patterns == []
        assert result.pattern_disclosures == []
