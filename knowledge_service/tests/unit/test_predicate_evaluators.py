##############################################################################
# Module: test_predicate_evaluators.py
# Service: knowledge-service
# Author: Haffey Enterprises LLC
# Created: 2026-07-23
# Revised: 2026-07-23
# Description: Unit tests for the production predicate evaluator (app/domain/
#   shared/predicate_evaluators.py) — FailClosedPredicateEvaluator, ratified at
#   RBT-78/R2 as the sole production implementation ahead of DDR-003's
#   condition vocabulary. It invents no grammar: it always raises
#   PredicateUnevaluable, honestly reporting that it cannot evaluate anything,
#   which the read-discipline core (app.domain.retrieval) converts to a
#   condition_unevaluable disclosure (SDD-001 §4.4 fail-closed).
##############################################################################

import pytest

from app.domain.shared.predicate_evaluators import FailClosedPredicateEvaluator
from app.ports.predicate_eval import PredicateEvaluationPort, PredicateUnevaluable


class TestFailClosedPredicateEvaluator:
    """Always raises PredicateUnevaluable — never returns a verdict."""

    async def test_evaluate_always_raises_predicate_unevaluable(self) -> None:
        # Arrange
        evaluator = FailClosedPredicateEvaluator()

        # Act / Assert
        with pytest.raises(PredicateUnevaluable):
            await evaluator.evaluate({"kind": "anything"}, {"environment_class": "prod"})

    async def test_evaluate_raises_regardless_of_predicate_or_context_content(self) -> None:
        # Arrange — no predicate/context shape can coax a verdict out of it;
        # a real grammar doesn't exist yet, so nothing is admissible.
        evaluator = FailClosedPredicateEvaluator()

        # Act / Assert
        with pytest.raises(PredicateUnevaluable):
            await evaluator.evaluate({}, {})

    def test_fail_closed_evaluator_satisfies_the_predicate_evaluation_port(self) -> None:
        # Act / Assert — it is a real, structurally-conforming implementation.
        assert isinstance(FailClosedPredicateEvaluator(), PredicateEvaluationPort)
