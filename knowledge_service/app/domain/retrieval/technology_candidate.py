##############################################################################
# Module: app/domain/retrieval/technology_candidate.py
# Service: knowledge-service
# Author: Haffey Enterprises LLC
# Created: 2026-07-23
# Revised: 2026-07-23
# Description: The Technology -> CandidateNode mapping (SDD-001 §3.3.1/§3.3.2)
#   — shared because more than one Catalog read op resolves approved Technology
#   options: resolve-technology (§3.3.2) maps its candidates, and select-patterns
#   (§3.3.1) maps the Technology options nested under each candidate Pattern's
#   capabilities. Promoted here (RBT-78 R3c review finding (a)) from
#   resolve_technology's private _to_candidate so both ops share one public home
#   rather than select-patterns cross-importing a sibling module's private
#   symbol. A retrieval-layer module by necessity: it yields a CandidateNode
#   (a retrieval type), so it cannot live in app/domain/shared/ (which must not
#   depend on retrieval). Applies the shared promoted-only-state guard
#   fail-closed BEFORE the read-discipline core, computes the Catalog-eligibility
#   annotation (never an exclusion, §4.4) and the deprecation notice
#   (marker-presence, §3.2 v1.7.0), and assembles the CandidateNode carrying the
#   REAL read-discipline structure the traversal resolved. Deprecation never
#   affects admission. The exclusion log event is surface-neutral
#   (`technology_candidate_excluded`) now that the mapper is not
#   resolve-technology-specific — a non-§8 operational log, no contract impact.
##############################################################################

import structlog

from app.domain.retrieval.types import CandidateNode, ConditionRef, ConsumingContext
from app.domain.shared.catalog_eligibility import compute_catalog_eligibility
from app.domain.shared.envelope import EnvelopeAttribution
from app.domain.shared.read_discipline_guard import is_promoted_only_state_contradiction
from app.models import DeprecationNotice
from app.ports.graph_store import ResolveTechnologyCandidateRecord

log = structlog.get_logger()


def to_technology_candidate(
    record: ResolveTechnologyCandidateRecord, context: ConsumingContext
) -> CandidateNode | None:
    """Map one approved-Technology record into a `CandidateNode`.

    Args:
        record: The port-level structural facts for one approved Technology
            option.
        context: The §3.2 consuming-context payload — supplies the fields the
            Catalog-eligibility fit-rule checks against.

    Returns:
        The `CandidateNode`, carrying the real retraction/conditional structure
        the traversal resolved plus the computed Catalog-eligibility verdict and
        deprecation notice, or `None` if the record's origin_mechanism
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
            "technology_candidate_excluded",
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
