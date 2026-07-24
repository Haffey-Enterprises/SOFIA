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
    CapabilityBlockRecord,
    FindPrecedentsCandidateRecord,
    FindPrecedentsCriteria,
    GateDecisionRecord,
    ObligationCandidateRecord,
    ReadAsOfNodeKind,
    ReadAsOfResolvedRecord,
    ResolvedConditionRecord,
    ResolveTechnologyCandidateRecord,
    SelectPatternsCandidateRecord,
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

# One traversal (ADR-002 §6 check 4): every Pattern REQUIRES_CAPABILITY any
# requested Capability, with the Pattern's OWN read-discipline structure
# resolved via the SAME sub-pattern _RESOLVE_TECHNOLOGY_QUERY uses (governing
# PromotionDecision -> HAS_CONDITION; EXISTS-based approving-RETRACTS check;
# see that query's comments for the full rationale — unchanged here), plus,
# per matched Capability, its taxonomy placement and every Technology
# APPROVED_OPTION_FOR it, each resolved EXACTLY as _RESOLVE_TECHNOLOGY_QUERY
# resolves one. No active/version scoping is applied, matching that query: all
# three traversed edges (REQUIRES_CAPABILITY, APPROVED_OPTION_FOR,
# PREFERRED_OVER) are declared `rebind:current` (DDR-002 §3) — supersession
# re-points them, so they structurally target the current version already; no
# explicit WHERE-status filter is needed or invented.
#
# One row per (pattern, matched capability, technology) triple; a capability
# with no approved Technology (the gap signal, SDD-001 §3.3.1 ruling #6)
# yields one row with every tech_* field null via the OPTIONAL MATCH — the
# adapter's mapping treats a null tech_node_id as "no candidate", never a
# phantom entry. PREFERRED_OVER and the Pattern's own read-discipline fields
# are resolved once per pattern (in dedicated CALL{} blocks scoped before the
# capability/technology MATCH), so they repeat identically across every row of
# the same pattern — the adapter groups by node_id/capability_id in Python
# rather than nesting the aggregation in Cypher, the same client-side-mapping
# discipline every adapter method here already uses.
_SELECT_PATTERNS_QUERY = """
MATCH (p:Catalog:Pattern)-[:REQUIRES_CAPABILITY]->(c0:Catalog:Capability)
WHERE c0.capability_id IN $capability_ids
WITH DISTINCT p
CALL {
  WITH p
  OPTIONAL MATCH (promotion:Reasoning:CandidatePromotion {proposal_kind: 'promotion'})
    -[:PROMOTES_TO_KNOWLEDGE]->(p)
  OPTIONAL MATCH (promotion)<-[decided:DECIDED_ON]-(decision:Governance:PromotionDecision)
  WHERE decided.outcome IN ['approved', 'approved_conditional']
  WITH decision
  ORDER BY decision.decided_at DESC
  LIMIT 1
  OPTIONAL MATCH (decision)-[:HAS_CONDITION]->(condition:Governance:Condition)
  RETURN collect(DISTINCT condition) AS pattern_governing_conditions
}
CALL {
  WITH p
  OPTIONAL MATCH (p)-[:PREFERRED_OVER]->(other:Catalog:Pattern)
  RETURN collect(DISTINCT other.pattern_id) AS preferred_over
}
MATCH (p)-[:REQUIRES_CAPABILITY]->(cap:Catalog:Capability)
WHERE cap.capability_id IN $capability_ids
OPTIONAL MATCH (tech:Catalog:Technology)-[:APPROVED_OPTION_FOR]->(cap)
CALL {
  WITH tech
  OPTIONAL MATCH (tpromotion:Reasoning:CandidatePromotion {proposal_kind: 'promotion'})
    -[:PROMOTES_TO_KNOWLEDGE]->(tech)
  OPTIONAL MATCH (tpromotion)<-[tdecided:DECIDED_ON]-(tdecision:Governance:PromotionDecision)
  WHERE tech IS NOT NULL AND tdecided.outcome IN ['approved', 'approved_conditional']
  WITH tdecision
  ORDER BY tdecision.decided_at DESC
  LIMIT 1
  OPTIONAL MATCH (tdecision)-[:HAS_CONDITION]->(tcondition:Governance:Condition)
  RETURN collect(DISTINCT tcondition) AS tech_governing_conditions
}
RETURN
  p.pattern_id AS node_id,
  p.version AS version,
  p.origin_mechanism AS origin_mechanism,
  p.derivation_class AS derivation_class,
  p.applicability_state AS applicability_state,
  EXISTS {
    MATCH (retraction:Reasoning:CandidatePromotion {proposal_kind: 'retraction'})
      -[:RETRACTS]->(p)
    MATCH (retraction)<-[retraction_decided:DECIDED_ON]-(:Governance:PromotionDecision)
    WHERE retraction_decided.outcome IN ['approved', 'approved_conditional']
  } AS retracted,
  [c IN pattern_governing_conditions WHERE c IS NOT NULL |
    {predicate: c.predicate, dependency_manifest: c.dependency_manifest}] AS conditions,
  preferred_over,
  cap.capability_id AS capability_id,
  cap.l1_taxonomy AS l1_taxonomy,
  cap.l2_taxonomy AS l2_taxonomy,
  cap.l3_taxonomy AS l3_taxonomy,
  tech.technology_id AS tech_node_id,
  tech.version AS tech_version,
  tech.origin_mechanism AS tech_origin_mechanism,
  tech.derivation_class AS tech_derivation_class,
  tech.tier_applicability AS tech_tier_applicability,
  tech.approved_data_classifications AS tech_approved_data_classifications,
  tech.applicability_state AS tech_applicability_state,
  tech.deprecation_date AS tech_deprecation_date,
  (tech IS NOT NULL AND EXISTS {
    MATCH (tretraction:Reasoning:CandidatePromotion {proposal_kind: 'retraction'})
      -[:RETRACTS]->(tech)
    MATCH (tretraction)<-[tretraction_decided:DECIDED_ON]-(:Governance:PromotionDecision)
    WHERE tretraction_decided.outcome IN ['approved', 'approved_conditional']
  }) AS tech_retracted,
  [c IN tech_governing_conditions WHERE c IS NOT NULL |
    {predicate: c.predicate, dependency_manifest: c.dependency_manifest}] AS tech_conditions
ORDER BY node_id, capability_id, tech_node_id
"""

# One traversal (ADR-002 §6 check 4): from the solution's USES(Technology)/
# FOLLOWS(Pattern) entity set, every PolicyRule reached via outbound
# GOVERNED_BY (entity to rule) or inbound MANDATES (rule to Technology only,
# DDR-002 §3 edge catalog), with the rule's OWN read-discipline structure
# resolved via the SAME sub-pattern _SELECT_PATTERNS_QUERY uses (governing
# PromotionDecision -> HAS_CONDITION; EXISTS-based approving-RETRACTS check).
#
# Absent solution -> zero rows (the leading MATCH finds nothing; empty-never-
# error, SDD-001 §3.3.4 O1). A solution governed by nothing (no USES/FOLLOWS,
# or entities reaching no rule) also falls out to zero rows naturally: each
# CALL{} aggregation over zero input rows still yields exactly one row with an
# empty collect() (standard Cypher aggregation semantics — no explicit
# grouping key), so candidate_rules ends up [] and the final UNWIND produces
# no rows, never an error.
#
# USES/FOLLOWS are traversed unfiltered (RBT-78 R4a Item-4 resolution,
# operator-ratified): DDR-002 §3's re-bind discipline classifies "a solution's
# use of a version" as rebind:pinned, so the traversal correctly follows
# whichever Technology/Pattern version the solution actually pinned at design
# time — no active-version filter on that side.
#
# The resolved PolicyRule itself DOES get an explicit active-version filter
# (`rule.superseded_by IS NULL`) — same R4a ruling: GOVERNED_BY/MANDATES carry
# no stated rebind classification in DDR-002 §3 (unlike the Selection
# sub-graph's explicit `rebind:current` heading), so self-maintaining
# supersession re-pointing is NOT assumed. PolicyRule is one of §6 Option-A's
# versioned-ground-truth types ("superseding creates a new retained node and
# marks the old superseded"), so `superseded_by IS NULL` is the schema-literal
# current-version test — closes the case where a superseded rule still carries
# its own outbound MANDATES edge and would otherwise surface as stale.
#
# Direct USES/FOLLOWS entities only (O4) — no transitive Pattern ->
# REQUIRES_CAPABILITY -> Capability governance is traversed.
#
# Obligation closure (condition-triggered rules from rule_definition, the
# satisfaction join) is NOT computed here — the constraint-validator's job
# (SDD-001 §3.3.4). rule_definition is returned opaque, never parsed.
_OBLIGATION_CONTEXT_QUERY = """
MATCH (sol:Artifact:Solution {artifact_id: $solution_id})
CALL {
  WITH sol
  OPTIONAL MATCH (sol)-[:USES]->(tech:Catalog:Technology)
  RETURN collect(DISTINCT tech) AS used_techs
}
CALL {
  WITH sol
  OPTIONAL MATCH (sol)-[:FOLLOWS]->(pat:Catalog:Pattern)
  RETURN collect(DISTINCT pat) AS followed_patterns
}
CALL {
  WITH used_techs, followed_patterns
  UNWIND used_techs + followed_patterns AS entity
  MATCH (entity)-[:GOVERNED_BY]->(governed_rule:Standards:PolicyRule)
  RETURN collect(DISTINCT governed_rule) AS governed_rules
}
CALL {
  WITH used_techs
  UNWIND used_techs AS tech
  MATCH (mandated_rule:Standards:PolicyRule)-[:MANDATES]->(tech)
  RETURN collect(DISTINCT mandated_rule) AS mandated_rules
}
WITH governed_rules + mandated_rules AS candidate_rules
UNWIND candidate_rules AS rule
WITH DISTINCT rule
WHERE rule.superseded_by IS NULL
CALL {
  WITH rule
  OPTIONAL MATCH (promotion:Reasoning:CandidatePromotion {proposal_kind: 'promotion'})
    -[:PROMOTES_TO_KNOWLEDGE]->(rule)
  OPTIONAL MATCH (promotion)<-[decided:DECIDED_ON]-(decision:Governance:PromotionDecision)
  WHERE decided.outcome IN ['approved', 'approved_conditional']
  WITH decision
  ORDER BY decision.decided_at DESC
  LIMIT 1
  OPTIONAL MATCH (decision)-[:HAS_CONDITION]->(condition:Governance:Condition)
  RETURN collect(DISTINCT condition) AS governing_conditions
}
RETURN
  rule.policy_rule_id AS node_id,
  rule.version AS version,
  rule.origin_mechanism AS origin_mechanism,
  rule.derivation_class AS derivation_class,
  rule.applicability_state AS applicability_state,
  EXISTS {
    MATCH (retraction:Reasoning:CandidatePromotion {proposal_kind: 'retraction'})
      -[:RETRACTS]->(rule)
    MATCH (retraction)<-[retraction_decided:DECIDED_ON]-(:Governance:PromotionDecision)
    WHERE retraction_decided.outcome IN ['approved', 'approved_conditional']
  } AS retracted,
  [c IN governing_conditions WHERE c IS NOT NULL |
    {predicate: c.predicate, dependency_manifest: c.dependency_manifest}] AS conditions,
  rule.statement AS statement,
  rule.rule_definition AS rule_definition,
  rule.dependency_manifest AS dependency_manifest,
  rule.enforcement_level AS enforcement_level,
  rule.enforced_at_gate AS enforced_at_gate,
  rule.domain AS domain
ORDER BY node_id
"""

# One traversal (ADR-002 §6 check 4): every produced (:Artifact:Solution)
# matching the requested structural criteria (SDD-001 §3.3.5) — AND-across
# the non-empty linkage/target_environment/gate_outcome dimensions, OR-within
# a given dimension's own list (an empty list parameter is a no-op filter on
# that dimension via `size(...) = 0 OR EXISTS {...}`). Deterministic
# structural match only; no similarity scoring, no ranking.
#
# Capability linkage is the 2-hop FOLLOWS -> REQUIRES_CAPABILITY path ONLY
# (DDR-001's gap model: "gap = required capability with no resolving
# technology" — the capability a Solution's Pattern *requires*, not what its
# Technology choices *resolve* via USES -> APPROVED_OPTION_FOR, which would
# conflate a different question).
#
# No active/version scoping is invented here. USES/FOLLOWS are traversed
# unfiltered (DDR-002 §3: "a solution's use of a version" is rebind:pinned,
# same precedent as R4a's obligation-context traversal). REQUIRES_CAPABILITY
# is traversed unfiltered too (rebind:current, the SAME precedent
# _RESOLVE_TECHNOLOGY_QUERY/_SELECT_PATTERNS_QUERY already establish for this
# exact edge type — supersession re-points it, so it structurally targets the
# current Capability already). Solution itself carries no supersession
# concept at all: DDR-002 §6 scopes Option-A version supersession to Catalog/
# Standards/RateCard/CostFactor/PlaneDefinition only — Solutions/Artifacts are
# "dual-home" (§6 preamble), each node its own permanent record, with no
# `status`/`superseded_by` field to filter on (§5's Solution property list).
# Matching by artifact_id/pattern_id/technology_id/capability_id equality
# against the caller's lists is therefore unambiguous regardless of any
# business-key-wide version question: each MATCH above reaches one specific
# node (via the Solution's own pinned or self-maintaining edge), never an
# open business-key-wide lookup across versions.
#
# Every GateDecision on a matching Solution is collected in a dedicated
# CALL{} (isolating the aggregation from the other returned scalar fields,
# the same idiom _SELECT_PATTERNS_QUERY/_OBLIGATION_CONTEXT_QUERY use): the
# CASE-wrapped OPTIONAL MATCH lets collect() correctly yield [] for a
# Solution with no GateDecision at all, rather than one all-null entry.
_FIND_PRECEDENTS_QUERY = """
MATCH (sol:Artifact:Solution)
WHERE
  (size($technology_ids) = 0 OR EXISTS {
    MATCH (sol)-[:USES]->(tech:Catalog:Technology)
    WHERE tech.technology_id IN $technology_ids
  })
  AND (size($pattern_ids) = 0 OR EXISTS {
    MATCH (sol)-[:FOLLOWS]->(pat:Catalog:Pattern)
    WHERE pat.pattern_id IN $pattern_ids
  })
  AND (size($capability_ids) = 0 OR EXISTS {
    MATCH (sol)-[:FOLLOWS]->(:Catalog:Pattern)-[:REQUIRES_CAPABILITY]->(cap:Catalog:Capability)
    WHERE cap.capability_id IN $capability_ids
  })
  AND ($target_environment IS NULL OR sol.target_environment = $target_environment)
  AND ($gate_outcome IS NULL OR EXISTS {
    MATCH (:Governance:Decision:GateDecision)-[filter_decided:DECIDED_ON]->(sol)
    WHERE filter_decided.outcome = $gate_outcome
  })
CALL {
  WITH sol
  OPTIONAL MATCH (gate_decision:Governance:Decision:GateDecision)-[decided:DECIDED_ON]->(sol)
  RETURN collect(
    CASE WHEN gate_decision IS NULL THEN NULL ELSE {
      outcome: decided.outcome,
      gate: gate_decision.gate,
      decision_id: gate_decision.decision_id
    } END
  ) AS gate_decision_maps
}
RETURN
  sol.artifact_id AS node_id,
  sol.version AS version,
  sol.origin_mechanism AS origin_mechanism,
  sol.target_environment AS target_environment,
  [g IN gate_decision_maps WHERE g IS NOT NULL] AS gate_decisions
ORDER BY node_id
"""

# The 6 versioned Catalog+Standards labels read-as-of resolves (SDD-001
# §3.3.6, pin-mode) -> (Cypher label, PK property, plane label). Verified
# fresh against DDR-002 §2.1/§2.5. `ComplianceControl` is excluded (no
# `version` property); Cost/PlaneDefinition remain deferred. This is a fixed
# internal map, never user input — its values are safe to interpolate
# directly into Cypher (labels/property names are not parameterizable in
# Neo4j; business_key/version are the query's actual $params).
_READ_AS_OF_NODE_KIND_MAP: dict[ReadAsOfNodeKind, tuple[str, str, str]] = {
    "Pattern": ("Catalog:Pattern", "pattern_id", "Catalog"),
    "Technology": ("Catalog:Technology", "technology_id", "Catalog"),
    "Capability": ("Catalog:Capability", "capability_id", "Catalog"),
    "IacTemplate": ("Catalog:IacTemplate", "iac_template_id", "Catalog"),
    "Standard": ("Standards:Standard", "standard_id", "Standards"),
    "PolicyRule": ("Standards:PolicyRule", "policy_rule_id", "Standards"),
}

# One traversal (ADR-002 §6 check 4): the exact retained version node for
# (label, pk_property=business_key, version) — a supplied pin, never
# filtered on status/superseded_by (read-as-of deliberately resolves a
# specific, possibly-superseded version; filtering here would defeat pin
# resolution). Resolves 0-or-1 node by the (business_key, version)
# uniqueness DDR-002 §2.4 names. Read-discipline structure resolved
# alongside via the SAME sub-pattern _SELECT_PATTERNS_QUERY uses (governing
# PromotionDecision -> HAS_CONDITION; EXISTS-based approving-RETRACTS check)
# — never pre-excluded here (SDD-001 §4.4 is the operation's job).
#
# `effective_from` is read directly off the node regardless of label:
# Cypher property access on a label that doesn't declare a property returns
# null rather than erroring, so this single template correctly yields null
# for every label except `Pattern` (the one label DDR-002 §2.1 declares it
# on) without needing a per-label field list. `effective_to` is not read at
# all — no in-scope label declares it (RBT-83).
#
# `__LABEL__`/`__PK__` are plain string-replace tokens, not str.format()
# placeholders — chosen so the query's own Cypher `{...}` map/list syntax
# needs no brace-escaping.
_READ_AS_OF_QUERY_TEMPLATE = """
MATCH (n:__LABEL__ {__PK__: $business_key, version: $version})
CALL {
  WITH n
  OPTIONAL MATCH (promotion:Reasoning:CandidatePromotion {proposal_kind: 'promotion'})
    -[:PROMOTES_TO_KNOWLEDGE]->(n)
  OPTIONAL MATCH (promotion)<-[decided:DECIDED_ON]-(decision:Governance:PromotionDecision)
  WHERE decided.outcome IN ['approved', 'approved_conditional']
  WITH decision
  ORDER BY decision.decided_at DESC
  LIMIT 1
  OPTIONAL MATCH (decision)-[:HAS_CONDITION]->(condition:Governance:Condition)
  RETURN collect(DISTINCT condition) AS governing_conditions
}
RETURN
  n.__PK__ AS node_id,
  n.version AS version,
  n.origin_mechanism AS origin_mechanism,
  n.derivation_class AS derivation_class,
  n.effective_from AS effective_from,
  n.applicability_state AS applicability_state,
  EXISTS {
    MATCH (retraction:Reasoning:CandidatePromotion {proposal_kind: 'retraction'})
      -[:RETRACTS]->(n)
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

    async def select_patterns(
        self, capability_ids: Sequence[str]
    ) -> Sequence[SelectPatternsCandidateRecord]:
        """Resolve candidate Patterns for the given required Capabilities.

        One single-store Cypher traversal (ADR-002 §6 check 4). Structural
        match and read-discipline-structure resolution only — no exclusion and
        no eligibility computation happen here (SDD-001 §4.4 and
        app.domain.shared.catalog_eligibility are the operation's job).

        Args:
            capability_ids: The required Capabilities to resolve candidate
                Patterns for.

        Returns:
            One `SelectPatternsCandidateRecord` per candidate Pattern, each
            with one `CapabilityBlockRecord` per matched requested Capability.

        Raises:
            RuntimeError: If no driver is open — a data operation with no
                driver must fail loud, never silently return an empty (and
                misleading) result.
        """
        if self._driver is None:
            raise RuntimeError("No graph driver is open: application startup did not complete")

        if not capability_ids:
            return []

        result = await self._driver.execute_query(
            _SELECT_PATTERNS_QUERY,
            {"capability_ids": list(capability_ids)},
            routing_=RoutingControl.READ,
            database_=self._settings.neo4j_database,
        )

        patterns: dict[str, dict[str, Any]] = {}
        for record in result.records:
            pattern_entry = patterns.setdefault(
                record["node_id"],
                {
                    "version": record["version"],
                    "origin_mechanism": record["origin_mechanism"],
                    "derivation_class": record["derivation_class"],
                    "applicability_state": record["applicability_state"] or "unconditional",
                    "retracted": record["retracted"],
                    "conditions": record["conditions"],
                    "preferred_over": record["preferred_over"],
                    "capabilities": {},
                },
            )
            cap_entry = pattern_entry["capabilities"].setdefault(
                record["capability_id"],
                {
                    "l1_taxonomy": record["l1_taxonomy"],
                    "l2_taxonomy": record["l2_taxonomy"],
                    "l3_taxonomy": record["l3_taxonomy"],
                    "technology_options": [],
                },
            )
            if record["tech_node_id"] is not None:
                cap_entry["technology_options"].append(
                    ResolveTechnologyCandidateRecord(
                        node_id=record["tech_node_id"],
                        version=record["tech_version"],
                        origin_mechanism=record["tech_origin_mechanism"],
                        derivation_class=record["tech_derivation_class"],
                        tier_applicability=tuple(record["tech_tier_applicability"] or ()),
                        approved_data_classifications=tuple(
                            record["tech_approved_data_classifications"] or ()
                        ),
                        applicability_state=record["tech_applicability_state"] or "unconditional",
                        retracted=record["tech_retracted"],
                        deprecation_date=record["tech_deprecation_date"],
                        conditions=tuple(
                            ResolvedConditionRecord(
                                predicate=condition["predicate"],
                                required_context_fields=frozenset(
                                    condition["dependency_manifest"] or ()
                                ),
                            )
                            for condition in record["tech_conditions"]
                        ),
                    )
                )

        return [
            SelectPatternsCandidateRecord(
                node_id=node_id,
                version=entry["version"],
                origin_mechanism=entry["origin_mechanism"],
                derivation_class=entry["derivation_class"],
                applicability_state=entry["applicability_state"],
                retracted=entry["retracted"],
                conditions=tuple(
                    ResolvedConditionRecord(
                        predicate=condition["predicate"],
                        required_context_fields=frozenset(condition["dependency_manifest"] or ()),
                    )
                    for condition in entry["conditions"]
                ),
                capabilities=tuple(
                    CapabilityBlockRecord(
                        capability_id=capability_id,
                        l1_taxonomy=cap["l1_taxonomy"],
                        l2_taxonomy=cap["l2_taxonomy"],
                        l3_taxonomy=cap["l3_taxonomy"],
                        technology_options=tuple(cap["technology_options"]),
                    )
                    for capability_id, cap in entry["capabilities"].items()
                ),
                preferred_over=tuple(entry["preferred_over"]),
            )
            for node_id, entry in patterns.items()
        ]

    async def obligation_context(self, solution_id: str) -> Sequence[ObligationCandidateRecord]:
        """Resolve applicable PolicyRules for the given solution.

        One single-store Cypher traversal (ADR-002 §6 check 4), resolving the
        real read-discipline structure alongside — no read-discipline
        exclusion happens here (SDD-001 §4.4 is the R2 core's job alone).

        Args:
            solution_id: The solution to resolve applicable PolicyRules for.

        Returns:
            One `ObligationCandidateRecord` per applicable PolicyRule. An
            absent solution or a solution governed by nothing yields an
            empty sequence, never an error.

        Raises:
            RuntimeError: If no driver is open — a data operation with no
                driver must fail loud, never silently return an empty (and
                misleading) result.
        """
        if self._driver is None:
            raise RuntimeError("No graph driver is open: application startup did not complete")

        result = await self._driver.execute_query(
            _OBLIGATION_CONTEXT_QUERY,
            {"solution_id": solution_id},
            routing_=RoutingControl.READ,
            database_=self._settings.neo4j_database,
        )
        return [
            ObligationCandidateRecord(
                node_id=record["node_id"],
                version=record["version"],
                origin_mechanism=record["origin_mechanism"],
                derivation_class=record["derivation_class"],
                applicability_state=record["applicability_state"] or "unconditional",
                retracted=record["retracted"],
                conditions=tuple(
                    ResolvedConditionRecord(
                        predicate=condition["predicate"],
                        required_context_fields=frozenset(condition["dependency_manifest"] or ()),
                    )
                    for condition in record["conditions"]
                ),
                statement=record["statement"],
                rule_definition=record["rule_definition"],
                dependency_manifest=tuple(record["dependency_manifest"] or ()),
                enforcement_level=record["enforcement_level"],
                enforced_at_gate=record["enforced_at_gate"],
                domain=record["domain"],
            )
            for record in result.records
        ]

    async def find_precedents(
        self, criteria: FindPrecedentsCriteria
    ) -> Sequence[FindPrecedentsCandidateRecord]:
        """Resolve prior produced Solutions matching the given structural criteria.

        One single-store Cypher traversal (ADR-002 §6 check 4). Structural
        match only — no read-discipline exclusion happens here (SDD-001 §4.4
        is the operation's job alone, via fixed constants).

        Args:
            criteria: The structural match criteria.

        Returns:
            One `FindPrecedentsCandidateRecord` per matching Solution.

        Raises:
            RuntimeError: If no driver is open — a data operation with no
                driver must fail loud, never silently return an empty (and
                misleading) result.
        """
        if self._driver is None:
            raise RuntimeError("No graph driver is open: application startup did not complete")

        result = await self._driver.execute_query(
            _FIND_PRECEDENTS_QUERY,
            {
                "technology_ids": list(criteria.technology_ids),
                "pattern_ids": list(criteria.pattern_ids),
                "capability_ids": list(criteria.capability_ids),
                "target_environment": criteria.target_environment,
                "gate_outcome": criteria.gate_outcome,
            },
            routing_=RoutingControl.READ,
            database_=self._settings.neo4j_database,
        )
        return [
            FindPrecedentsCandidateRecord(
                node_id=record["node_id"],
                version=record["version"],
                origin_mechanism=record["origin_mechanism"],
                target_environment=record["target_environment"],
                gate_decisions=tuple(
                    GateDecisionRecord(
                        outcome=gate_decision["outcome"],
                        gate=gate_decision["gate"],
                        decision_id=gate_decision["decision_id"],
                    )
                    for gate_decision in record["gate_decisions"]
                ),
            )
            for record in result.records
        ]

    async def read_as_of(
        self,
        node_kind: ReadAsOfNodeKind,
        business_key: str,
        version: str,
    ) -> ReadAsOfResolvedRecord | None:
        """Resolve a supplied version pin over versioned ground truth.

        One single-store Cypher traversal (ADR-002 §6 check 4). Structural
        match and read-discipline-structure resolution only — no exclusion
        happens here (SDD-001 §4.4 is the operation's job).

        Args:
            node_kind: The versioned label to resolve.
            business_key: The entity's PK value for that label.
            version: The exact retained version to resolve.

        Returns:
            The resolved `ReadAsOfResolvedRecord`, or `None` if the pin
            resolves nothing.

        Raises:
            RuntimeError: If no driver is open — a data operation with no
                driver must fail loud, never silently return an empty (and
                misleading) result.
        """
        if self._driver is None:
            raise RuntimeError("No graph driver is open: application startup did not complete")

        label, pk_property, plane_label = _READ_AS_OF_NODE_KIND_MAP[node_kind]
        query = _READ_AS_OF_QUERY_TEMPLATE.replace("__LABEL__", label).replace(
            "__PK__", pk_property
        )
        result = await self._driver.execute_query(
            query,
            {"business_key": business_key, "version": version},
            routing_=RoutingControl.READ,
            database_=self._settings.neo4j_database,
        )
        if not result.records:
            return None

        record = result.records[0]
        return ReadAsOfResolvedRecord(
            node_id=record["node_id"],
            plane_labels=(plane_label,),
            version=record["version"],
            origin_mechanism=record["origin_mechanism"],
            derivation_class=record["derivation_class"],
            effective_from=record["effective_from"],
            effective_to=None,
            applicability_state=record["applicability_state"] or "unconditional",
            retracted=record["retracted"],
            conditions=tuple(
                ResolvedConditionRecord(
                    predicate=condition["predicate"],
                    required_context_fields=frozenset(condition["dependency_manifest"] or ()),
                )
                for condition in record["conditions"]
            ),
        )
