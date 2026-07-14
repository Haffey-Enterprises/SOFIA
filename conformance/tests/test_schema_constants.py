##############################################################################
# Module: test_schema_constants.py
# Service: conformance (RBT-33)
# Author: Haffey Enterprises LLC
# Created: 2026-06-22
# Revised: 2026-06-22
# Description: Locks the DDR-002-fresh-fetched enum value-sets in the shared
#   schema-constants module against silent drift. These are the value-sets the
#   Increment-1 assertions key on (#11 origin_mechanism, #15 approving outcomes,
#   #16 decision subtypes, #17 source_record_ref triggers, #19 applicability).
# Standards: ENG-STD-001 v3.2.0
##############################################################################
"""Guard the fresh-fetched DDR-002 §1/§2.4/§5/§7 enum value-sets."""

from conformance import schema_constants as sc


def test_origin_mechanisms_match_ddr_002_section_1() -> None:
    assert sc.ORIGIN_MECHANISMS == {"ingested", "authored", "promoted", "derived"}


def test_derivation_classes_match_ddr_002_section_1() -> None:
    assert sc.DERIVATION_CLASSES == {"primary", "distilled", "aggregated"}


def test_approving_outcomes_are_the_two_approval_verdicts() -> None:
    assert sc.APPROVING_OUTCOMES == {"approved", "approved_conditional"}
    assert sc.APPROVING_OUTCOMES < sc.DECISION_OUTCOMES
    assert "rejected" not in sc.APPROVING_OUTCOMES


def test_decision_subtypes_are_gate_and_promotion() -> None:
    assert sc.DECISION_SUBTYPE_LABELS == {"GateDecision", "PromotionDecision"}


def test_applicability_states_match_ddr_002_section_5() -> None:
    assert sc.APPLICABILITY_STATES == {"unconditional", "conditional"}
    # The singleton values #19/#22 key on and §5's default; pinned as vocabulary.
    assert sc.APPLICABILITY_STATE_CONDITIONAL == "conditional"
    assert sc.APPLICABILITY_STATE_UNCONDITIONAL == "unconditional"
    assert {sc.APPLICABILITY_STATE_CONDITIONAL, sc.APPLICABILITY_STATE_UNCONDITIONAL} == (
        sc.APPLICABILITY_STATES
    )


def test_source_record_ref_triggers_are_ingested_and_distilled() -> None:
    assert sc.ORIGIN_REQUIRES_SOURCE_RECORD_REF == "ingested"
    assert sc.DERIVATION_REQUIRES_SOURCE_RECORD_REF == "distilled"
    assert sc.PROMOTED_ORIGIN == "promoted"


def test_plane_labels_exclude_reasoning_and_artifact() -> None:
    # RG and Artifact nodes carry no KG plane label (DDR-002 §1).
    assert sc.RG_LABEL not in sc.KG_PLANE_LABELS
    assert sc.ARTIFACT_LABEL not in sc.KG_PLANE_LABELS


# --- RBT-48 catch-up: DDR-002 v1.3.0 vocabulary --------------------------------
# The value-sets the catch-up checks (#20-#27, #15 companions) key on.


def test_proposal_kinds_match_ddr_002_section_5() -> None:
    # CandidatePromotion.proposal_kind direction discriminator (DDR-002 §5).
    assert sc.PROPOSAL_KINDS == {"promotion", "retraction"}
    assert sc.PROPOSAL_KIND_RETRACTION == "retraction"
    assert sc.PROPOSAL_KIND_RETRACTION in sc.PROPOSAL_KINDS


def test_candidate_statuses_match_ddr_002_section_5() -> None:
    # CandidatePromotion lifecycle status (DDR-002 §5); 'promoted' is terminal-
    # executed and is the subject of #20 (materialization) and #25 (executed
    # proposal scoping).
    assert sc.CANDIDATE_STATUSES == {
        "proposed",
        "under_review",
        "approved",
        "approved_conditional",
        "rejected",
        "promoted",
    }
    assert sc.CANDIDATE_STATUS_PROMOTED == "promoted"
    assert sc.CANDIDATE_STATUS_PROMOTED in sc.CANDIDATE_STATUSES


def test_reasoner_categories_are_adr_001_four() -> None:
    # ReasoningProgress.reasoner_category — ADR-001 §2.2's four categories (§4).
    assert sc.REASONER_CATEGORIES == {
        "encoded_reasoning",
        "specialized_agent",
        "llm_advisory",
        "human_override",
    }
    # reasoner_ref is required for specialized_agent (DDR-002 §4).
    assert sc.REASONER_CATEGORY_REQUIRING_REF == "specialized_agent"
    assert sc.REASONER_CATEGORY_REQUIRING_REF in sc.REASONER_CATEGORIES


def test_non_authoritative_category_is_only_llm_advisory() -> None:
    # #23 fixed mapping: llm_advisory -> authoritative False, all others -> True.
    assert sc.NON_AUTHORITATIVE_CATEGORY == "llm_advisory"
    assert sc.NON_AUTHORITATIVE_CATEGORY in sc.REASONER_CATEGORIES


def test_reasoner_ref_property_name() -> None:
    # DDR-002 §4: the specific reasoner, required when reasoner_category is
    # specialized_agent. No numbered §7 check consumes it (write-time / SDD
    # concern), so it is pinned here as vocabulary against drift.
    assert sc.PROP_REASONER_REF == "reasoner_ref"


def test_observed_pattern_statuses_include_archived() -> None:
    # 'archived' is the v1.1.0 retention-tier-demotion status value (DDR-002 §2.3).
    assert sc.OBSERVED_PATTERN_STATUSES == {"active", "superseded", "resolved", "archived"}
    assert sc.OBSERVED_PATTERN_STATUS_ARCHIVED == "archived"
    assert sc.OBSERVED_PATTERN_STATUS_ARCHIVED in sc.OBSERVED_PATTERN_STATUSES


def test_confidence_bases_are_the_four_way_enumeration() -> None:
    # DDR-002 §2 preamble / §2.6 — basis kind only, no values (DDR-004's).
    assert sc.CONFIDENCE_BASES == {"native_confidence", "flat_base", "aging", "non_citable"}


def test_citable_bases_exclude_only_non_citable() -> None:
    # #27 admissibility: a SOURCED_FROM target must resolve to a citable basis.
    assert sc.CITABLE_BASES == {"native_confidence", "flat_base", "aging"}
    assert sc.CITABLE_BASES < sc.CONFIDENCE_BASES
    assert sc.NON_CITABLE_BASIS == "non_citable"
    assert sc.NON_CITABLE_BASIS not in sc.CITABLE_BASES
    assert sc.CITABLE_BASES == sc.CONFIDENCE_BASES - {sc.NON_CITABLE_BASIS}


def test_aging_basis_is_the_operand_bearing_basis() -> None:
    # #26 operand-iff-aging: only the aging basis carries a freshness operand.
    assert sc.AGING_BASIS == "aging"
    assert sc.AGING_BASIS in sc.CITABLE_BASES


def test_core_plane_basis_resolution_matches_ddr_002_sections_2_1_to_2_5() -> None:
    # Plane-level declared basis per core KG plane (DDR-002 §2.1-§2.5).
    assert sc.CORE_PLANE_BASIS == {
        "Catalog": "flat_base",
        "Environment": "aging",
        "Operational": "native_confidence",
        "Governance": "flat_base",
        "Standards": "flat_base",
    }
    # Every declared plane basis is a member of the four-way enumeration.
    assert set(sc.CORE_PLANE_BASIS.values()) <= sc.CONFIDENCE_BASES
    # The core planes carry no non_citable class (only Extension/Cost can, §2.6).
    assert sc.NON_CITABLE_BASIS not in sc.CORE_PLANE_BASIS.values()


def test_deployment_environment_overrides_environment_aging_to_flat_base() -> None:
    # DDR-002 §2.2 per-label override: DeploymentEnvironment is a realized identity
    # that does not age, so flat_base, not the plane's aging signature.
    assert sc.NODE_LABEL_BASIS_OVERRIDES == {"DeploymentEnvironment": "flat_base"}
    assert sc.CORE_PLANE_BASIS["Environment"] == "aging"
    assert sc.NODE_LABEL_BASIS_OVERRIDES["DeploymentEnvironment"] == "flat_base"


def test_new_labels_and_edges_are_the_ddr_002_v1_3_0_names() -> None:
    assert sc.PROVENANCE_SUMMARY_LABEL == "ProvenanceSummary"
    assert sc.PLANE_DEFINITION_LABEL == "PlaneDefinition"
    assert sc.OBSERVED_PATTERN_LABEL == "ObservedPattern"
    assert sc.PROPOSED_FROM == "PROPOSED_FROM"
    assert sc.SUPPORTED_BY == "SUPPORTED_BY"
    assert sc.RETRACTS == "RETRACTS"
    assert sc.MATERIALIZES_PROVENANCE_OF == "MATERIALIZES_PROVENANCE_OF"


def test_provenance_summary_frozen_arrays_are_the_four_keyed_arrays() -> None:
    # The four index-aligned, evidence_id-keyed frozen arrays (DDR-002 §4).
    assert sc.PROP_FROZEN_EVIDENCE_IDS == "frozen_evidence_ids"
    assert sc.PROP_FROZEN_FACT_SUMMARIES == "frozen_fact_summaries"
    assert sc.PROP_FROZEN_SOURCE_VERSION_PINS == "frozen_source_version_pins"
    assert sc.PROP_FROZEN_SOURCE_NODE_REFS == "frozen_source_node_refs"


def test_plane_definition_declaration_properties() -> None:
    # The declarations #26 checks for key-set equality (DDR-002 §2.6).
    assert sc.PROP_ATTACHES_TO == "attaches_to"
    assert sc.PROP_PROPERTY_SCHEMA == "property_schema"
    assert sc.PROP_CONFIDENCE_BASIS == "confidence_basis"


def test_non_citable_source_rejection_type() -> None:
    # The declared-contract steering rejection for a non_citable citation (§2.6).
    assert sc.NON_CITABLE_SOURCE == "NON_CITABLE_SOURCE"


def test_version_status_active_is_the_active_version_value() -> None:
    # §6 one-active-version-per-business_key; #27 resolves off the active plane.
    assert sc.VERSION_STATUS_ACTIVE == "active"
