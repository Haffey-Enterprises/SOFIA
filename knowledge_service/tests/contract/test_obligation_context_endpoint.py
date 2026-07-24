##############################################################################
# Module: test_obligation_context_endpoint.py
# Service: knowledge-service
# Author: Haffey Enterprises LLC
# Created: 2026-07-23
# Revised: 2026-07-23
# Description: Contract tests for the obligation-context endpoint (SDD-001
#   §3.3.4) — the request/response shape over HTTP, the envelope + PolicyRule
#   payload surviving the wire, and the graph store genuinely receiving the
#   forwarded solution id. Runs against the in-memory double (SDD-001 §6).
##############################################################################

from httpx import AsyncClient

from app.adapters.in_memory_graph import InMemoryGraphStore
from app.ports.graph_store import ObligationCandidateRecord

_REQUEST_BODY = {
    "solution_id": "sol-1",
    "consuming_context": {
        "environment_class": "production",
        "data_classification": "internal",
    },
}


class TestObligationContextEndpointContract:
    """The endpoint's request/response shape and graph-store wiring."""

    async def test_returns_200_with_empty_result_when_solution_is_ungoverned(
        self, async_client: AsyncClient
    ) -> None:
        # Act
        response = await async_client.post("/api/v1/obligation-context", json=_REQUEST_BODY)

        # Assert
        assert response.status_code == 200
        assert response.json() == {"obligations": [], "disclosures": []}

    async def test_returns_the_admitted_obligation_with_its_envelope_and_payload(
        self, async_client: AsyncClient, graph_store: InMemoryGraphStore
    ) -> None:
        # Arrange
        graph_store.set_obligation_candidates(
            [
                ObligationCandidateRecord(
                    node_id="rule-1",
                    version="1",
                    origin_mechanism="ingested",
                    derivation_class="primary",
                    applicability_state="unconditional",
                    retracted=False,
                    conditions=(),
                    statement="Data at rest must be encrypted.",
                    rule_definition="IF classification == 'restricted' THEN require(encryption)",
                    dependency_manifest=("Technology",),
                    enforcement_level="hard",
                    enforced_at_gate="architecture_review",
                    domain="security",
                )
            ]
        )

        # Act
        response = await async_client.post("/api/v1/obligation-context", json=_REQUEST_BODY)

        # Assert
        assert response.status_code == 200
        body = response.json()
        assert body["disclosures"] == []
        assert len(body["obligations"]) == 1
        entry = body["obligations"][0]
        assert entry["envelope"]["node_id"] == "rule-1"
        assert entry["envelope"]["node_kind"] == "PolicyRule"
        assert entry["envelope"]["plane_labels"] == ["Standards"]
        assert entry["envelope"]["applicability"]["catalog_eligibility"] is None
        assert entry["envelope"]["applicability"]["deprecation"] is None
        assert entry["policy_rule"]["statement"] == "Data at rest must be encrypted."
        assert entry["policy_rule"]["rule_definition"] == (
            "IF classification == 'restricted' THEN require(encryption)"
        )
        assert entry["policy_rule"]["dependency_manifest"] == ["Technology"]
        assert entry["policy_rule"]["enforcement_level"] == "hard"
        assert entry["policy_rule"]["enforced_at_gate"] == "architecture_review"
        assert entry["policy_rule"]["domain"] == "security"

    async def test_forwards_the_requested_solution_id_to_the_graph_store(
        self, async_client: AsyncClient, graph_store: InMemoryGraphStore
    ) -> None:
        # Act
        await async_client.post("/api/v1/obligation-context", json=_REQUEST_BODY)

        # Assert
        assert graph_store.obligation_context_calls == ["sol-1"]

    async def test_retracted_rule_is_excluded_from_the_response(
        self, async_client: AsyncClient, graph_store: InMemoryGraphStore
    ) -> None:
        # Arrange
        graph_store.set_obligation_candidates(
            [
                ObligationCandidateRecord(
                    node_id="rule-2",
                    version="1",
                    origin_mechanism="promoted",
                    derivation_class=None,
                    applicability_state="unconditional",
                    retracted=True,
                    conditions=(),
                    statement=None,
                    rule_definition=None,
                    dependency_manifest=(),
                    enforcement_level=None,
                    enforced_at_gate=None,
                    domain=None,
                )
            ]
        )

        # Act
        response = await async_client.post("/api/v1/obligation-context", json=_REQUEST_BODY)

        # Assert — silent exclusion: no obligation, no disclosure.
        assert response.status_code == 200
        assert response.json() == {"obligations": [], "disclosures": []}
