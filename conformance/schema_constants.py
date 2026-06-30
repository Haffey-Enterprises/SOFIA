##############################################################################
# Module: schema_constants.py
# Service: conformance (repo-level enforcement-mechanization tooling, RBT-33)
# Author: Haffey Enterprises LLC
# Created: 2026-06-22
# Revised: 2026-06-22
# Description: Single source of truth for the DDR-002 graph-schema label,
#   property, edge-type, and enum constants the conformance assertions and the
#   seeded fixtures share (the M-2 fixture/real-schema parity mitigation). Values
#   are fresh-fetched from the committed DDR-002 v1.0.0 §1-§7 — NOT from the
#   substrate's representative Cypher sketches. A future real-schema definition
#   (RBT-15) is intended to source the same names from here.
# Standards: ENG-STD-001 v3.2.0
##############################################################################
"""DDR-002 schema constants shared by conformance assertions and fixtures.

Section references in comments point at the committed DDR-002 v1.0.0
(``docs/ddr/DDR-002-graph-schema.md``). Scope is the RBT-33 Increment-1
(safety-critical tier) surface; the follow-tier (Increment 2) constants extend
this module additively.
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

# --- Provenance property group (DDR-002 §1) -----------------------------------
# The provenance existence constraint (§7) is on origin_mechanism + recorded_at.
PROP_ORIGIN_MECHANISM: Final = "origin_mechanism"
PROP_RECORDED_AT: Final = "recorded_at"
PROP_DERIVATION_CLASS: Final = "derivation_class"
PROP_SOURCE_RECORD_REF: Final = "source_record_ref"

# --- Primary-key properties (DDR-002 §2, §4, §5; <entity>_id per §1) ----------
PROP_EVIDENCE_ID: Final = "evidence_id"
PROP_REJECTED_ID: Final = "rejected_id"
PROP_DECISION_ID: Final = "decision_id"
PROP_CANDIDATE_ID: Final = "candidate_id"

# --- Other Increment-1 properties ---------------------------------------------
PROP_SOURCE_NODE_VERSION: Final = "source_node_version"  # Evidence version pin (§4)
PROP_BUSINESS_KEY: Final = "business_key"  # versioned-type lineage key (§6)
PROP_VERSION: Final = "version"  # version-node discriminator (§6)
PROP_DECIDED_AT: Final = "decided_at"  # governing-edge selector for #15 (§2.4)
PROP_OUTCOME: Final = "outcome"  # DECIDED_ON edge verdict (§2.4, §3)
PROP_APPLICABILITY_STATE: Final = "applicability_state"  # promoted-node marker (§5)

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
# what the #19 read-discipline contract filters on.
APPLICABILITY_STATES: Final[frozenset[str]] = frozenset({"unconditional", "conditional"})

# origin_mechanism values that, per invariant #17, require a source_record_ref:
# every ``ingested`` node, plus every ``distilled`` (derivation_class) node.
ORIGIN_REQUIRES_SOURCE_RECORD_REF: Final = "ingested"  # DDR-002 §7 #17
DERIVATION_REQUIRES_SOURCE_RECORD_REF: Final = "distilled"  # DDR-002 §7 #17
PROMOTED_ORIGIN: Final = "promoted"  # DDR-002 §7 #15 subject
