##############################################################################
# Module: test_extension.py
# Service: conformance (RBT-48 catch-up)
# Author: Haffey Enterprises LLC
# Created: 2026-07-13
# Revised: 2026-07-13
# Description: Validator-correctness tests for the confidence-basis graph-state
#   assertions — DDR-002 §7 #26 (basis-declaration totality) and #27 (basis-
#   admissibility: every SOURCED_FROM target resolves to a citable basis; a
#   non_citable class carries no inbound SOURCED_FROM). Each assertion is exercised
#   against its conformant + violation fixtures.
# Standards: ENG-STD-001 v3.2.0
##############################################################################
"""Tests: the Extension-registry assertions vs. their conformant / violation fixtures.

Covers DDR-002 §7 #26 (basis-declaration totality) and #27 (basis-admissibility).
"""

from neo4j import Driver

from conformance.assertions import extension
from conformance.fixtures import extension as fx
from conformance.fixtures.seeding import seed


# --- #26 basis-declaration totality -------------------------------------------
def test_totality_conformant_registrations_pass(graph: Driver) -> None:
    # The §2.6 cost-plane exemplar (three non-aging labels) + an aging plane with
    # its freshness operand — both totality-conformant.
    seed(graph, fx.BASIS_DECLARATION_CONFORMANT)
    assert extension.basis_declaration_totality(graph) == []


def test_label_without_a_basis_is_caught(graph: Driver) -> None:
    # property_schema declares a label that confidence_basis omits — key-set
    # inequality (a label without a basis).
    seed(graph, fx.LABEL_WITHOUT_BASIS)
    violations = extension.basis_declaration_totality(graph)
    assert [v.identity for v in violations] == ["plane-label-nobasis"]
    assert violations[0].invariant == "DDR-002 §7 #26"


def test_basis_for_undeclared_label_is_caught(graph: Driver) -> None:
    # confidence_basis declares a label property_schema omits — the other key-set
    # inequality direction (a basis for an undeclared label).
    seed(graph, fx.BASIS_FOR_UNDECLARED_LABEL)
    violations = extension.basis_declaration_totality(graph)
    assert [v.identity for v in violations] == ["plane-extrabasis"]


def test_invalid_basis_value_is_caught(graph: Driver) -> None:
    seed(graph, fx.INVALID_BASIS_VALUE)
    violations = extension.basis_declaration_totality(graph)
    assert [v.identity for v in violations] == ["plane-badbasis"]


def test_aging_label_without_operand_is_caught(graph: Driver) -> None:
    seed(graph, fx.AGING_WITHOUT_OPERAND)
    violations = extension.basis_declaration_totality(graph)
    assert [v.identity for v in violations] == ["plane-aging-noop"]


def test_non_aging_label_with_stray_operand_is_caught(graph: Driver) -> None:
    seed(graph, fx.STRAY_OPERAND_ON_NON_AGING)
    violations = extension.basis_declaration_totality(graph)
    assert [v.identity for v in violations] == ["plane-strayop"]


def test_missing_declaration_is_caught(graph: Driver) -> None:
    # confidence_basis / property_schema are T2 — no DB existence constraint forces
    # them. A PlaneDefinition missing either cannot be verified for totality, so a
    # follow-tier check must still fail loud rather than skip (the A-1/A-3 pattern).
    seed(graph, fx.MISSING_DECLARATION)
    violations = extension.basis_declaration_totality(graph)
    assert [v.identity for v in violations] == ["plane-nodecl"]


def test_unparseable_declaration_is_caught(graph: Driver) -> None:
    # A present-but-unparseable declaration is unverifiable — fail loud, not skip.
    seed(graph, fx.UNPARSEABLE_DECLARATION)
    violations = extension.basis_declaration_totality(graph)
    assert [v.identity for v in violations] == ["plane-unparseable"]


def test_malformed_label_declaration_is_caught(graph: Driver) -> None:
    # A label mapped to a bare string (not a {"basis": ...} object) is malformed.
    seed(graph, fx.MALFORMED_LABEL_DECLARATION)
    violations = extension.basis_declaration_totality(graph)
    assert [v.identity for v in violations] == ["plane-malformed"]
    assert "malformed" in violations[0].detail


def test_non_string_declaration_is_caught(graph: Driver) -> None:
    # A declaration stored as a non-string property is not a serialized declaration.
    seed(graph, fx.NON_STRING_DECLARATION)
    violations = extension.basis_declaration_totality(graph)
    assert [v.identity for v in violations] == ["plane-nonstring"]


def test_non_object_json_declaration_is_caught(graph: Driver) -> None:
    # Valid JSON but not an object (a JSON array) — no top-level label map.
    seed(graph, fx.NON_OBJECT_JSON_DECLARATION)
    violations = extension.basis_declaration_totality(graph)
    assert [v.identity for v in violations] == ["plane-nonobject"]


def test_duplicate_label_key_is_caught(graph: Driver) -> None:
    # A-4 serialization-collapse: a duplicate label key survives in the stored
    # bytes but json.loads keeps last-wins — the object_pairs_hook must reject it
    # so the "exactly one basis per label" violation is not eaten before the check.
    seed(graph, fx.DUPLICATE_LABEL_KEY)
    violations = extension.basis_declaration_totality(graph)
    assert [v.identity for v in violations] == ["plane-dupkey"]
    assert "duplicate key" in violations[0].detail


# --- #27 basis-admissibility --------------------------------------------------
def test_admissible_citations_pass(graph: Driver) -> None:
    # SOURCED_FROM a core-plane node (Catalog flat_base) and a Cost estimate
    # (native_confidence, declared in the cost PlaneDefinition) — both citable.
    seed(graph, fx.BASIS_ADMISSIBILITY_CONFORMANT)
    assert extension.basis_admissibility(graph) == []


def test_non_citable_source_is_caught(graph: Driver) -> None:
    # SOURCED_FROM a Cost:RateCard — declared non_citable in the cost
    # PlaneDefinition; the citation is inadmissible (DDR-002 §7 #27 / §2.6).
    seed(graph, fx.SOURCED_FROM_NON_CITABLE)
    violations = extension.basis_admissibility(graph)
    assert [v.identity for v in violations] == ["ev-ratecard"]
    assert violations[0].invariant == "DDR-002 §7 #27"


def test_unresolvable_basis_source_is_caught(graph: Driver) -> None:
    # SOURCED_FROM a node whose class declares no basis (an unregistered Extension
    # label) — admissibility unverifiable, fail loud (the A-1 pattern).
    seed(graph, fx.SOURCED_FROM_UNRESOLVABLE_BASIS)
    violations = extension.basis_admissibility(graph)
    assert [v.identity for v in violations] == ["ev-mystery"]
    assert "no declared basis" in violations[0].detail


def test_superseded_version_declaration_does_not_govern(graph: Driver) -> None:
    # A-5 version-filtering: a citation of RateCard resolves from the ACTIVE plane
    # version (non_citable), not the superseded v1's citable declaration.
    seed(graph, fx.SUPERSEDED_VERSION_DIFFERENT_DECLARATION)
    violations = extension.basis_admissibility(graph)
    assert [v.identity for v in violations] == ["ev-superseded"]
    assert "non-citable" in violations[0].detail


def test_conflicting_active_declarations_fail_loud(graph: Driver) -> None:
    # A-5 collision: a label declared by two active planes is a conflict; the
    # map-build must not silently pick one — a citation of it is flagged fail loud.
    seed(graph, fx.CONFLICTING_ACTIVE_DECLARATIONS)
    violations = extension.basis_admissibility(graph)
    assert [v.identity for v in violations] == ["ev-conflict"]
    assert "conflicting" in violations[0].detail
