##############################################################################
# Module: predicate_eval.py
# Service: knowledge-service
# Author: Haffey Enterprises LLC
# Created: 2026-07-21
# Revised: 2026-07-23
# Description: PredicateEvaluationPort — the in-process host for Condition
#   predicate evaluation (SDD-001 §4.2). Declared at RBT-77 as a pure Protocol
#   with no runtime behavior; RBT-78 fixes the port's THREE-outcome contract
#   (SDD-001 §3.2 needs unsatisfied and unevaluable held distinct) and adds
#   `PredicateUnevaluable`, the typed signal for the unevaluable case. This
#   module still invents no predicate grammar — the concrete `Condition`
#   vocabulary remains DDR-003's, routed onward to the constraint-validator
#   design; evaluation semantics are single-sourced from that shared component
#   (one grammar, one implementation, two hosts) once it lands.
##############################################################################

from collections.abc import Mapping
from typing import Protocol, runtime_checkable


class PredicateUnevaluable(Exception):
    """Signals that a `Condition` predicate could not be evaluated.

    Raised by a `PredicateEvaluationPort` implementation for any can't-evaluate
    case — missing manifest-declared context, a malformed predicate, or
    unratified vocabulary (SDD-001 §4.4). This is a control-flow signal
    consumed entirely by the read-discipline core (`app.domain.retrieval`),
    which converts it to a `condition_unevaluable` disclosure; it never crosses
    the API boundary and is deliberately not a `DomainError` subclass — nothing
    maps it through the §3.2 exception handler.
    """


@runtime_checkable
class PredicateEvaluationPort(Protocol):
    """Evaluates a `Condition` predicate against a retrieval context.

    **Three-outcome contract (SDD-001 §3.2, fixed at RBT-78):** `evaluate`
    returns `True` when the predicate admits its node, `False` when it does
    not, and *raises* `PredicateUnevaluable` when it cannot reach a verdict at
    all. A two-outcome boolean would collapse "unsatisfied" and "unevaluable"
    into one signal, which the §3.2 disclosure channel needs held apart
    (`condition_unsatisfied` vs. `condition_unevaluable`).

    The concrete predicate grammar is still DDR-003's condition vocabulary
    (forthcoming), routed onward to the constraint-validator design; no
    implementation may invent it here, and none may fork its semantics once
    ratified. The signature below is the seam's expected shape, not a ratified
    grammar — treat a change to it as cheap until the vocabulary lands.

    Evaluation is hosted **in-process** by design (SDD-001 §4.2): a
    safety-critical read control does not take a network hop on the hot path,
    and enforcement keeps one home.

    **Fail-closed is the ratified posture** (SDD-001 §4.4). An implementation
    that cannot evaluate a predicate must raise `PredicateUnevaluable`, never
    return a bare `False` to mean "couldn't tell" and never return `True` to
    mean "assume admitted." The worst reachable state is over-exclusion; silent
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

        Raises:
            PredicateUnevaluable: If the predicate cannot be evaluated at all
                — missing manifest-declared context, a malformed predicate, or
                unratified vocabulary. Never signalled by a return value.
        """
        ...
