##############################################################################
# Module: test_read_discipline.py
# Service: knowledge-service
# Author: Haffey Enterprises LLC
# Created: 2026-07-23
# Revised: 2026-07-23
# Description: Unit tests for the read-discipline core (app/domain/retrieval/
#   read_discipline.py) — the §4.4 ordered trio (proposal exclusion, retraction
#   exclusion, conditional admission) applied over candidate nodes, its nine
#   outcome branches (including the applicability_state/conditions consistency
#   guard — an R2 review finding: a "conditional"-marked node with no resolved
#   condition fails closed rather than falling through to an unconditional
#   admit), the §8 event emissions on each excluding path, and the envelope
#   assembler wiring. An elevated 100%-branch surface (SDD-001 §6): a
#   `ControllablePredicateEvaluator` test double (admit / unsatisfied /
#   raise-unevaluable / never-called-assertion on demand) makes every branch
#   reachable without a real predicate grammar, which does not exist yet.
##############################################################################

import json
from collections.abc import Mapping
from typing import Literal

import pytest

from app.domain.retrieval.read_discipline import apply_read_discipline
from app.domain.retrieval.types import CandidateNode, ConditionRef, ConsumingContext
from app.domain.shared.envelope import EnvelopeAttribution
from app.models import ConditionalAdmissionStatus, DisclosureReason
from app.observability.logging import configure_logging
from app.ports.predicate_eval import PredicateUnevaluable


class ControllablePredicateEvaluator:
    """Test-only double: admits, refuses, or raises unevaluable on demand.

    Never wired into the production path — the sole production implementation
    is `FailClosedPredicateEvaluator` (app/domain/shared/predicate_evaluators.py).
    Exists purely to make every read-discipline branch reachable ahead of a
    real predicate grammar (DDR-003, forthcoming).
    """

    def __init__(self, *, verdict: bool | None = None) -> None:
        """Args: verdict — True/False to return; None to raise PredicateUnevaluable."""
        self._verdict = verdict

    async def evaluate(
        self, predicate: Mapping[str, object], context: Mapping[str, object]
    ) -> bool:
        if self._verdict is None:
            raise PredicateUnevaluable("test double: configured to raise")
        return self._verdict


class NeverCalledPredicateEvaluator:
    """Test-only double that fails the test if `evaluate` is ever invoked.

    Used to prove ordering: proposal exclusion and retraction exclusion must
    both short-circuit before the conditional-admission step would touch the
    predicate port at all.
    """

    async def evaluate(
        self, predicate: Mapping[str, object], context: Mapping[str, object]
    ) -> bool:
        raise AssertionError("evaluate() must not be called for this candidate")


def _attribution(node_id: str = "node-1") -> EnvelopeAttribution:
    return EnvelopeAttribution(
        node_id=node_id,
        node_kind="Technology",
        plane_labels=("Catalog",),
        origin_mechanism="promoted",
        derivation_class=None,
        version="1",
        effective_from=None,
        effective_to=None,
        version_pin="v-1",
        confidences=(0.75,),
    )


def _candidate(
    *,
    node_id: str = "node-1",
    proposal_pending: bool = False,
    retracted: bool = False,
    conditions: tuple[ConditionRef, ...] = (),
    applicability_state: Literal["unconditional", "conditional"] | None = None,
) -> CandidateNode:
    return CandidateNode(
        attribution=_attribution(node_id),
        proposal_pending=proposal_pending,
        retracted=retracted,
        applicability_state=(
            applicability_state
            if applicability_state is not None
            else ("conditional" if conditions else "unconditional")
        ),
        conditions=conditions,
    )


_CONTEXT = ConsumingContext(
    environment_class="production",
    data_classification="internal",
    declared_fields={"tier": "gold"},
)

_ONE_CONDITION = (
    ConditionRef(predicate={"op": "eq"}, required_context_fields=frozenset({"tier"})),
)
_TWO_CONDITIONS = (
    ConditionRef(predicate={"op": "eq"}, required_context_fields=frozenset({"tier"})),
    ConditionRef(predicate={"op": "ne"}, required_context_fields=frozenset({"tier"})),
)
_MISSING_FIELD_CONDITION = (
    ConditionRef(predicate={"op": "eq"}, required_context_fields=frozenset({"missing_field"})),
)


def _log_events(capsys: pytest.CaptureFixture[str]) -> list[dict[str, object]]:
    out = capsys.readouterr().out.strip()
    return [json.loads(line) for line in out.splitlines() if line]


class TestSilentExclusions:
    """(a) proposal exclusion and (b) retraction exclusion — silent, in order."""

    async def test_proposal_pending_node_is_silently_excluded(self) -> None:
        # Arrange — a condition present too, evaluated by an evaluator that
        # fails the test if reached: proves proposal exclusion runs first.
        candidate = _candidate(proposal_pending=True, conditions=_ONE_CONDITION)

        # Act
        result = await apply_read_discipline([candidate], _CONTEXT, NeverCalledPredicateEvaluator())

        # Assert
        assert result.admitted == []
        assert result.disclosures == []

    async def test_retracted_node_is_silently_excluded(self) -> None:
        # Arrange
        candidate = _candidate(retracted=True, conditions=_ONE_CONDITION)

        # Act
        result = await apply_read_discipline([candidate], _CONTEXT, NeverCalledPredicateEvaluator())

        # Assert
        assert result.admitted == []
        assert result.disclosures == []

    async def test_proposal_and_retraction_exclusions_emit_no_disclosure_event(
        self, capsys: pytest.CaptureFixture[str]
    ) -> None:
        # Arrange
        configure_logging("INFO")
        candidates = [
            _candidate(node_id="proposal-node", proposal_pending=True),
            _candidate(node_id="retracted-node", retracted=True),
        ]

        # Act
        await apply_read_discipline(candidates, _CONTEXT, NeverCalledPredicateEvaluator())

        # Assert — SDD-001 §3.2: excluded without disclosure, silently.
        assert _log_events(capsys) == []


class TestUnconditionalAdmission:
    """No HAS_CONDITION path — admit unconditionally."""

    async def test_unconditional_node_is_admitted(self) -> None:
        # Arrange
        candidate = _candidate()

        # Act
        result = await apply_read_discipline(
            [candidate], _CONTEXT, ControllablePredicateEvaluator(verdict=True)
        )

        # Assert
        assert result.disclosures == []
        assert len(result.admitted) == 1
        envelope = result.admitted[0]
        assert envelope.node_id == "node-1"
        assert envelope.node_kind == "Technology"
        assert (
            envelope.applicability.conditional_admission == ConditionalAdmissionStatus.UNCONDITIONAL
        )


class TestApplicabilityStateConsistencyGuard:
    """applicability_state is authoritative — fail-closed on any mismatch.

    R2 review finding: keying conditional-ness purely off `conditions`'
    emptiness let a "conditional"-marked node with no resolved condition
    (a resolution defect) fall through to an unconditional admit — a
    fail-open hole in exactly the control #19 exists to guard.
    """

    async def test_conditional_marker_with_no_resolved_condition_is_excluded(self) -> None:
        # Arrange — marked conditional, but conditions resolved empty: never
        # admit; the evaluator must not even be reached.
        candidate = _candidate(applicability_state="conditional", conditions=())

        # Act
        result = await apply_read_discipline([candidate], _CONTEXT, NeverCalledPredicateEvaluator())

        # Assert
        assert result.admitted == []
        assert len(result.disclosures) == 1
        assert result.disclosures[0].node_id == "node-1"
        assert result.disclosures[0].reason == DisclosureReason.CONDITION_UNEVALUABLE

    async def test_conditional_marker_with_no_resolved_condition_emits_the_fail_closed_events(
        self, capsys: pytest.CaptureFixture[str]
    ) -> None:
        # Arrange
        configure_logging("INFO")
        candidate = _candidate(applicability_state="conditional", conditions=())

        # Act
        await apply_read_discipline([candidate], _CONTEXT, NeverCalledPredicateEvaluator())

        # Assert
        events = _log_events(capsys)
        event_names = {e["event"] for e in events}
        assert "conditional_excluded" in event_names
        assert "predicate_evaluation_failed" in event_names
        failed = next(e for e in events if e["event"] == "predicate_evaluation_failed")
        assert failed["level"] == "warning"
        assert failed["cause"] == "conditional_without_resolvable_condition"

    async def test_unconditional_marker_with_a_resolved_condition_still_evaluates(self) -> None:
        # Arrange — the reverse inconsistency: marked unconditional, but a
        # condition was resolved anyway. Fail-closed is the tiebreaker: it
        # must evaluate (and can still exclude), never blind-admit on the
        # marker alone. A refusing evaluator proves this — a blind admit
        # would ignore it and return the node.
        candidate = _candidate(applicability_state="unconditional", conditions=_ONE_CONDITION)

        # Act
        result = await apply_read_discipline(
            [candidate], _CONTEXT, ControllablePredicateEvaluator(verdict=False)
        )

        # Assert
        assert result.admitted == []
        assert len(result.disclosures) == 1
        assert result.disclosures[0].reason == DisclosureReason.CONDITION_UNSATISFIED

    async def test_unconditional_marker_with_a_resolved_condition_can_still_admit(self) -> None:
        # Arrange — same inconsistency, but the resolved condition is
        # satisfied: evaluation (not the stale marker) decides the outcome.
        candidate = _candidate(applicability_state="unconditional", conditions=_ONE_CONDITION)

        # Act
        result = await apply_read_discipline(
            [candidate], _CONTEXT, ControllablePredicateEvaluator(verdict=True)
        )

        # Assert
        assert result.disclosures == []
        assert len(result.admitted) == 1
        assert (
            result.admitted[0].applicability.conditional_admission
            == ConditionalAdmissionStatus.CONDITIONALLY_ADMITTED
        )


class TestMultiConditionExclusion:
    """Multiple HAS_CONDITION paths — exclude + disclose, never composed."""

    async def test_multi_condition_node_is_excluded_and_disclosed(self) -> None:
        # Arrange — an evaluator that would fail the test if invoked: no
        # composition rule is invented, so neither condition is evaluated.
        candidate = _candidate(conditions=_TWO_CONDITIONS)

        # Act
        result = await apply_read_discipline([candidate], _CONTEXT, NeverCalledPredicateEvaluator())

        # Assert
        assert result.admitted == []
        assert len(result.disclosures) == 1
        assert result.disclosures[0].node_id == "node-1"
        assert result.disclosures[0].reason == DisclosureReason.MULTI_CONDITION_SCOPE_CONFLICT

    async def test_multi_condition_node_emits_scope_conflict_blocked(
        self, capsys: pytest.CaptureFixture[str]
    ) -> None:
        # Arrange
        configure_logging("INFO")
        candidate = _candidate(conditions=_TWO_CONDITIONS)

        # Act
        await apply_read_discipline([candidate], _CONTEXT, NeverCalledPredicateEvaluator())

        # Assert — governance-significant WARN (SDD-001 §8), plus the ordinary
        # #19-exclusion INFO event (it is, structurally, a #19 exclusion too).
        events = _log_events(capsys)
        event_names = {e["event"] for e in events}
        assert "scope_conflict_blocked" in event_names
        assert "conditional_excluded" in event_names
        blocked = next(e for e in events if e["event"] == "scope_conflict_blocked")
        assert blocked["level"] == "warning"
        assert blocked["node_id"] == "node-1"


class TestSingleConditionMissingContext:
    """Required manifest-declared fields absent from context — unevaluable."""

    async def test_missing_required_field_excludes_and_discloses_unevaluable(self) -> None:
        # Arrange — no evaluator call should even be attempted.
        candidate = _candidate(conditions=_MISSING_FIELD_CONDITION)

        # Act
        result = await apply_read_discipline([candidate], _CONTEXT, NeverCalledPredicateEvaluator())

        # Assert
        assert result.admitted == []
        assert len(result.disclosures) == 1
        assert result.disclosures[0].reason == DisclosureReason.CONDITION_UNEVALUABLE

    async def test_missing_required_field_emits_conditional_excluded_and_predicate_failed(
        self, capsys: pytest.CaptureFixture[str]
    ) -> None:
        # Arrange
        configure_logging("INFO")
        candidate = _candidate(conditions=_MISSING_FIELD_CONDITION)

        # Act
        await apply_read_discipline([candidate], _CONTEXT, NeverCalledPredicateEvaluator())

        # Assert
        events = _log_events(capsys)
        event_names = {e["event"] for e in events}
        assert "conditional_excluded" in event_names
        assert "predicate_evaluation_failed" in event_names
        failed = next(e for e in events if e["event"] == "predicate_evaluation_failed")
        assert failed["level"] == "warning"


class TestSingleConditionPredicateUnevaluable:
    """The port raises PredicateUnevaluable — fail-closed, disclosed."""

    async def test_predicate_unevaluable_excludes_and_discloses_unevaluable(self) -> None:
        # Arrange
        candidate = _candidate(conditions=_ONE_CONDITION)

        # Act
        result = await apply_read_discipline(
            [candidate], _CONTEXT, ControllablePredicateEvaluator(verdict=None)
        )

        # Assert
        assert result.admitted == []
        assert len(result.disclosures) == 1
        assert result.disclosures[0].reason == DisclosureReason.CONDITION_UNEVALUABLE

    async def test_predicate_unevaluable_emits_conditional_excluded_and_predicate_failed(
        self, capsys: pytest.CaptureFixture[str]
    ) -> None:
        # Arrange
        configure_logging("INFO")
        candidate = _candidate(conditions=_ONE_CONDITION)

        # Act
        await apply_read_discipline(
            [candidate], _CONTEXT, ControllablePredicateEvaluator(verdict=None)
        )

        # Assert
        events = _log_events(capsys)
        event_names = {e["event"] for e in events}
        assert "conditional_excluded" in event_names
        assert "predicate_evaluation_failed" in event_names


class TestSingleConditionSatisfied:
    """The predicate admits — conditionally admitted."""

    async def test_satisfied_predicate_admits_the_node(self) -> None:
        # Arrange
        candidate = _candidate(conditions=_ONE_CONDITION)

        # Act
        result = await apply_read_discipline(
            [candidate], _CONTEXT, ControllablePredicateEvaluator(verdict=True)
        )

        # Assert
        assert result.disclosures == []
        assert len(result.admitted) == 1
        assert (
            result.admitted[0].applicability.conditional_admission
            == ConditionalAdmissionStatus.CONDITIONALLY_ADMITTED
        )

    async def test_satisfied_predicate_emits_no_exclusion_event(
        self, capsys: pytest.CaptureFixture[str]
    ) -> None:
        # Arrange
        configure_logging("INFO")
        candidate = _candidate(conditions=_ONE_CONDITION)

        # Act
        await apply_read_discipline(
            [candidate], _CONTEXT, ControllablePredicateEvaluator(verdict=True)
        )

        # Assert
        assert _log_events(capsys) == []


class TestSingleConditionUnsatisfied:
    """The predicate refuses — excluded and disclosed, no fail-closed event."""

    async def test_unsatisfied_predicate_excludes_and_discloses(self) -> None:
        # Arrange
        candidate = _candidate(conditions=_ONE_CONDITION)

        # Act
        result = await apply_read_discipline(
            [candidate], _CONTEXT, ControllablePredicateEvaluator(verdict=False)
        )

        # Assert
        assert result.admitted == []
        assert len(result.disclosures) == 1
        assert result.disclosures[0].reason == DisclosureReason.CONDITION_UNSATISFIED

    async def test_unsatisfied_predicate_emits_conditional_excluded_only(
        self, capsys: pytest.CaptureFixture[str]
    ) -> None:
        # Arrange
        configure_logging("INFO")
        candidate = _candidate(conditions=_ONE_CONDITION)

        # Act
        await apply_read_discipline(
            [candidate], _CONTEXT, ControllablePredicateEvaluator(verdict=False)
        )

        # Assert — a plain refusal is not a fail-closed event: no WARN.
        events = _log_events(capsys)
        event_names = {e["event"] for e in events}
        assert event_names == {"conditional_excluded"}


class TestMultipleCandidatesIndependence:
    """Each candidate is evaluated independently; results compose in order."""

    async def test_mixed_batch_yields_the_expected_admitted_and_disclosed_sets(self) -> None:
        # Arrange
        admitted_candidate = _candidate(node_id="admit-me")
        proposal_candidate = _candidate(node_id="hide-me-proposal", proposal_pending=True)
        unsatisfied_candidate = _candidate(node_id="disclose-me", conditions=_ONE_CONDITION)

        # Act
        result = await apply_read_discipline(
            [admitted_candidate, proposal_candidate, unsatisfied_candidate],
            _CONTEXT,
            ControllablePredicateEvaluator(verdict=False),
        )

        # Assert
        assert [e.node_id for e in result.admitted] == ["admit-me"]
        assert [d.node_id for d in result.disclosures] == ["disclose-me"]
