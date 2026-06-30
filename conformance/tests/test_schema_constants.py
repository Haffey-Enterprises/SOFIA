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


def test_source_record_ref_triggers_are_ingested_and_distilled() -> None:
    assert sc.ORIGIN_REQUIRES_SOURCE_RECORD_REF == "ingested"
    assert sc.DERIVATION_REQUIRES_SOURCE_RECORD_REF == "distilled"
    assert sc.PROMOTED_ORIGIN == "promoted"


def test_plane_labels_exclude_reasoning_and_artifact() -> None:
    # RG and Artifact nodes carry no KG plane label (DDR-002 §1).
    assert sc.RG_LABEL not in sc.KG_PLANE_LABELS
    assert sc.ARTIFACT_LABEL not in sc.KG_PLANE_LABELS
