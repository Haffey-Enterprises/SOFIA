##############################################################################
# Module: app/domain/retrieval/provenance_of.py
# Service: knowledge-service
# Author: Haffey Enterprises LLC
# Created: 2026-07-24
# Revised: 2026-07-24
# Description: provenance-of (SDD-001 §3.3.8) — the provenance-survival
#   retrieval affordance for a promoted node: traverses `PROMOTES_TO_KNOWLEDGE`
#   to the `CandidatePromotion`, then its two parallel inbound edges —
#   `MATERIALIZES_PROVENANCE_OF` (the frozen `ProvenanceSummary`) and
#   `DECIDED_ON` (the governing `PromotionDecision`). Returns the frozen layer
#   always, plus the live `Evidence` chain where it still exists.
#
#   THE AUDIT SET'S SECOND OP (SDD-001 §1/§3.2), same posture as
#   citation_lookup (R6a): deliberately reaches read-excluded nodes, runs NO
#   §4.4 trio, builds NO CandidateNode. Unlike citation_lookup, this is
#   single-subject and unpaginated (P-D2) — one specific promoted node, keyed
#   (node_kind, business_key, version); the frozen set is returned whole,
#   bounded by the promotion's own Evidence-span closure.
#
#   TARGET_NOT_FOUND (P-D3) fires on TWO distinct conditions, distinguished by
#   message, never by a new ErrorType: the entry node does not exist at all,
#   or it exists but was never promoted (no PROMOTES_TO_KNOWLEDGE chain). A
#   promoted-then-retracted or -superseded node IS promoted (the chain is
#   intact) and returns normally — the inversion.
#
#   frozen_layer_present=False (P-D4) is an honest anomaly flag for a resolved
#   candidate with no ProvenanceSummary (a #20 violation reached pre-CI-catch)
#   — never raised, never a fabricated present-but-empty layer; `candidate`
#   remains populated in that case. governing_decision=None (review fix M3)
#   is a SECOND, independent anomaly signal — a promoted node with no
#   DECIDED_ON edge at all — surfaced the same honest way, never raised.
#   Per DDR-002 #15, "governing" is the latest-decided_at DECIDED_ON edge
#   REGARDLESS of outcome (it may be `rejected`): the initial build filtered
#   to approving outcomes before selecting latest, which would hide a
#   flipped-to-rejected verdict behind a stale earlier approval — exactly
#   the failure #15's own clarifying clause names. Fixed at the Cypher
#   layer (neo4j_adapter.py); this module just stopped treating
#   governing_decision as a promoted-node invariant.
#
#   entry_markers reuses CitationEntryStatus (app.models) — the identical
#   three-marker audit-disclosure vocabulary citation_lookup already
#   established, never a second enum (deferred n=2 rename to
#   AuditEntryStatus, not this build's).
##############################################################################

from app.domain.exceptions import GatewayError
from app.models import (
    CandidatePromotionContext,
    CitationEntryStatus,
    ErrorType,
    EvidenceFacts,
    GoverningDecisionContext,
    ProvenanceEntry,
    ProvenanceOfResult,
)
from app.ports.graph_store import (
    GraphStoragePort,
    ProvenanceOfFrozenEntryRecord,
    ReadAsOfNodeKind,
)


async def provenance_of(
    node_kind: ReadAsOfNodeKind,
    business_key: str,
    version: str,
    graph_store: GraphStoragePort,
) -> ProvenanceOfResult:
    """Resolve the provenance-survival affordance for one promoted node.

    Args:
        node_kind: The entry node's versioned label (the six labels
            `ReadAsOfNodeKind` enumerates).
        business_key: The entry's PK value for that label.
        version: The exact retained version — one specific promoted node.
        graph_store: The graph port (production: Neo4jAdapter; tests: the
            in-memory double).

    Returns:
        The resolved provenance: entry markers (never exclusionary), the
        originating candidate + governing decision, and the frozen entry
        set (frozen floor always, live overlay where extant).

    Raises:
        GatewayError: `TARGET_NOT_FOUND` if the entry node does not exist at
            all, or exists but was never promoted (distinct messages, same
            error type) — a currently-retracted or -superseded promoted node
            is NOT this case; it resolves normally (the inversion).
    """
    page = await graph_store.provenance_of(node_kind, business_key, version)
    if not page.entry_found:
        raise GatewayError(
            ErrorType.TARGET_NOT_FOUND,
            "No node resolves for the given node_kind, business_key, and version.",
        )
    if not page.is_promoted:
        raise GatewayError(
            ErrorType.TARGET_NOT_FOUND,
            "The node exists but was never promoted (no PROMOTES_TO_KNOWLEDGE chain).",
        )

    if page.candidate is None or page.origin_mechanism is None:
        # is_promoted=True is the port's contract guarantee that BOTH are
        # populated: candidate by §5's structural invariant (a
        # PROMOTES_TO_KNOWLEDGE-materialized node always has an originating
        # promotion-kind CandidatePromotion) and origin_mechanism by the same
        # §5 invariant (always stamped origin_mechanism: promoted).
        # governing_decision is NOT included here (review fix M3) — a
        # promoted node with no DECIDED_ON edge at all is a real, surfaced
        # anomaly (ProvenanceOfResult.governing_decision=None), not a port
        # contract violation. A violation of the two invariants that DO hold
        # is a gateway defect, not a client-caused condition, so this fails
        # loud rather than silently degrading (house pattern, e.g. app.main's
        # get_graph_store).
        raise RuntimeError(
            "provenance_of: is_promoted=True but candidate/origin_mechanism "
            "is missing — port contract violation."
        )

    markers: set[CitationEntryStatus] = set()
    if page.is_superseded:
        markers.add(CitationEntryStatus.SUPERSEDED)
    if page.is_retracted:
        markers.add(CitationEntryStatus.RETRACTED)
    if page.is_conditional:
        markers.add(CitationEntryStatus.CONDITIONAL)

    return ProvenanceOfResult(
        node_kind=node_kind,
        business_key=business_key,
        version=version,
        origin_mechanism=page.origin_mechanism,
        entry_markers=frozenset(markers),
        candidate=CandidatePromotionContext(
            candidate_id=page.candidate.candidate_id,
            proposal_kind=page.candidate.proposal_kind,
            status=page.candidate.status,
        ),
        governing_decision=GoverningDecisionContext(
            decision_id=page.governing_decision.decision_id,
            outcome=page.governing_decision.outcome,
            decided_at=page.governing_decision.decided_at,
        )
        if page.governing_decision is not None
        else None,
        provenance_summary_id=page.provenance_summary_id,
        frozen_layer_present=page.frozen_layer_present,
        entries=[_to_provenance_entry(entry) for entry in page.entries],
    )


def _to_provenance_entry(record: ProvenanceOfFrozenEntryRecord) -> ProvenanceEntry:
    """Translate one port-level frozen entry record into its wire shape.

    Args:
        record: The frozen floor plus live-overlay facts for one Evidence.

    Returns:
        The wire `ProvenanceEntry` — `live_evidence` present iff `is_live`.
    """
    return ProvenanceEntry(
        evidence_id=record.evidence_id,
        frozen_fact_summary=record.frozen_fact_summary,
        frozen_source_version_pin=record.frozen_source_version_pin,
        frozen_source_node_ref=record.frozen_source_node_ref,
        live=record.is_live,
        live_evidence=EvidenceFacts(
            evidence_id=record.evidence_id,
            fact_summary=record.live_fact_summary,
            confidence=record.live_confidence,
            weight=record.live_weight,
            source_node_version=record.live_source_node_version,
            observed_at=record.live_observed_at,
        )
        if record.is_live
        else None,
    )
