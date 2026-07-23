##############################################################################
# Module: graph_store.py
# Service: knowledge-service
# Author: Haffey Enterprises LLC
# Created: 2026-07-21
# Revised: 2026-07-23
# Description: GraphStoragePort — the DDR-001 substitution seam (SDD-001 §4.2).
#   Domain code depends on this Protocol and never on a concrete adapter, which
#   is what makes ADR-002 §2.2's substitution contract enforceable in code:
#   Neo4jAdapter is the sole production implementation, InMemoryGraphStore
#   serves the tests, and a substitute must satisfy the DDR-001
#   Substitution-Contract Capability Bar (a port swap in code, an ADR-002
#   amendment in governance). RBT-78/R3a adds the first §3.3 read method,
#   `find_track_record` — one named, single-store traversal per operation
#   (ADR-002 §6 check 4: no application-layer join), never a generic/raw query
#   surface (SDD-001 §3.2 "No raw access").
##############################################################################

from collections.abc import Sequence
from dataclasses import dataclass
from typing import Literal, Protocol, runtime_checkable

# The four node types an OBSERVED_IN edge targets (DDR-002 §3), each with its
# own PK property name (DDR-002 §1 `<entity>_id`, §2.1/§2.2).
TargetEntityKind = Literal["Technology", "Pattern", "Capability", "DeploymentEnvironment"]


@dataclass(frozen=True)
class TargetEntityRef:
    """One target entity to look up Operational-plane track record for.

    `entity_kind` is the target's label (also the OBSERVED_IN edge's target
    type, DDR-002 §3); `entity_id` is that label's own PK value — the four
    kinds do not share an ID namespace.
    """

    entity_kind: TargetEntityKind
    entity_id: str


@dataclass(frozen=True)
class TrackRecordCandidateRecord:
    """One `ObservedPattern` OBSERVED_IN a requested target (SDD-001 §3.3.3).

    The raw structural facts `find_track_record` resolves per candidate —
    deliberately NOT a `CandidateNode` (app.domain.retrieval.types): the port
    returns port-level data, never a domain type, so adapters stay
    domain-agnostic. The operation maps this into a `CandidateNode`.

    `node_confidence` is the `ObservedPattern`'s own lesson-reliability
    `confidence` (DDR-002 §2.3/§4); `edge_confidence` is the OBSERVED_IN edge's
    per-target observation certainty (DDR-002 §3) — the two are returned
    uncomposed (SDD-001 §3.3.3): composing them is the solutioning-agent SDD's
    call, not this gateway's to make. Both are optional (R3a review finding):
    DDR-002 §7's DB-enforced existence constraints cover only the provenance
    group and T1 properties, `confidence` is T2 on both surfaces, and no CI
    check (#1-28) guarantees its presence on `ObservedPattern` or
    `OBSERVED_IN` — unlike `Evidence.confidence`, which check #28 exists
    specifically to cover. A null is carried honestly, never defaulted.

    No read-discipline flags travel on this record. `ObservedPattern` is
    always `origin_mechanism: derived` (DDR-002 §2.3) — never `promoted` — so
    it structurally cannot be an un-approved `CandidatePromotion` (#9, a
    distinct label), cannot carry `applicability_state`/`HAS_CONDITION` (§5,
    exclusive to nodes materialized via `PROMOTES_TO_KNOWLEDGE`), and cannot be
    a `RETRACTS` target (§7 #21, which un-promotes a promoted fact). The
    operation checks `origin_mechanism` against that invariant and supplies
    the flags as fixed values when it holds, excluding the record when it
    does not — never taken on faith from this record alone.
    """

    node_id: str
    origin_mechanism: str
    derivation_class: str | None
    node_confidence: float | None
    edge_confidence: float | None
    first_observed_at: str | None
    last_observed_at: str | None


@runtime_checkable
class GraphStoragePort(Protocol):
    """The graph system-of-record seam the gateway's domain code depends on.

    **Day-one surface.** At RBT-77 this port declared exactly one operation:
    the connectivity and authentication verification that the `/readyz`
    readiness check consumes (SDD-001 §3.1, check 1). That is deliberate — the
    port is not a speculative sketch of the eventual graph API.

    The surface **grows additively**: RBT-78/R3a adds `find_track_record`, the
    first §3.3 read method. Additive growth is what keeps the in-memory double
    a true substitute: every method added here must be implemented by *both*
    adapters in the same story, never by the production adapter alone.
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

    async def find_track_record(
        self, target_refs: Sequence[TargetEntityRef]
    ) -> Sequence[TrackRecordCandidateRecord]:
        """Resolve Operational-plane track record for the given target entities.

        One single-store traversal (ADR-002 §6 check 4): every `ObservedPattern`
        OBSERVED_IN any of the requested targets, active only (a superseded/
        resolved/archived lesson is not current ground truth). Performs no
        read-discipline exclusion itself — that is the R2 core's sole job
        (SDD-001 §4.4); this method returns raw structural facts only.

        Args:
            target_refs: The target entities to look up track record for.

        Returns:
            One `TrackRecordCandidateRecord` per matching `ObservedPattern` x
            target pair.
        """
        ...
