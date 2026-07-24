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
#   "No raw access"). R6a adds `citation_lookup` (SDD-001 §3.3.7) — the
#   platform's FIRST audit-posture read: it deliberately reaches
#   read-excluded nodes and returns raw RG facts, never a `CandidateNode`, so
#   its record types (`CitationRecord`/`CitationLookupPage`/
#   `CitationEntryStatusRecord`) carry no read-discipline fields at all — there
#   is no trio for this op to enforce. It is also the FIRST paginated method:
#   `CitationLookupPage` carries a keyset cursor (`next_cursor`), and callers
#   pass an already-resolved `limit` (config-default-substituted, hard-capped)
#   rather than a raw request value. R6b adds `provenance_of` (SDD-001 §3.3.8)
#   — the audit set's SECOND op, same posture as `citation_lookup`, but
#   single-subject and unpaginated (P-D2: one promoted node, keyed
#   `(node_kind, business_key, version)`, its Evidence-span frozen set
#   returned whole). Reuses `CitationEntryStatusRecord`'s three-marker
#   vocabulary for its own entry markers (the identical audit-disclosure set,
#   not a new one) and `ReadAsOfNodeKind` for the entry-node label.
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


@dataclass(frozen=True)
class ObligationCandidateRecord:
    """One `PolicyRule` applicable to a solution's `USES`/`FOLLOWS` entity set
    via `GOVERNED_BY`/`MANDATES` (SDD-001 §3.3.4). Port-level facts, not a
    `CandidateNode`. A `PolicyRule` is Standards ground truth — genuinely
    promotable-conditional or retractable, so it carries its OWN real
    read-discipline structure (`retracted`, `applicability_state`, resolved
    `conditions`) for the R2 core to enforce, resolved by the traversal, never
    assumed.

    The remaining fields are the rule's content payload: `statement` and
    `rule_definition` (opaque — never parsed here), `dependency_manifest`
    (declared, introspectable Catalog entity-type labels), `enforcement_level`,
    `enforced_at_gate`, and `domain`.
    """

    node_id: str
    version: str
    origin_mechanism: str
    derivation_class: str | None
    applicability_state: Literal["unconditional", "conditional"]
    retracted: bool
    conditions: tuple[ResolvedConditionRecord, ...]
    statement: str | None
    rule_definition: str | None
    dependency_manifest: tuple[str, ...]
    enforcement_level: str | None
    enforced_at_gate: str | None
    domain: str | None


@dataclass(frozen=True)
class FindPrecedentsCriteria:
    """The structural match criteria for find-precedents (SDD-001 §3.3.5).

    Matching is AND-across the non-empty dimensions here and OR-within a
    given dimension's own list — an empty tuple on any one dimension is a
    no-op filter on that dimension, never a rejection. Capability linkage is
    the 2-hop `FOLLOWS` ∘ `REQUIRES_CAPABILITY` path only (DDR-001's gap
    model: the capability a Solution's Pattern *requires*, distinct from
    what its Technology choices *resolve*).
    """

    capability_ids: tuple[str, ...]
    pattern_ids: tuple[str, ...]
    technology_ids: tuple[str, ...]
    target_environment: str | None
    gate_outcome: str | None


@dataclass(frozen=True)
class GateDecisionRecord:
    """One `GateDecision` on a candidate precedent Solution (port-level).

    Structurally identical to `app.models.GateDecisionContext`, but declared
    separately here so the port stays domain-agnostic.
    """

    outcome: str
    gate: str | None
    decision_id: str | None


@dataclass(frozen=True)
class FindPrecedentsCandidateRecord:
    """One prior produced `(:Artifact:Solution)` matching the requested
    structural criteria (SDD-001 §3.3.5). Port-level facts, not a
    `CandidateNode`.

    Carries no read-discipline flags: a Solution is an Artifact (DDR-002 §5)
    — it carries no KG plane label and is never a promotion/conditional/
    retraction subject, so the operation supplies fixed read-discipline
    constants rather than reading them from this record (unlike
    `ResolveTechnologyCandidateRecord`/`SelectPatternsCandidateRecord`/
    `ObligationCandidateRecord`, whose flags are REAL traversal-resolved
    values). `origin_mechanism` is carried so the operation can verify the
    Solution invariant (`authored`, §5) as a local, fail-closed defense-in-
    depth check.
    """

    node_id: str
    version: str
    origin_mechanism: str
    target_environment: str | None
    gate_decisions: tuple[GateDecisionRecord, ...]


# The 6 versioned Catalog+Standards labels read-as-of resolves (SDD-001
# §3.3.6, pin-mode). `ComplianceControl` is excluded — it carries no
# `version` property (DDR-002 §2.5) — and as-of-by-timestamp resolution is
# out of scope for this build; both are routed to RBT-83.
ReadAsOfNodeKind = Literal[
    "Pattern",
    "Technology",
    "Capability",
    "IacTemplate",
    "Standard",
    "PolicyRule",
]


@dataclass(frozen=True)
class ReadAsOfResolvedRecord:
    """One versioned-ground-truth node resolved by a supplied version pin
    (SDD-001 §3.3.6). Port-level facts, not a `CandidateNode`.

    `node_id` is the `business_key` PK value; `version` is the resolved
    (pinned) version, echoed back rather than re-derived. Like
    `ResolveTechnologyCandidateRecord`/`SelectPatternsCandidateRecord`/
    `ObligationCandidateRecord`, `applicability_state`/`retracted`/
    `conditions` are REAL, traversal-resolved read-discipline structure —
    read-as-of enforces the trio at read time even though the pin resolves a
    specific (possibly superseded, possibly retracted) version. `effective_from`
    is populated only for the one label that declares it (`Pattern`, DDR-002
    §2.1); `effective_to` is always `None` — no in-scope label declares it
    (the as-of-by-timestamp window is out of scope this build, RBT-83).
    """

    node_id: str
    plane_labels: tuple[str, ...]
    version: str
    origin_mechanism: str
    derivation_class: str | None
    effective_from: str | None
    effective_to: str | None
    applicability_state: Literal["unconditional", "conditional"]
    retracted: bool
    conditions: tuple[ResolvedConditionRecord, ...]


# The two citation-lookup modes (SDD-001 §3.3.7 D3): per_version requires an
# exact pinned version; business_key_wide unions citations across the entire
# (node_kind, business_key) version chain and forbids a version.
CitationMode = Literal["per_version", "business_key_wide"]


@dataclass(frozen=True)
class CitationEntryStatusRecord:
    """The three INDEPENDENT audit-disclosure markers for one entry version
    (SDD-001 §3.3.7 D1/D4, R6a delta A3 — supersedes a single-value reading).

    Not a read-discipline exclusion surface: `citation_lookup` never admits or
    excludes on these — the inversion (SDD-001 §1) holds regardless of which
    markers are set. An empty marker set means "active"; "active" is not its
    own enum member, it is the absence of markers (app.models.
    CitationEntryStatus carries the same three-member vocabulary).

    `is_superseded`: this version is no longer current (`superseded_by`
    non-null). `is_retracted`: an EA-approved inbound `RETRACTS` targets this
    version (same existence pattern as read_as_of/obligation_context).
    `is_conditional`: `applicability_state = 'conditional'` on this version,
    read raw — never resolved to an actual `Condition` set, since this is
    disclosure only, not admission.
    """

    version: str
    is_superseded: bool
    is_retracted: bool
    is_conditional: bool


@dataclass(frozen=True)
class CitationOwnerRecord:
    """One `ReasoningProgress` (+ its owning `ReasoningSession`) that a cited
    `Evidence` `SUPPORTED_BY`-supports (SDD-001 §3.3.7). Port-level facts —
    one `Evidence` may support more than one conclusion, so a `CitationRecord`
    carries a sequence of these, never a single owner.

    Only `progress_id` (T1 PK) is required. The rest are Optional (review fix
    M1) — this is the audit op that deliberately reaches read-excluded,
    possibly malformed reasoning nodes (no DDR-002 existence constraint on
    these T2 fields), and `session_id` is additionally null whenever the
    traversal's `OPTIONAL MATCH` to the owning session resolves nothing. A
    null here must surface honestly on the wire model, never 500.
    """

    progress_id: str
    conclusion_type: str | None
    reasoner_category: str | None
    authoritative: bool | None
    progress_confidence: float | None
    session_id: str | None


@dataclass(frozen=True)
class CitationRecord:
    """One `Evidence` `SOURCED_FROM` a citation-lookup entry node, with every
    owning `ReasoningProgress`/`ReasoningSession` (SDD-001 §3.3.7). Port-level
    facts, not a domain type — this operation builds no `CandidateNode` at
    all (R6a delta A3; the audit posture, SDD-001 §1/§3.2).
    """

    evidence_id: str
    fact_summary: str | None
    confidence: float | None
    weight: float | None
    source_node_version: str | None
    observed_at: str | None
    owners: tuple[CitationOwnerRecord, ...]


@dataclass(frozen=True)
class CitationLookupPage:
    """One keyset page of `citation_lookup` results (SDD-001 §3.3.7 D3/D5/D7).

    `entry_found` distinguishes a truly-absent entry (the operation raises
    `TARGET_NOT_FOUND`) from an existing entry with zero citations (empty
    `citations`, `next_cursor=None`, never an error) — the reason the
    traversal OPTIONAL-matches the entry node(s) rather than requiring a hit.
    `entry_statuses` carries one record per resolved entry version: 0-or-1 for
    `per_version` (absent entirely when `entry_found` is False), 0-or-more for
    `business_key_wide` (one per version in the chain). `next_cursor` is the
    last returned `evidence_id`, or `None` on the final page — evidence_id is
    globally unique (PK), so it paginates uniformly across both modes without
    a new index (DDR-002 §7's reverse-lookup note; SDD-001 §3.3.7).
    """

    entry_found: bool
    entry_statuses: tuple[CitationEntryStatusRecord, ...]
    citations: tuple[CitationRecord, ...]
    next_cursor: str | None


@dataclass(frozen=True)
class ProvenanceOfCandidateRecord:
    """The originating `promotion`-kind `CandidatePromotion`'s own facts
    (SDD-001 §3.3.8). Port-level facts, not a domain type."""

    candidate_id: str
    proposal_kind: str
    status: str


@dataclass(frozen=True)
class ProvenanceOfGoverningDecisionRecord:
    """The governing (latest-`decided_at`, ANY outcome) `DECIDED_ON` edge's
    facts (DDR-002 §7 #15) — never a stale earlier approval (SDD-001
    §3.3.8). `outcome` may be `rejected`: #15 fixes "governing" as the
    latest edge regardless of outcome, not the latest approving one (review
    fix M3 — a filter-to-approving selection would hide a flipped-to-
    rejected verdict behind a stale earlier approval, exactly the failure
    #15's own clarifying clause names)."""

    decision_id: str
    outcome: str
    decided_at: str


@dataclass(frozen=True)
class ProvenanceOfFrozenEntryRecord:
    """One frozen `ProvenanceSummary` entry, zipped by position from the four
    index-aligned `frozen_*` arrays (DDR-002 §4), with live `Evidence`
    overlaid where it still exists (SDD-001 §3.3.8). Port-level facts.

    `evidence_id` is the correlation key (mechanical, never pin-matching).
    The `live_*` fields are populated only when `is_live` — carried flat
    here rather than as a nested record so the operation can build
    `EvidenceFacts` directly (citation-lookup's model, reused).
    """

    evidence_id: str
    frozen_fact_summary: str | None
    frozen_source_version_pin: str | None
    frozen_source_node_ref: str | None
    is_live: bool
    live_fact_summary: str | None
    live_confidence: float | None
    live_weight: float | None
    live_source_node_version: str | None
    live_observed_at: str | None


@dataclass(frozen=True)
class ProvenanceOfPage:
    """The resolved provenance-of facts for one specific promoted node
    (SDD-001 §3.3.8). NOT paginated (P-D2 — one entry, the frozen set is
    bounded by the promotion's own Evidence-span closure) — the name
    parallels `CitationLookupPage` for consistency, not because this page
    is keyset-paginated.

    `entry_found`/`is_promoted` are the two independent P-D3 raise signals:
    a truly-absent entry vs. an existing-but-never-promoted one — the
    operation's error message distinguishes them, both raise
    `TARGET_NOT_FOUND`. Two INDEPENDENT anomaly signals, neither ever
    raised: `frozen_layer_present=False` with `candidate` still populated
    (a #20 violation reached pre-CI-catch — no `ProvenanceSummary`), and
    `governing_decision=None` (review fix M3 — a promoted node with no
    `DECIDED_ON` edge at all). `entry_markers_*` are the three INDEPENDENT
    audit-disclosure booleans citation-lookup already established (never
    exclusionary — the inversion holds here too).
    """

    entry_found: bool
    is_promoted: bool
    origin_mechanism: str | None
    is_superseded: bool
    is_retracted: bool
    is_conditional: bool
    candidate: ProvenanceOfCandidateRecord | None
    governing_decision: ProvenanceOfGoverningDecisionRecord | None
    frozen_layer_present: bool
    provenance_summary_id: str | None
    entries: tuple[ProvenanceOfFrozenEntryRecord, ...]


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

    async def obligation_context(self, solution_id: str) -> Sequence[ObligationCandidateRecord]:
        """Resolve applicable PolicyRules for the given solution.

        One single-store traversal (ADR-002 §6 check 4): from the solution's
        `USES`/`FOLLOWS` entity set, every `PolicyRule` reached via outbound
        `GOVERNED_BY` (entity to rule) or inbound `MANDATES` (rule to
        Technology), current version only, with its own read-discipline
        structure resolved alongside — never pre-excluded here. Performs no
        read-discipline exclusion itself; that is the operation's job (the R2
        core). Obligation closure (condition-triggered rules, the
        satisfaction join) is out of scope — the constraint-validator's.

        Args:
            solution_id: The solution to resolve applicable PolicyRules for.

        Returns:
            One `ObligationCandidateRecord` per applicable PolicyRule. An
            absent solution or a solution governed by nothing yields an
            empty sequence, never an error.
        """
        ...

    async def find_precedents(
        self, criteria: FindPrecedentsCriteria
    ) -> Sequence[FindPrecedentsCandidateRecord]:
        """Resolve prior produced Solutions matching the given structural criteria.

        One single-store traversal (ADR-002 §6 check 4): every
        `(:Artifact:Solution)` matching the AND-across/OR-within linkage,
        `target_environment`, and `gate_outcome` filters, with every
        `GateDecision` on each matching Solution resolved alongside.
        Deterministic structural match only — no similarity scoring or
        ranking, and no read-discipline exclusion performed here (the
        operation supplies fixed constants; that is its job, not this port's).

        Args:
            criteria: The structural match criteria.

        Returns:
            One `FindPrecedentsCandidateRecord` per matching Solution. No
            matching criteria configured, or no Solution matching the given
            criteria, yields an empty sequence, never an error.
        """
        ...

    async def read_as_of(
        self,
        node_kind: ReadAsOfNodeKind,
        business_key: str,
        version: str,
    ) -> ReadAsOfResolvedRecord | None:
        """Resolve a supplied version pin over versioned ground truth.

        One single-store traversal: resolve the node by `(node_kind` label,
        `business_key` PK, `version)`, with its read-discipline structure
        resolved alongside. No status/superseded_by filter — a pin resolves
        the exact retained version, even a superseded one. Performs no
        read-discipline exclusion itself; that is the operation's job.

        Args:
            node_kind: The versioned label to resolve.
            business_key: The entity's PK value for that label.
            version: The exact retained version to resolve.

        Returns:
            The resolved record, or `None` if the pin resolves nothing (the
            operation raises `TARGET_NOT_FOUND`).
        """
        ...

    async def citation_lookup(
        self,
        node_kind: ReadAsOfNodeKind,
        business_key: str,
        version: str | None,
        mode: CitationMode,
        after_evidence_id: str | None,
        limit: int,
    ) -> CitationLookupPage:
        """Resolve the reverse cross-graph citation affordance for an entry node.

        One single-store traversal (ADR-002 §6 check 4): the entry node(s) —
        OPTIONAL-matched so a truly-absent entry is distinguishable from zero
        citations — reverse `SOURCED_FROM` to every citing `Evidence`, each
        with every owning `ReasoningProgress`/`ReasoningSession` via reverse
        `SUPPORTED_BY`/`CONTAINS`. Keyset-paginated by `evidence_id`. THE
        AUDIT-POSTURE EXCEPTION (SDD-001 §1/§3.2, §3.3.7): performs no
        read-discipline exclusion and resolves no `Condition` set — a
        retracted/superseded/conditional entry's citations are returned
        exactly as an active entry's would be; the three markers on
        `CitationEntryStatusRecord` are disclosure only.

        Args:
            node_kind: The entry node's versioned label (the six labels
                `ReadAsOfNodeKind` enumerates).
            business_key: The entry's PK value for that label.
            version: The exact retained version to resolve — required for
                `per_version`, forbidden for `business_key_wide`. Presence
                validation against `mode` is the operation's job, not this
                port's.
            mode: `per_version` (one entry version) or `business_key_wide`
                (every version sharing `business_key`).
            after_evidence_id: The keyset cursor — citations with a strictly
                greater `evidence_id`, or every citation from the start when
                `None`.
            limit: The already-resolved page size (config-default-substituted,
                hard-capped) — never a raw, unclamped request value.

        Returns:
            The resolved page. `entry_found=False` signals a truly-absent
            entry (the operation raises `TARGET_NOT_FOUND`); a `True` entry
            with empty `citations` is the zero-citations case, never an error.
        """
        ...

    async def provenance_of(
        self,
        node_kind: ReadAsOfNodeKind,
        business_key: str,
        version: str,
    ) -> ProvenanceOfPage:
        """Resolve the provenance-survival affordance for one promoted node.

        One single-store traversal (ADR-002 §6 check 4): the entry node —
        OPTIONAL-matched so a truly-absent entry is distinguishable from an
        existing-but-never-promoted one — reverse `PROMOTES_TO_KNOWLEDGE` to
        its `promotion`-kind `CandidatePromotion`, then that candidate's
        governing (latest-`decided_at`, ANY outcome) `DECIDED_ON` edge and
        its `MATERIALIZES_PROVENANCE_OF`-linked `ProvenanceSummary`. THE
        AUDIT-POSTURE EXCEPTION (SDD-001 §1/§3.2, §3.3.8): performs no
        read-discipline exclusion — a retracted/superseded/conditional
        promoted node's provenance is returned exactly as an active node's
        would be. Frozen entries are the four index-aligned `frozen_*`
        arrays zipped by position, each overlaid with its live `Evidence`
        where it still exists — the whole (unpaginated) set, bounded by the
        promotion's own Evidence-span closure.

        Args:
            node_kind: The entry node's versioned label (the six labels
                `ReadAsOfNodeKind` enumerates).
            business_key: The entry's PK value for that label.
            version: The exact retained version — one specific promoted node,
                never a business-key-wide resolution.

        Returns:
            The resolved page. `entry_found=False` or `is_promoted=False`
            both signal the operation's `TARGET_NOT_FOUND` raise (distinct
            messages, same error type) — an existing, currently-retracted or
            -superseded promoted node still resolves normally.
            `frozen_layer_present=False` is the honest anomaly signal for a
            resolved candidate with no `ProvenanceSummary` — never raised.
        """
        ...
