##############################################################################
# Module: main.py
# Service: knowledge-service
# Author: Haffey Enterprises LLC
# Created: 2026-07-21
# Revised: 2026-07-21
# Description: The knowledge-service FastAPI application (SDD-001 §4.1) — app
#   construction, lifespan-owned driver wiring, correlation-ID middleware, the
#   graph-store dependency, and the §3.1 health and readiness routes. Per
#   SDD-001 §4.1 this module homes the routes directly; this service's tree has
#   no separate api/ layer. The lifespan is the single place a Neo4j driver is
#   opened in this platform (ADR-002 §2.5).
##############################################################################

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from typing import Annotated

import structlog
from fastapi import Depends, FastAPI
from fastapi.responses import JSONResponse
from starlette.requests import Request

from app.adapters.neo4j_adapter import Neo4jAdapter
from app.config import Settings, get_settings
from app.models import CheckStatus, HealthResponse, ReadinessResponse
from app.observability.correlation_id import CorrelationIdMiddleware
from app.observability.logging import configure_logging
from app.ports.graph_store import GraphStoragePort

log = structlog.get_logger()

NEO4J_CONNECTIVITY_CHECK = "neo4j_connectivity"


@asynccontextmanager
async def lifespan(fastapi_app: FastAPI) -> AsyncIterator[None]:
    """Configure logging, open the graph driver, and dispose it on shutdown.

    Startup order matters: logging is configured before anything that might
    log, and the driver is published on application state only after it has
    been opened, so no request can reach a half-initialised store.

    Args:
        fastapi_app: The application whose state carries the graph store.

    Yields:
        None, for the duration of the serving window.
    """
    settings = get_settings()
    configure_logging(settings.log_level)

    adapter = Neo4jAdapter(settings)
    await adapter.connect()
    fastapi_app.state.graph_store = adapter
    log.info(
        "service_started",
        service=settings.service_name,
        service_version=settings.service_version,
        app_env=settings.app_env,
    )

    try:
        yield
    finally:
        # `finally`, not a trailing statement: an abnormal shutdown that leaked
        # the driver would leak its connection pool with it.
        await adapter.close()
        fastapi_app.state.graph_store = None
        log.info("service_stopped", service=settings.service_name)


app = FastAPI(title="knowledge-service", lifespan=lifespan)

# Registered first so every downstream log line carries the correlation ID.
app.add_middleware(CorrelationIdMiddleware)


def get_graph_store(request: Request) -> GraphStoragePort:
    """Return the lifespan-owned graph store for this request.

    Args:
        request: The inbound request, carrying application state.

    Returns:
        The graph store published by the lifespan, as its port type — handlers
        depend on the seam, never on the concrete adapter.

    Raises:
        RuntimeError: If no graph store has been published, which means the
            lifespan did not complete. Serving without one is never correct, so
            this fails loudly rather than degrading.
    """
    store: GraphStoragePort | None = getattr(request.app.state, "graph_store", None)
    if store is None:
        raise RuntimeError("No graph store is available: application startup did not complete")
    return store


# Annotated dependencies rather than call-in-default: same wiring, and it
# keeps the module clean under ruff's B008 without suppressing the rule.
SettingsDep = Annotated[Settings, Depends(get_settings)]
GraphStoreDep = Annotated[GraphStoragePort, Depends(get_graph_store)]


@app.get("/healthz", response_model=HealthResponse, tags=["health"])
async def healthz(settings: SettingsDep) -> HealthResponse:
    """Report process liveness (SDD-001 §3.1).

    Performs no I/O and consults no dependency: a graph outage must not take
    liveness negative, or the orchestrator would kill containers that are
    perfectly capable of recovering.

    Returns:
        The liveness response.
    """
    return HealthResponse(status="ok", service=settings.service_name)


@app.get("/readyz", tags=["health"])
async def readyz(
    settings: SettingsDep,
    graph_store: GraphStoreDep,
) -> JSONResponse:
    """Report whether the service can serve (SDD-001 §3.1).

    Checks run in the order §3.1 fixes, each critical. There is no degraded
    mode: this service has exactly one backing store and every operation
    requires it, so any failed check answers 503.

    Returns:
        A 200 response when every check passes, 503 otherwise, carrying the
        per-check outcomes either way.
    """
    checks: dict[str, CheckStatus] = {}

    # Check 1 — Neo4j connectivity and authentication.
    if await graph_store.check_connectivity():
        checks[NEO4J_CONNECTIVITY_CHECK] = CheckStatus.OK
    else:
        checks[NEO4J_CONNECTIVITY_CHECK] = CheckStatus.UNAVAILABLE
        log.warning("readiness_check_failed", check=NEO4J_CONNECTIVITY_CHECK)

    # Check 2 — schema metadata loaded (the PlaneDefinition registry and the
    # validation metadata the write paths enforce against) is NOT implemented
    # here. It lands with RBT-78's app/domain/shared/schema_metadata.py, and is
    # staged deliberately rather than stubbed: reporting a check this service
    # cannot yet perform would be the one failure mode §3.1 exists to prevent
    # ("the gateway must not execute writes it cannot validate"). Until then a
    # 200 from this endpoint attests check 1 only — and no write path exists
    # for check 2 to gate.

    ready = all(status is CheckStatus.OK for status in checks.values())
    body = ReadinessResponse(
        status="ok" if ready else "unavailable",
        service=settings.service_name,
        checks=checks,
    )
    return JSONResponse(content=body.model_dump(mode="json"), status_code=200 if ready else 503)
