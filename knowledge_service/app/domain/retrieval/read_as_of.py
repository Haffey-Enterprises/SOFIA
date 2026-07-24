##############################################################################
# Module: app/domain/retrieval/read_as_of.py
# Service: knowledge-service
# Author: Haffey Enterprises LLC
# Created: 2026-07-24
# Revised: 2026-07-24
# Description: read-as-of, PIN-MODE ONLY (SDD-001 §3.3.6) — resolution of a
#   supplied version pin over Option-A versioned ground truth: given a
#   versioned entity's business key and an exact retained version, resolve
#   that single version node, apply the §4.4 read-discipline trio at READ
#   time, and return its §3.2 envelope. As-of-by-timestamp resolution is out
#   of scope this build (routed to RBT-83: no in-scope label carries an
#   effective_from/effective_to window).
#
#   This is a single-SUBJECT resolver, not a candidate-set retriever, and the
#   FIRST read op that RAISES: a resolution miss (the pinned (business_key,
#   version) node doesn't exist) is TARGET_NOT_FOUND (D2). read-as-of is NOT
#   an audit op (SDD-001 §1 — that exception is scoped to §3.3.7-§3.3.8): it
#   enforces the trio on CURRENT read-discipline state, so a currently-
#   retracted pinned version is excluded even though the pin itself resolves
#   cleanly. A resolution HIT that the trio then excludes (silent drop,
#   guard-contradiction, or a conditional disclosure) is never
#   TARGET_NOT_FOUND — the node exists; only its absence raises.
#
#   `_to_candidate` is a LOCAL, third plain-ground-truth mapper (select_
#   patterns._to_pattern_candidate is the first, obligation_context's is the
#   second) — deliberately not shared or cross-imported here; consolidating
#   the three is a deferred, dedicated refactor task, not this leg's.
##############################################################################

import structlog

from app.domain.exceptions import GatewayError
from app.domain.retrieval.read_discipline import apply_read_discipline
from app.domain.retrieval.types import CandidateNode, ConditionRef, ConsumingContext
from app.domain.shared.envelope import EnvelopeAttribution
from app.domain.shared.read_discipline_guard import is_promoted_only_state_contradiction
from app.models import ErrorType, ReadResult
from app.ports.graph_store import GraphStoragePort, ReadAsOfNodeKind, ReadAsOfResolvedRecord
from app.ports.predicate_eval import PredicateEvaluationPort

log = structlog.get_logger()


async def read_as_of(
    node_kind: ReadAsOfNodeKind,
    business_key: str,
    version: str,
    context: ConsumingContext,
    graph_store: GraphStoragePort,
    predicate_evaluator: PredicateEvaluationPort,
) -> ReadResult:
    """Resolve a supplied version pin over versioned ground truth.

    Args:
        node_kind: The versioned label to resolve.
        business_key: The entity's PK value for that label.
        version: The exact retained version to resolve.
        context: The §3.2 consuming-context payload — used only for the R2
            core's #19 conditional-admission check.
        graph_store: The graph port (production: Neo4jAdapter; tests: the
            in-memory double).
        predicate_evaluator: The in-process predicate port (production: the
            fail-closed evaluator; tests: a controllable double).

    Returns:
        The `ReadResult`: 0-or-1 admitted envelope, 0-or-1 disclosures. The
        pinned version's real read-discipline structure is enforced by the
        R2 core exactly as any other candidate's — a resolution HIT is never
        guaranteed admission.

    Raises:
        GatewayError: `TARGET_NOT_FOUND` if the pin resolves no node — the
            (business_key, version) pair does not exist for this node_kind.
    """
    record = await graph_store.read_as_of(node_kind, business_key, version)
    if record is None:
        raise GatewayError(
            ErrorType.TARGET_NOT_FOUND,
            "No node resolves for the given node_kind, business_key, and version.",
        )

    candidate = _to_candidate(record, node_kind)
    candidates = [candidate] if candidate is not None else []
    return await apply_read_discipline(candidates, context, predicate_evaluator)


def _to_candidate(
    record: ReadAsOfResolvedRecord, node_kind: ReadAsOfNodeKind
) -> CandidateNode | None:
    """Map one resolved read-as-of record into a `CandidateNode`.

    Args:
        record: The port-level structural facts for the resolved node.
        node_kind: The label the record was resolved under.

    Returns:
        The `CandidateNode`, carrying the real retraction/conditional
        structure the traversal resolved, with `catalog_eligibility` and
        `deprecation` both `None` (read-as-of is a resolution primitive, not
        a selection op), or `None` if the record's origin_mechanism
        contradicts a promoted-only surface it claims to carry — excluded,
        fail-closed, rather than admitted (or silently trusted) on a broken
        assumption.
    """
    if is_promoted_only_state_contradiction(
        origin_mechanism=record.origin_mechanism,
        retracted=record.retracted,
        applicability_state=record.applicability_state,
    ):
        log.warning(
            "read_as_of_candidate_excluded",
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
            node_kind=node_kind,
            plane_labels=record.plane_labels,
            origin_mechanism=record.origin_mechanism,
            derivation_class=record.derivation_class,
            version=record.version,
            effective_from=record.effective_from,
            effective_to=record.effective_to,
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
