##############################################################################
# Module: test_read_as_of_endpoint.py
# Service: knowledge-service
# Author: Haffey Enterprises LLC
# Created: 2026-07-24
# Revised: 2026-07-24
# Description: Contract tests for the read-as-of endpoint (SDD-001 §3.3.6),
#   pin-mode — the request/response shape over HTTP, a resolved pin
#   surviving the wire as a ReadResult, a resolution miss rendering as the
#   §3.2 error envelope at its resolved HTTP status (the first read endpoint
#   that can raise), and a request missing the required `version` field
#   rejected 422 by Pydantic. Runs against the in-memory double (SDD-001 §6).
##############################################################################

from httpx import AsyncClient

from app.adapters.in_memory_graph import InMemoryGraphStore
from app.ports.graph_store import ReadAsOfResolvedRecord

_REQUEST_BODY = {
    "node_kind": "Technology",
    "business_key": "tech-1",
    "version": "3",
    "consuming_context": {
        "environment_class": "production",
        "data_classification": "internal",
    },
}


class TestReadAsOfEndpointContract:
    """The endpoint's request/response shape, raise behavior, and wiring."""

    async def test_returns_200_with_the_admitted_envelope_on_a_resolved_pin(
        self, async_client: AsyncClient, graph_store: InMemoryGraphStore
    ) -> None:
        # Arrange
        graph_store.set_read_as_of_result(
            ReadAsOfResolvedRecord(
                node_id="tech-1",
                plane_labels=("Catalog",),
                version="3",
                origin_mechanism="ingested",
                derivation_class="primary",
                effective_from=None,
                effective_to=None,
                applicability_state="unconditional",
                retracted=False,
                conditions=(),
            )
        )

        # Act
        response = await async_client.post("/api/v1/read-as-of", json=_REQUEST_BODY)

        # Assert
        assert response.status_code == 200
        body = response.json()
        assert body["disclosures"] == []
        assert len(body["admitted"]) == 1
        envelope = body["admitted"][0]
        assert envelope["node_id"] == "tech-1"
        assert envelope["node_kind"] == "Technology"
        assert envelope["version"] == "3"
        assert envelope["version_pin"] == "3"
        assert envelope["applicability"]["catalog_eligibility"] is None
        assert envelope["applicability"]["deprecation"] is None

    async def test_resolution_miss_returns_target_not_found_error_envelope(
        self, async_client: AsyncClient, graph_store: InMemoryGraphStore
    ) -> None:
        # Arrange — the double reports no configured result: a resolution miss.

        # Act
        response = await async_client.post("/api/v1/read-as-of", json=_REQUEST_BODY)

        # Assert
        assert response.status_code == 404
        body = response.json()
        assert body["error_code"] == "TARGET_NOT_FOUND"

    async def test_request_missing_version_is_rejected_422(self, async_client: AsyncClient) -> None:
        # Arrange
        request_body = {
            "node_kind": "Technology",
            "business_key": "tech-1",
            "consuming_context": {
                "environment_class": "production",
                "data_classification": "internal",
            },
        }

        # Act
        response = await async_client.post("/api/v1/read-as-of", json=request_body)

        # Assert
        assert response.status_code == 422

    async def test_forwards_node_kind_business_key_version_to_the_graph_store(
        self, async_client: AsyncClient, graph_store: InMemoryGraphStore
    ) -> None:
        # Act
        await async_client.post("/api/v1/read-as-of", json=_REQUEST_BODY)

        # Assert
        assert graph_store.read_as_of_calls == [("Technology", "tech-1", "3")]
