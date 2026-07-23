##############################################################################
# Module: test_track_record_lookup_endpoint.py
# Service: knowledge-service
# Author: Haffey Enterprises LLC
# Created: 2026-07-23
# Revised: 2026-07-23
# Description: Contract tests for the track-record-lookup endpoint (SDD-001
#   §3.3.3) — the request/response shape over HTTP, the graph store genuinely
#   receiving the forwarded target refs, and request validation on the closed
#   entity_kind vocabulary. Runs against the in-memory double (SDD-001 §6).
##############################################################################

from httpx import AsyncClient

from app.adapters.in_memory_graph import InMemoryGraphStore
from app.ports.graph_store import TargetEntityRef, TrackRecordCandidateRecord

_REQUEST_BODY = {
    "target_refs": [{"entity_kind": "Technology", "entity_id": "tech-1"}],
    "consuming_context": {
        "environment_class": "production",
        "data_classification": "internal",
    },
}


class TestTrackRecordLookupEndpointContract:
    """The endpoint's request/response shape and graph-store wiring."""

    async def test_returns_200_with_empty_result_when_no_candidates_match(
        self, async_client: AsyncClient
    ) -> None:
        # Act
        response = await async_client.post("/api/v1/track-record-lookup", json=_REQUEST_BODY)

        # Assert
        assert response.status_code == 200
        assert response.json() == {"admitted": [], "disclosures": []}

    async def test_returns_the_admitted_envelope_for_a_matching_candidate(
        self, async_client: AsyncClient, graph_store: InMemoryGraphStore
    ) -> None:
        # Arrange
        graph_store.set_track_record_candidates(
            [
                TrackRecordCandidateRecord(
                    node_id="op-1",
                    origin_mechanism="derived",
                    derivation_class="distilled",
                    node_confidence=0.8,
                    edge_confidence=0.6,
                    first_observed_at="2026-01-01T00:00:00Z",
                    last_observed_at="2026-06-01T00:00:00Z",
                )
            ]
        )

        # Act
        response = await async_client.post("/api/v1/track-record-lookup", json=_REQUEST_BODY)

        # Assert
        assert response.status_code == 200
        body = response.json()
        assert body["disclosures"] == []
        assert len(body["admitted"]) == 1
        envelope = body["admitted"][0]
        assert envelope["node_id"] == "op-1"
        assert envelope["node_kind"] == "ObservedPattern"
        assert envelope["plane_labels"] == ["Operational"]
        assert envelope["origin_mechanism"] == "derived"
        assert envelope["derivation_class"] == "distilled"
        assert envelope["version"] is None
        assert envelope["version_pin"] is None
        assert envelope["effective_from"] == "2026-01-01T00:00:00Z"
        assert envelope["effective_to"] == "2026-06-01T00:00:00Z"
        assert envelope["confidences"] == [0.8, 0.6]
        assert envelope["applicability"]["conditional_admission"] == "unconditional"
        assert envelope["applicability"]["catalog_eligibility"] is None

    async def test_forwards_the_requested_target_refs_to_the_graph_store(
        self, async_client: AsyncClient, graph_store: InMemoryGraphStore
    ) -> None:
        # Act
        await async_client.post("/api/v1/track-record-lookup", json=_REQUEST_BODY)

        # Assert
        assert graph_store.find_track_record_calls == [
            [TargetEntityRef(entity_kind="Technology", entity_id="tech-1")]
        ]

    async def test_rejects_an_unratified_entity_kind_with_422(
        self, async_client: AsyncClient
    ) -> None:
        # Arrange
        body = {
            "target_refs": [{"entity_kind": "NotARealKind", "entity_id": "x"}],
            "consuming_context": {
                "environment_class": "production",
                "data_classification": "internal",
            },
        }

        # Act
        response = await async_client.post("/api/v1/track-record-lookup", json=body)

        # Assert — the closed four-kind vocabulary is enforced at the request
        # boundary, not left to fail later inside the traversal.
        assert response.status_code == 422
