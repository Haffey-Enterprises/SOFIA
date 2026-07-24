##############################################################################
# Module: test_find_precedents_endpoint.py
# Service: knowledge-service
# Author: Haffey Enterprises LLC
# Created: 2026-07-23
# Revised: 2026-07-23
# Description: Contract tests for the find-precedents endpoint (SDD-001
#   §3.3.5) — the request/response shape over HTTP, the envelope +
#   target_environment + gate_decisions surviving the wire, and the graph
#   store genuinely receiving the forwarded criteria. Runs against the
#   in-memory double (SDD-001 §6).
##############################################################################

from httpx import AsyncClient

from app.adapters.in_memory_graph import InMemoryGraphStore
from app.ports.graph_store import FindPrecedentsCandidateRecord, GateDecisionRecord

_REQUEST_BODY = {
    "capability_ids": [],
    "pattern_ids": [],
    "technology_ids": ["tech-1"],
    "target_environment": "production",
    "gate_outcome": "approved",
    "consuming_context": {
        "environment_class": "production",
        "data_classification": "internal",
    },
}


class TestFindPrecedentsEndpointContract:
    """The endpoint's request/response shape and graph-store wiring."""

    async def test_returns_200_with_empty_result_when_no_precedents_match(
        self, async_client: AsyncClient
    ) -> None:
        # Act
        response = await async_client.post("/api/v1/find-precedents", json=_REQUEST_BODY)

        # Assert
        assert response.status_code == 200
        assert response.json() == {"precedents": []}

    async def test_returns_the_matching_precedent_with_its_envelope_and_context(
        self, async_client: AsyncClient, graph_store: InMemoryGraphStore
    ) -> None:
        # Arrange
        graph_store.set_precedent_candidates(
            [
                FindPrecedentsCandidateRecord(
                    node_id="sol-1",
                    version="1",
                    origin_mechanism="authored",
                    target_environment="production",
                    gate_decisions=(
                        GateDecisionRecord(outcome="approved", gate="gate_1", decision_id="gd-1"),
                    ),
                )
            ]
        )

        # Act
        response = await async_client.post("/api/v1/find-precedents", json=_REQUEST_BODY)

        # Assert
        assert response.status_code == 200
        body = response.json()
        assert len(body["precedents"]) == 1
        entry = body["precedents"][0]
        assert entry["envelope"]["node_id"] == "sol-1"
        assert entry["envelope"]["node_kind"] == "Solution"
        assert entry["envelope"]["plane_labels"] == []
        assert entry["envelope"]["origin_mechanism"] == "authored"
        assert entry["envelope"]["applicability"]["catalog_eligibility"] is None
        assert entry["envelope"]["applicability"]["deprecation"] is None
        assert entry["target_environment"] == "production"
        assert len(entry["gate_decisions"]) == 1
        assert entry["gate_decisions"][0]["outcome"] == "approved"
        assert entry["gate_decisions"][0]["gate"] == "gate_1"
        assert entry["gate_decisions"][0]["decision_id"] == "gd-1"

    async def test_forwards_the_requested_criteria_to_the_graph_store(
        self, async_client: AsyncClient, graph_store: InMemoryGraphStore
    ) -> None:
        # Act
        await async_client.post("/api/v1/find-precedents", json=_REQUEST_BODY)

        # Assert
        assert len(graph_store.find_precedents_calls) == 1
        criteria = graph_store.find_precedents_calls[0]
        assert criteria.technology_ids == ("tech-1",)
        assert criteria.capability_ids == ()
        assert criteria.pattern_ids == ()
        assert criteria.target_environment == "production"
        assert criteria.gate_outcome == "approved"

    async def test_non_authored_origin_is_excluded_from_the_response(
        self, async_client: AsyncClient, graph_store: InMemoryGraphStore
    ) -> None:
        # Arrange
        graph_store.set_precedent_candidates(
            [
                FindPrecedentsCandidateRecord(
                    node_id="sol-2",
                    version="1",
                    origin_mechanism="ingested",
                    target_environment=None,
                    gate_decisions=(),
                )
            ]
        )

        # Act
        response = await async_client.post("/api/v1/find-precedents", json=_REQUEST_BODY)

        # Assert — silent exclusion: fail-closed on the Solution invariant.
        assert response.status_code == 200
        assert response.json() == {"precedents": []}

    async def test_all_empty_linkage_criteria_returns_empty_without_querying(
        self, async_client: AsyncClient, graph_store: InMemoryGraphStore
    ) -> None:
        # Arrange — F4: at least one linkage criterion is required.
        request_body = {
            "capability_ids": [],
            "pattern_ids": [],
            "technology_ids": [],
            "consuming_context": {
                "environment_class": "production",
                "data_classification": "internal",
            },
        }

        # Act
        response = await async_client.post("/api/v1/find-precedents", json=request_body)

        # Assert
        assert response.status_code == 200
        assert response.json() == {"precedents": []}
        assert graph_store.find_precedents_calls == []
