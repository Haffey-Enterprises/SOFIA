##############################################################################
# Module: app/domain/retrieval/session_trace.py
# Service: knowledge-service
# Author: Haffey Enterprises LLC
# Created: 2026-07-24
# Revised: 2026-07-24
# Description: session-trace (SDD-001 §3.3.9) — the explainability
#   traversal over a `ReasoningSession`: conclusions, evidence with resolved
#   pins, rejected alternatives, `LED_TO` chains.
#
#   THE AUDIT SET'S THIRD AND LAST OP, trio-free by a DIFFERENT route than
#   citation_lookup (R6a) / provenance_of (R6b): NOT the §1 disclosed
#   exception — §4.4 binds the read-discipline trio to GROUND-TRUTH
#   retrieval, and every entity here is RG (session, conclusions, evidence,
#   rejected alternatives — no KG plane label), so proposal/retraction/
#   conditional exclusion is structurally N/A (ST-D1). This module imports
#   neither `apply_read_discipline` nor `CandidateNode`.
#
#   "Resolved pins" (ST-D1) are each Evidence's point-in-time `SOURCED_FROM`
#   pin (DDR-002 §4/§6: `fact_summary` + `source_node_version` are immune to
#   KG drift) — shown REGARDLESS of the cited node's CURRENT read-discipline
#   state. The per-pin `CitedNodeRef.markers` disclose that current state
#   (reusing `CitationEntryStatus`, never exclusionary) — a now-retracted or
#   -superseded cited node still surfaces with its marker, the point-in-time
#   fidelity point this op exists to serve.
#
#   TARGET_NOT_FOUND (ST-D4) fires iff the `ReasoningSession` is absent. An
#   existing session with zero conclusions is a legal non-blocking capture
#   state (DDR-001) — empty trace, never an error.
##############################################################################

from app.domain.exceptions import GatewayError
from app.models import (
    CitationEntryStatus,
    CitedNodeRef,
    ErrorType,
    EvidenceFacts,
    LedToLink,
    SessionTraceResult,
    TraceConclusion,
    TraceEvidence,
    TraceRejectedAlternative,
)
from app.ports.graph_store import (
    CitedNodeRefRecord,
    GraphStoragePort,
    TraceConclusionRecord,
    TraceEvidenceRecord,
    TraceRejectedAlternativeRecord,
)


async def session_trace(session_id: str, graph_store: GraphStoragePort) -> SessionTraceResult:
    """Resolve the explainability trace over one `ReasoningSession`.

    Args:
        session_id: The `ReasoningSession`'s PK value.
        graph_store: The graph port (production: Neo4jAdapter; tests: the
            in-memory double).

    Returns:
        The resolved trace: every conclusion with its evidence (each
        resolved to its point-in-time pin) and rejected alternatives, plus
        the flat `LED_TO` adjacency across the session's conclusions.

    Raises:
        GatewayError: `TARGET_NOT_FOUND` if the `ReasoningSession` does not
            exist at all. An existing session with zero conclusions is
            never this case — it returns an empty trace.
    """
    page = await graph_store.session_trace(session_id)
    if not page.session_found:
        raise GatewayError(
            ErrorType.TARGET_NOT_FOUND,
            "No ReasoningSession resolves for the given session_id.",
        )

    return SessionTraceResult(
        session_id=session_id,
        conclusions=[_to_trace_conclusion(record) for record in page.conclusions],
        led_to=[
            LedToLink(from_progress_id=link.from_progress_id, to_progress_id=link.to_progress_id)
            for link in page.led_to
        ],
    )


def _to_trace_conclusion(record: TraceConclusionRecord) -> TraceConclusion:
    """Translate one port-level conclusion record into its wire shape."""
    return TraceConclusion(
        progress_id=record.progress_id,
        conclusion_type=record.conclusion_type,
        reasoner_category=record.reasoner_category,
        authoritative=record.authoritative,
        confidence=record.confidence,
        overridden_by_human=record.overridden_by_human,
        created_at=record.created_at,
        evidence=[_to_trace_evidence(evidence) for evidence in record.evidence],
        rejected_alternatives=[
            _to_trace_rejected(rejected) for rejected in record.rejected_alternatives
        ],
    )


def _to_trace_evidence(record: TraceEvidenceRecord) -> TraceEvidence:
    """Translate one port-level evidence record into its wire shape."""
    return TraceEvidence(
        evidence=EvidenceFacts(
            evidence_id=record.evidence_id,
            fact_summary=record.fact_summary,
            confidence=record.confidence,
            weight=record.weight,
            source_node_version=record.source_node_version,
            observed_at=record.observed_at,
        ),
        resolved_pin=_to_cited_node_ref(record.resolved_pin)
        if record.resolved_pin is not None
        else None,
    )


def _to_trace_rejected(record: TraceRejectedAlternativeRecord) -> TraceRejectedAlternative:
    """Translate one port-level rejected-alternative record into its wire shape."""
    return TraceRejectedAlternative(
        rejected_id=record.rejected_id,
        candidate_type=record.candidate_type,
        rejection_reason=record.rejection_reason,
        score_delta=record.score_delta,
        human_accepted=record.human_accepted,
        would_have_used=[_to_cited_node_ref(ref) for ref in record.would_have_used],
    )


def _to_cited_node_ref(record: CitedNodeRefRecord) -> CitedNodeRef:
    """Translate one port-level cited-node record into its wire shape.

    Args:
        record: The cited node's identity + the three raw marker facts.

    Returns:
        The wire `CitedNodeRef` — markers as a set, never exclusionary.
    """
    markers: set[CitationEntryStatus] = set()
    if record.is_superseded:
        markers.add(CitationEntryStatus.SUPERSEDED)
    if record.is_retracted:
        markers.add(CitationEntryStatus.RETRACTED)
    if record.is_conditional:
        markers.add(CitationEntryStatus.CONDITIONAL)
    return CitedNodeRef(
        node_kind=record.node_kind,
        node_id=record.node_id,
        version=record.version,
        markers=frozenset(markers),
    )
