##############################################################################
# Module: app/domain/retrieval/read_discipline.py
# Service: knowledge-service
# Author: Haffey Enterprises LLC
# Created: 2026-07-23
# Revised: 2026-07-23
# Description: The read-discipline core (SDD-001 §4.4) — the ordered trio
#   every ground-truth §3.3 retrieval operation applies over its candidate
#   nodes: proposal exclusion (#9), retraction exclusion (#21), conditional
#   admission (#19). Factored out of the nine operations (R3+) so the order,
#   the fail-closed posture, and the §3.2 disclosure channel are enforced in
#   exactly one place. Silent exclusions (proposal, retraction) never call the
#   predicate port and never appear in either output list; conditional
#   exclusions always disclose via the §3.2 channel, never the node's content.
#   `applicability_state` is authoritative over `conditions`' emptiness: a
#   node marked `conditional` with no resolved `HAS_CONDITION` path is a
#   resolution defect, not license to admit unconditionally — it excludes,
#   fail-closed, as `condition_unevaluable` (R2 review finding).
##############################################################################

from collections.abc import Sequence

import structlog

from app.domain.retrieval.types import CandidateNode, ConsumingContext
from app.domain.shared.envelope import assemble_envelope, build_disclosure_entry
from app.models import (
    ConditionalAdmissionStatus,
    DisclosureEntry,
    DisclosureReason,
    ReadResult,
    ResultEnvelope,
)
from app.ports.predicate_eval import PredicateEvaluationPort, PredicateUnevaluable

log = structlog.get_logger()


async def apply_read_discipline(
    candidates: Sequence[CandidateNode],
    context: ConsumingContext,
    predicate_evaluator: PredicateEvaluationPort,
) -> ReadResult:
    """Apply the §4.4 ordered trio over a batch of candidate nodes.

    Each candidate is evaluated independently, in the fixed order: proposal
    exclusion, retraction exclusion, conditional admission. Results compose in
    the candidates' own order.

    Args:
        candidates: The retrieval candidates to admit or exclude.
        context: The §3.2 consuming-context payload.
        predicate_evaluator: The in-process predicate port (production: the
            fail-closed evaluator; tests: a controllable double).

    Returns:
        The admitted envelopes and the disclosed exclusions. Silently-excluded
        candidates (proposal, retraction) appear in neither list.
    """
    admitted: list[ResultEnvelope] = []
    disclosures: list[DisclosureEntry] = []

    for candidate in candidates:
        outcome = await _apply_to_one(candidate, context, predicate_evaluator)
        if isinstance(outcome, DisclosureEntry):
            disclosures.append(outcome)
        elif outcome is not None:
            admitted.append(outcome)
        # else: silent exclusion (proposal / retraction) — neither list.

    return ReadResult(admitted=admitted, disclosures=disclosures)


async def _apply_to_one(
    candidate: CandidateNode,
    context: ConsumingContext,
    predicate_evaluator: PredicateEvaluationPort,
) -> ResultEnvelope | DisclosureEntry | None:
    """Apply the ordered trio to one candidate. See `apply_read_discipline`."""
    node_id = candidate.attribution.node_id

    # (a) Proposal exclusion (#9) — un-approved CandidatePromotion. Silent.
    if candidate.proposal_pending:
        return None

    # (b) Retraction exclusion (#21) — EA-approved inbound RETRACTS. Silent.
    if candidate.retracted:
        return None

    # (c) Conditional admission (#19). `applicability_state` is authoritative
    # over `conditions`' emptiness — a node marked "conditional" with no
    # resolved HAS_CONDITION path is a resolution defect (the marker says a
    # Condition governs it; none was found), never an unconditional admit.
    if not candidate.conditions:
        if candidate.applicability_state == "conditional":
            log.info(
                "conditional_excluded",
                node_id=node_id,
                reason=DisclosureReason.CONDITION_UNEVALUABLE,
            )
            log.warning(
                "predicate_evaluation_failed",
                node_id=node_id,
                cause="conditional_without_resolvable_condition",
            )
            return build_disclosure_entry(node_id, DisclosureReason.CONDITION_UNEVALUABLE)

        return assemble_envelope(
            candidate.attribution,
            conditional_admission=ConditionalAdmissionStatus.UNCONDITIONAL,
        )

    # `conditions` is non-empty here regardless of what `applicability_state`
    # says — the reverse inconsistency (marked "unconditional" but carrying a
    # resolved condition) still falls through to evaluation below rather than
    # a blind admit: fail-closed is the tiebreaker in both directions.
    if len(candidate.conditions) > 1:
        # DDR-002's stated safe interim: surface to EA, never silently compose.
        # Structurally still a #19 exclusion (carries its reason) AND the
        # governance-significant scope-conflict event (SDD-001 §8) — neither
        # condition is ever evaluated.
        log.info(
            "conditional_excluded",
            node_id=node_id,
            reason=DisclosureReason.MULTI_CONDITION_SCOPE_CONFLICT,
        )
        log.warning(
            "scope_conflict_blocked",
            node_id=node_id,
            reason=DisclosureReason.MULTI_CONDITION_SCOPE_CONFLICT,
        )
        return build_disclosure_entry(node_id, DisclosureReason.MULTI_CONDITION_SCOPE_CONFLICT)

    condition = candidate.conditions[0]
    missing_fields = condition.required_context_fields - context.declared_fields.keys()
    if missing_fields:
        log.info(
            "conditional_excluded",
            node_id=node_id,
            reason=DisclosureReason.CONDITION_UNEVALUABLE,
        )
        log.warning(
            "predicate_evaluation_failed",
            node_id=node_id,
            cause="missing_manifest_declared_context",
            missing_fields=sorted(missing_fields),
        )
        return build_disclosure_entry(node_id, DisclosureReason.CONDITION_UNEVALUABLE)

    try:
        admits = await predicate_evaluator.evaluate(
            condition.predicate, dict(context.declared_fields)
        )
    except PredicateUnevaluable:
        log.info(
            "conditional_excluded",
            node_id=node_id,
            reason=DisclosureReason.CONDITION_UNEVALUABLE,
        )
        log.warning(
            "predicate_evaluation_failed",
            node_id=node_id,
            cause="predicate_unevaluable",
        )
        return build_disclosure_entry(node_id, DisclosureReason.CONDITION_UNEVALUABLE)

    if admits:
        return assemble_envelope(
            candidate.attribution,
            conditional_admission=ConditionalAdmissionStatus.CONDITIONALLY_ADMITTED,
        )

    log.info(
        "conditional_excluded",
        node_id=node_id,
        reason=DisclosureReason.CONDITION_UNSATISFIED,
    )
    return build_disclosure_entry(node_id, DisclosureReason.CONDITION_UNSATISFIED)
