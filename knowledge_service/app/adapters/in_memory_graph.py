##############################################################################
# Module: in_memory_graph.py
# Service: knowledge-service
# Author: Haffey Enterprises LLC
# Created: 2026-07-21
# Revised: 2026-07-21
# Description: In-memory GraphStoragePort implementation — the double every
#   knowledge-service test runs against (SDD-001 §4.2, §6). It is a first-class
#   implementation of the port, not a mock: keeping it a true substitute is
#   what lets the domain suite verify behavior without a live Neo4j, and it is
#   never omitted from coverage measurement.
##############################################################################


class InMemoryGraphStore:
    """A controllable in-memory implementation of `GraphStoragePort`.

    At RBT-77 the port's surface is the connectivity verdict alone, so that is
    all this double holds. It grows in step with the port: when RBT-78/79 add
    operations, they are implemented here in the same story as in the Neo4j
    adapter — a port method implemented on only one side would silently break
    substitutability.

    The connectivity verdict is settable in both directions so the SDD-001
    §3.1 readiness check can be exercised ready *and* not-ready without a
    database.
    """

    def __init__(self, *, connectivity_healthy: bool = True) -> None:
        """Create the double.

        Args:
            connectivity_healthy: The verdict `check_connectivity` reports
                until `set_connectivity` changes it. Defaults to healthy.
        """
        self._connectivity_healthy = connectivity_healthy
        self._check_connectivity_calls = 0

    @property
    def check_connectivity_calls(self) -> int:
        """How many times `check_connectivity` has been awaited.

        Lets a readiness test assert the check was genuinely consumed rather
        than short-circuited around.
        """
        return self._check_connectivity_calls

    def set_connectivity(self, *, healthy: bool) -> None:
        """Set the verdict subsequent connectivity checks will report.

        Args:
            healthy: True to report the store reachable and authenticated,
                False to report it unavailable.
        """
        self._connectivity_healthy = healthy

    async def check_connectivity(self) -> bool:
        """Report the configured connectivity verdict.

        Returns:
            The verdict currently set on this double.
        """
        self._check_connectivity_calls += 1
        return self._connectivity_healthy
