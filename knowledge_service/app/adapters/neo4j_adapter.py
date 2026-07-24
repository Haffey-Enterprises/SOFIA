##############################################################################
# Module: neo4j_adapter.py
# Service: knowledge-service
# Author: Haffey Enterprises LLC
# Created: 2026-07-21
# Revised: 2026-07-21
# Description: The platform's only Neo4j driver holder (ADR-002 §2.5, SDD-001
#   §4.2). At RBT-77 this is the driver-lifecycle shell alone — construction
#   from Settings, connect, connectivity/auth verification, and graceful
#   disposal. No Cypher is executed here yet; the operation-shaped transactions
#   of SDD-001 §3.3-§3.6 land in later stories. Driver-level exceptions are
#   translated at this boundary and never cross the port.
##############################################################################

from collections.abc import Callable
from typing import Any

import structlog
from neo4j import AsyncDriver, AsyncGraphDatabase

from app.config import Settings

log = structlog.get_logger()

DriverFactory = Callable[..., AsyncDriver]


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
