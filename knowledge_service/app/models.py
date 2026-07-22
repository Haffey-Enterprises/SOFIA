##############################################################################
# Module: models.py
# Service: knowledge-service
# Author: Haffey Enterprises LLC
# Created: 2026-07-21
# Revised: 2026-07-21
# Description: Request/response contracts for knowledge-service (SDD-001
#   §4.1). At RBT-77 the surface is the §3.1 health and readiness shapes; the
#   operation-shaped request/response contracts and the result envelope of
#   §3.2-§3.6 land with the operations themselves. These typed models are the
#   source of truth for the contract tests — when an implementation and a
#   contract diverge, the contract wins.
##############################################################################

from enum import StrEnum
from typing import Literal

from pydantic import BaseModel, Field


class CheckStatus(StrEnum):
    """Outcome of a single readiness check."""

    OK = "ok"
    UNAVAILABLE = "unavailable"


class HealthResponse(BaseModel):
    """Liveness response — the process is up (SDD-001 §3.1).

    Deliberately carries no dependency state: liveness performs no I/O, so a
    graph outage must never take this endpoint negative and get the container
    killed.
    """

    status: Literal["ok"] = "ok"
    service: str


class ReadinessResponse(BaseModel):
    """Readiness response — the service can actually serve (SDD-001 §3.1).

    There is no degraded mode: this service has exactly one backing store and
    every operation requires it, so any failed check makes the whole response
    negative and the endpoint answers 503.
    """

    status: Literal["ok", "unavailable"]
    service: str
    checks: dict[str, CheckStatus] = Field(
        description="Per-check outcomes, keyed by check name, in SDD-001 §3.1 order.",
    )
