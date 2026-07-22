##############################################################################
# Module: correlation_id.py
# Service: knowledge-service
# Author: Haffey Enterprises LLC
# Created: 2026-07-21
# Revised: 2026-07-21
# Description: Correlation-ID middleware. SDD-001 §8 requires `correlation_id`
#   on every structured log event and end-to-end propagation across the
#   platform; this middleware is where the ID enters the process — minted when
#   the caller supplies none, honoured when they do — and is bound into the
#   structlog context so every line emitted while serving the request carries
#   it without any call site having to pass it along.
##############################################################################

import uuid

import structlog
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response

CORRELATION_ID_HEADER = "X-Correlation-ID"


class CorrelationIdMiddleware(BaseHTTPMiddleware):
    """Bind a correlation ID for the lifetime of each request.

    Registered first in the middleware stack so that everything downstream —
    routing, handlers, exception handlers — logs under the bound ID.
    """

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        """Mint or accept the correlation ID, bind it, and echo it back.

        Args:
            request: The inbound request.
            call_next: The remainder of the middleware/route chain.

        Returns:
            The downstream response, with the correlation ID on its headers.
        """
        correlation_id = request.headers.get(CORRELATION_ID_HEADER) or str(uuid.uuid4())

        # Cleared first: contextvars can survive on a reused worker task, and a
        # stale ID on a new request is worse than none.
        structlog.contextvars.clear_contextvars()
        structlog.contextvars.bind_contextvars(correlation_id=correlation_id)
        request.state.correlation_id = correlation_id

        response = await call_next(request)
        response.headers[CORRELATION_ID_HEADER] = correlation_id
        return response
