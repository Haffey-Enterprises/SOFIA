##############################################################################
# Module: app/domain/retrieval/citation_lookup.py
# Service: knowledge-service
# Author: Haffey Enterprises LLC
# Created: 2026-07-24
# Revised: 2026-07-24
# Description: citation-lookup (SDD-001 §3.3.7) — the reverse cross-graph
#   affordance (KG node -> citing Evidence -> owning ReasoningProgress /
#   ReasoningSession). The platform's FIRST AUDIT-POSTURE read op: the
#   DISCLOSED EXCEPTION named by SDD-001 §1/§3.2. It deliberately reaches
#   read-excluded nodes and returns raw RG facts — it does NOT build a
#   CandidateNode and does NOT call apply_read_discipline (contrast
#   find_precedents, which runs the trio with fixed no-op constants; contrast
#   read_as_of, whose module docstring explicitly disclaims this exception).
#   A retracted/superseded/conditional-but-EXISTING entry's citations are
#   returned exactly as an active entry's would be — the audit inversion.
#
#   Mode/version pairing (D3) is the one domain-raised SCHEMA_VIOLATION on
#   this op (R6a delta A1): per_version requires version, business_key_wide
#   forbids it. TARGET_NOT_FOUND (D6) fires iff the entry KG node does not
#   exist at all — never on an existing-but-marked entry, and never on zero
#   citations for an existing entry.
#
#   entry_status markers (R6a delta A3, supersedes a single-value reading of
#   D1/D4) are three INDEPENDENT booleans resolved by the port per entry
#   version, translated here into the app.models.CitationEntryStatus set —
#   no precedence, no exclusion; an empty set is "active" by the absence of
#   markers, not a fourth member.
##############################################################################

from app.domain.exceptions import GatewayError
from app.domain.retrieval.types import CitationPage
from app.models import (
    CitationEntry,
    CitationEntryStatus,
    CitationEntryStatusEntry,
    CitationLookupMode,
    CitationLookupResult,
    CitationOwner,
    CitationOwnerProgress,
    CitationOwnerSession,
    ErrorType,
    EvidenceFacts,
)
from app.ports.graph_store import (
    CitationEntryStatusRecord,
    CitationOwnerRecord,
    CitationRecord,
    GraphStoragePort,
    ReadAsOfNodeKind,
)


async def citation_lookup(
    node_kind: ReadAsOfNodeKind,
    business_key: str,
    version: str | None,
    mode: CitationLookupMode,
    page: CitationPage,
    graph_store: GraphStoragePort,
) -> CitationLookupResult:
    """Resolve the reverse cross-graph citation affordance for an entry node.

    Args:
        node_kind: The entry node's versioned label (SDD-001 §3.3.7 D2 — the
            six `ReadAsOfNodeKind` labels).
        business_key: The entry's PK value for that label.
        version: The exact retained version — required for `per_version`,
            forbidden for `business_key_wide` (D3).
        mode: `per_version` or `business_key_wide`.
        page: The keyset-pagination request, `limit` already resolved by the
            API layer (default-substituted, hard-capped).
        graph_store: The graph port (production: Neo4jAdapter; tests: the
            in-memory double).

    Returns:
        The resolved citations, with per-version audit-disclosure markers.
        Markers never exclude — a retracted/superseded/conditional entry's
        citations are returned in full (D1's inversion).

    Raises:
        GatewayError: `SCHEMA_VIOLATION` if `mode` and `version` presence
            disagree (D3). `TARGET_NOT_FOUND` if the entry KG node does not
            exist at all (D6) — an existing entry with zero citations is
            never an error.
    """
    if mode == "per_version" and version is None:
        raise GatewayError(
            ErrorType.SCHEMA_VIOLATION,
            "per_version mode requires a version; none was supplied.",
        )
    if mode == "business_key_wide" and version is not None:
        raise GatewayError(
            ErrorType.SCHEMA_VIOLATION,
            "business_key_wide mode must not carry a version.",
        )

    port_page = await graph_store.citation_lookup(
        node_kind, business_key, version, mode, page.after_evidence_id, page.limit
    )
    if not port_page.entry_found:
        raise GatewayError(
            ErrorType.TARGET_NOT_FOUND,
            "No node resolves for the given node_kind and business_key.",
        )

    return CitationLookupResult(
        mode=mode,
        node_kind=node_kind,
        business_key=business_key,
        version=version,
        entry_status=[_to_entry_status(status) for status in port_page.entry_statuses],
        citations=[_to_citation_entry(record) for record in port_page.citations],
        next_cursor=port_page.next_cursor,
    )


def _to_entry_status(record: CitationEntryStatusRecord) -> CitationEntryStatusEntry:
    """Translate one port-level marker-fact record into its wire marker set.

    Args:
        record: The three independent boolean marker facts for one entry
            version.

    Returns:
        The version's marker set — empty when none of the three facts hold.
    """
    markers: set[CitationEntryStatus] = set()
    if record.is_superseded:
        markers.add(CitationEntryStatus.SUPERSEDED)
    if record.is_retracted:
        markers.add(CitationEntryStatus.RETRACTED)
    if record.is_conditional:
        markers.add(CitationEntryStatus.CONDITIONAL)
    return CitationEntryStatusEntry(version=record.version, markers=frozenset(markers))


def _to_citation_entry(record: CitationRecord) -> CitationEntry:
    """Translate one port-level citation record into its wire shape.

    Args:
        record: The port-level `Evidence` facts plus every owning
            `ReasoningProgress`/`ReasoningSession`.

    Returns:
        The wire `CitationEntry`.
    """
    return CitationEntry(
        evidence=EvidenceFacts(
            evidence_id=record.evidence_id,
            fact_summary=record.fact_summary,
            confidence=record.confidence,
            weight=record.weight,
            source_node_version=record.source_node_version,
            observed_at=record.observed_at,
        ),
        owners=[_to_owner(owner) for owner in record.owners],
    )


def _to_owner(record: CitationOwnerRecord) -> CitationOwner:
    """Translate one port-level owner record into its wire shape.

    Args:
        record: The port-level owning `ReasoningProgress` + `ReasoningSession`
            facts.

    Returns:
        The wire `CitationOwner`.
    """
    return CitationOwner(
        progress=CitationOwnerProgress(
            progress_id=record.progress_id,
            conclusion_type=record.conclusion_type,
            reasoner_category=record.reasoner_category,
            authoritative=record.authoritative,
            confidence=record.progress_confidence,
        ),
        session=CitationOwnerSession(session_id=record.session_id),
    )
