##############################################################################
# Module: app/domain/shared/envelope.py
# Service: knowledge-service
# Author: Haffey Enterprises LLC
# Created: 2026-07-23
# Revised: 2026-07-23
# Description: The §3.2 result-envelope assembler (SDD-001 §4.1) — attribution,
#   the applicability block, and the disclosure channel. `EnvelopeAttribution`
#   is the structural-fact bundle any retrieval operation supplies once it has
#   resolved a node (plane/origin/version/confidence data); `assemble_envelope`
#   and `build_disclosure_entry` are the sole construction points for
#   `ResultEnvelope` and `DisclosureEntry` (app.models), reused by every §3.3
#   operation and by the read-discipline core (app.domain.retrieval) so the
#   §3.2 shape is built in exactly one place. Deliberately independent of
#   app.domain.retrieval — a shared module must not depend on one specific
#   consumer's types, or no other domain package (capture/promotion/ingestion)
#   could reuse it.
##############################################################################

from dataclasses import dataclass

from app.models import (
    ApplicabilityBlock,
    ConditionalAdmissionStatus,
    DisclosureEntry,
    DisclosureReason,
    ResultEnvelope,
)


@dataclass(frozen=True)
class EnvelopeAttribution:
    """The structural facts a §3.2 result envelope is assembled from.

    `node_id` + `node_kind` are the identity/discriminator pair; `confidences`
    holds node confidence first, then any composed edge confidences (DDR-002
    §3/§4 semantics) — a tuple because a traversal may compose more than one.
    """

    node_id: str
    node_kind: str
    plane_labels: tuple[str, ...]
    origin_mechanism: str
    derivation_class: str | None
    version: str
    effective_from: str | None
    effective_to: str | None
    version_pin: str
    confidences: tuple[float, ...]


def assemble_envelope(
    attribution: EnvelopeAttribution,
    *,
    conditional_admission: ConditionalAdmissionStatus,
) -> ResultEnvelope:
    """Build the §3.2 result envelope for an admitted node.

    Args:
        attribution: The node's structural facts.
        conditional_admission: The applicability block's conditional-admission
            verdict — `UNCONDITIONAL` when the node carries no `HAS_CONDITION`
            path, `CONDITIONALLY_ADMITTED` when it was admitted because its
            single condition's predicate evaluated true.

    Returns:
        The assembled `ResultEnvelope`. `catalog_eligibility` is always `None`
        — R2's named-forward slot; R3 computes it alongside its catalog-read
        consumers.
    """
    return ResultEnvelope(
        node_id=attribution.node_id,
        node_kind=attribution.node_kind,
        plane_labels=list(attribution.plane_labels),
        origin_mechanism=attribution.origin_mechanism,
        derivation_class=attribution.derivation_class,
        version=attribution.version,
        effective_from=attribution.effective_from,
        effective_to=attribution.effective_to,
        version_pin=attribution.version_pin,
        confidences=list(attribution.confidences),
        applicability=ApplicabilityBlock(
            conditional_admission=conditional_admission,
            catalog_eligibility=None,
        ),
    )


def build_disclosure_entry(node_id: str, reason: DisclosureReason) -> DisclosureEntry:
    """Build one §3.2 disclosure-channel entry — no content payload.

    Args:
        node_id: The excluded conditional node's identity.
        reason: The exclusion reason (one of the closed three).

    Returns:
        The `DisclosureEntry`, carrying only identity and reason.
    """
    return DisclosureEntry(node_id=node_id, reason=reason)
