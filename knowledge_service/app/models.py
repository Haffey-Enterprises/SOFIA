##############################################################################
# Module: models.py
# Service: knowledge-service
# Author: Haffey Enterprises LLC
# Created: 2026-07-21
# Revised: 2026-07-23
# Description: Request/response contracts for knowledge-service (SDD-001
#   §4.1). At RBT-77 the surface was the §3.1 health and readiness shapes;
#   RBT-78 adds the §3.2 error contract — the typed-error taxonomy (ErrorType,
#   the whole ratified §3.2 vocabulary) and the ErrorResponse envelope the
#   gateway's exception handler renders. The operation-shaped request/response
#   contracts and the result envelope of §3.3-§3.6 land with the operations
#   themselves. These typed models are the source of truth for the contract
#   tests — when an implementation and a contract diverge, the contract wins.
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


class ErrorType(StrEnum):
    """The SDD-001 §3.2 typed-error taxonomy — one type per enforced invariant.

    The closed, ratified vocabulary of every rejection the gateway can return
    (SDD-001 §3.2), enumerated whole here as its single source: the exception
    layer (app.domain.exceptions) and the response envelope both draw from it,
    and the write stories (RBT-79+) raise from it rather than re-opening it.
    Enumerating it in full is transcription of a ratified list, not invented
    vocabulary — the distinction from the forthcoming predicate grammar, which
    is genuinely unowned. RBT-78 (reads) raises only TARGET_NOT_FOUND; the rest
    carry write-side raising sites landing with their operations.
    """

    AUTHOR_VIOLATION = "AUTHOR_VIOLATION"
    DECISION_NOT_APPROVING = "DECISION_NOT_APPROVING"
    MONOTONICITY_VIOLATION = "MONOTONICITY_VIOLATION"
    SCOPE_DISPOSITION_MISSING = "SCOPE_DISPOSITION_MISSING"
    SCOPE_CONFLICT = "SCOPE_CONFLICT"
    SUBTYPE_VIOLATION = "SUBTYPE_VIOLATION"
    CLASSIFICATION_REJECTED = "CLASSIFICATION_REJECTED"
    SCHEMA_VIOLATION = "SCHEMA_VIOLATION"
    PROVENANCE_MISSING = "PROVENANCE_MISSING"
    SOURCE_REF_MISSING = "SOURCE_REF_MISSING"
    FLAG_CATEGORY_MISMATCH = "FLAG_CATEGORY_MISMATCH"
    UNIQUENESS_CONFLICT = "UNIQUENESS_CONFLICT"
    TARGET_NOT_FOUND = "TARGET_NOT_FOUND"
    NON_CITABLE_SOURCE = "NON_CITABLE_SOURCE"
    CONFIDENCE_UNDERIVABLE = "CONFIDENCE_UNDERIVABLE"


class FaultClass(StrEnum):
    """Retry-decision class for an error response (house application-code §1).

    Carried on the error envelope so an inter-service consumer branches on the
    fault's nature rather than on the HTTP status alone. Optional on the
    gateway's rejections; populated when a raising site has a fault nature to
    declare.
    """

    TRANSIENT = "transient"
    PERMANENT = "permanent"
    UPSTREAM = "upstream"
    TIMEOUT = "timeout"
    AUTH = "auth"


class ErrorResponse(BaseModel):
    """The typed error envelope (SDD-001 §3.2; house application-code §1).

    Every gateway rejection renders as this shape through the single exception
    handler. `error_code` carries the ErrorType member; `correlation_id` ties
    the response to its request's log line. No credential and no Tier 3/4 value
    is ever placed in `message` or `detail` — the response ceiling is Tier 2.
    """

    success: Literal[False] = False
    error_code: ErrorType
    message: str
    detail: str | None = None
    correlation_id: str | None = None
    fault_class: FaultClass | None = None
