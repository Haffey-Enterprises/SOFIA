##############################################################################
# Module: main.py
# Service: knowledge-service
# Author: Haffey Enterprises LLC
# Created: 2026-07-21
# Revised: 2026-07-23
# Description: The knowledge-service FastAPI application (SDD-001 §4.1) — app
#   construction, lifespan-owned driver wiring, the in-process schema-metadata
#   registry, correlation-ID middleware, the graph-store/schema-registry/
#   predicate-evaluator dependencies, the SDD-001 §3.2 typed-error handler, the
#   §3.1 health and readiness routes, and the §3.3 read routes (RBT-78/R3a
#   track-record-lookup, R3b resolve-technology, R3c select-patterns, R6a
#   citation-lookup, R6b provenance-of). Per SDD-001 §4.1 this module homes
#   the routes directly; this service's tree has no separate api/ layer. The
#   lifespan is the single place a Neo4j driver is opened in this platform
#   (ADR-002 §2.5) and the place the schema-metadata registry is loaded
#   (SDD-001 §3.1 check 2). citation_lookup_endpoint is the FIRST route with
#   no `predicate_evaluator` dependency at all (the audit posture, SDD-001
#   §1/§3.2, runs no trio) and the FIRST to resolve a `SettingsDep` for its
#   config-capped pagination default/clamp (R6a delta A2). provenance_of_
#   endpoint shares the no-`predicate_evaluator` posture but needs no
#   `SettingsDep` either — it is single-subject and unpaginated (P-D2), so
#   its handler is pure wire<->domain type conversion.
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
from app.domain.exceptions import GatewayError, resolve_http_status
from app.domain.retrieval.citation_lookup import citation_lookup
from app.domain.retrieval.find_precedents import find_precedents
from app.domain.retrieval.obligation_context import obligation_context
from app.domain.retrieval.provenance_of import provenance_of
from app.domain.retrieval.read_as_of import read_as_of
from app.domain.retrieval.resolve_technology import resolve_technology
from app.domain.retrieval.select_patterns import select_patterns
from app.domain.retrieval.track_record_lookup import track_record_lookup
from app.domain.retrieval.types import CitationPage, ConsumingContext
from app.domain.shared.predicate_evaluators import FailClosedPredicateEvaluator
from app.domain.shared.schema_metadata import SchemaRegistry, load_core_registry
from app.models import (
    CheckStatus,
    CitationLookupRequest,
    CitationLookupResult,
    ErrorResponse,
    FindPrecedentsRequest,
    FindPrecedentsResult,
    HealthResponse,
    ObligationContextRequest,
    ObligationContextResult,
    ProvenanceOfRequest,
    ProvenanceOfResult,
    ReadAsOfRequest,
    ReadinessResponse,
    ReadResult,
    ResolveTechnologyRequest,
    SelectPatternsRequest,
    SelectPatternsResult,
    TrackRecordLookupRequest,
)
from app.observability.correlation_id import CorrelationIdMiddleware
from app.observability.logging import configure_logging
from app.ports.graph_store import FindPrecedentsCriteria, GraphStoragePort, TargetEntityRef
from app.ports.predicate_eval import PredicateEvaluationPort

log = structlog.get_logger()

NEO4J_CONNECTIVITY_CHECK = "neo4j_connectivity"
SCHEMA_METADATA_CHECK = "schema_metadata"


@asynccontextmanager
async def lifespan(fastapi_app: FastAPI) -> AsyncIterator[None]:
    """Configure logging, open the graph driver, load schema metadata, dispose.

    Startup order matters: logging is configured before anything that might
    log; the driver and the schema-metadata registry are published on
    application state only after they are ready, so no request can reach a
    half-initialised service. The registry loads in-process from the declared
    descriptor and needs no graph, so it is independent of the instance being
    reachable or populated (ADR-004 §2.2).

    Args:
        fastapi_app: The application whose state carries the graph store and the
            schema-metadata registry.

    Yields:
        None, for the duration of the serving window.
    """
    settings = get_settings()
    configure_logging(settings.log_level)

    adapter = Neo4jAdapter(settings)
    await adapter.connect()
    fastapi_app.state.graph_store = adapter

    registry = load_core_registry()
    fastapi_app.state.schema_registry = registry
    log.info(
        "service_started",
        service=settings.service_name,
        service_version=settings.service_version,
        app_env=settings.app_env,
        schema_metadata_ready=registry.is_ready(),
    )

    try:
        yield
    finally:
        # `finally`, not a trailing statement: an abnormal shutdown that leaked
        # the driver would leak its connection pool with it.
        await adapter.close()
        fastapi_app.state.graph_store = None
        fastapi_app.state.schema_registry = None
        log.info("service_stopped", service=settings.service_name)


app = FastAPI(title="knowledge-service", lifespan=lifespan)

# Registered first so every downstream log line carries the correlation ID.
app.add_middleware(CorrelationIdMiddleware)


@app.exception_handler(GatewayError)
async def handle_gateway_error(request: Request, exc: GatewayError) -> JSONResponse:
    """Render a typed gateway rejection as the SDD-001 §3.2 error envelope.

    The single mapping point from the domain exception layer to HTTP (house
    application-code §5): the taxonomy member becomes `error_code`, its status
    is resolved from the additive map, and the request's correlation ID ties
    the response to its log line. No status codes are scattered through route
    handlers.

    Args:
        request: The inbound request, carrying the bound correlation ID.
        exc: The typed gateway rejection.

    Returns:
        The error envelope at the resolved HTTP status.
    """
    body = ErrorResponse(
        error_code=exc.error_type,
        message=exc.message,
        detail=exc.detail,
        correlation_id=getattr(request.state, "correlation_id", None),
    )
    return JSONResponse(
        content=body.model_dump(mode="json"),
        status_code=resolve_http_status(exc.error_type),
    )


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


def get_schema_registry(request: Request) -> SchemaRegistry:
    """Return the lifespan-owned schema-metadata registry for this request.

    Args:
        request: The inbound request, carrying application state.

    Returns:
        The schema-metadata registry published by the lifespan.

    Raises:
        RuntimeError: If no registry has been published, which means the
            lifespan did not complete. A readiness check that cannot find the
            registry is a startup fault, not a not-ready verdict, so this fails
            loudly rather than reporting 503.
    """
    registry: SchemaRegistry | None = getattr(request.app.state, "schema_registry", None)
    if registry is None:
        raise RuntimeError("No schema registry is available: application startup did not complete")
    return registry


def get_predicate_evaluator() -> PredicateEvaluationPort:
    """Return the production predicate-evaluation port.

    Stateless and constructed fresh per request — cheap, since
    `FailClosedPredicateEvaluator` holds no state — and lets a test override
    this dependency with a controllable double without touching the route.

    Returns:
        The production fail-closed evaluator.
    """
    return FailClosedPredicateEvaluator()


# Annotated dependencies rather than call-in-default: same wiring, and it
# keeps the module clean under ruff's B008 without suppressing the rule.
SettingsDep = Annotated[Settings, Depends(get_settings)]
GraphStoreDep = Annotated[GraphStoragePort, Depends(get_graph_store)]
SchemaRegistryDep = Annotated[SchemaRegistry, Depends(get_schema_registry)]
PredicateEvaluatorDep = Annotated[PredicateEvaluationPort, Depends(get_predicate_evaluator)]


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
    schema_registry: SchemaRegistryDep,
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

    # Check 2 — schema metadata loaded: the PlaneDefinition registry and the
    # core-plane validation metadata the write paths enforce against. Loaded
    # in-process from the declared descriptor; the gateway must not report ready
    # against metadata it could not verify (SDD-001 §3.1).
    if schema_registry.is_ready():
        checks[SCHEMA_METADATA_CHECK] = CheckStatus.OK
    else:
        checks[SCHEMA_METADATA_CHECK] = CheckStatus.UNAVAILABLE
        log.warning("readiness_check_failed", check=SCHEMA_METADATA_CHECK)

    ready = all(status is CheckStatus.OK for status in checks.values())
    body = ReadinessResponse(
        status="ok" if ready else "unavailable",
        service=settings.service_name,
        checks=checks,
    )
    return JSONResponse(content=body.model_dump(mode="json"), status_code=200 if ready else 503)


@app.post(
    "/api/v1/track-record-lookup",
    response_model=ReadResult,
    tags=["retrieval"],
)
async def track_record_lookup_endpoint(
    request: TrackRecordLookupRequest,
    graph_store: GraphStoreDep,
    predicate_evaluator: PredicateEvaluatorDep,
) -> ReadResult:
    """Operational-plane track-record-lookup (SDD-001 §3.3.3).

    Returns `ObservedPattern` lesson-reliability and `OBSERVED_IN` per-target
    certainty as uncomposed structural facts on the envelope — composing them
    is the solutioning-agent SDD's call, not this gateway's to make. The
    schema-metadata registry is not consulted here: this operation performs no
    write-path validation.

    Args:
        request: The target entities and the §3.2 consuming-context payload.
        graph_store: The graph port.
        predicate_evaluator: The predicate port (production: fail-closed).

    Returns:
        The admitted envelopes and disclosed exclusions.
    """
    target_refs = [
        TargetEntityRef(entity_kind=ref.entity_kind, entity_id=ref.entity_id)
        for ref in request.target_refs
    ]
    context = ConsumingContext(
        environment_class=request.consuming_context.environment_class,
        data_classification=request.consuming_context.data_classification,
        declared_fields=request.consuming_context.declared_fields,
    )
    return await track_record_lookup(target_refs, context, graph_store, predicate_evaluator)


@app.post(
    "/api/v1/resolve-technology",
    response_model=ReadResult,
    tags=["retrieval"],
)
async def resolve_technology_endpoint(
    request: ResolveTechnologyRequest,
    graph_store: GraphStoreDep,
    predicate_evaluator: PredicateEvaluatorDep,
) -> ReadResult:
    """Approved Technology options for a Capability (SDD-001 §3.3.2).

    Eligibility verdicts are disclosed per option (annotation, never
    exclusion, SDD-001 §4.4) — an ineligible Technology is still returned. No
    recommended pick is returned; the schema-metadata registry is not
    consulted here (this operation performs no write-path validation).

    Args:
        request: The Capability and the §3.2 consuming-context payload.
        graph_store: The graph port.
        predicate_evaluator: The predicate port (production: fail-closed).

    Returns:
        The admitted envelopes (each carrying its Catalog-eligibility verdict)
        and disclosed exclusions.
    """
    context = ConsumingContext(
        environment_class=request.consuming_context.environment_class,
        data_classification=request.consuming_context.data_classification,
        declared_fields=request.consuming_context.declared_fields,
    )
    return await resolve_technology(
        request.capability_id, context, graph_store, predicate_evaluator
    )


@app.post(
    "/api/v1/select-patterns",
    response_model=SelectPatternsResult,
    tags=["retrieval"],
)
async def select_patterns_endpoint(
    request: SelectPatternsRequest,
    graph_store: GraphStoreDep,
    predicate_evaluator: PredicateEvaluatorDep,
) -> SelectPatternsResult:
    """The selection-web read: candidate Patterns for required Capabilities
    (SDD-001 §3.3.1).

    Read-discipline applies per-node, at both the Pattern and the per-
    Capability Technology levels; PREFERRED_OVER is returned uncomposed; a
    Capability with no approved Technology is the gap signal, never an error.
    The schema-metadata registry is not consulted here (this operation
    performs no write-path validation), and this route raises no
    TARGET_NOT_FOUND — select-patterns is not that kind of op.

    Args:
        request: The required Capabilities and the §3.2 consuming-context
            payload.
        graph_store: The graph port.
        predicate_evaluator: The predicate port (production: fail-closed).

    Returns:
        The admitted candidate Patterns (with nested capabilities and
        Technology options) and the top-level pattern-level disclosures.
    """
    context = ConsumingContext(
        environment_class=request.consuming_context.environment_class,
        data_classification=request.consuming_context.data_classification,
        declared_fields=request.consuming_context.declared_fields,
    )
    return await select_patterns(request.capability_ids, context, graph_store, predicate_evaluator)


@app.post(
    "/api/v1/obligation-context",
    response_model=ObligationContextResult,
    tags=["retrieval"],
)
async def obligation_context_endpoint(
    request: ObligationContextRequest,
    graph_store: GraphStoreDep,
    predicate_evaluator: PredicateEvaluatorDep,
) -> ObligationContextResult:
    """Applicable PolicyRules for a solution's USES/FOLLOWS entity set
    (SDD-001 §3.3.4).

    Entity-triggered graph half only (GOVERNED_BY/MANDATES traversal);
    obligation closure (condition-triggered rules, the satisfaction join) is
    the constraint-validator's. The schema-metadata registry is not consulted
    here (this operation performs no write-path validation), and this route
    raises no TARGET_NOT_FOUND — an absent solution or one governed by
    nothing yields an empty result.

    Args:
        request: The solution id and the §3.2 consuming-context payload.
        graph_store: The graph port.
        predicate_evaluator: The predicate port (production: fail-closed).

    Returns:
        The admitted obligations (each with its envelope and PolicyRule
        payload) and the disclosed conditionally-excluded rules.
    """
    context = ConsumingContext(
        environment_class=request.consuming_context.environment_class,
        data_classification=request.consuming_context.data_classification,
        declared_fields=request.consuming_context.declared_fields,
    )
    return await obligation_context(request.solution_id, context, graph_store, predicate_evaluator)


@app.post(
    "/api/v1/find-precedents",
    response_model=FindPrecedentsResult,
    tags=["retrieval"],
)
async def find_precedents_endpoint(
    request: FindPrecedentsRequest,
    graph_store: GraphStoreDep,
    predicate_evaluator: PredicateEvaluatorDep,
) -> FindPrecedentsResult:
    """Prior produced Solutions matching structural criteria (SDD-001 §3.3.5).

    Deterministic structural match by shared capability/pattern/technology
    linkage, target_environment, and gate outcome — no similarity scoring, no
    ranking. The schema-metadata registry is not consulted here (this
    operation performs no write-path validation), and this route raises no
    TARGET_NOT_FOUND — an all-empty linkage criteria set, or no matching
    Solution, yields an empty result.

    Args:
        request: The structural match criteria and the §3.2 consuming-context
            payload.
        graph_store: The graph port.
        predicate_evaluator: The predicate port (production: fail-closed).

    Returns:
        The matching precedents, each with its envelope, target_environment,
        and gate-decision context.
    """
    criteria = FindPrecedentsCriteria(
        capability_ids=tuple(request.capability_ids),
        pattern_ids=tuple(request.pattern_ids),
        technology_ids=tuple(request.technology_ids),
        target_environment=request.target_environment,
        gate_outcome=request.gate_outcome,
    )
    context = ConsumingContext(
        environment_class=request.consuming_context.environment_class,
        data_classification=request.consuming_context.data_classification,
        declared_fields=request.consuming_context.declared_fields,
    )
    return await find_precedents(criteria, context, graph_store, predicate_evaluator)


@app.post(
    "/api/v1/read-as-of",
    response_model=ReadResult,
    tags=["retrieval"],
)
async def read_as_of_endpoint(
    request: ReadAsOfRequest,
    graph_store: GraphStoreDep,
    predicate_evaluator: PredicateEvaluatorDep,
) -> ReadResult:
    """Resolve a supplied version pin over versioned ground truth (SDD-001 §3.3.6).

    Pin-mode only this build (as-of-by-timestamp is deferred, RBT-83). A
    resolution miss raises `TARGET_NOT_FOUND` (handled by the existing §3.2
    exception handler) — unlike the prior read endpoints, this route can
    raise. A resolution hit still runs the full §4.4 read-discipline trio at
    read time: a currently-retracted pinned version is excluded even though
    the pin itself resolves. The schema-metadata registry is not consulted
    here (this operation performs no write-path validation).

    Args:
        request: The node_kind, business_key, version, and the §3.2
            consuming-context payload.
        graph_store: The graph port.
        predicate_evaluator: The predicate port (production: fail-closed).

    Returns:
        The `ReadResult`: 0-or-1 admitted envelope, 0-or-1 disclosures.
    """
    context = ConsumingContext(
        environment_class=request.consuming_context.environment_class,
        data_classification=request.consuming_context.data_classification,
        declared_fields=request.consuming_context.declared_fields,
    )
    return await read_as_of(
        request.node_kind,
        request.business_key,
        request.version,
        context,
        graph_store,
        predicate_evaluator,
    )


@app.post(
    "/api/v1/citation-lookup",
    response_model=CitationLookupResult,
    tags=["retrieval"],
)
async def citation_lookup_endpoint(
    request: CitationLookupRequest,
    graph_store: GraphStoreDep,
    settings: SettingsDep,
) -> CitationLookupResult:
    """The reverse cross-graph citation affordance (SDD-001 §3.3.7).

    THE DISCLOSED AUDIT EXCEPTION (§1/§3.2): deliberately reaches
    read-excluded nodes and runs none of the §4.4 trio — there is no
    `predicate_evaluator` dependency on this route at all, and the response
    is raw RG facts, never the §3.2 envelope. A retracted/superseded/
    conditional-but-existing entry's citations are returned exactly as an
    active entry's would be.

    This route performs the ONE piece of logic beyond wire<->domain
    conversion any route in this module does: resolving `limit` from the
    request against the configured pagination tunables (R6a delta A2) — an
    omitted value uses `citation_page_size_default`; a supplied value above
    `citation_page_size_max` is silently clamped, never rejected (a value
    below 1 is rejected 422 by Pydantic before this handler ever runs).

    Args:
        request: The entry pin, mode, and keyset-pagination request.
        graph_store: The graph port.
        settings: The service configuration, for the pagination tunables.

    Returns:
        The resolved citations, with per-version audit-disclosure markers.

    Raises:
        GatewayError: `SCHEMA_VIOLATION` (400) on a mode/version presence
            mismatch; `TARGET_NOT_FOUND` (404) if the entry node does not
            exist at all — handled by the existing §3.2 exception handler.
    """
    limit = (
        settings.citation_page_size_default
        if request.limit is None
        else min(request.limit, settings.citation_page_size_max)
    )
    page = CitationPage(after_evidence_id=request.after_evidence_id, limit=limit)
    return await citation_lookup(
        request.node_kind,
        request.business_key,
        request.version,
        request.mode,
        page,
        graph_store,
    )


@app.post(
    "/api/v1/provenance-of",
    response_model=ProvenanceOfResult,
    tags=["retrieval"],
)
async def provenance_of_endpoint(
    request: ProvenanceOfRequest,
    graph_store: GraphStoreDep,
) -> ProvenanceOfResult:
    """The provenance-survival affordance for one promoted node (SDD-001 §3.3.8).

    THE DISCLOSED AUDIT EXCEPTION (§1/§3.2), the audit set's second op: same
    posture as `citation_lookup_endpoint` (no `predicate_evaluator`
    dependency, no §4.4 trio), but single-subject and unpaginated — one
    specific promoted node, keyed `(node_kind, business_key, version)`. A
    retracted/superseded/conditional promoted node's provenance is returned
    exactly as an active node's would be.

    Args:
        request: The entry pin.
        graph_store: The graph port.

    Returns:
        The resolved provenance: entry markers, the originating candidate +
        governing decision, and the frozen entry set (frozen floor always,
        live overlay where extant).

    Raises:
        GatewayError: `TARGET_NOT_FOUND` (404) if the entry node does not
            exist at all, or exists but was never promoted — handled by the
            existing §3.2 exception handler.
    """
    return await provenance_of(
        request.node_kind, request.business_key, request.version, graph_store
    )
