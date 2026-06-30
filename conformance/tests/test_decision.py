##############################################################################
# Module: test_decision.py
# Service: conformance (RBT-33)
# Author: Haffey Enterprises LLC
# Created: 2026-06-22
# Revised: 2026-06-22
# Description: Validator-correctness tests for the Decision-subtype assertion
#   (DDR-002 §7 #16) — exactly one subtype label per Decision; bare and
#   both-subtype Decisions are caught.
# Standards: ENG-STD-001 v3.2.0
##############################################################################
"""Tests: Decision-subtype assertion vs. its conformant / violation fixtures."""

from neo4j import Driver

from conformance.assertions import decision
from conformance.fixtures import decision as fx
from conformance.fixtures.seeding import seed


def test_single_subtype_decisions_pass(graph: Driver) -> None:
    seed(graph, fx.DECISION_SUBTYPE_CONFORMANT)
    assert decision.decision_subtype_cardinality(graph) == []


def test_bare_decision_is_caught(graph: Driver) -> None:
    seed(graph, fx.DECISION_BARE_VIOLATION)
    violations = decision.decision_subtype_cardinality(graph)
    assert [v.identity for v in violations] == ["dec-bare"]
    assert violations[0].invariant == "DDR-002 §7 #16"


def test_decision_with_both_subtypes_is_caught(graph: Driver) -> None:
    seed(graph, fx.DECISION_BOTH_SUBTYPES_VIOLATION)
    violations = decision.decision_subtype_cardinality(graph)
    assert [v.identity for v in violations] == ["dec-both"]
