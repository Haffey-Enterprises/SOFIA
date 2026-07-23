##############################################################################
# Module: app/domain/retrieval/resolve_technology.py
# Service: knowledge-service
# Author: Haffey Enterprises LLC
# Created: 2026-07-23
# Revised: 2026-07-23
# Description: resolve-technology (SDD-001 §3.3.2) — approved Technology
#   options for a Capability under the consuming context; eligibility verdicts
#   disclosed per option (annotation, never exclusion, SDD-001 §4.4); no
#   recommended pick is returned. Calls the port's resolve_technology_options
#   traversal, computes the Catalog-eligibility verdict per candidate
#   (app.domain.shared.catalog_eligibility, E1-E5), maps each raw record into a
#   CandidateNode carrying the REAL read-discipline structure the traversal
#   resolved (D1 — a Technology can genuinely be promoted-conditional or
#   retracted, unlike track-record-lookup's fixed constants), and applies the
#   R2 read-discipline core.
#
#   `proposal_pending` stays a fixed False (same reasoning as R3a): a
#   plane-scoped Catalog traversal never returns a CandidatePromotion node
#   (it carries no plane label, DDR-002 §5). Retraction (#21) and conditional-
#   admission (#19) are real per-candidate values here — resolved by the
#   traversal, enforced by the R2 core, never pre-excluded here (A2).
#
#   Origin-mechanism contradiction guard (D1, extending the R3a pattern to
#   both promoted-only surfaces): DDR-002 §5 states applicability_state/
#   Condition is exclusive to nodes materialized via PROMOTES_TO_KNOWLEDGE, and
#   §7 #21 states RETRACTS un-promotes a PROMOTED fact — so an ingested-origin
#   Technology carrying either is a data-integrity contradiction. Excluded,
#   fail-closed, before it ever reaches the read-discipline core — never
#   admitted, and never trusted to the core's ordinary exclusion path, on a
#   broken assumption about what only a promoted-origin node may carry.
#
#   Deprecation notice (SDD-001 §3.2 v1.7.0): built alongside the Catalog-
#   eligibility verdict and carried on the same attribution. `deprecated` is
#   marker-presence — set iff `record.deprecation_date` is not `None` — never
#   a comparison against the read clock, and it NEVER affects admission: a
#   deprecated Technology is admitted or excluded solely by the read-
#   discipline trio, unchanged. `approval_status` is never read (unratified
#   value-set, DDR-002 §2.1).
##############################################################################

import structlog

from app.domain.retrieval.read_discipline import apply_read_discipline
from app.domain.retrieval.types import CandidateNode, ConditionRef, ConsumingContext
from app.domain.shared.catalog_eligibility import compute_catalog_eligibility
from app.domain.shared.envelope import EnvelopeAttribution
from app.models import DeprecationNotice, ReadResult
from app.ports.graph_store import GraphStoragePort, ResolveTechnologyCandidateRecord
from app.ports.predicate_eval import PredicateEvaluationPort

log = structlog.get_logger()

# The one origin_mechanism that may carry applicability_state: conditional or
# a governing RETRACTS edge (DDR-002 §5 / §7 #21). Checked, not assumed.
_PROMOTED_ONLY_ORIGIN_MECHANISM = "promoted"


async def resolve_technology(
    capability_id: str,
    context: ConsumingContext,
    graph_store: GraphStoragePort,
    predicate_evaluator: PredicateEvaluationPort,
) -> ReadResult:
    """Resolve approved Technology options for the given Capability.

    Args:
        capability_id: The Capability to resolve approved options for.
        context: The §3.2 consuming-context payload.
        graph_store: The graph port (production: Neo4jAdapter; tests: the
            in-memory double).
        predicate_evaluator: The in-process predicate port (production: the
            fail-closed evaluator; tests: a controllable double).

    Returns:
        The admitted envelopes (each annotated with its Catalog-eligibility
        verdict and deprecation notice) and disclosed exclusions (SDD-001
        §3.2). A record whose origin_mechanism contradicts a promoted-only
        read-discipline surface it claims to carry is excluded before it
        reaches the core. Deprecation never affects admission either way.
    """
    records = await graph_store.resolve_technology_options(capability_id)
    candidates = [
        candidate
        for candidate in (_to_candidate(record, context) for record in records)
        if candidate is not None
    ]
    return await apply_read_discipline(candidates, context, predicate_evaluator)


def _to_candidate(
    record: ResolveTechnologyCandidateRecord, context: ConsumingContext
) -> CandidateNode | None:
    """Map one raw resolve-technology record into a `CandidateNode`.

    Args:
        record: The port-level structural facts for one approved Technology
            option.
        context: The §3.2 consuming-context payload — supplies the fields the
            Catalog-eligibility fit-rule checks against.

    Returns:
        The `CandidateNode`, carrying the real retraction/conditional
        structure the traversal resolved plus the computed Catalog-eligibility
        verdict and deprecation notice, or `None` if the record's
        origin_mechanism contradicts a promoted-only surface it claims to
        carry — excluded, fail-closed, rather than admitted (or silently
        trusted) on a broken assumption.
    """
    claims_promoted_only_state = record.retracted or record.applicability_state == "conditional"
    if claims_promoted_only_state and record.origin_mechanism != _PROMOTED_ONLY_ORIGIN_MECHANISM:
        log.warning(
            "resolve_technology_candidate_excluded",
            node_id=record.node_id,
            reason="promoted_only_state_on_non_promoted_origin",
            origin_mechanism=record.origin_mechanism,
            retracted=record.retracted,
            applicability_state=record.applicability_state,
        )
        return None

    eligibility = compute_catalog_eligibility(
        tier_applicability=record.tier_applicability,
        approved_data_classifications=record.approved_data_classifications,
        environment_class=context.environment_class,
        data_classification=context.data_classification,
    )
    deprecation = DeprecationNotice(
        deprecated=record.deprecation_date is not None,
        deprecation_date=record.deprecation_date,
    )

    return CandidateNode(
        attribution=EnvelopeAttribution(
            node_id=record.node_id,
            node_kind="Technology",
            plane_labels=("Catalog",),
            origin_mechanism=record.origin_mechanism,
            derivation_class=record.derivation_class,
            version=record.version,
            effective_from=None,
            effective_to=None,
            version_pin=record.version,
            confidences=(),
            catalog_eligibility=eligibility,
            deprecation=deprecation,
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
