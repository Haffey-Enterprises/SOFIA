##############################################################################
# Module: graph_store.py
# Service: knowledge-service
# Author: Haffey Enterprises LLC
# Created: 2026-07-21
# Revised: 2026-07-21
# Description: GraphStoragePort — the DDR-001 substitution seam (SDD-001 §4.2).
#   Domain code depends on this Protocol and never on a concrete adapter, which
#   is what makes ADR-002 §2.2's substitution contract enforceable in code:
#   Neo4jAdapter is the sole production implementation, InMemoryGraphStore
#   serves the tests, and a substitute must satisfy the DDR-001
#   Substitution-Contract Capability Bar (a port swap in code, an ADR-002
#   amendment in governance).
##############################################################################

from typing import Protocol, runtime_checkable


@runtime_checkable
class GraphStoragePort(Protocol):
    """The graph system-of-record seam the gateway's domain code depends on.

    **Day-one surface.** At RBT-77 this port declares exactly one operation:
    the connectivity and authentication verification that the `/readyz`
    readiness check consumes (SDD-001 §3.1, check 1). That is deliberate — the
    port is not a speculative sketch of the eventual graph API.

    The surface **grows additively** in RBT-78 (schema-metadata and
    validation-facing reads) and RBT-79 (the operation-shaped transactional
    writes of SDD-001 §3.3-§3.6). Additive growth is what keeps the in-memory
    double a true substitute: every method added here must be implemented by
    *both* adapters in the same story, never by the production adapter alone.
    """

    async def check_connectivity(self) -> bool:
        """Report whether the graph store is reachable and authenticated.

        This is a verdict, not a raising probe: the implementing adapter
        catches its own infrastructure exceptions and translates them here, so
        no driver-level error crosses the port boundary into domain or API
        code.

        Returns:
            True when a connection can be established and credentials are
            accepted; False otherwise.
        """
        ...
