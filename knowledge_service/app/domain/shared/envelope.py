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
#   `version`/`version_pin` are optional (R3a correction, track-record-lookup):
#   DDR-002 §6 scopes versioning/supersession to Catalog/Standards/RateCard/
#   PlaneDefinition; an Operational-plane `ObservedPattern` distills
#   update-in-place and carries no `version` property, so a non-versioned
#   node's attribution carries `None` here rather than a fabricated value.
#   `confidences` elements are individually optional (R3a review finding):
#   DDR-002 §7's existence constraints cover only the provenance group + T1
#   properties, and `confidence` is T2 on the surfaces this envelope draws
#   from (e.g. `ObservedPattern.confidence`, `OBSERVED_IN.confidence`) with no
#   CI check guaranteeing presence — unlike `Evidence.confidence` (check #28).
#   A null confidence is carried honestly rather than crashing or defaulting.
#   `catalog_eligibility` (R3b): carried through from the attribution rather
#   than hardcoded `None` — computed by a Catalog operation (app.domain.shared.
#   catalog_eligibility) and attached to the attribution before assembly; a
#   non-Catalog operation (e.g. track-record-lookup) simply leaves it at its
#   `None` default. `deprecation` (SDD-001 §3.2 v1.7.0) is the same pattern:
#   carried through unchanged, never computed here — the operation builds the
#   `DeprecationNotice` (marker-presence from `deprecation_date`, never a
#   read-clock comparison) and attaches it to the attribution before assembly.
#   This module still computes nothing itself — assembly only.
##############################################################################

from dataclasses import dataclass

from app.models import (
    ApplicabilityBlock,
    CatalogEligibility,
    ConditionalAdmissionStatus,
    DeprecationNotice,
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
    An individual confidence is `None` when the underlying graph property is
    absent — not guaranteed present by any DDR-002 constraint or CI check for
    every surface that carries one. `version`/`version_pin` are `None` for a
    non-versioned node type (e.g. an Operational `ObservedPattern`, which
    distills update-in-place). `catalog_eligibility` is `None` unless the
    supplying operation computed it (Catalog reads only, e.g.
    resolve-technology) — the two-surface applicability distinction (DDR-002
    §5) means it is simply inapplicable to non-Catalog candidates.
    `deprecation` (SDD-001 §3.2 v1.7.0) is `None` unless the supplying
    operation built it — populated only for a deprecatable Catalog candidate.
    """

    node_id: str
    node_kind: str
    plane_labels: tuple[str, ...]
    origin_mechanism: str
    derivation_class: str | None
    version: str | None
    effective_from: str | None
    effective_to: str | None
    version_pin: str | None
    confidences: tuple[float | None, ...]
    catalog_eligibility: CatalogEligibility | None = None
    deprecation: DeprecationNotice | None = None


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
        The assembled `ResultEnvelope`. `catalog_eligibility` and `deprecation`
        carry through from `attribution` unchanged — this function computes
        neither surface, it only assembles what it is given.
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
            catalog_eligibility=attribution.catalog_eligibility,
            deprecation=attribution.deprecation,
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
