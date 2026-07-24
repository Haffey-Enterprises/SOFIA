##############################################################################
# Module: test_provenance_of_endpoint.py
# Service: knowledge-service
# Author: Haffey Enterprises LLC
# Created: 2026-07-24
# Revised: 2026-07-24
# Description: Contract tests for the provenance-of endpoint (SDD-001
#   §3.3.8), the disclosed audit exception (§1/§3.2) — the request/response
#   shape over HTTP, TARGET_NOT_FOUND rendering 404 on both an absent and a
#   not-promoted entry, the inversion (a retracted/superseded promoted node
#   still returns its provenance), frozen_layer_present=false never
#   rendering an error, and a request missing the required `version` field
#   rejected 422 by Pydantic. Runs against the in-memory double (SDD-001 §6).
##############################################################################

from httpx import AsyncClient

from app.adapters.in_memory_graph import InMemoryGraphStore
from app.ports.graph_store import (
    ProvenanceOfCandidateRecord,
    ProvenanceOfFrozenEntryRecord,
    ProvenanceOfGoverningDecisionRecord,
    ProvenanceOfPage,
)

_REQUEST_BODY = {
    "node_kind": "Technology",
    "business_key": "tech-1",
    "version": "3",
}

_CANDIDATE = ProvenanceOfCandidateRecord(
    candidate_id="cand-1", proposal_kind="promotion", status="promoted"
)
_DECISION = ProvenanceOfGoverningDecisionRecord(
    decision_id="dec-1", outcome="approved", decided_at="2026-07-01T00:00:00Z"
)


def _promoted_page(**overrides: object) -> ProvenanceOfPage:
    base: dict[str, object] = {
        "entry_found": True,
        "is_promoted": True,
        "origin_mechanism": "promoted",
        "is_superseded": False,
        "is_retracted": False,
        "is_conditional": False,
        "candidate": _CANDIDATE,
        "governing_decision": _DECISION,
        "frozen_layer_present": True,
        "provenance_summary_id": "summary-1",
        "entries": (),
    }
    base.update(overrides)
    return ProvenanceOfPage(**base)  # type: ignore[arg-type]


class TestProvenanceOfEndpointContract:
    """The endpoint's request/response shape, raise behavior, and wiring."""

    async def test_returns_200_with_provenance_for_a_promoted_node(
        self, async_client: AsyncClient, graph_store: InMemoryGraphStore
    ) -> None:
        # Arrange
        graph_store.set_provenance_of_result(
            _promoted_page(
                entries=(
                    ProvenanceOfFrozenEntryRecord(
                        evidence_id="ev-1",
                        frozen_fact_summary="a fact",
                        frozen_source_version_pin="1",
                        frozen_source_node_ref="tech-1",
                        is_live=True,
                        live_fact_summary="a fact",
                        live_confidence=0.8,
                        live_weight=1.0,
                        live_source_node_version="1",
                        live_observed_at="2026-07-01T00:00:00Z",
                    ),
                )
            )
        )

        # Act
        response = await async_client.post("/api/v1/provenance-of", json=_REQUEST_BODY)

        # Assert
        assert response.status_code == 200
        body = response.json()
        assert body["node_kind"] == "Technology"
        assert body["business_key"] == "tech-1"
        assert body["version"] == "3"
        assert body["candidate"]["candidate_id"] == "cand-1"
        assert body["governing_decision"]["decision_id"] == "dec-1"
        assert body["frozen_layer_present"] is True
        assert len(body["entries"]) == 1
        assert body["entries"][0]["evidence_id"] == "ev-1"
        assert body["entries"][0]["live"] is True

    async def test_absent_entry_returns_404_target_not_found(
        self, async_client: AsyncClient, graph_store: InMemoryGraphStore
    ) -> None:
        # Arrange — the double defaults to entry_found=False.

        # Act
        response = await async_client.post("/api/v1/provenance-of", json=_REQUEST_BODY)

        # Assert
        assert response.status_code == 404
        body = response.json()
        assert body["error_code"] == "TARGET_NOT_FOUND"

    async def test_not_promoted_entry_returns_404_target_not_found(
        self, async_client: AsyncClient, graph_store: InMemoryGraphStore
    ) -> None:
        # Arrange — the node exists (e.g. ingested) but was never promoted.
        graph_store.set_provenance_of_result(
            _promoted_page(
                is_promoted=False,
                origin_mechanism="ingested",
                candidate=None,
                governing_decision=None,
                frozen_layer_present=False,
                provenance_summary_id=None,
            )
        )

        # Act
        response = await async_client.post("/api/v1/provenance-of", json=_REQUEST_BODY)

        # Assert
        assert response.status_code == 404
        body = response.json()
        assert body["error_code"] == "TARGET_NOT_FOUND"

    async def test_retracted_promoted_node_still_returns_200_with_provenance(
        self, async_client: AsyncClient, graph_store: InMemoryGraphStore
    ) -> None:
        # Arrange — the audit inversion, asserted at the HTTP layer.
        graph_store.set_provenance_of_result(_promoted_page(is_retracted=True))

        # Act
        response = await async_client.post("/api/v1/provenance-of", json=_REQUEST_BODY)

        # Assert
        assert response.status_code == 200
        body = response.json()
        assert body["entry_markers"] == ["retracted"]

    async def test_missing_frozen_layer_returns_200_never_an_error(
        self, async_client: AsyncClient, graph_store: InMemoryGraphStore
    ) -> None:
        # Arrange — a #20 violation reached pre-CI-catch: candidate resolves
        # but no ProvenanceSummary exists.
        graph_store.set_provenance_of_result(
            _promoted_page(frozen_layer_present=False, provenance_summary_id=None)
        )

        # Act
        response = await async_client.post("/api/v1/provenance-of", json=_REQUEST_BODY)

        # Assert — never a 500, never a raised error.
        assert response.status_code == 200
        body = response.json()
        assert body["frozen_layer_present"] is False
        assert body["provenance_summary_id"] is None

    async def test_request_missing_version_is_rejected_422(
        self, async_client: AsyncClient
    ) -> None:
        # Arrange
        request_body = {"node_kind": "Technology", "business_key": "tech-1"}

        # Act
        response = await async_client.post("/api/v1/provenance-of", json=request_body)

        # Assert
        assert response.status_code == 422

    async def test_forwards_node_kind_business_key_version_to_the_graph_store(
        self, async_client: AsyncClient, graph_store: InMemoryGraphStore
    ) -> None:
        # Arrange
        graph_store.set_provenance_of_result(_promoted_page())

        # Act
        await async_client.post("/api/v1/provenance-of", json=_REQUEST_BODY)

        # Assert
        assert graph_store.provenance_of_calls == [("Technology", "tech-1", "3")]
