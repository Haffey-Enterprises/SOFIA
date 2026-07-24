##############################################################################
# Module: schema_constants.py
# Service: conformance (repo-level enforcement-mechanization tooling, RBT-33)
# Author: Haffey Enterprises LLC
# Created: 2026-06-22
# Revised: 2026-07-13
# Description: Single source of truth for the DDR-002 graph-schema label,
#   property, edge-type, and enum constants the conformance assertions and the
#   seeded fixtures share (the M-2 fixture/real-schema parity mitigation). Values
#   are fresh-fetched from the committed DDR-002 v1.4.0 §1-§7 — NOT from the
#   substrate's representative Cypher sketches. A future real-schema definition
#   (RBT-15) is intended to source the same names from here.
#
#   RBT-48 catch-up: refreshed from the v1.0.0 vocabulary to the ratified v1.3.0
#   contract — the full post-v1.0.0 delta. New vocabulary feeds checks #20-#27
#   and the #15 companions: ProvenanceSummary / RETRACTS / MATERIALIZES_
#   PROVENANCE_OF / archived (v1.1.0); reasoner_category / reasoner_ref /
#   authoritative, proposal_kind (v1.2.0); the confidence_basis declaration, the
#   §2 four-basis enumeration + core-plane basis-resolution map, NON_CITABLE_
#   SOURCE (v1.3.0).
#   RBT-62 (v1.4.0): pin catch-up to the v1.4.0 contract, which adds §7 check #28
#   (Evidence.confidence presence, follow tier). No new labels/props/enums — #28
#   reuses the existing confidence surface (PROP_CONFIDENCE, EVIDENCE_LABEL,
#   RG_LABEL, PROP_EVIDENCE_ID); the refresh is the pin + PROP_CONFIDENCE's
#   #24/#28 co-ownership annotation only.
# Authority: DDR-002 v1.4.0 — docs/ddr/DDR-002-graph-schema.md, content sha256
#   2fdd403b6b5ee0477ffa2f9ab8cc7f4ef43601e413c38ed08202e9e74deaa32e. This
#   module is a vendored snapshot of that canonical text; the pin above is what a
#   currency check keys on (F4 / RBT-54). Re-fetch and re-verify the pin before
#   any refresh.
# Standards: ENG-STD-001 v3.2.0
##############################################################################
"""DDR-002 schema constants shared by conformance assertions and fixtures.

Section references in comments point at the committed DDR-002 v1.4.0
(``docs/ddr/DDR-002-graph-schema.md``). The Increment-1 (safety-critical tier)
surface, the RBT-48 catch-up checks (#20-#27, #15 companions), and the RBT-62
v1.4.0 addition (#28) all source their labels/props/edges/enums here.
"""

from typing import Final

# --- Graph-family discriminator labels (DDR-002 §1, §3, §4, §5) ---------------
# KG nodes carry a secondary plane label; RG nodes carry ``Reasoning``; the
# Artifact family carries ``Artifact``. RG and Artifact nodes carry NO plane
# label (DDR-002 §1 "Plane membership — hybrid"), which is how plane-scoped
# ground-truth traversals structurally skip reasoning state and artifacts.
RG_LABEL: Final = "Reasoning"
ARTIFACT_LABEL: Final = "Artifact"

# The five core planes (DDR-001) + Extension + the Cost first-registration
# (DDR-002 §2). Membership in this set is how an assertion recognises a
# "provenance-bearing KG node" (the SOURCED_FROM target in invariant #1).
KG_PLANE_LABELS: Final[frozenset[str]] = frozenset(
    {"Catalog", "Environment", "Operational", "Governance", "Standards", "Extension", "Cost"}
)

# --- Node labels referenced by the Increment-1 invariants ---------------------
# Reasoning Graph (DDR-002 §4).
EVIDENCE_LABEL: Final = "Evidence"  # (:Reasoning:Evidence)
REASONING_PROGRESS_LABEL: Final = "ReasoningProgress"
REJECTED_ALTERNATIVE_LABEL: Final = "RejectedAlternative"
REASONING_SESSION_LABEL: Final = "ReasoningSession"
CANDIDATE_PROMOTION_LABEL: Final = "CandidatePromotion"  # (:Reasoning:CandidatePromotion)
PROVENANCE_SUMMARY_LABEL: Final = "ProvenanceSummary"  # (:Reasoning:ProvenanceSummary); §4, #20

# Operational plane (DDR-002 §2.3) — a PROPOSED_FROM target in the #20 span
# (contributes nothing to freeze: a durable, live-traversable KG node).
OBSERVED_PATTERN_LABEL: Final = "ObservedPattern"

# Extension registry (DDR-002 §2.6) — the #26 basis-declaration-totality subject.
PLANE_DEFINITION_LABEL: Final = "PlaneDefinition"  # (:Extension:PlaneDefinition)

# Governance decision supertype + subtypes (DDR-002 §2.4).
DECISION_LABEL: Final = "Decision"
GATE_DECISION_LABEL: Final = "GateDecision"
PROMOTION_DECISION_LABEL: Final = "PromotionDecision"
CONDITION_LABEL: Final = "Condition"

# The exactly-one-of subtype set for invariant #16 (DDR-002 §7 #16, §2.4).
DECISION_SUBTYPE_LABELS: Final[frozenset[str]] = frozenset(
    {GATE_DECISION_LABEL, PROMOTION_DECISION_LABEL}
)

# --- Edge types (DDR-002 §3, §5) ----------------------------------------------
SOURCED_FROM: Final = "SOURCED_FROM"  # (Evidence)->(KG node); §5, mandatory (#1/#14)
REJECTED: Final = "REJECTED"  # (ReasoningProgress)->(RejectedAlternative); §4
PROMOTES_TO_KNOWLEDGE: Final = "PROMOTES_TO_KNOWLEDGE"  # (CandidatePromotion)->(KG node); §5
DECIDED_ON: Final = "DECIDED_ON"  # (Decision)->(target) carrying {outcome}; §3, §5
HAS_CONDITION: Final = "HAS_CONDITION"  # (PromotionDecision)->(Condition); §2.4, §5

# Promotion / provenance-survival edges (DDR-002 §5). PROPOSED_FROM + SUPPORTED_BY
# are the two Evidence-reaching paths of the #20 span closure; RETRACTS is the
# reversing-candidate un-promotion edge (#21/#25); MATERIALIZES_PROVENANCE_OF
# binds the at-promotion ProvenanceSummary to its durable candidate (#20).
PROPOSED_FROM: Final = "PROPOSED_FROM"  # (CandidatePromotion)->(RP|Evidence|ObservedPattern|RA)
SUPPORTED_BY: Final = "SUPPORTED_BY"  # (ReasoningProgress)->(Evidence); §4, #20/#24
RETRACTS: Final = "RETRACTS"  # (CandidatePromotion{retraction})->(KG node); §5, #21/#25
MATERIALIZES_PROVENANCE_OF: Final = "MATERIALIZES_PROVENANCE_OF"  # (ProvSummary)->(CandPromotion)

# --- Provenance property group (DDR-002 §1) -----------------------------------
# The provenance existence constraint (§7) is on origin_mechanism + recorded_at.
PROP_ORIGIN_MECHANISM: Final = "origin_mechanism"
PROP_RECORDED_AT: Final = "recorded_at"
PROP_DERIVATION_CLASS: Final = "derivation_class"
PROP_SOURCE_RECORD_REF: Final = "source_record_ref"

# --- Primary-key properties (DDR-002 §2, §4, §5; <entity>_id per §1) ----------
PROP_EVIDENCE_ID: Final = "evidence_id"
PROP_PROGRESS_ID: Final = "progress_id"  # (:Reasoning:ReasoningProgress) PK; §4
PROP_REJECTED_ID: Final = "rejected_id"
PROP_DECISION_ID: Final = "decision_id"
PROP_CANDIDATE_ID: Final = "candidate_id"
PROP_PROVENANCE_SUMMARY_ID: Final = "provenance_summary_id"  # (:ProvenanceSummary) PK; §4
PROP_PLANE_ID: Final = "plane_id"  # (:PlaneDefinition) PK; §2.6

# --- Other Increment-1 properties ---------------------------------------------
PROP_SOURCE_NODE_VERSION: Final = "source_node_version"  # Evidence version pin (§4)
PROP_BUSINESS_KEY: Final = "business_key"  # versioned-type lineage key (§6)
PROP_VERSION: Final = "version"  # version-node discriminator (§6)
PROP_DECIDED_AT: Final = "decided_at"  # governing-edge selector for #15 (§2.4)
PROP_OUTCOME: Final = "outcome"  # DECIDED_ON edge verdict (§2.4, §3)
PROP_APPLICABILITY_STATE: Final = "applicability_state"  # promoted-node marker (§5)

# --- Catch-up (DDR-002 v1.3.0) properties -------------------------------------
PROP_STATUS: Final = "status"  # lifecycle / version status (§2.3, §5, §6)
PROP_SUPERSEDED_BY: Final = "superseded_by"  # versioned supersession pointer (§6); #22
VERSION_STATUS_ACTIVE: Final = "active"  # the one active version per business_key (§6)
PROP_CONFIDENCE: Final = "confidence"  # node/edge confidence scalar (§3, §4); #24/#28

# CandidatePromotion direction discriminator (DDR-002 §5).
PROP_PROPOSAL_KIND: Final = "proposal_kind"

# ReasoningProgress reasoner attribution (DDR-002 §4); #23 keys on the first two.
PROP_REASONER_CATEGORY: Final = "reasoner_category"
PROP_REASONER_REF: Final = "reasoner_ref"
PROP_AUTHORITATIVE: Final = "authoritative"

# ProvenanceSummary frozen-layer arrays (DDR-002 §4) — index-aligned, keyed by
# evidence_id; #20 completeness is set-equality on frozen_evidence_ids.
PROP_FROZEN_EVIDENCE_IDS: Final = "frozen_evidence_ids"
PROP_FROZEN_FACT_SUMMARIES: Final = "frozen_fact_summaries"
PROP_FROZEN_SOURCE_VERSION_PINS: Final = "frozen_source_version_pins"
PROP_FROZEN_SOURCE_NODE_REFS: Final = "frozen_source_node_refs"

# PlaneDefinition declaration properties (DDR-002 §2.6); #26 checks confidence_basis
# and property_schema for key-set equality.
PROP_ATTACHES_TO: Final = "attaches_to"
PROP_PROPERTY_SCHEMA: Final = "property_schema"
PROP_CONFIDENCE_BASIS: Final = "confidence_basis"

# --- Enum value-sets (DDR-002 §1, §2.4, §5) -----------------------------------
# origin_mechanism — how a node entered (DDR-002 §1). Always present, invariant-
# bearing; this is the valid-value set invariant #11 checks.
ORIGIN_MECHANISMS: Final[frozenset[str]] = frozenset(
    {"ingested", "authored", "promoted", "derived"}
)

# derivation_class — nature of the content (DDR-002 §1). N/A for promoted.
DERIVATION_CLASSES: Final[frozenset[str]] = frozenset({"primary", "distilled", "aggregated"})

# DECIDED_ON outcome verdicts (DDR-002 §2.4); the approving subset is keyed by
# invariant #15 (promoted-origin -> governing approving decision).
DECISION_OUTCOMES: Final[frozenset[str]] = frozenset(
    {"approved", "approved_conditional", "rejected"}
)
APPROVING_OUTCOMES: Final[frozenset[str]] = frozenset({"approved", "approved_conditional"})

# applicability_state on promoted KG nodes (DDR-002 §5); the conditional value is
# what the #19 read-discipline contract filters on and the #22 carry-forward keys.
APPLICABILITY_STATES: Final[frozenset[str]] = frozenset({"unconditional", "conditional"})
APPLICABILITY_STATE_CONDITIONAL: Final = "conditional"  # #19/#22 subject
APPLICABILITY_STATE_UNCONDITIONAL: Final = "unconditional"  # §5 default

# origin_mechanism values that, per invariant #17, require a source_record_ref:
# every ``ingested`` node, plus every ``distilled`` (derivation_class) node.
ORIGIN_REQUIRES_SOURCE_RECORD_REF: Final = "ingested"  # DDR-002 §7 #17
DERIVATION_REQUIRES_SOURCE_RECORD_REF: Final = "distilled"  # DDR-002 §7 #17
PROMOTED_ORIGIN: Final = "promoted"  # DDR-002 §7 #15 subject

# --- Catch-up (DDR-002 v1.3.0) enum value-sets --------------------------------
# proposal_kind — CandidatePromotion direction discriminator (DDR-002 §5). #25
# keys the executed-proposal biconditional off the retraction value.
PROPOSAL_KINDS: Final[frozenset[str]] = frozenset({"promotion", "retraction"})
PROPOSAL_KIND_PROMOTION: Final = "promotion"  # forward promotion; #20 subject
PROPOSAL_KIND_RETRACTION: Final = "retraction"  # reversing un-promotion; #21/#25

# CandidatePromotion lifecycle status (DDR-002 §5). Terminal ``promoted`` denotes
# the proposal's effect was materialized — read uniformly across both
# proposal_kinds (for a retraction: the un-promotion applied). #20/#25 subject.
CANDIDATE_STATUSES: Final[frozenset[str]] = frozenset(
    {"proposed", "under_review", "approved", "approved_conditional", "rejected", "promoted"}
)
CANDIDATE_STATUS_PROMOTED: Final = "promoted"  # terminal-executed; DDR-002 §7 #20/#25

# ReasoningProgress.reasoner_category — ADR-001 §2.2's four categories (DDR-002 §4).
REASONER_CATEGORIES: Final[frozenset[str]] = frozenset(
    {"encoded_reasoning", "specialized_agent", "llm_advisory", "human_override"}
)
# reasoner_ref is required when the category is specialized_agent (DDR-002 §4).
REASONER_CATEGORY_REQUIRING_REF: Final = "specialized_agent"
# The fixed reasoner_category -> authoritative mapping (#23): ``llm_advisory``
# maps to False, every other category to True. Named as the sole non-authoritative
# category so the mapping stays a single fact (DDR-002 §4, §7 #23).
NON_AUTHORITATIVE_CATEGORY: Final = "llm_advisory"

# ObservedPattern.status (DDR-002 §2.3); ``archived`` is the v1.1.0 retention-
# tier-demotion value (never hard-deletion).
OBSERVED_PATTERN_STATUSES: Final[frozenset[str]] = frozenset(
    {"active", "superseded", "resolved", "archived"}
)
OBSERVED_PATTERN_STATUS_ARCHIVED: Final = "archived"

# confidence-derivation bases — the §2 four-way enumeration (DDR-002 §2 preamble,
# §2.6). Basis KIND only, no values (derivation semantics/values are DDR-004's).
CONFIDENCE_BASES: Final[frozenset[str]] = frozenset(
    {"native_confidence", "flat_base", "aging", "non_citable"}
)
# The citable subset — a SOURCED_FROM target must resolve to one of these (#27).
CITABLE_BASES: Final[frozenset[str]] = frozenset({"native_confidence", "flat_base", "aging"})
NON_CITABLE_BASIS: Final = "non_citable"  # basis 4; #27 rejects inbound SOURCED_FROM
AGING_BASIS: Final = "aging"  # the one operand-bearing basis (#26 operand-iff-aging)

# --- Core-plane confidence-derivation basis resolution (DDR-002 §2.1-§2.6) -----
# Basis KINDS are DDR-002 carriage (the map below); derivation values/semantics
# are DDR-004's — never encoded here.
# Plane-level declared basis per core KG plane; #27 resolves a SOURCED_FROM
# target's basis from its plane label, then applies any per-label override below.
# Extension/Cost nodes resolve their basis from the ``PlaneDefinition.
# confidence_basis`` declaration in the graph (§2.6), not from this static map.
CORE_PLANE_BASIS: Final[dict[str, str]] = {
    "Catalog": "flat_base",  # §2.1 — versioned authoritative ground truth
    "Environment": "aging",  # §2.2 — freshness operand observed_at
    "Operational": "native_confidence",  # §2.3 — lesson reliability
    "Governance": "flat_base",  # §2.4 — immutable append-only record
    "Standards": "flat_base",  # §2.5 — versioned authoritative ground truth
}
# Per-label overrides on a plane-level basis (DDR-002 §2.2): DeploymentEnvironment
# is the structurally-stable Environment member — a realized identity that does
# not age, so flat_base, not the plane's aging signature.
NODE_LABEL_BASIS_OVERRIDES: Final[dict[str, str]] = {
    "DeploymentEnvironment": "flat_base",  # §2.2 per-label override
}

# --- Gateway rejection type strings (1b contract vocabulary) ------------------
# A well-formed citation of a non_citable-basis class is rejected typed at capture
# — the declared-contract steering rejection, distinct from CONFIDENCE_UNDERIVABLE
# (DDR-002 §2.6; SDD-001 §3.2). #27's gateway write-time half.
NON_CITABLE_SOURCE: Final = "NON_CITABLE_SOURCE"
