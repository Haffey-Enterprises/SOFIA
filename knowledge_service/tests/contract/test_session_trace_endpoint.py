##############################################################################
# Module: test_session_trace_endpoint.py
# Service: knowledge-service
# Author: Haffey Enterprises LLC
# Created: 2026-07-24
# Revised: 2026-07-24
# Description: Contract tests for the session-trace endpoint (SDD-001
#   §3.3.9), trio-free by inapplicability (ST-D1) — the request/response
#   shape over HTTP, TARGET_NOT_FOUND rendering 404 on an absent session
#   only, an existing-but-empty session rendering 200 with an empty trace,
#   a now-retracted cited node still surfacing with its marker, and a
#   request missing the required `session_id` field rejected 422 by
#   Pydantic. Runs against the in-memory double (SDD-001 §6).
##############################################################################

from httpx import AsyncClient

from app.adapters.in_memory_graph import InMemoryGraphStore
from app.ports.graph_store import (
    CitedNodeRefRecord,
    SessionTracePage,
    TraceConclusionRecord,
    TraceEvidenceRecord,
)

_REQUEST_BODY = {"session_id": "sess-1"}


def _conclusion(**overrides: object) -> TraceConclusionRecord:
    base: dict[str, object] = {
        "progress_id": "prog-1",
        "conclusion_type": "TechnologySelection",
        "reasoner_category": "encoded_reasoning",
        "authoritative": True,
        "confidence": 0.9,
        "overridden_by_human": False,
        "created_at": "2026-07-01T00:00:00Z",
        "evidence": (),
        "rejected_alternatives": (),
    }
    base.update(overrides)
    return TraceConclusionRecord(**base)  # type: ignore[arg-type]


class TestSessionTraceEndpointContract:
    """The endpoint's request/response shape, raise behavior, and wiring."""

    async def test_returns_200_with_the_trace_for_an_existing_session(
        self, async_client: AsyncClient, graph_store: InMemoryGraphStore
    ) -> None:
        # Arrange
        graph_store.set_session_trace_result(
            SessionTracePage(session_found=True, conclusions=(_conclusion(),), led_to=())
        )

        # Act
        response = await async_client.post("/api/v1/session-trace", json=_REQUEST_BODY)

        # Assert
        assert response.status_code == 200
        body = response.json()
        assert body["session_id"] == "sess-1"
        assert len(body["conclusions"]) == 1
        assert body["conclusions"][0]["progress_id"] == "prog-1"

    async def test_absent_session_returns_404_target_not_found(
        self, async_client: AsyncClient, graph_store: InMemoryGraphStore
    ) -> None:
        # Arrange — the double defaults to session_found=False.

        # Act
        response = await async_client.post("/api/v1/session-trace", json=_REQUEST_BODY)

        # Assert
        assert response.status_code == 404
        body = response.json()
        assert body["error_code"] == "TARGET_NOT_FOUND"

    async def test_existing_but_empty_session_returns_200_with_empty_trace(
        self, async_client: AsyncClient, graph_store: InMemoryGraphStore
    ) -> None:
        # Arrange — a legal non-blocking capture state (DDR-001).
        graph_store.set_session_trace_result(
            SessionTracePage(session_found=True, conclusions=(), led_to=())
        )

        # Act
        response = await async_client.post("/api/v1/session-trace", json=_REQUEST_BODY)

        # Assert
        assert response.status_code == 200
        body = response.json()
        assert body["conclusions"] == []
        assert body["led_to"] == []

    async def test_now_retracted_cited_node_still_surfaces_with_its_marker(
        self, async_client: AsyncClient, graph_store: InMemoryGraphStore
    ) -> None:
        # Arrange — the point-in-time fidelity point, asserted at the HTTP layer.
        retracted_pin = CitedNodeRefRecord(
            node_kind="Technology",
            node_id="tech-1",
            version="1",
            is_superseded=False,
            is_retracted=True,
            is_conditional=False,
        )
        graph_store.set_session_trace_result(
            SessionTracePage(
                session_found=True,
                conclusions=(
                    _conclusion(
                        evidence=(
                            TraceEvidenceRecord(
                                evidence_id="ev-1",
                                fact_summary="a fact",
                                confidence=0.8,
                                weight=1.0,
                                source_node_version="1",
                                observed_at="2026-07-01T00:00:00Z",
                                resolved_pin=retracted_pin,
                            ),
                        )
                    ),
                ),
                led_to=(),
            )
        )

        # Act
        response = await async_client.post("/api/v1/session-trace", json=_REQUEST_BODY)

        # Assert
        assert response.status_code == 200
        body = response.json()
        pin = body["conclusions"][0]["evidence"][0]["resolved_pin"]
        assert pin["markers"] == ["retracted"]

    async def test_request_missing_session_id_is_rejected_422(
        self, async_client: AsyncClient
    ) -> None:
        # Act
        response = await async_client.post("/api/v1/session-trace", json={})

        # Assert
        assert response.status_code == 422

    async def test_forwards_session_id_to_the_graph_store(
        self, async_client: AsyncClient, graph_store: InMemoryGraphStore
    ) -> None:
        # Arrange
        graph_store.set_session_trace_result(
            SessionTracePage(session_found=True, conclusions=(), led_to=())
        )

        # Act
        await async_client.post("/api/v1/session-trace", json=_REQUEST_BODY)

        # Assert
        assert graph_store.session_trace_calls == ["sess-1"]
