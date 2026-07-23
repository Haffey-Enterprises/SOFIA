##############################################################################
# Module: test_resolve_technology_endpoint.py
# Service: knowledge-service
# Author: Haffey Enterprises LLC
# Created: 2026-07-23
# Revised: 2026-07-23
# Description: Contract tests for the resolve-technology endpoint (SDD-001
#   §3.3.2) — the request/response shape over HTTP, the eligibility annotation
#   surviving the wire, and the graph store genuinely receiving the forwarded
#   capability id. Runs against the in-memory double (SDD-001 §6).
##############################################################################

from httpx import AsyncClient

from app.adapters.in_memory_graph import InMemoryGraphStore
from app.ports.graph_store import ResolveTechnologyCandidateRecord

_REQUEST_BODY = {
    "capability_id": "cap-1",
    "consuming_context": {
        "environment_class": "production",
        "data_classification": "internal",
    },
}


class TestResolveTechnologyEndpointContract:
    """The endpoint's request/response shape and graph-store wiring."""

    async def test_returns_200_with_empty_result_when_no_candidates_match(
        self, async_client: AsyncClient
    ) -> None:
        # Act
        response = await async_client.post("/api/v1/resolve-technology", json=_REQUEST_BODY)

        # Assert
        assert response.status_code == 200
        assert response.json() == {"admitted": [], "disclosures": []}

    async def test_returns_the_admitted_envelope_with_its_eligibility_verdict(
        self, async_client: AsyncClient, graph_store: InMemoryGraphStore
    ) -> None:
        # Arrange
        graph_store.set_technology_option_candidates(
            [
                ResolveTechnologyCandidateRecord(
                    node_id="tech-1",
                    version="1",
                    origin_mechanism="ingested",
                    derivation_class="primary",
                    tier_applicability=("staging",),
                    approved_data_classifications=("internal",),
                    applicability_state="unconditional",
                    retracted=False,
                    conditions=(),
                )
            ]
        )

        # Act
        response = await async_client.post("/api/v1/resolve-technology", json=_REQUEST_BODY)

        # Assert — ineligible (tier mismatch), but still admitted (§4.4).
        assert response.status_code == 200
        body = response.json()
        assert body["disclosures"] == []
        assert len(body["admitted"]) == 1
        envelope = body["admitted"][0]
        assert envelope["node_id"] == "tech-1"
        assert envelope["node_kind"] == "Technology"
        assert envelope["plane_labels"] == ["Catalog"]
        assert envelope["version"] == "1"
        assert envelope["version_pin"] == "1"
        eligibility = envelope["applicability"]["catalog_eligibility"]
        assert eligibility["eligible"] is False
        assert eligibility["failing_fields"] == ["tier_applicability"]

    async def test_forwards_the_requested_capability_id_to_the_graph_store(
        self, async_client: AsyncClient, graph_store: InMemoryGraphStore
    ) -> None:
        # Act
        await async_client.post("/api/v1/resolve-technology", json=_REQUEST_BODY)

        # Assert
        assert graph_store.resolve_technology_options_calls == ["cap-1"]

    async def test_retracted_technology_is_excluded_from_the_response(
        self, async_client: AsyncClient, graph_store: InMemoryGraphStore
    ) -> None:
        # Arrange
        graph_store.set_technology_option_candidates(
            [
                ResolveTechnologyCandidateRecord(
                    node_id="tech-2",
                    version="1",
                    origin_mechanism="promoted",
                    derivation_class=None,
                    tier_applicability=(),
                    approved_data_classifications=(),
                    applicability_state="unconditional",
                    retracted=True,
                    conditions=(),
                )
            ]
        )

        # Act
        response = await async_client.post("/api/v1/resolve-technology", json=_REQUEST_BODY)

        # Assert — silent exclusion: not admitted, not disclosed.
        assert response.status_code == 200
        assert response.json() == {"admitted": [], "disclosures": []}
