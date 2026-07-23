##############################################################################
# Module: app/domain/retrieval/select_patterns.py
# Service: knowledge-service
# Author: Haffey Enterprises LLC
# Created: 2026-07-23
# Revised: 2026-07-23
# Description: select-patterns (SDD-001 §3.3.1) — the selection-web read: from
#   a set of required Capabilities, return candidate Patterns, each with its
#   per-Capability taxonomy + approved Technology options + PREFERRED_OVER
#   facts. Reuses the R2/R3b core verbatim rather than re-deriving it: the
#   Pattern-level read-discipline application below and the per-capability
#   Technology-level application both call apply_read_discipline (the R2
#   core), and every Technology option is mapped through
#   resolve_technology._to_candidate — the SAME Technology→CandidateNode path
#   resolve-technology uses (shared guard → compute_catalog_eligibility →
#   DeprecationNotice → CandidateNode) — imported and reused directly rather
#   than duplicated (RBT-78 R3c mutation rider: resolve_technology.py's pinned
#   3-touch-point refactor forecloses lifting that mapping elsewhere this leg;
#   importing it directly is the reuse path that doesn't touch that file
#   further).
#
#   Per-node read discipline (ruling #2): the Pattern and each Technology
#   option are independent read-discipline subjects. A Pattern silently
#   excluded (proposal/retraction) drops its whole subtree with NO disclosure;
#   a Pattern conditionally excluded drops its subtree and emits exactly ONE
#   top-level `pattern_disclosures` entry; an admitted Pattern's capabilities
#   are then built, each running its OWN Technology-level trio independently
#   (silent-drop, a per-capability `technology_disclosures` entry, or
#   admitted) — never the Pattern's outcome propagated onto its Technologies
#   or vice versa.
#
#   PREFERRED_OVER (ruling #3) is carried through as the bare pattern_id list
#   — uncomposed, no ordering, no pick; that judgment is the reasoning
#   component's (§2.2), never this gateway's.
#
#   IacTemplate/IMPLEMENTS (ruling #4) is out of scope this leg — neither
#   traversed nor returned.
#
#   Catalog-eligibility and the deprecation notice (ruling #5) are
#   Technology-only surfaces: a Pattern's own CandidateNode always carries
#   catalog_eligibility=None and deprecation=None on its attribution.
#
#   Empty-never-error (ruling #6): an empty `capability_ids`, a capability
#   with no matching Patterns, or a capability with no approved Technology (the
#   gap signal) all fall out of the same admit/disclose/drop machinery as
#   empty lists — no special-casing, no raised error. select-patterns raises
#   only what apply_read_discipline and the port raise, and neither ever
#   raises TARGET_NOT_FOUND for this operation.
#
#   The promoted-only-state contradiction guard (ruling #7) is the shared
#   predicate (app.domain.shared.read_discipline_guard), applied identically
#   to the Pattern record here and to each Technology record inside
#   resolve_technology._to_candidate — one rule, one home, two call sites.
#
#   Taxonomy placement (ruling #8) is carried per-capability inside each
#   CapabilityBlock (l1/l2/l3), read straight off the Capability node the
#   traversal resolved — never a Pattern-level property.
##############################################################################

from collections.abc import Sequence

import structlog

from app.domain.retrieval.read_discipline import apply_read_discipline
from app.domain.retrieval.technology_candidate import to_technology_candidate
from app.domain.retrieval.types import CandidateNode, ConditionRef, ConsumingContext
from app.domain.shared.envelope import EnvelopeAttribution
from app.domain.shared.read_discipline_guard import is_promoted_only_state_contradiction
from app.models import CapabilityBlock, DisclosureEntry, PatternCandidate, SelectPatternsResult
from app.ports.graph_store import (
    GraphStoragePort,
    SelectPatternsCandidateRecord,
)
from app.ports.predicate_eval import PredicateEvaluationPort

log = structlog.get_logger()


async def select_patterns(
    capability_ids: Sequence[str],
    context: ConsumingContext,
    graph_store: GraphStoragePort,
    predicate_evaluator: PredicateEvaluationPort,
) -> SelectPatternsResult:
    """Resolve candidate Patterns for the given required Capabilities.

    Args:
        capability_ids: The required Capabilities to resolve candidate
            Patterns for.
        context: The §3.2 consuming-context payload.
        graph_store: The graph port (production: Neo4jAdapter; tests: the
            in-memory double).
        predicate_evaluator: The in-process predicate port (production: the
            fail-closed evaluator; tests: a controllable double).

    Returns:
        The admitted candidate Patterns (each with its nested capabilities and
        Technology options) and the top-level pattern-level disclosures. A
        Pattern whose origin_mechanism contradicts a promoted-only surface it
        claims to carry is excluded before it reaches the core; empty inputs
        or empty resolutions yield empty lists, never an error.
    """
    records = await graph_store.select_patterns(capability_ids)
    patterns: list[PatternCandidate] = []
    pattern_disclosures: list[DisclosureEntry] = []

    for record in records:
        candidate = _to_pattern_candidate(record)
        if candidate is None:
            continue

        pattern_result = await apply_read_discipline([candidate], context, predicate_evaluator)
        if pattern_result.disclosures:
            pattern_disclosures.append(pattern_result.disclosures[0])
            continue
        if not pattern_result.admitted:
            continue

        capabilities: list[CapabilityBlock] = []
        for cap_record in record.capabilities:
            tech_candidates = [
                tech_candidate
                for tech_candidate in (
                    to_technology_candidate(tech_record, context)
                    for tech_record in cap_record.technology_options
                )
                if tech_candidate is not None
            ]
            tech_result = await apply_read_discipline(tech_candidates, context, predicate_evaluator)
            capabilities.append(
                CapabilityBlock(
                    capability_id=cap_record.capability_id,
                    l1_taxonomy=cap_record.l1_taxonomy,
                    l2_taxonomy=cap_record.l2_taxonomy,
                    l3_taxonomy=cap_record.l3_taxonomy,
                    technology_options=tech_result.admitted,
                    technology_disclosures=tech_result.disclosures,
                )
            )

        patterns.append(
            PatternCandidate(
                envelope=pattern_result.admitted[0],
                capabilities=capabilities,
                preferred_over=list(record.preferred_over),
            )
        )

    return SelectPatternsResult(patterns=patterns, pattern_disclosures=pattern_disclosures)


def _to_pattern_candidate(record: SelectPatternsCandidateRecord) -> CandidateNode | None:
    """Map one raw select-patterns record into a Pattern `CandidateNode`.

    Args:
        record: The port-level structural facts for one candidate Pattern.

    Returns:
        The `CandidateNode`, carrying the real retraction/conditional
        structure the traversal resolved, with `catalog_eligibility` and
        `deprecation` both `None` (ruling #5 — Technology-only surfaces), or
        `None` if the record's origin_mechanism contradicts a promoted-only
        surface it claims to carry — excluded, fail-closed, rather than
        admitted (or silently trusted) on a broken assumption.
    """
    if is_promoted_only_state_contradiction(
        origin_mechanism=record.origin_mechanism,
        retracted=record.retracted,
        applicability_state=record.applicability_state,
    ):
        log.warning(
            "select_patterns_candidate_excluded",
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
            node_kind="Pattern",
            plane_labels=("Catalog",),
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
