##############################################################################
# Module: test_correlation_id.py
# Service: knowledge-service
# Author: Haffey Enterprises LLC
# Created: 2026-07-21
# Revised: 2026-07-21
# Description: Integration tests for correlation-ID propagation through the
#   real application. SDD-001 §8 requires `correlation_id` on every structured
#   log event and end-to-end propagation; these tests hold the middleware to
#   minting one when absent, honouring one when supplied, and binding it so it
#   reaches the log line an in-request event emits.
##############################################################################

import json
import uuid

import pytest
import structlog
from httpx import AsyncClient

from app.adapters.in_memory_graph import InMemoryGraphStore
from app.observability.correlation_id import CORRELATION_ID_HEADER
from app.observability.logging import configure_logging


class TestCorrelationIdPropagation:
    """Every response carries a correlation ID, minted or echoed."""

    async def test_response_carries_a_minted_correlation_id_when_none_supplied(
        self, async_client: AsyncClient
    ) -> None:
        # Act
        response = await async_client.get("/healthz")

        # Assert
        minted = response.headers[CORRELATION_ID_HEADER]
        assert uuid.UUID(minted)

    async def test_response_echoes_the_supplied_correlation_id(
        self, async_client: AsyncClient
    ) -> None:
        # Arrange
        supplied = "cid-from-upstream-caller"

        # Act
        response = await async_client.get("/healthz", headers={CORRELATION_ID_HEADER: supplied})

        # Assert
        assert response.headers[CORRELATION_ID_HEADER] == supplied

    async def test_each_request_mints_a_distinct_correlation_id(
        self, async_client: AsyncClient
    ) -> None:
        # Act
        first = await async_client.get("/healthz")
        second = await async_client.get("/healthz")

        # Assert
        assert first.headers[CORRELATION_ID_HEADER] != second.headers[CORRELATION_ID_HEADER]


class TestCorrelationIdReachesTheLogChannel:
    """The bound ID must ride the structured events emitted during the request."""

    async def test_in_request_log_event_carries_the_supplied_correlation_id(
        self,
        async_client: AsyncClient,
        graph_store: InMemoryGraphStore,
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        # Arrange — a failing readiness check gives us an in-request event.
        configure_logging("INFO")
        structlog.contextvars.clear_contextvars()
        graph_store.set_connectivity(healthy=False)

        # Act
        await async_client.get("/readyz", headers={CORRELATION_ID_HEADER: "cid-under-test"})

        # Assert
        emitted = [
            json.loads(line) for line in capsys.readouterr().out.splitlines() if line.strip()
        ]
        readiness_events = [e for e in emitted if e["event"] == "readiness_check_failed"]
        assert readiness_events, "expected a readiness_check_failed event"
        assert all(e["correlation_id"] == "cid-under-test" for e in readiness_events)
