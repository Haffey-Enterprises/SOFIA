##############################################################################
# Module: test_select_patterns_endpoint.py
# Service: knowledge-service
# Author: Haffey Enterprises LLC
# Created: 2026-07-23
# Revised: 2026-07-23
# Description: Contract tests for the select-patterns endpoint (SDD-001
#   §3.3.1) — the nested request/response shape over HTTP, the per-capability
#   taxonomy + Technology options surviving the wire, and the graph store
#   genuinely receiving the forwarded capability ids. Runs against the
#   in-memory double (SDD-001 §6).
##############################################################################

from httpx import AsyncClient

from app.adapters.in_memory_graph import InMemoryGraphStore
from app.ports.graph_store import (
    CapabilityBlockRecord,
    ResolveTechnologyCandidateRecord,
    SelectPatternsCandidateRecord,
)

_REQUEST_BODY = {
    "capability_ids": ["cap-1"],
    "consuming_context": {
        "environment_class": "production",
        "data_classification": "internal",
    },
}


class TestSelectPatternsEndpointContract:
    """The endpoint's nested request/response shape and graph-store wiring."""

    async def test_returns_200_with_empty_result_when_no_candidates_match(
        self, async_client: AsyncClient
    ) -> None:
        # Act
        response = await async_client.post("/api/v1/select-patterns", json=_REQUEST_BODY)

        # Assert
        assert response.status_code == 200
        assert response.json() == {"patterns": [], "pattern_disclosures": []}

    async def test_returns_an_admitted_pattern_with_nested_capability_and_tech(
        self, async_client: AsyncClient, graph_store: InMemoryGraphStore
    ) -> None:
        # Arrange
        graph_store.set_pattern_candidates(
            [
                SelectPatternsCandidateRecord(
                    node_id="pattern-1",
                    version="1",
                    origin_mechanism="ingested",
                    derivation_class="primary",
                    applicability_state="unconditional",
                    retracted=False,
                    conditions=(),
                    capabilities=(
                        CapabilityBlockRecord(
                            capability_id="cap-1",
                            l1_taxonomy="compute",
                            l2_taxonomy="serverless",
                            l3_taxonomy="functions",
                            technology_options=(
                                ResolveTechnologyCandidateRecord(
                                    node_id="tech-1",
                                    version="1",
                                    origin_mechanism="ingested",
                                    derivation_class="primary",
                                    tier_applicability=("production",),
                                    approved_data_classifications=("internal",),
                                    applicability_state="unconditional",
                                    retracted=False,
                                    conditions=(),
                                ),
                            ),
                        ),
                    ),
                    preferred_over=("pattern-2",),
                )
            ]
        )

        # Act
        response = await async_client.post("/api/v1/select-patterns", json=_REQUEST_BODY)

        # Assert
        assert response.status_code == 200
        body = response.json()
        assert body["pattern_disclosures"] == []
        assert len(body["patterns"]) == 1
        pattern = body["patterns"][0]
        assert pattern["envelope"]["node_id"] == "pattern-1"
        assert pattern["envelope"]["node_kind"] == "Pattern"
        assert pattern["envelope"]["applicability"]["catalog_eligibility"] is None
        assert pattern["envelope"]["applicability"]["deprecation"] is None
        assert pattern["preferred_over"] == ["pattern-2"]
        assert len(pattern["capabilities"]) == 1
        block = pattern["capabilities"][0]
        assert block["capability_id"] == "cap-1"
        assert block["l1_taxonomy"] == "compute"
        assert block["technology_disclosures"] == []
        assert len(block["technology_options"]) == 1
        assert block["technology_options"][0]["node_id"] == "tech-1"

    async def test_forwards_the_requested_capability_ids_to_the_graph_store(
        self, async_client: AsyncClient, graph_store: InMemoryGraphStore
    ) -> None:
        # Act
        await async_client.post("/api/v1/select-patterns", json=_REQUEST_BODY)

        # Assert
        assert graph_store.select_patterns_calls == [["cap-1"]]

    async def test_retracted_pattern_is_excluded_from_the_response(
        self, async_client: AsyncClient, graph_store: InMemoryGraphStore
    ) -> None:
        # Arrange
        graph_store.set_pattern_candidates(
            [
                SelectPatternsCandidateRecord(
                    node_id="pattern-2",
                    version="1",
                    origin_mechanism="promoted",
                    derivation_class=None,
                    applicability_state="unconditional",
                    retracted=True,
                    conditions=(),
                    capabilities=(),
                    preferred_over=(),
                )
            ]
        )

        # Act
        response = await async_client.post("/api/v1/select-patterns", json=_REQUEST_BODY)

        # Assert — silent exclusion: no pattern, no disclosure.
        assert response.status_code == 200
        assert response.json() == {"patterns": [], "pattern_disclosures": []}
