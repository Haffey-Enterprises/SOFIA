##############################################################################
# Module: app/domain/retrieval/obligation_context.py
# Service: knowledge-service
# Author: Haffey Enterprises LLC
# Created: 2026-07-23
# Revised: 2026-07-23
# Description: obligation-context (SDD-001 §3.3.4) — the entity-triggered
#   graph half of the obligation model (DDR-002 §3): from a solution's
#   USES(Technology)/FOLLOWS(Pattern) entity set, the applicable PolicyRules
#   reached via outbound GOVERNED_BY and inbound MANDATES. Applies the R2
#   read-discipline core (a PolicyRule is Standards ground truth — genuinely
#   promotable-conditional or retractable, like Technology/Pattern), and
#   carries each rule's content payload (statement, opaque rule_definition,
#   dependency_manifest, enforcement_level, enforced_at_gate, domain)
#   alongside its envelope. Does NOT compute obligation closure
#   (condition-triggered rules from rule_definition, or the satisfaction join
#   against Attestation/structural evidence) and does NOT parse rule_definition
#   — both are the constraint-validator's (SDD-001 §3.3.4, DDR-002 §3).
#
#   The solution's USES/FOLLOWS entities are traversal ROOTS, not results — no
#   read-discipline runs on them (O2); only the resolved PolicyRules are
#   read-discipline subjects. Direct USES/FOLLOWS entities only — transitive
#   Pattern -> REQUIRES_CAPABILITY -> Capability governance is out of scope
#   this leg (O4).
#
#   `_to_obligation_candidate` is a local, second "plain ground-truth" mapper
#   (select_patterns._to_pattern_candidate is the first) — deliberately NOT
#   shared with it. Shared extraction is deferred by operator ruling until a
#   third consumer appears (under-govern); this module does not cross-import
#   _to_pattern_candidate.
##############################################################################

import structlog

from app.domain.retrieval.read_discipline import apply_read_discipline
from app.domain.retrieval.types import CandidateNode, ConditionRef, ConsumingContext
from app.domain.shared.envelope import EnvelopeAttribution
from app.domain.shared.read_discipline_guard import is_promoted_only_state_contradiction
from app.models import ObligationContextResult, ObligationEntry, PolicyRulePayload
from app.ports.graph_store import GraphStoragePort, ObligationCandidateRecord
from app.ports.predicate_eval import PredicateEvaluationPort

log = structlog.get_logger()


async def obligation_context(
    solution_id: str,
    context: ConsumingContext,
    graph_store: GraphStoragePort,
    predicate_evaluator: PredicateEvaluationPort,
) -> ObligationContextResult:
    """Resolve applicable PolicyRules for the given solution.

    Args:
        solution_id: The solution to resolve applicable PolicyRules for.
        context: The §3.2 consuming-context payload.
        graph_store: The graph port (production: Neo4jAdapter; tests: the
            in-memory double).
        predicate_evaluator: The in-process predicate port (production: the
            fail-closed evaluator; tests: a controllable double).

    Returns:
        The admitted obligations (each with its envelope and PolicyRule
        payload) and the disclosed conditionally-excluded rules (SDD-001
        §3.2). A record whose origin_mechanism contradicts a promoted-only
        surface it claims to carry is excluded before it reaches the core.
        An absent solution or a solution governed by nothing yields empty
        lists, never an error.
    """
    records = await graph_store.obligation_context(solution_id)

    candidates: list[CandidateNode] = []
    payload_by_node_id: dict[str, PolicyRulePayload] = {}
    for record in records:
        candidate = _to_obligation_candidate(record)
        if candidate is None:
            continue
        candidates.append(candidate)
        payload_by_node_id[record.node_id] = PolicyRulePayload(
            statement=record.statement,
            rule_definition=record.rule_definition,
            dependency_manifest=list(record.dependency_manifest),
            enforcement_level=record.enforcement_level,
            enforced_at_gate=record.enforced_at_gate,
            domain=record.domain,
        )

    result = await apply_read_discipline(candidates, context, predicate_evaluator)
    obligations = [
        ObligationEntry(envelope=envelope, policy_rule=payload_by_node_id[envelope.node_id])
        for envelope in result.admitted
    ]
    return ObligationContextResult(obligations=obligations, disclosures=result.disclosures)


def _to_obligation_candidate(record: ObligationCandidateRecord) -> CandidateNode | None:
    """Map one raw obligation-context record into a PolicyRule `CandidateNode`.

    Args:
        record: The port-level structural facts for one applicable PolicyRule.

    Returns:
        The `CandidateNode`, carrying the real retraction/conditional
        structure the traversal resolved, with `catalog_eligibility` and
        `deprecation` both `None` (Technology-only surfaces, DDR-002 §2.1),
        or `None` if the record's origin_mechanism contradicts a
        promoted-only surface it claims to carry — excluded, fail-closed,
        rather than admitted (or silently trusted) on a broken assumption.
    """
    if is_promoted_only_state_contradiction(
        origin_mechanism=record.origin_mechanism,
        retracted=record.retracted,
        applicability_state=record.applicability_state,
    ):
        log.warning(
            "obligation_context_candidate_excluded",
            node_id=record.node_id,
            reason="promoted_only_state_on_non_promoted_origin",
            origin_mechanism=record.origin_mechanism,
            retracted=record.retracted,
            applicability_state=record.applicability_state,
        )
        return None

    return CandidateNode(
        attribution=EnvelopeAttribution(
            node_id=record.node_id,
            node_kind="PolicyRule",
            plane_labels=("Standards",),
            origin_mechanism=record.origin_mechanism,
            derivation_class=record.derivation_class,
            version=record.version,
            effective_from=None,
            effective_to=None,
            version_pin=record.version,
            confidences=(),
            catalog_eligibility=None,
            deprecation=None,
        ),
        proposal_pending=False,
        retracted=record.retracted,
        applicability_state=record.applicability_state,
        conditions=tuple(
            ConditionRef(
                predicate=condition.predicate,
                required_context_fields=condition.required_context_fields,
            )
            for condition in record.conditions
        ),
    )
