##############################################################################
# Module: neo4j_adapter.py
# Service: knowledge-service
# Author: Haffey Enterprises LLC
# Created: 2026-07-21
# Revised: 2026-07-21
# Description: The platform's only Neo4j driver holder (ADR-002 §2.5, SDD-001
#   §4.2). At RBT-77 this was the driver-lifecycle shell alone. RBT-78/R3a adds
#   the first Cypher traversal, `find_track_record` (SDD-001 §3.3.3) — one
#   single-store query (ADR-002 §6 check 4), no application-layer join. It does
#   structural-match only: it populates raw facts (node/edge confidence,
#   observation window), never read-discipline exclusion — the R2 core
#   (app.domain.retrieval.read_discipline) is the sole enforcement point.
#   Driver-level exceptions are translated at this boundary and never cross
#   the port.
##############################################################################

from collections.abc import Callable, Sequence
from typing import Any

import structlog
from neo4j import AsyncDriver, AsyncGraphDatabase, RoutingControl

from app.config import Settings
from app.ports.graph_store import TargetEntityKind, TargetEntityRef, TrackRecordCandidateRecord

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
