##############################################################################
# Module: models.py
# Service: knowledge-service
# Author: Haffey Enterprises LLC
# Created: 2026-07-21
# Revised: 2026-07-23
# Description: Request/response contracts for knowledge-service (SDD-001
#   §4.1). At RBT-77 the surface was the §3.1 health and readiness shapes; the
#   R1 legs of RBT-78 added the §3.2 error contract (ErrorType, ErrorResponse).
#   This leg (R2) adds the §3.2 RESULT envelope — the applicability block, the
#   disclosure channel (+ its three reasons), the per-node ResultEnvelope, and
#   the ReadResult that bundles admitted envelopes with disclosures. These are
#   assembled by app.domain.shared.envelope from the read-discipline core's
#   verdicts (app.domain.retrieval); the nine §3.3 operation-shaped
#   request/response contracts land with the operations themselves (R3+).
#   SDD-001 v1.7.0 adds the applicability block's deprecation notice
#   (DeprecationNotice) — marker-presence only (set iff the resolved Catalog
#   node carries a deprecation_date), on the same annotation-never-exclusion
#   footing as CatalogEligibility.
#   These typed models are the source of truth for the contract tests — when
#   an implementation and a contract diverge, the contract wins.
##############################################################################

from enum import StrEnum
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class CheckStatus(StrEnum):
    """Outcome of a single readiness check."""

    OK = "ok"
    UNAVAILABLE = "unavailable"


class HealthResponse(BaseModel):
    """Liveness response — the process is up (SDD-001 §3.1).

    Deliberately carries no dependency state: liveness performs no I/O, so a
    graph outage must never take this endpoint negative and get the container
    killed.
    """

    status: Literal["ok"] = "ok"
    service: str


class ReadinessResponse(BaseModel):
    """Readiness response — the service can actually serve (SDD-001 §3.1).

    There is no degraded mode: this service has exactly one backing store and
    every operation requires it, so any failed check makes the whole response
    negative and the endpoint answers 503.
    """

    status: Literal["ok", "unavailable"]
    service: str
    checks: dict[str, CheckStatus] = Field(
        description="Per-check outcomes, keyed by check name, in SDD-001 §3.1 order.",
    )


class ErrorType(StrEnum):
    """The SDD-001 §3.2 typed-error taxonomy — one type per enforced invariant.

    The closed, ratified vocabulary of every rejection the gateway can return
    (SDD-001 §3.2), enumerated whole here as its single source: the exception
    layer (app.domain.exceptions) and the response envelope both draw from it,
    and the write stories (RBT-79+) raise from it rather than re-opening it.
    Enumerating it in full is transcription of a ratified list, not invented
    vocabulary — the distinction from the forthcoming predicate grammar, which
    is genuinely unowned. RBT-78 (reads) raises only TARGET_NOT_FOUND; the rest
    carry write-side raising sites landing with their operations.
    """

    AUTHOR_VIOLATION = "AUTHOR_VIOLATION"
    DECISION_NOT_APPROVING = "DECISION_NOT_APPROVING"
    MONOTONICITY_VIOLATION = "MONOTONICITY_VIOLATION"
    SCOPE_DISPOSITION_MISSING = "SCOPE_DISPOSITION_MISSING"
    SCOPE_CONFLICT = "SCOPE_CONFLICT"
    SUBTYPE_VIOLATION = "SUBTYPE_VIOLATION"
    CLASSIFICATION_REJECTED = "CLASSIFICATION_REJECTED"
    SCHEMA_VIOLATION = "SCHEMA_VIOLATION"
    PROVENANCE_MISSING = "PROVENANCE_MISSING"
    SOURCE_REF_MISSING = "SOURCE_REF_MISSING"
    FLAG_CATEGORY_MISMATCH = "FLAG_CATEGORY_MISMATCH"
    UNIQUENESS_CONFLICT = "UNIQUENESS_CONFLICT"
    TARGET_NOT_FOUND = "TARGET_NOT_FOUND"
    NON_CITABLE_SOURCE = "NON_CITABLE_SOURCE"
    CONFIDENCE_UNDERIVABLE = "CONFIDENCE_UNDERIVABLE"


class FaultClass(StrEnum):
    """Retry-decision class for an error response (house application-code §1).

    Carried on the error envelope so an inter-service consumer branches on the
    fault's nature rather than on the HTTP status alone. Optional on the
    gateway's rejections; populated when a raising site has a fault nature to
    declare.
    """

    TRANSIENT = "transient"
    PERMANENT = "permanent"
    UPSTREAM = "upstream"
    TIMEOUT = "timeout"
    AUTH = "auth"


class ErrorResponse(BaseModel):
    """The typed error envelope (SDD-001 §3.2; house application-code §1).

    Every gateway rejection renders as this shape through the single exception
    handler. `error_code` carries the ErrorType member; `correlation_id` ties
    the response to its request's log line. No credential and no Tier 3/4 value
    is ever placed in `message` or `detail` — the response ceiling is Tier 2.
    """

    success: Literal[False] = False
    error_code: ErrorType
    message: str
    detail: str | None = None
    correlation_id: str | None = None
    fault_class: FaultClass | None = None


class ConditionalAdmissionStatus(StrEnum):
    """The applicability block's conditional-admission verdict (SDD-001 §3.2).

    Only meaningful on an ADMITTED envelope: an excluded conditional node
    produces a disclosure entry instead, never a `ResultEnvelope`. A node with
    no `HAS_CONDITION` path is `UNCONDITIONAL`; a node admitted because its
    single condition's predicate evaluated true is `CONDITIONALLY_ADMITTED`.
    """

    UNCONDITIONAL = "unconditional"
    CONDITIONALLY_ADMITTED = "conditionally_admitted"


class CatalogEligibility(BaseModel):
    """The Catalog-eligibility verdict (SDD-001 §4.4; DDR-002 §2.1/§5).

    Computed per DDR-002 §2.1's two Technology fields: tier fit
    (`context.environment_class ∈ tier_applicability[]`) and classification
    fit (`context.data_classification ∈ approved_data_classifications[]`).
    `failing_fields` names which check(s) failed — `"tier_applicability"` and/
    or `"approved_data_classifications"` — empty when `eligible` is true.
    Annotation only: an ineligible Technology is still returned (SDD-001 §4.4
    "annotation, never exclusion") — silently filtering it would erase the
    gap-vs-ineligible distinction the reasoning capture depends on.
    """

    eligible: bool
    failing_fields: list[str]


class DeprecationNotice(BaseModel):
    """The deprecation notice (SDD-001 §3.2 v1.7.0; DDR-002 §2.1).

    `deprecated` is **marker-presence, not a temporal evaluation against the
    read clock**: it is set iff the resolved Catalog node carries a
    `deprecation_date`, never by comparing that date to "now." On the same
    annotation-never-exclusion footing as `CatalogEligibility` — a deprecated
    Technology is disclosed, never read-excluded; whether to admit it is the
    approver's decision, not the gateway's. `approval_status` is deliberately
    not surfaced here — its value-set is unratified in DDR-002.
    """

    model_config = ConfigDict(frozen=True)

    deprecated: bool
    deprecation_date: str | None = None


class ApplicabilityBlock(BaseModel):
    """The §3.2 applicability block carried on every admitted result.

    `catalog_eligibility` and `conditional_admission` are two DISTINCT
    applicability surfaces (DDR-002 §5 "two-surface applicability... both
    bind") — the gateway annotates both but composes NEITHER into a single
    "may I use this here?" verdict; that composition is the consuming SDD's
    call (solutioning-agent), not this gateway's to make (§4.4). Non-Catalog
    operations (e.g. track-record-lookup) carry `catalog_eligibility=None` —
    the surface simply does not apply to their candidates. `deprecation`
    (v1.7.0) is the same kind of annotation-only surface, additive across
    every §3.3 read port resolving a deprecatable Catalog node; `None` where
    no resolved node is deprecatable.
    """

    conditional_admission: ConditionalAdmissionStatus
    catalog_eligibility: CatalogEligibility | None = None
    deprecation: DeprecationNotice | None = None


class DisclosureReason(StrEnum):
    """The §3.2 disclosure channel's closed reason vocabulary.

    The three reasons an excluded *conditional* node is disclosed (never a
    fourth): its predicate evaluated false, its predicate could not be
    evaluated at all (fail-closed), or it carries more than one `HAS_CONDITION`
    path (the DDR-002 multi-condition named gap, surfaced rather than
    silently composed). Un-approved proposals and retracted nodes are excluded
    WITHOUT disclosure (SDD-001 §3.2) — they never produce a `DisclosureEntry`.
    """

    CONDITION_UNSATISFIED = "condition_unsatisfied"
    CONDITION_UNEVALUABLE = "condition_unevaluable"
    MULTI_CONDITION_SCOPE_CONFLICT = "multi_condition_scope_conflict"


class DisclosureEntry(BaseModel):
    """One excluded-conditional disclosure (SDD-001 §3.2) — no content payload.

    Deliberately carries nothing beyond identity and reason: the excluded
    node's content is never disclosed, only the fact and reason of exclusion.
    """

    node_id: str
    reason: DisclosureReason


class ResultEnvelope(BaseModel):
    """The §3.2 result envelope carried by every admitted retrieval result.

    `node_id` + `node_kind` are the identity/discriminator pair RBT-80's
    binding adapter projects onto the conformance seam's `{id, node_kind}`
    shape. `confidences` holds node confidence first, then any composed edge
    confidences (DDR-002 §3/§4 semantics) — plural because a traversal may
    compose more than one; an element is `None` when the underlying graph
    property is absent (R3a review finding) — no DDR-002 constraint or CI
    check guarantees presence on every confidence-bearing surface (contrast
    `Evidence.confidence`, which check #28 covers specifically). `version` /
    `version_pin` are optional (R3a correction): DDR-002 §6 scopes the
    versioning/supersession model to Catalog/Standards/RateCard/PlaneDefinition
    only — an Operational-plane `ObservedPattern` (§2.3) distills
    update-in-place and carries no `version` property at all, so a
    non-versioned node's envelope carries `None` here rather than a fabricated
    value.

    `effective_from`/`effective_to` carry **plane-dependent** semantics (R3a
    review finding) — there is one pair of fields, not one meaning: for a
    versioned plane (Catalog/Standards/RateCard/PlaneDefinition, DDR-002 §6)
    they are the effective-dating window (`effective_from`/`superseded_by`-
    adjacent); for an update-in-place Operational node (e.g. `ObservedPattern`,
    §2.3) they are the observation window (`first_observed_at`/
    `last_observed_at`) — there is no version-effective window to report. A
    consumer cannot tell which from the envelope alone; it is a function of
    `node_kind` (and, transitively, `plane_labels`).
    """

    node_id: str
    node_kind: str
    plane_labels: list[str]
    origin_mechanism: str
    derivation_class: str | None = None
    version: str | None = None
    effective_from: str | None = None
    effective_to: str | None = None
    version_pin: str | None = None
    confidences: list[float | None]
    applicability: ApplicabilityBlock


class ReadResult(BaseModel):
    """The read-discipline core's output: admitted envelopes + disclosures.

    What a §3.3 operation returns once read-discipline (SDD-001 §4.4) has run
    over its candidate nodes — admitted results carry a full `ResultEnvelope`;
    excluded-conditional nodes surface only as a `DisclosureEntry`. Silent
    exclusions (un-approved proposals, retracted nodes) appear in neither list.
    """

    admitted: list[ResultEnvelope]
    disclosures: list[DisclosureEntry]


class TrackRecordTargetRef(BaseModel):
    """One target entity in a track-record-lookup request (SDD-001 §3.3.3).

    `entity_kind` is the target's label (also the OBSERVED_IN edge's target
    type, DDR-002 §3); the four kinds do not share an ID namespace.
    """

    entity_kind: Literal["Technology", "Pattern", "Capability", "DeploymentEnvironment"]
    entity_id: str


class ConsumingContextPayload(BaseModel):
    """The §3.2 consuming-context payload, as submitted on a request.

    `declared_fields` carries the manifest-declared fields any applicable
    `Condition.dependency_manifest` requires — introspected by the caller, not
    the full graph-wide field superset.
    """

    environment_class: str
    data_classification: str
    declared_fields: dict[str, object] = Field(default_factory=dict)


class TrackRecordLookupRequest(BaseModel):
    """The track-record-lookup request body (SDD-001 §3.3.3)."""

    target_refs: list[TrackRecordTargetRef]
    consuming_context: ConsumingContextPayload


class ResolveTechnologyRequest(BaseModel):
    """The resolve-technology request body (SDD-001 §3.3.2)."""

    capability_id: str
    consuming_context: ConsumingContextPayload


class CapabilityBlock(BaseModel):
    """One requested Capability under a candidate Pattern (SDD-001 §3.3.1;
    DDR-002 §2.1): its taxonomy placement and the approved Technology options
    that realize it. An empty `technology_options` with no `technology_disclosures`
    IS the gap signal (DDR-001: a required capability with no resolving
    technology) — never an error. `catalog_eligibility` and `deprecation` live
    on each Technology envelope's applicability block; a Pattern carries neither
    (DDR-002 §2.1 — Technology-only surfaces)."""

    capability_id: str
    l1_taxonomy: str | None = None
    l2_taxonomy: str | None = None
    l3_taxonomy: str | None = None
    technology_options: list[ResultEnvelope]
    technology_disclosures: list[DisclosureEntry]


class PatternCandidate(BaseModel):
    """One admitted candidate Pattern with its nested selection-web (SDD-001
    §3.3.1). `envelope` carries node_kind="Pattern" with an applicability block
    whose conditional_admission is the only populated surface. `preferred_over`
    is the set of pattern_ids this Pattern is PREFERRED_OVER — an UNCOMPOSED
    structural fact (§2.2 selection judgment is the reasoning component's, never
    the gateway's): no ordering, no pick."""

    envelope: ResultEnvelope
    capabilities: list[CapabilityBlock]
    preferred_over: list[str]


class SelectPatternsResult(BaseModel):
    """The select-patterns nested result (SDD-001 §3.3.1). `patterns` are the
    admitted candidates; `pattern_disclosures` are the conditionally-excluded
    patterns (whole subtree dropped, §4.4). Silently-excluded patterns
    (un-approved proposals, retracted) appear in neither list (§3.2)."""

    patterns: list[PatternCandidate]
    pattern_disclosures: list[DisclosureEntry]


class SelectPatternsRequest(BaseModel):
    """The select-patterns request body (SDD-001 §3.3.1)."""

    capability_ids: list[str]
    consuming_context: ConsumingContextPayload


class PolicyRulePayload(BaseModel):
    """One `PolicyRule`'s content (SDD-001 §3.3.4; DDR-002 §2.5). `statement`
    is the natural-language requirement; `rule_definition` is the opaque
    declarative IF/THEN evaluation logic — carried verbatim, never parsed or
    traversed here (the constraint-validator's job). `dependency_manifest` is
    the declared, introspectable list of Catalog entity-types/labels the rule
    reads."""

    statement: str | None = None
    rule_definition: str | None = None
    dependency_manifest: list[str]
    enforcement_level: str | None = None
    enforced_at_gate: str | None = None
    domain: str | None = None


class ObligationEntry(BaseModel):
    """One applicable `PolicyRule` reached from a solution's `USES`/`FOLLOWS`
    entity set via `GOVERNED_BY`/`MANDATES` (SDD-001 §3.3.4). `envelope`
    carries node_kind="PolicyRule" with plane_labels=("Standards",); the
    applicability block's conditional_admission is the only populated surface
    (catalog_eligibility and deprecation are Technology-only, DDR-002 §2.1).
    `policy_rule` is the rule's content payload."""

    envelope: ResultEnvelope
    policy_rule: PolicyRulePayload


class ObligationContextResult(BaseModel):
    """The obligation-context result (SDD-001 §3.3.4). `obligations` are the
    admitted applicable PolicyRules; `disclosures` are the conditionally-
    excluded ones (§4.4). This is the entity-triggered graph half only —
    condition-triggered rules and the satisfaction join are obligation
    closure, out of scope here (the constraint-validator's)."""

    obligations: list[ObligationEntry]
    disclosures: list[DisclosureEntry]


class ObligationContextRequest(BaseModel):
    """The obligation-context request body (SDD-001 §3.3.4)."""

    solution_id: str
    consuming_context: ConsumingContextPayload
