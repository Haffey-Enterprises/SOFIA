##############################################################################
# Module: neo4j_adapter.py
# Service: knowledge-service
# Author: Haffey Enterprises LLC
# Created: 2026-07-21
# Revised: 2026-07-23
# Description: The platform's only Neo4j driver holder (ADR-002 §2.5, SDD-001
#   §4.2). At RBT-77 this was the driver-lifecycle shell alone. RBT-78/R3a added
#   the first Cypher traversal, `find_track_record` (SDD-001 §3.3.3). R3b adds
#   `resolve_technology_options` (SDD-001 §3.3.2) — the first traversal that
#   resolves REAL read-discipline structure from the graph (a Technology's
#   retraction status via RETRACTS + the governing DECIDED_ON's outcome, its
#   applicability_state, and its resolved HAS_CONDITION set), rather than a
#   fixed constant, plus (SDD-001 §3.2 v1.7.0) the raw `deprecation_date`
#   Catalog-eligibility-adjacent field. Both traversals are one single-store
#   query each (ADR-002 §6 check 4), no application-layer join, and neither
#   pre-excludes — the R2 core (app.domain.retrieval.read_discipline) is the
#   sole enforcement point. Driver-level exceptions are translated at this
#   boundary and never cross the port.
##############################################################################

from collections.abc import Callable, Sequence
from typing import Any

import structlog
from neo4j import AsyncDriver, AsyncGraphDatabase, RoutingControl

from app.config import Settings
from app.ports.graph_store import (
    ResolvedConditionRecord,
    ResolveTechnologyCandidateRecord,
    TargetEntityKind,
    TargetEntityRef,
    TrackRecordCandidateRecord,
)

log = structlog.get_logger()

DriverFactory = Callable[..., AsyncDriver]

# Each OBSERVED_IN target kind's own PK property (DDR-002 §1 `<entity>_id`;
# §2.1 Technology/Pattern/Capability, §2.2 DeploymentEnvironment).
_ID_PROPERTY_BY_KIND: dict[TargetEntityKind, str] = {
    "Technology": "technology_id",
    "Pattern": "pattern_id",
    "Capability": "capability_id",
    "DeploymentEnvironment": "environment_id",
}

# One traversal (ADR-002 §6 check 4): every active ObservedPattern OBSERVED_IN
# any requested target. `status = 'active'` excludes superseded/resolved/
# archived lessons — not current ground truth (DDR-002 §2.3) — a plane-level
# data-quality filter, distinct from and layered on top of the R2 read-
# discipline trio (which this query never applies; SDD-001 §4.4 is the core's
# job alone).
_TRACK_RECORD_QUERY = """
UNWIND $target_refs AS ref
MATCH (target)
WHERE ref.entity_kind IN labels(target) AND target[ref.id_property] = ref.entity_id
MATCH (op:Operational:ObservedPattern)-[edge:OBSERVED_IN]->(target)
WHERE op.status = 'active'
RETURN
  op.observed_pattern_id AS node_id,
  op.origin_mechanism AS origin_mechanism,
  op.derivation_class AS derivation_class,
  op.confidence AS node_confidence,
  edge.confidence AS edge_confidence,
  op.first_observed_at AS first_observed_at,
  op.last_observed_at AS last_observed_at
"""

# One traversal (ADR-002 §6 check 4): every Technology APPROVED_OPTION_FOR the
# requested Capability, with its real read-discipline structure resolved
# alongside — never pre-excluded (SDD-001 §4.4 is the R2 core's job alone).
#
# Retraction (#21): existence, not governance. DDR-002 §2.4 states #21
# explicitly "traces to an approving decision, not the governing one" — the
# opposite of #15's promoted-origin rule (below), which keys off the
# GOVERNING (latest decided_at) decision. retracted is therefore an EXISTS{}
# existential subquery: true iff at least one retraction CandidatePromotion
# RETRACTS this tech with at least one approving DECIDED_ON edge, regardless of
# any later re-decision's outcome. A boolean subquery cannot multiply the
# outer row — exactly one row per tech either way (review fix: the prior
# ORDER BY/collect[0] "governing retraction" form was both fail-open — a later
# non-approving re-decision could flip a validly-retracted node back to
# admitted — and wrong on its own terms, since DDR-002 never governs
# retraction validity by latest decided_at at all).
#
# Conditional (#19): a promoted Technology's HAS_CONDITION set is scoped to
# the decision that is BOTH approving AND governing (latest decided_at among
# approving PROMOTES_TO_KNOWLEDGE-reachable decisions for this tech) — the
# CALL{} subquery resolves that one decision first (ORDER BY decided_at DESC
# LIMIT 1, filtered to approving outcomes), then collects only ITS
# HAS_CONDITION set. This is what keeps a superseded earlier decision's
# conditions from leaking once a later approving re-decision has re-scoped or
# cleared them (review fix: the prior form collected HAS_CONDITION from ANY
# approving-or-not decision, unscoped).
#
# decided_at lives on the (:Governance:Decision) NODE, not the DECIDED_ON edge
# (DDR-002 §2.4's Decision property list) — review fix: the prior form read it
# off the edge variable, which carries only {outcome} (§3), so the old ORDER
# BY was silently comparing nulls.
#
# Deprecation notice (SDD-001 §3.2 v1.7.0): tech.deprecation_date is returned
# as-is (ISO string or null) — the operation derives `deprecated` from its
# mere presence, never a comparison against the read clock. approval_status is
# deliberately NOT read: its value-set is unratified in DDR-002.
_RESOLVE_TECHNOLOGY_QUERY = """
MATCH (cap:Catalog:Capability {capability_id: $capability_id})
MATCH (tech:Catalog:Technology)-[:APPROVED_OPTION_FOR]->(cap)
CALL {
  WITH tech
  OPTIONAL MATCH (promotion:Reasoning:CandidatePromotion {proposal_kind: 'promotion'})
    -[:PROMOTES_TO_KNOWLEDGE]->(tech)
  OPTIONAL MATCH (promotion)<-[decided:DECIDED_ON]-(decision:Governance:PromotionDecision)
  WHERE decided.outcome IN ['approved', 'approved_conditional']
  WITH decision
  ORDER BY decision.decided_at DESC
  LIMIT 1
  OPTIONAL MATCH (decision)-[:HAS_CONDITION]->(condition:Governance:Condition)
  RETURN collect(DISTINCT condition) AS governing_conditions
}
RETURN
  tech.technology_id AS node_id,
  tech.version AS version,
  tech.origin_mechanism AS origin_mechanism,
  tech.derivation_class AS derivation_class,
  tech.tier_applicability AS tier_applicability,
  tech.approved_data_classifications AS approved_data_classifications,
  tech.applicability_state AS applicability_state,
  tech.deprecation_date AS deprecation_date,
  EXISTS {
    MATCH (retraction:Reasoning:CandidatePromotion {proposal_kind: 'retraction'})
      -[:RETRACTS]->(tech)
    MATCH (retraction)<-[retraction_decided:DECIDED_ON]-(:Governance:PromotionDecision)
    WHERE retraction_decided.outcome IN ['approved', 'approved_conditional']
  } AS retracted,
  [c IN governing_conditions WHERE c IS NOT NULL |
    {predicate: c.predicate, dependency_manifest: c.dependency_manifest}] AS conditions
"""


class Neo4jAdapter:
    """The Neo4j-backed implementation of `GraphStoragePort`.

    Construction is inert: it records configuration and opens nothing. The
    driver is created by `connect`, which the application lifespan calls at
    startup, and released by `close` at shutdown — so a constructed-but-unused
    adapter never holds a connection pool.

    The driver is deliberately injectable so unit tests can mock at this
    boundary; no test in this service connects to a live Neo4j (SDD-001 §6).
    """

    def __init__(self, settings: Settings, *, driver_factory: DriverFactory | None = None) -> None:
        """Record configuration for a driver that is not yet opened.

        Args:
            settings: The service configuration carrying the Neo4j URI,
                credentials, and pool sizing (SDD-001 §4.6).
            driver_factory: Builder for the underlying driver. Defaults to the
                real `AsyncGraphDatabase.driver`; tests inject a double.
        """
        self._settings = settings
        self._driver_factory = driver_factory
        self._driver: AsyncDriver | None = None

    def _build_driver(self, *args: Any, **kwargs: Any) -> AsyncDriver:
        """Build a driver via the injected factory, or the real one by default.

        Resolved at call time rather than in `__init__` so a test that patches
        the neo4j entry point still takes effect on an already-constructed
        adapter.
        """
        factory = self._driver_factory or AsyncGraphDatabase.driver
        return factory(*args, **kwargs)

    async def connect(self) -> None:
        """Open the driver if it is not already open.

        Idempotent: a second call is a no-op rather than a second connection
        pool. The credential is read out of its `SecretStr` here and nowhere
        else — this is the single point at which the plain value exists.
        """
        if self._driver is not None:
            return

        self._driver = self._build_driver(
            self._settings.neo4j_uri,
            auth=(
                self._settings.neo4j_username,
                self._settings.neo4j_password.get_secret_value(),
            ),
            max_connection_pool_size=self._settings.neo4j_max_connection_pool_size,
            connection_acquisition_timeout=(
                self._settings.neo4j_connection_acquisition_timeout_seconds
            ),
        )
        log.info(
            "neo4j_driver_opened",
            neo4j_uri=self._settings.neo4j_uri,
            neo4j_database=self._settings.neo4j_database,
        )

    async def check_connectivity(self) -> bool:
        """Verify the graph store is reachable and the credentials are accepted.

        Authentication failure is not a distinct condition here: SDD-001 §3.1
        makes connectivity *and* authentication one readiness check, so both
        resolve to the same negative verdict.

        Returns:
            True when the driver verifies; False when it is not open, or when
            verification fails for any reason.
        """
        if self._driver is None:
            log.warning("neo4j_connectivity_check_failed", reason="driver_not_open")
            return False

        try:
            await self._driver.verify_connectivity()
        except Exception as exc:
            # A readiness probe must not itself become a failure mode, so every
            # driver-level error is translated to the port's negative verdict.
            # Only the exception's class is logged: a driver message can echo
            # connection detail, and the log ceiling is Tier 2.
            log.warning(
                "neo4j_connectivity_check_failed",
                reason="verification_failed",
                error_type=type(exc).__name__,
            )
            return False

        return True

    async def close(self) -> None:
        """Dispose the driver if one is open.

        Idempotent, so shutdown is safe whether or not startup completed.
        """
        if self._driver is None:
            return

        await self._driver.close()
        self._driver = None
        log.info("neo4j_driver_closed")

    async def find_track_record(
        self, target_refs: Sequence[TargetEntityRef]
    ) -> Sequence[TrackRecordCandidateRecord]:
        """Resolve Operational-plane track record for the given target entities.

        One single-store Cypher traversal (ADR-002 §6 check 4). Structural
        match only — no read-discipline exclusion happens here (SDD-001 §4.4
        is the R2 core's job alone).

        Args:
            target_refs: The target entities to look up track record for.

        Returns:
            One `TrackRecordCandidateRecord` per matching `ObservedPattern` x
            target pair.

        Raises:
            RuntimeError: If no driver is open — a data operation with no
                driver must fail loud, never silently return an empty (and
                misleading) track record.
        """
        if self._driver is None:
            raise RuntimeError("No graph driver is open: application startup did not complete")

        params = [
            {
                "entity_kind": ref.entity_kind,
                "id_property": _ID_PROPERTY_BY_KIND[ref.entity_kind],
                "entity_id": ref.entity_id,
            }
            for ref in target_refs
        ]
        result = await self._driver.execute_query(
            _TRACK_RECORD_QUERY,
            {"target_refs": params},
            routing_=RoutingControl.READ,
            database_=self._settings.neo4j_database,
        )
        return [
            TrackRecordCandidateRecord(
                node_id=record["node_id"],
                origin_mechanism=record["origin_mechanism"],
                derivation_class=record["derivation_class"],
                node_confidence=record["node_confidence"],
                edge_confidence=record["edge_confidence"],
                first_observed_at=record["first_observed_at"],
                last_observed_at=record["last_observed_at"],
            )
            for record in result.records
        ]

    async def resolve_technology_options(
        self, capability_id: str
    ) -> Sequence[ResolveTechnologyCandidateRecord]:
        """Resolve approved Technology options for the given Capability.

        One single-store Cypher traversal (ADR-002 §6 check 4), resolving the
        real read-discipline structure alongside — no read-discipline
        exclusion happens here (SDD-001 §4.4 is the R2 core's job alone).

        Args:
            capability_id: The Capability to resolve approved options for.

        Returns:
            One `ResolveTechnologyCandidateRecord` per approved Technology
            option.

        Raises:
            RuntimeError: If no driver is open — a data operation with no
                driver must fail loud, never silently return an empty (and
                misleading) result.
        """
        if self._driver is None:
            raise RuntimeError("No graph driver is open: application startup did not complete")

        result = await self._driver.execute_query(
            _RESOLVE_TECHNOLOGY_QUERY,
            {"capability_id": capability_id},
            routing_=RoutingControl.READ,
            database_=self._settings.neo4j_database,
        )
        return [
            ResolveTechnologyCandidateRecord(
                node_id=record["node_id"],
                version=record["version"],
                origin_mechanism=record["origin_mechanism"],
                derivation_class=record["derivation_class"],
                tier_applicability=tuple(record["tier_applicability"] or ()),
                approved_data_classifications=tuple(record["approved_data_classifications"] or ()),
                applicability_state=record["applicability_state"] or "unconditional",
                retracted=record["retracted"],
                deprecation_date=record["deprecation_date"],
                conditions=tuple(
                    ResolvedConditionRecord(
                        predicate=condition["predicate"],
                        required_context_fields=frozenset(condition["dependency_manifest"] or ()),
                    )
                    for condition in record["conditions"]
                ),
            )
            for record in result.records
        ]
