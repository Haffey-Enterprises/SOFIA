##############################################################################
# Module: app/domain/exceptions.py
# Service: knowledge-service
# Author: Haffey Enterprises LLC
# Created: 2026-07-23
# Revised: 2026-07-23
# Description: Domain exception hierarchy for knowledge-service (house
#   application-code standard §5; SDD-001 §3.2 error semantics). `DomainError`
#   is the base every domain-layer exception extends; `GatewayError` is the
#   single typed rejection the gateway raises, carrying one member of the
#   SDD-001 §3.2 error taxonomy (`ErrorType`, defined in app.models as the wire
#   vocabulary). The taxonomy is enumerated whole there; the HTTP-status map
#   below grows additively — a type gains its status when the operation that
#   raises it is built. RBT-78 seeded TARGET_NOT_FOUND (the read-side miss,
#   ratified per the point-2b disposition); R6a adds SCHEMA_VIOLATION -> 400,
#   its FIRST raising site being READ-side (citation-lookup's mode/version
#   pairing rule, SDD-001 §3.3.7 D3) rather than write-side — a client-caused
#   contract violation rendered through this same typed-rejection path, not
#   FastAPI body validation (operator-ratified, RBT-78 R6a delta A1). The
#   additive rule itself is unchanged: every other type maps when its raising
#   site lands (RBT-79+).
##############################################################################

from app.models import ErrorType


class DomainError(Exception):
    """Base for knowledge-service domain-layer exceptions.

    Domain code raises subclasses of this; the API layer maps them to the
    SDD-001 §3.2 error envelope through a single FastAPI exception handler
    (house application-code §5) — status codes are never scattered through
    route handlers.
    """


class GatewayError(DomainError):
    """A typed gateway rejection — one member of the SDD-001 §3.2 taxonomy.

    One exception type carries the whole taxonomy through its `error_type`
    member, rather than a class per type: the taxonomy is a closed, ratified
    vocabulary (SDD-001 §3.2) whose single source is the `ErrorType` enum
    (app.models). The handler renders `error_type` as the response
    `error_code` and resolves its HTTP status through `resolve_http_status`.
    """

    def __init__(self, error_type: ErrorType, message: str, *, detail: str | None = None) -> None:
        """Create a typed gateway rejection.

        Args:
            error_type: The taxonomy member this rejection carries.
            message: A human-readable statement of the rejection, safe to
                surface — no credential and no Tier 3/4 value (the response and
                log ceiling is Tier 2).
            detail: Optional additional context for the response body.
        """
        self.error_type = error_type
        self.message = message
        self.detail = detail
        super().__init__(message)


# The internal-defect fallback: a GatewayError whose type carries no status
# mapping was raised without its status being declared — a build error, not a
# client error. Fail loud as 500 rather than guess a 4xx.
_DEFAULT_STATUS = 500

# ErrorType -> HTTP status. Grows additively: a type is added here when the
# operation that raises it is built. RBT-78 raises TARGET_NOT_FOUND
# (SDD-001 §3.3 explicit-subject / supplied-pin misses; the point-2b
# disposition) and, from R6a, SCHEMA_VIOLATION (citation-lookup's mode/version
# presence-mismatch rule, SDD-001 §3.3.7 D3) — a client-caused contract
# violation, 400, not the FastAPI 422 body-validation path. Every other member
# gains its status with its own raising site (RBT-79+).
_HTTP_STATUS_BY_ERROR_TYPE: dict[ErrorType, int] = {
    ErrorType.TARGET_NOT_FOUND: 404,
    ErrorType.SCHEMA_VIOLATION: 400,
}


def resolve_http_status(error_type: ErrorType) -> int:
    """Resolve the HTTP status for a taxonomy member.

    Args:
        error_type: The taxonomy member to map.

    Returns:
        The declared HTTP status, or `_DEFAULT_STATUS` (500) when the type
        carries no mapping yet — an unmapped raised type is a build defect, so
        the fallback fails loud rather than inventing a 4xx.
    """
    return _HTTP_STATUS_BY_ERROR_TYPE.get(error_type, _DEFAULT_STATUS)
