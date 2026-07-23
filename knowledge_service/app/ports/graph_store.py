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
#   amendment in governance). RBT-78/R3a added the first §3.3 read method,
#   `find_track_record`. R3b adds `resolve_technology_options` — the first
#   method whose candidates carry REAL read-discipline structure (a `Technology`
#   can be promoted-conditional or retracted, unlike `ObservedPattern`'s fixed
#   constants): the retraction status, `applicability_state`, and the resolved
#   `Condition` set travel on its record, for the R2 core to enforce. Both are
#   one named, single-store traversal per operation (ADR-002 §6 check 4: no
#   application-layer join), never a generic/raw query surface (SDD-001 §3.2
#   "No raw access").
##############################################################################

from collections.abc import Mapping, Sequence
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


@dataclass(frozen=True)
class ResolvedConditionRecord:
    """One resolved `HAS_CONDITION` path for a candidate node (port-level).

    Structurally identical to `app.domain.retrieval.types.ConditionRef`, but
    declared separately here so the port stays domain-agnostic (adapters must
    not import from `domain/retrieval`). `predicate` is opaque — DDR-003's
    grammar, not interpreted here or by any operation; `required_context_fields`
    is read directly off the `Condition.dependency_manifest` property, assumed
    to already be a flat list of field names (DDR-002 names it "declared-
    introspectable" but does not fix an internal shape beyond that).
    """

    predicate: Mapping[str, object]
    required_context_fields: frozenset[str]


@dataclass(frozen=True)
class ResolveTechnologyCandidateRecord:
    """One `Technology` APPROVED_OPTION_FOR the requested `Capability` (SDD-001
    §3.3.2).

    The raw structural facts `resolve_technology_options` resolves per
    candidate — port-level data, not a `CandidateNode` (same separation as
    `TrackRecordCandidateRecord`). Unlike track-record-lookup's fixed constants,
    `retracted`/`applicability_state`/`conditions` here are REAL, traversal-
    determined values (R3b D1): a `Technology` can genuinely be promoted-
    conditional or retracted, so the traversal must resolve them from the graph
    rather than assume a fixed answer.

    `tier_applicability`/`approved_data_classifications` are the raw DDR-002
    §2.1 Catalog-eligibility fields — the operation computes the eligibility
    verdict from them (app.domain.shared.catalog_eligibility); this record
    carries the inputs, not the verdict.

    `applicability_state` defaults to `"unconditional"` at the adapter when the
    graph property is absent — DDR-002 §5 states `unconditional` is the
    schema's own default for a node with no promotion-conditional history.

    `deprecation_date` (SDD-001 §3.2 v1.7.0) is the raw `deprecation_date`
    property (ISO date string, or `None` when absent) — the operation derives
    the `deprecated` marker from its mere presence, never from a comparison
    against the read clock. `approval_status` is deliberately not read at all:
    its value-set is unratified in DDR-002, so keying on it would encode an
    unpinned literal.
    """

    node_id: str
    version: str
    origin_mechanism: str
    derivation_class: str | None
    tier_applicability: tuple[str, ...]
    approved_data_classifications: tuple[str, ...]
    applicability_state: Literal["unconditional", "conditional"]
    retracted: bool
    conditions: tuple[ResolvedConditionRecord, ...]
    deprecation_date: str | None = None


@dataclass(frozen=True)
class CapabilityBlockRecord:
    """One requested Capability a candidate Pattern REQUIRES_CAPABILITY, with its
    taxonomy placement (DDR-002 §2.1) and the approved Technology options
    resolved for it (SDD-001 §3.3.1) — port-level facts, not domain types.
    Reuses `ResolveTechnologyCandidateRecord`: an approved Technology option here
    is structurally identical to a resolve-technology candidate, so the operation
    maps it through the same path (shared guard + catalog_eligibility +
    deprecation)."""

    capability_id: str
    l1_taxonomy: str | None
    l2_taxonomy: str | None
    l3_taxonomy: str | None
    technology_options: tuple[ResolveTechnologyCandidateRecord, ...]


@dataclass(frozen=True)
class SelectPatternsCandidateRecord:
    """One candidate `Pattern` REQUIRES_CAPABILITY at least one requested
    Capability (SDD-001 §3.3.1). Port-level facts, not a `CandidateNode`. A
    Pattern is Catalog ground truth — genuinely promotable-conditional or
    retractable (like Technology, unlike an ObservedPattern), so it carries its
    OWN real read-discipline structure (`retracted`, `applicability_state`,
    resolved `conditions`) for the R2 core to enforce; the traversal resolves
    them, never assumes them. `capabilities` carries one block per requested
    Capability this Pattern requires; `preferred_over` is the pattern_ids this
    Pattern is PREFERRED_OVER (uncomposed)."""

    node_id: str
    version: str
    origin_mechanism: str
    derivation_class: str | None
    applicability_state: Literal["unconditional", "conditional"]
    retracted: bool
    conditions: tuple[ResolvedConditionRecord, ...]
    capabilities: tuple[CapabilityBlockRecord, ...]
    preferred_over: tuple[str, ...]


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

    async def resolve_technology_options(
        self, capability_id: str
    ) -> Sequence[ResolveTechnologyCandidateRecord]:
        """Resolve approved Technology options for the given Capability.

        One single-store traversal (ADR-002 §6 check 4): every `Technology`
        APPROVED_OPTION_FOR the requested `Capability`, with its real
        read-discipline structure (retraction status, `applicability_state`,
        resolved `Condition` set) resolved alongside — never pre-excluded here.
        Performs no read-discipline exclusion and no eligibility computation
        itself; both are the operation's job (the R2 core, and
        app.domain.shared.catalog_eligibility, respectively).

        Args:
            capability_id: The Capability to resolve approved options for.

        Returns:
            One `ResolveTechnologyCandidateRecord` per approved Technology
            option.
        """
        ...

    async def select_patterns(
        self, capability_ids: Sequence[str]
    ) -> Sequence[SelectPatternsCandidateRecord]:
        """Resolve candidate Patterns for the given required Capabilities.

        One single-store traversal (ADR-002 §6 check 4): every `Pattern`
        REQUIRES_CAPABILITY any requested Capability, with its own read-discipline
        structure resolved, and per requested Capability the taxonomy placement
        plus every `Technology` APPROVED_OPTION_FOR it (each carrying its real
        read-discipline structure + Catalog-eligibility inputs + deprecation_date),
        plus the PREFERRED_OVER pattern_ids. Performs no read-discipline exclusion
        and no eligibility computation itself — both are the operation's job.

        Args:
            capability_ids: The required Capabilities to resolve candidate
                Patterns for.

        Returns:
            One `SelectPatternsCandidateRecord` per candidate Pattern.
        """
        ...
