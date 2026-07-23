##############################################################################
# Module: app/domain/shared/predicate_evaluators.py
# Service: knowledge-service
# Author: Haffey Enterprises LLC
# Created: 2026-07-23
# Revised: 2026-07-23
# Description: Production PredicateEvaluationPort implementations (SDD-001
#   §4.2, §4.4). `FailClosedPredicateEvaluator` is the sole production
#   evaluator at RBT-78/R2: no `Condition` predicate grammar is ratified yet
#   (DDR-003, forthcoming), so it invents none — it always raises
#   `PredicateUnevaluable`, honestly reporting that it cannot evaluate
#   anything. Consequence, by design: every conditional node today is excluded
#   with reason `condition_unevaluable`; `condition_unsatisfied` only becomes
#   reachable once a real evaluator lands. This is the ratified never-auto-
#   admit posture (§4.4), not a gap.
##############################################################################

from collections.abc import Mapping

from app.ports.predicate_eval import PredicateUnevaluable


class FailClosedPredicateEvaluator:
    """The production `PredicateEvaluationPort` — always fails closed.

    A structurally-conforming `PredicateEvaluationPort` implementation with no
    predicate vocabulary behind it. It never returns a bare verdict: absent a
    ratified grammar there is nothing to evaluate `predicate` or `context`
    against, so every call raises `PredicateUnevaluable`.
    """

    async def evaluate(
        self,
        predicate: Mapping[str, object],
        context: Mapping[str, object],
    ) -> bool:
        """Always raise — no predicate grammar exists to evaluate against.

        Args:
            predicate: Unused; no grammar exists yet to interpret it.
            context: Unused; no grammar exists yet to interpret it.

        Raises:
            PredicateUnevaluable: Always.
        """
        raise PredicateUnevaluable(
            "no predicate vocabulary is ratified yet (DDR-003, forthcoming); "
            "fail-closed per SDD-001 §4.4"
        )
