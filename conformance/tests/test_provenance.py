##############################################################################
# Module: test_provenance.py
# Service: conformance (RBT-33)
# Author: Haffey Enterprises LLC
# Created: 2026-06-22
# Revised: 2026-06-22
# Description: Validator-correctness tests for the provenance-cluster assertions
#   (DDR-002 §7 #1, #11, #15, #17, DDR-001 check 5) — each assertion must pass
#   the conformant fixture and catch every seeded violation fixture.
# Standards: ENG-STD-001 v3.2.0
##############################################################################
"""Tests: provenance assertions vs. their conformant / violation fixtures."""

from neo4j import Driver

from conformance.assertions import provenance
from conformance.fixtures import provenance as fx
from conformance.fixtures.seeding import seed


# --- #1 RG-provenance edges ---------------------------------------------------
def test_evidence_with_valid_source_passes(graph: Driver) -> None:
    seed(graph, fx.RG_PROVENANCE_CONFORMANT)
    assert provenance.evidence_missing_sourced_from(graph) == []


def test_evidence_without_source_is_caught(graph: Driver) -> None:
    seed(graph, fx.EVIDENCE_WITHOUT_SOURCE)
    violations = provenance.evidence_missing_sourced_from(graph)
    assert [v.identity for v in violations] == ["ev-orphan"]
    assert violations[0].invariant == "DDR-002 §7 #1"


def test_evidence_sourced_from_non_kg_node_is_caught(graph: Driver) -> None:
    seed(graph, fx.EVIDENCE_SOURCED_FROM_NON_KG)
    violations = provenance.evidence_missing_sourced_from(graph)
    assert [v.identity for v in violations] == ["ev-badsrc"]


def test_rejected_alternative_with_one_parent_passes(graph: Driver) -> None:
    seed(graph, fx.RG_PROVENANCE_CONFORMANT)
    assert provenance.rejected_alternative_parent_cardinality(graph) == []


def test_rejected_alternative_with_no_parent_is_caught(graph: Driver) -> None:
    seed(graph, fx.REJECTED_ALTERNATIVE_NO_PARENT)
    violations = provenance.rejected_alternative_parent_cardinality(graph)
    assert [v.identity for v in violations] == ["ra-orphan"]
    assert violations[0].invariant == "DDR-002 §7 #1"


def test_rejected_alternative_with_two_parents_is_caught(graph: Driver) -> None:
    seed(graph, fx.REJECTED_ALTERNATIVE_TWO_PARENTS)
    violations = provenance.rejected_alternative_parent_cardinality(graph)
    assert [v.identity for v in violations] == ["ra-double"]


# --- #11 provenance distinguishability ----------------------------------------
def test_valid_origin_mechanisms_pass(graph: Driver) -> None:
    seed(graph, fx.ORIGIN_MECHANISM_CONFORMANT)
    assert provenance.origin_mechanism_invalid_value(graph) == []


def test_invalid_origin_mechanism_value_is_caught(graph: Driver) -> None:
    seed(graph, fx.ORIGIN_MECHANISM_INVALID_VALUE)
    violations = provenance.origin_mechanism_invalid_value(graph)
    assert len(violations) == 1
    assert violations[0].invariant == "DDR-002 §7 #11"
    assert "made_up" in violations[0].detail


# --- #15 promoted -> governing approving decision -----------------------------
def test_promoted_with_governing_approval_passes(graph: Driver) -> None:
    # Includes the re-approved (earlier rejected, later approved) and the
    # approved_conditional cases — all governed by an approving verdict.
    seed(graph, fx.PROMOTED_GOVERNING_CONFORMANT)
    assert provenance.promoted_without_governing_approval(graph) == []


def test_promoted_with_superseded_approval_is_caught(graph: Driver) -> None:
    # The trap: latest verdict is 'rejected', earlier 'approved'. Must be caught.
    seed(graph, fx.PROMOTED_SUPERSEDED_APPROVAL_VIOLATION)
    violations = provenance.promoted_without_governing_approval(graph)
    assert [v.identity for v in violations] == ["pat-sup"]
    assert violations[0].invariant == "DDR-002 §7 #15"


def test_promoted_without_any_decision_is_caught(graph: Driver) -> None:
    seed(graph, fx.PROMOTED_NO_DECISION_VIOLATION)
    violations = provenance.promoted_without_governing_approval(graph)
    assert [v.identity for v in violations] == ["pat-nodec"]


# --- #17 ingested/distilled -> source_record_ref ------------------------------
def test_source_record_ref_present_and_aggregated_exempt_pass(graph: Driver) -> None:
    # The aggregated node carries no source_record_ref and must NOT be flagged.
    seed(graph, fx.SOURCE_RECORD_REF_CONFORMANT)
    assert provenance.missing_source_record_ref(graph) == []


def test_ingested_without_source_record_ref_is_caught(graph: Driver) -> None:
    seed(graph, fx.INGESTED_MISSING_SOURCE_RECORD_REF)
    violations = provenance.missing_source_record_ref(graph)
    assert [v.identity for v in violations] == ["cap-noref"]
    assert violations[0].invariant == "DDR-002 §7 #17"


def test_distilled_without_source_record_ref_is_caught(graph: Driver) -> None:
    seed(graph, fx.DISTILLED_MISSING_SOURCE_RECORD_REF)
    violations = provenance.missing_source_record_ref(graph)
    assert [v.identity for v in violations] == ["op-noref"]


# --- DDR-001 check 5: Evidence version-pin integrity --------------------------
def test_resolving_version_pin_passes(graph: Driver) -> None:
    # Pinned version 1 resolves to the retained v1 of the cited lineage.
    seed(graph, fx.EVIDENCE_VERSION_PIN_CONFORMANT)
    assert provenance.evidence_dangling_version_pin(graph) == []


def test_dangling_version_pin_is_caught(graph: Driver) -> None:
    # Pinned version 1 has no retained version node in the cited lineage.
    seed(graph, fx.EVIDENCE_DANGLING_VERSION_PIN)
    violations = provenance.evidence_dangling_version_pin(graph)
    assert [v.identity for v in violations] == ["ev-dangling"]
    assert violations[0].invariant == "DDR-001 check 5"
