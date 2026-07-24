##############################################################################
# Module: logging.py
# Service: knowledge-service
# Author: Haffey Enterprises LLC
# Created: 2026-07-21
# Revised: 2026-07-21
# Description: Structured-logging configuration for knowledge-service — JSON
#   output on structlog, level-filtered from Settings, with contextvars merged
#   so the per-request correlation ID rides every subsequent line. This is the
#   emission substrate for the SDD-001 §8 event contract; per §4.7 the log
#   channel is the only home of the gateway's operational record, and its
#   content ceiling is Tier 2 — no credential and no Tier 3/4 value.
##############################################################################

import logging

import structlog

_LEVEL_NAMES = logging.getLevelNamesMapping()


def configure_logging(level: str) -> None:
    """Configure structlog for level-filtered JSON logging on stdout.

    Called once at application startup, before any request is served.

    Args:
        level: A standard level name — DEBUG, INFO, WARNING, ERROR, or
            CRITICAL. Settings validates the value before it reaches here; the
            check below guards direct callers.

    Raises:
        ValueError: If `level` is not a recognised level name.
    """
    if level not in _LEVEL_NAMES:
        raise ValueError(f"Unrecognised log level: {level!r}")

    structlog.configure(
        processors=[
            structlog.contextvars.merge_contextvars,
            structlog.processors.add_log_level,
            structlog.processors.TimeStamper(fmt="iso", utc=True),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.JSONRenderer(),
        ],
        wrapper_class=structlog.make_filtering_bound_logger(_LEVEL_NAMES[level]),
        logger_factory=structlog.PrintLoggerFactory(),
        # Caching is off so a reconfiguration actually takes effect on loggers
        # that were already obtained — the module-level `log` objects in this
        # service are acquired at import, before configuration runs.
        cache_logger_on_first_use=False,
    )
