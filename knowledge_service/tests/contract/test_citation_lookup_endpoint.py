##############################################################################
# Module: test_citation_lookup_endpoint.py
# Service: knowledge-service
# Author: Haffey Enterprises LLC
# Created: 2026-07-24
# Revised: 2026-07-24
# Description: Contract tests for the citation-lookup endpoint (SDD-001
#   §3.3.7), the disclosed audit exception (§1/§3.2) — the request/response
#   shape over HTTP, the mode/version presence-mismatch SCHEMA_VIOLATION
#   rendering 400 (not 500, not 422 — R6a delta A1), a truly-absent entry
#   rendering TARGET_NOT_FOUND 404, the pagination default/clamp wiring
#   (R6a delta A2), and a below-1 limit rejected 422 by Pydantic. Runs
#   against the in-memory double (SDD-001 §6).
##############################################################################

from httpx import AsyncClient

from app.adapters.in_memory_graph import InMemoryGraphStore
from app.ports.graph_store import CitationEntryStatusRecord, CitationOwnerRecord, CitationRecord

_BASE_REQUEST = {
    "node_kind": "Technology",
    "business_key": "tech-1",
    "version": "3",
    "mode": "per_version",
}


def _citation(evidence_id: str = "ev-1") -> CitationRecord:
    return CitationRecord(
        evidence_id=evidence_id,
        fact_summary="a fact",
        confidence=0.8,
        weight=1.0,
        source_node_version="1",
        observed_at="2026-07-24T00:00:00Z",
        owners=(
            CitationOwnerRecord(
                progress_id="prog-1",
                conclusion_type="TechnologySelection",
                reasoner_category="encoded_reasoning",
                authoritative=True,
                progress_confidence=0.9,
                session_id="sess-1",
            ),
        ),
    )


class TestCitationLookupEndpointContract:
    """The endpoint's request/response shape, raise behavior, and wiring."""

    async def test_returns_200_with_citations_for_a_resolved_entry(
        self, async_client: AsyncClient, graph_store: InMemoryGraphStore
    ) -> None:
        # Arrange
        graph_store.set_citation_lookup_result(entry_found=True, citations=[_citation("ev-1")])

        # Act
        response = await async_client.post("/api/v1/citation-lookup", json=_BASE_REQUEST)

        # Assert
        assert response.status_code == 200
        body = response.json()
        assert body["mode"] == "per_version"
        assert body["node_kind"] == "Technology"
        assert body["business_key"] == "tech-1"
        assert body["version"] == "3"
        assert len(body["citations"]) == 1
        assert body["citations"][0]["evidence"]["evidence_id"] == "ev-1"
        assert body["next_cursor"] is None

    async def test_business_key_wide_omits_version_and_returns_per_version_status(
        self, async_client: AsyncClient, graph_store: InMemoryGraphStore
    ) -> None:
        # Arrange
        graph_store.set_citation_lookup_result(
            entry_found=True,
            entry_statuses=[
                CitationEntryStatusRecord(
                    version="1", is_superseded=True, is_retracted=False, is_conditional=False
                ),
                CitationEntryStatusRecord(
                    version="2", is_superseded=False, is_retracted=False, is_conditional=False
                ),
            ],
            citations=[_citation("ev-1")],
        )
        request_body = {
            "node_kind": "Technology",
            "business_key": "tech-1",
            "mode": "business_key_wide",
        }

        # Act
        response = await async_client.post("/api/v1/citation-lookup", json=request_body)

        # Assert
        assert response.status_code == 200
        body = response.json()
        assert body["mode"] == "business_key_wide"
        assert body["version"] is None
        assert [e["version"] for e in body["entry_status"]] == ["1", "2"]
        assert body["entry_status"][0]["markers"] == ["superseded"]

    async def test_mode_version_presence_mismatch_returns_400_schema_violation(
        self, async_client: AsyncClient, graph_store: InMemoryGraphStore
    ) -> None:
        # Arrange — per_version without a version.
        request_body = {"node_kind": "Technology", "business_key": "tech-1", "mode": "per_version"}

        # Act
        response = await async_client.post("/api/v1/citation-lookup", json=request_body)

        # Assert — 400, not 500 (unmapped) and not 422 (FastAPI body validation).
        assert response.status_code == 400
        body = response.json()
        assert body["error_code"] == "SCHEMA_VIOLATION"

    async def test_truly_absent_entry_returns_404_target_not_found(
        self, async_client: AsyncClient, graph_store: InMemoryGraphStore
    ) -> None:
        # Arrange — the double defaults to not-found.

        # Act
        response = await async_client.post("/api/v1/citation-lookup", json=_BASE_REQUEST)

        # Assert
        assert response.status_code == 404
        body = response.json()
        assert body["error_code"] == "TARGET_NOT_FOUND"

    async def test_retracted_entry_still_returns_its_citations(
        self, async_client: AsyncClient, graph_store: InMemoryGraphStore
    ) -> None:
        # Arrange — the audit inversion, asserted at the HTTP layer.
        graph_store.set_citation_lookup_result(
            entry_found=True,
            entry_statuses=[
                CitationEntryStatusRecord(
                    version="3", is_superseded=False, is_retracted=True, is_conditional=False
                )
            ],
            citations=[_citation("ev-1")],
        )

        # Act
        response = await async_client.post("/api/v1/citation-lookup", json=_BASE_REQUEST)

        # Assert
        assert response.status_code == 200
        body = response.json()
        assert len(body["citations"]) == 1
        assert body["entry_status"][0]["markers"] == ["retracted"]

    async def test_limit_below_one_is_rejected_422(
        self, async_client: AsyncClient, graph_store: InMemoryGraphStore
    ) -> None:
        # Arrange
        request_body = {**_BASE_REQUEST, "limit": 0}

        # Act
        response = await async_client.post("/api/v1/citation-lookup", json=request_body)

        # Assert — the Pydantic field bound (R6a delta A2), never a domain error.
        assert response.status_code == 422

    async def test_limit_omitted_uses_the_configured_default(
        self, async_client: AsyncClient, graph_store: InMemoryGraphStore
    ) -> None:
        # Arrange
        graph_store.set_citation_lookup_result(entry_found=True, citations=())

        # Act
        await async_client.post("/api/v1/citation-lookup", json=_BASE_REQUEST)

        # Assert — the resolved (not raw/None) limit reached the graph store.
        assert graph_store.citation_lookup_calls[0][5] == 50

    async def test_limit_above_the_max_is_silently_clamped(
        self, async_client: AsyncClient, graph_store: InMemoryGraphStore
    ) -> None:
        # Arrange
        graph_store.set_citation_lookup_result(entry_found=True, citations=())
        request_body = {**_BASE_REQUEST, "limit": 999999}

        # Act
        response = await async_client.post("/api/v1/citation-lookup", json=request_body)

        # Assert — clamped, never rejected.
        assert response.status_code == 200
        assert graph_store.citation_lookup_calls[0][5] == 200

    async def test_forwards_node_kind_business_key_version_mode_and_cursor(
        self, async_client: AsyncClient, graph_store: InMemoryGraphStore
    ) -> None:
        # Arrange
        graph_store.set_citation_lookup_result(entry_found=True, citations=())
        request_body = {**_BASE_REQUEST, "after_evidence_id": "ev-9"}

        # Act
        await async_client.post("/api/v1/citation-lookup", json=request_body)

        # Assert
        assert graph_store.citation_lookup_calls == [
            ("Technology", "tech-1", "3", "per_version", "ev-9", 50)
        ]
