##############################################################################
# Module: test_observability.py
# Service: knowledge-service
# Author: Haffey Enterprises LLC
# Created: 2026-07-21
# Revised: 2026-07-21
# Description: Unit tests for the day-one observability primitives (SDD-001
#   §8) — JSON structured-logging configuration at the configured level, and
#   the correlation-ID binding the middleware relies on. Per §4.7 these
#   surfaces are the only home of the gateway's operational record.
##############################################################################

import json

import pytest
import structlog

from app.observability.logging import configure_logging


class TestConfigureLogging:
    """Logs are JSON, level-filtered, and carry bound context."""

    def test_configure_logging_emits_json_with_the_event_name(
        self, capsys: pytest.CaptureFixture[str]
    ) -> None:
        # Arrange
        configure_logging("INFO")
        log = structlog.get_logger()

        # Act
        log.info("neo4j_driver_opened", neo4j_database="sofia")

        # Assert
        payload = json.loads(capsys.readouterr().out.strip())
        assert payload["event"] == "neo4j_driver_opened"
        assert payload["neo4j_database"] == "sofia"

    def test_configure_logging_stamps_level_and_timestamp(
        self, capsys: pytest.CaptureFixture[str]
    ) -> None:
        # Arrange
        configure_logging("INFO")
        log = structlog.get_logger()

        # Act
        log.warning("neo4j_connectivity_check_failed", reason="driver_not_open")

        # Assert
        payload = json.loads(capsys.readouterr().out.strip())
        assert payload["level"] == "warning"
        assert "timestamp" in payload

    def test_configure_logging_suppresses_events_below_the_configured_level(
        self, capsys: pytest.CaptureFixture[str]
    ) -> None:
        # Arrange
        configure_logging("WARNING")
        log = structlog.get_logger()

        # Act
        log.info("this_should_not_be_emitted")

        # Assert
        assert capsys.readouterr().out == ""

    def test_configure_logging_merges_bound_context_variables(
        self, capsys: pytest.CaptureFixture[str]
    ) -> None:
        # Arrange
        configure_logging("INFO")
        structlog.contextvars.clear_contextvars()
        structlog.contextvars.bind_contextvars(correlation_id="cid-abc-123")
        log = structlog.get_logger()

        # Act
        log.info("write_rejected")

        # Assert — the correlation ID must ride every subsequent line.
        payload = json.loads(capsys.readouterr().out.strip())
        assert payload["correlation_id"] == "cid-abc-123"
        structlog.contextvars.clear_contextvars()

    def test_configure_logging_with_unknown_level_raises_value_error(self) -> None:
        # Act / Assert
        with pytest.raises(ValueError):
            configure_logging("CHATTY")
