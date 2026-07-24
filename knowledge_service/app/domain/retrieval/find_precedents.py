##############################################################################
# Module: app/domain/retrieval/find_precedents.py
# Service: knowledge-service
# Author: Haffey Enterprises LLC
# Created: 2026-07-23
# Revised: 2026-07-23
# Description: find-precedents (SDD-001 §3.3.5) — prior produced
#   `(:Artifact:Solution)` retrieval by structural criteria (shared capability/
#   pattern/technology linkage, `target_environment`, gate outcome), with
#   gate-decision context. Deterministic traversal only — no similarity
#   scoring, no ranking.
#
#   This is a track-record-style operation, not a ground-truth one: a
#   Solution is an Artifact (DDR-002 §5) — it carries NO KG plane label and is
#   never a promotion/conditional/retraction subject, so the read-discipline
#   flags below are FIXED, exactly as track_record_lookup.py fixes
#   ObservedPattern's (same reasoning, same shape): a Solution is always
#   `origin_mechanism: authored` (§5), never a pending `CandidatePromotion`
#   (#9, a distinct label), never `applicability_state`/`HAS_CONDITION`-
#   bearing (§5, exclusive to `PROMOTES_TO_KNOWLEDGE`-materialized nodes), and
#   never a `RETRACTS` target (§7 #21). Fixing the flags is sound only because
#   the invariant is CHECKED, not assumed: a record whose `origin_mechanism`
#   disagrees is excluded, fail-closed, before it ever reaches the
#   read-discipline core. This is deliberately NOT the shared
#   `is_promoted_only_state_contradiction` guard — that guard fires on a
#   record CLAIMING a promoted-only surface with a non-promoted origin, which
#   can never happen here since this operation never reads such a surface off
#   the record in the first place; the check here is simpler (origin equals
#   the one fixed value) and would not be served by importing that guard.
#
#   At-least-one-linkage guard (F4): an all-empty linkage criteria set (no
#   capability_ids, pattern_ids, or technology_ids) returns an empty result
#   without ever reaching the port — an unconstrained scan of every produced
#   Solution is not this operation's contract.
#
#   `result.disclosures` from the R2 core is always empty for these
#   fixed-constant candidates (a Solution is never conditionally excluded) and
#   is deliberately not surfaced on `FindPrecedentsResult`, which carries no
#   disclosure channel (F4) — matching SDD-001's "no similarity scoring" and
#   "deterministic traversal" framing: there is nothing here to disclose.
##############################################################################

import structlog

from app.domain.retrieval.read_discipline import apply_read_discipline
from app.domain.retrieval.types import CandidateNode, ConsumingContext
from app.domain.shared.envelope import EnvelopeAttribution
from app.models import FindPrecedentsResult, GateDecisionContext, PrecedentEntry
from app.ports.graph_store import (
    FindPrecedentsCandidateRecord,
    FindPrecedentsCriteria,
    GraphStoragePort,
)
from app.ports.predicate_eval import PredicateEvaluationPort

log = structlog.get_logger()

# The one origin_mechanism a Solution is schema-permitted to carry (DDR-002
# §5). Checked, not assumed — see _to_precedent_candidate.
_SOLUTION_ORIGIN_MECHANISM = "authored"


async def find_precedents(
    criteria: FindPrecedentsCriteria,
    context: ConsumingContext,
    graph_store: GraphStoragePort,
    predicate_evaluator: PredicateEvaluationPort,
) -> FindPrecedentsResult:
    """Resolve prior produced Solutions matching the given structural criteria.

    Args:
        criteria: The structural match criteria (F4). At least one of
            `capability_ids`/`pattern_ids`/`technology_ids` must be non-empty.
        context: The §3.2 consuming-context payload. Threaded through so the
            R2 core's ordered trio runs unmodified, though this operation's
            candidates are always unconditional in practice.
        graph_store: The graph port (production: Neo4jAdapter; tests: the
            in-memory double).
        predicate_evaluator: The in-process predicate port. Never reached by
            this operation's candidates in practice.

    Returns:
        The matching precedents (each with its envelope, target_environment,
        and gate-decision context), deterministic and unranked. An all-empty
        linkage criteria set, or no Solution matching the given criteria,
        yields an empty result, never an error.
    """
    if not (criteria.capability_ids or criteria.pattern_ids or criteria.technology_ids):
        return FindPrecedentsResult(precedents=[])

    records = await graph_store.find_precedents(criteria)

    candidates: list[CandidateNode] = []
    context_by_node_id: dict[str, FindPrecedentsCandidateRecord] = {}
    for record in records:
        candidate = _to_precedent_candidate(record)
        if candidate is None:
            continue
        candidates.append(candidate)
        context_by_node_id[record.node_id] = record

    result = await apply_read_discipline(candidates, context, predicate_evaluator)
    precedents = [
        PrecedentEntry(
            envelope=envelope,
            target_environment=context_by_node_id[envelope.node_id].target_environment,
            gate_decisions=[
                GateDecisionContext(
                    outcome=gate_decision.outcome,
                    gate=gate_decision.gate,
                    decision_id=gate_decision.decision_id,
                )
                for gate_decision in context_by_node_id[envelope.node_id].gate_decisions
            ],
        )
        for envelope in result.admitted
    ]
    return FindPrecedentsResult(precedents=precedents)


def _to_precedent_candidate(record: FindPrecedentsCandidateRecord) -> CandidateNode | None:
    """Map one raw find-precedents record into a `CandidateNode`.

    The read-discipline flags below are fixed, not read from `record` — sound
    only because `origin_mechanism` is checked here first. A record that
    disagrees with the invariant this operation's fixed flags rely on is
    excluded rather than admitted with flags that would no longer be true.

    Args:
        record: The port-level structural facts for one matching Solution.

    Returns:
        The `CandidateNode`, with the read-discipline flags fixed to the
        values structurally forced by a Solution's Artifact provenance model
        (see the module description), or `None` if the record's
        `origin_mechanism` violates that invariant — excluded, fail-closed,
        rather than admitted on flags that would no longer hold.
    """
    if record.origin_mechanism != _SOLUTION_ORIGIN_MECHANISM:
        log.warning(
            "find_precedents_candidate_excluded",
            node_id=record.node_id,
            reason="unexpected_origin_mechanism",
            origin_mechanism=record.origin_mechanism,
        )
        return None

    return CandidateNode(
        attribution=EnvelopeAttribution(
            node_id=record.node_id,
            node_kind="Solution",
            plane_labels=(),
            origin_mechanism=record.origin_mechanism,
            derivation_class="primary",
            version=record.version,
            effective_from=None,
            effective_to=None,
            version_pin=record.version,
            confidences=(),
            catalog_eligibility=None,
            deprecation=None,
        ),
        proposal_pending=False,
        retracted=False,
        applicability_state="unconditional",
        conditions=(),
    )
