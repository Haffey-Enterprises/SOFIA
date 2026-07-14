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


# --- #15 companion: per-candidate decided_at uniqueness (§2.4 monotonicity) ----
def test_distinct_decided_at_per_candidate_passes(graph: Driver) -> None:
    seed(graph, fx.DECIDED_AT_DISTINCT_CONFORMANT)
    assert decision.decided_at_uniqueness(graph) == []


def test_duplicate_decided_at_on_candidate_is_caught(graph: Driver) -> None:
    # Two DECIDED_ON edges on one candidate sharing decided_at make "latest
    # decided_at" (the #15 governing selector) ambiguous — ties are structurally
    # excluded (§2.4).
    seed(graph, fx.DECIDED_AT_DUPLICATE)
    violations = decision.decided_at_uniqueness(graph)
    assert [v.identity for v in violations] == ["cp-dup"]
    assert violations[0].invariant == "DDR-002 §7 #15"


def test_gate_decision_duplicate_decided_at_is_not_scoped(graph: Driver) -> None:
    # The monotonicity rule is scoped to PromotionDecision -> CandidatePromotion
    # DECIDED_ON only; a GateDecision -> Solution with duplicate decided_at is NOT
    # flagged (SDD-001 §3.6.3 declines extending it to GateDecision edges).
    seed(graph, fx.GATE_DECISION_DUPLICATE_DECIDED_AT)
    assert decision.decided_at_uniqueness(graph) == []
