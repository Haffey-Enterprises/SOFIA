##############################################################################
# Module: test_obligation_context.py
# Service: knowledge-service
# Author: Haffey Enterprises LLC
# Created: 2026-07-23
# Revised: 2026-07-23
# Description: Unit tests for the obligation-context operation (app/domain/
#   retrieval/obligation_context.py, SDD-001 §3.3.4) — the applicable
#   PolicyRule envelope + content payload shape, the real read-discipline
#   trio on PolicyRules (a Standards-plane ground-truth type, like Technology/
#   Pattern), the opaque rule_definition pass-through, the origin-guard
#   contradiction, and empty-never-error for an absent or ungoverned
#   solution. Runs against the in-memory double — no live Neo4j (SDD-001 §6).
##############################################################################

from collections.abc import Mapping

from app.adapters.in_memory_graph import InMemoryGraphStore
from app.domain.retrieval.obligation_context import obligation_context
from app.domain.retrieval.types import ConsumingContext
from app.domain.shared.predicate_evaluators import FailClosedPredicateEvaluator
from app.models import ConditionalAdmissionStatus, DisclosureReason
from app.ports.graph_store import ObligationCandidateRecord, ResolvedConditionRecord
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


def _rule_record(
    *,
    node_id: str = "rule-1",
    version: str = "1",
    origin_mechanism: str = "ingested",
    derivation_class: str | None = "primary",
    applicability_state: str = "unconditional",
    retracted: bool = False,
    conditions: tuple[ResolvedConditionRecord, ...] = (),
    statement: str | None = "Data at rest must be encrypted.",
    rule_definition: str | None = "IF classification == 'restricted' THEN require(encryption)",
    dependency_manifest: tuple[str, ...] = ("Technology",),
    enforcement_level: str | None = "hard",
    enforced_at_gate: str | None = "architecture_review",
    domain: str | None = "security",
) -> ObligationCandidateRecord:
    return ObligationCandidateRecord(
        node_id=node_id,
        version=version,
        origin_mechanism=origin_mechanism,
        derivation_class=derivation_class,
        applicability_state=applicability_state,  # type: ignore[arg-type]
        retracted=retracted,
        conditions=conditions,
        statement=statement,
        rule_definition=rule_definition,
        dependency_manifest=dependency_manifest,
        enforcement_level=enforcement_level,
        enforced_at_gate=enforced_at_gate,
        domain=domain,
    )


_ONE_CONDITION = (
    ResolvedConditionRecord(predicate={"op": "eq"}, required_context_fields=frozenset({"tier"})),
)
_TWO_CONDITIONS = (
    ResolvedConditionRecord(predicate={"op": "eq"}, required_context_fields=frozenset({"tier"})),
    ResolvedConditionRecord(predicate={"op": "ne"}, required_context_fields=frozenset({"tier"})),
)


class TestObligationContextForwardsTheRequest:
    """The operation forwards the caller's solution id to the port unchanged."""

    async def test_obligation_context_forwards_solution_id_to_the_graph_store(self) -> None:
        # Arrange
        graph_store = InMemoryGraphStore()

        # Act
        await obligation_context("sol-1", _CONTEXT, graph_store, FailClosedPredicateEvaluator())

        # Assert
        assert graph_store.obligation_context_calls == ["sol-1"]


class TestObligationContextAdmittedObligation:
    """A governed solution's admitted obligation carries envelope + payload."""

    async def test_admitted_obligation_carries_the_rule_envelope(self) -> None:
        # Arrange
        graph_store = InMemoryGraphStore()
        graph_store.set_obligation_candidates([_rule_record(node_id="rule-42")])

        # Act
        result = await obligation_context(
            "sol-1", _CONTEXT, graph_store, NeverCalledPredicateEvaluator()
        )

        # Assert
        assert result.disclosures == []
        assert len(result.obligations) == 1
        entry = result.obligations[0]
        assert entry.envelope.node_id == "rule-42"
        assert entry.envelope.node_kind == "PolicyRule"
        assert entry.envelope.plane_labels == ["Standards"]
        assert (
            entry.envelope.applicability.conditional_admission
            == ConditionalAdmissionStatus.UNCONDITIONAL
        )

    async def test_admitted_obligation_never_carries_catalog_eligibility_or_deprecation(
        self,
    ) -> None:
        # Arrange — Technology-only surfaces (DDR-002 §2.1).
        graph_store = InMemoryGraphStore()
        graph_store.set_obligation_candidates([_rule_record()])

        # Act
        result = await obligation_context(
            "sol-1", _CONTEXT, graph_store, NeverCalledPredicateEvaluator()
        )

        # Assert
        applicability = result.obligations[0].envelope.applicability
        assert applicability.catalog_eligibility is None
        assert applicability.deprecation is None

    async def test_admitted_obligation_carries_the_policy_rule_payload(self) -> None:
        # Arrange
        graph_store = InMemoryGraphStore()
        graph_store.set_obligation_candidates(
            [
                _rule_record(
                    statement="Data at rest must be encrypted.",
                    rule_definition="IF classification == 'restricted' THEN require(encryption)",
                    dependency_manifest=("Technology", "Pattern"),
                    enforcement_level="hard",
                    enforced_at_gate="architecture_review",
                    domain="security",
                )
            ]
        )

        # Act
        result = await obligation_context(
            "sol-1", _CONTEXT, graph_store, NeverCalledPredicateEvaluator()
        )

        # Assert — all six payload fields, rule_definition carried opaque.
        payload = result.obligations[0].policy_rule
        assert payload.statement == "Data at rest must be encrypted."
        assert payload.rule_definition == (
            "IF classification == 'restricted' THEN require(encryption)"
        )
        assert payload.dependency_manifest == ["Technology", "Pattern"]
        assert payload.enforcement_level == "hard"
        assert payload.enforced_at_gate == "architecture_review"
        assert payload.domain == "security"


class TestObligationContextReadDiscipline:
    """The PolicyRule runs the full §4.4 trio, exactly like Technology/Pattern."""

    async def test_retracted_rule_is_silently_dropped(self) -> None:
        # Arrange
        graph_store = InMemoryGraphStore()
        graph_store.set_obligation_candidates(
            [_rule_record(origin_mechanism="promoted", retracted=True)]
        )

        # Act
        result = await obligation_context(
            "sol-1", _CONTEXT, graph_store, NeverCalledPredicateEvaluator()
        )

        # Assert — silent: no obligation, no disclosure.
        assert result.obligations == []
        assert result.disclosures == []

    async def test_conditional_rule_excluded_yields_one_disclosure(self) -> None:
        # Arrange
        graph_store = InMemoryGraphStore()
        graph_store.set_obligation_candidates(
            [
                _rule_record(
                    node_id="rule-cond",
                    origin_mechanism="promoted",
                    applicability_state="conditional",
                    conditions=_ONE_CONDITION,
                )
            ]
        )

        # Act — the fail-closed evaluator: no vocabulary exists yet.
        result = await obligation_context(
            "sol-1", _CONTEXT, graph_store, FailClosedPredicateEvaluator()
        )

        # Assert
        assert result.obligations == []
        assert len(result.disclosures) == 1
        assert result.disclosures[0].node_id == "rule-cond"
        assert result.disclosures[0].reason == DisclosureReason.CONDITION_UNEVALUABLE

    async def test_conditional_rule_admitted_when_predicate_satisfied(self) -> None:
        # Arrange
        graph_store = InMemoryGraphStore()
        graph_store.set_obligation_candidates(
            [
                _rule_record(
                    origin_mechanism="promoted",
                    applicability_state="conditional",
                    conditions=_ONE_CONDITION,
                )
            ]
        )

        # Act
        result = await obligation_context(
            "sol-1", _CONTEXT, graph_store, ControllablePredicateEvaluator(verdict=True)
        )

        # Assert
        assert result.disclosures == []
        assert len(result.obligations) == 1
        assert (
            result.obligations[0].envelope.applicability.conditional_admission
            == ConditionalAdmissionStatus.CONDITIONALLY_ADMITTED
        )

    async def test_multi_condition_rule_is_surfaced_as_scope_conflict(self) -> None:
        # Arrange
        graph_store = InMemoryGraphStore()
        graph_store.set_obligation_candidates(
            [
                _rule_record(
                    origin_mechanism="promoted",
                    applicability_state="conditional",
                    conditions=_TWO_CONDITIONS,
                )
            ]
        )

        # Act
        result = await obligation_context(
            "sol-1", _CONTEXT, graph_store, NeverCalledPredicateEvaluator()
        )

        # Assert
        assert result.obligations == []
        assert len(result.disclosures) == 1
        assert result.disclosures[0].reason == DisclosureReason.MULTI_CONDITION_SCOPE_CONFLICT


class TestObligationContextOriginGuard:
    """A non-promoted origin claiming a promoted-only surface is excluded."""

    async def test_ingested_and_retracted_rule_is_excluded_fail_closed(self) -> None:
        # Arrange
        graph_store = InMemoryGraphStore()
        graph_store.set_obligation_candidates(
            [_rule_record(origin_mechanism="ingested", retracted=True)]
        )

        # Act
        result = await obligation_context(
            "sol-1", _CONTEXT, graph_store, NeverCalledPredicateEvaluator()
        )

        # Assert
        assert result.obligations == []
        assert result.disclosures == []

    async def test_ingested_and_conditional_rule_is_excluded_fail_closed(self) -> None:
        # Arrange
        graph_store = InMemoryGraphStore()
        graph_store.set_obligation_candidates(
            [
                _rule_record(
                    origin_mechanism="ingested",
                    applicability_state="conditional",
                    conditions=_ONE_CONDITION,
                )
            ]
        )

        # Act
        result = await obligation_context(
            "sol-1", _CONTEXT, graph_store, NeverCalledPredicateEvaluator()
        )

        # Assert
        assert result.obligations == []
        assert result.disclosures == []


class TestObligationContextGovernedByAndMandatesBothReachRules:
    """The traversal reaches rules whether the record models an entity-
    triggered GOVERNED_BY hop or an inbound MANDATES hop — the operation
    itself is agnostic to which edge resolved a given candidate record, since
    the port already flattens both into one candidate stream."""

    async def test_multiple_distinct_rules_are_all_admitted(self) -> None:
        # Arrange — one record standing in for a GOVERNED_BY-reached rule, one
        # for a MANDATES-reached rule; the operation treats both identically.
        graph_store = InMemoryGraphStore()
        graph_store.set_obligation_candidates(
            [_rule_record(node_id="rule-governed-by"), _rule_record(node_id="rule-mandates")]
        )

        # Act
        result = await obligation_context(
            "sol-1", _CONTEXT, graph_store, NeverCalledPredicateEvaluator()
        )

        # Assert
        node_ids = {entry.envelope.node_id for entry in result.obligations}
        assert node_ids == {"rule-governed-by", "rule-mandates"}


class TestObligationContextEmptyInputs:
    """Empty resolutions yield empty lists, never an error."""

    async def test_solution_governed_by_nothing_yields_an_empty_result(self) -> None:
        # Arrange — the in-memory double reports no configured candidates,
        # standing in for a solution whose USES/FOLLOWS entities reach no rule.
        graph_store = InMemoryGraphStore()

        # Act
        result = await obligation_context(
            "sol-ungoverned", _CONTEXT, graph_store, FailClosedPredicateEvaluator()
        )

        # Assert
        assert result.obligations == []
        assert result.disclosures == []

    async def test_absent_solution_yields_an_empty_result(self) -> None:
        # Arrange — the in-memory double reports no configured candidates,
        # standing in for an absent solution (the port's leading MATCH finds
        # nothing) — never TARGET_NOT_FOUND (O1).
        graph_store = InMemoryGraphStore()

        # Act
        result = await obligation_context(
            "sol-does-not-exist", _CONTEXT, graph_store, FailClosedPredicateEvaluator()
        )

        # Assert
        assert result.obligations == []
        assert result.disclosures == []
