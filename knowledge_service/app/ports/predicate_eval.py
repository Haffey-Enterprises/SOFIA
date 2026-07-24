##############################################################################
# Module: predicate_eval.py
# Service: knowledge-service
# Author: Haffey Enterprises LLC
# Created: 2026-07-21
# Revised: 2026-07-21
# Description: PredicateEvaluationPort — the in-process host for Condition
#   predicate evaluation (SDD-001 §4.2). Declared, not implemented, at RBT-77:
#   a pure Protocol with no runtime behavior. Evaluation semantics are
#   single-sourced from the constraint-validator SDD's shared predicate
#   component — one grammar, one implementation, two hosts; a gateway-local
#   fork of predicate semantics is prohibited.
##############################################################################

from collections.abc import Mapping
from typing import Protocol, runtime_checkable


@runtime_checkable
class PredicateEvaluationPort(Protocol):
    """Evaluates a `Condition` predicate against a retrieval context.

    **Not implemented at RBT-77.** The concrete predicate grammar is DDR-003's
    condition vocabulary, routed onward by DDR-003 to the constraint-validator
    design; no implementation may be written here until that vocabulary is
    ratified, and none may fork its semantics when it is. The signature below
    is the seam's expected shape, not a ratified grammar — treat a change to it
    as cheap until the vocabulary lands.

    Evaluation is hosted **in-process** by design (SDD-001 §4.2): a
    safety-critical read control does not take a network hop on the hot path,
    and enforcement keeps one home.

    **Fail-closed is the ratified posture** (SDD-001 §4.4). An implementation
    that cannot evaluate a predicate — missing manifest-declared context, a
    malformed predicate, unratified vocabulary — must cause its node to be
    *excluded*, always. The worst reachable state is over-exclusion; silent
    admission is never a permitted outcome.
    """

    async def evaluate(
        self,
        predicate: Mapping[str, object],
        context: Mapping[str, object],
    ) -> bool:
        """Evaluate one predicate against the supplied retrieval context.

        Args:
            predicate: The `Condition`'s predicate payload, as carried on the
                graph node. Structure is DDR-003's to fix.
            context: The retrieval context fields the predicate is evaluated
                against, as determined from the `dependency_manifest`.

        Returns:
            True when the predicate admits its node; False when it does not.
            An implementation that cannot reach a verdict must not return True:
            fail-closed means exclusion, never admission.
        """
        ...
