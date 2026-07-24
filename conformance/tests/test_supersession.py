##############################################################################
# Module: test_supersession.py
# Service: conformance (RBT-48 catch-up)
# Author: Haffey Enterprises LLC
# Created: 2026-07-13
# Revised: 2026-07-13
# Description: Validator-correctness tests for the supersession graph-state
#   assertions — DDR-002 §7 #22 (conditional-scope carry-forward on supersession,
#   predecessor-keyed): a superseded applicability_state:conditional predecessor
#   must yield a successor that is conditional, or unconditional-with-a-governing-
#   approving-PromotionDecision (the explicit EA re-scope). Each assertion is
#   exercised against its conformant + violation fixtures.
# Standards: ENG-STD-001 v3.2.0
##############################################################################
"""Tests: the supersession assertions vs. their conformant / violation fixtures."""

from neo4j import Driver

from conformance.assertions import supersession
from conformance.fixtures import supersession as fx
from conformance.fixtures.seeding import seed


# --- #22 conditional-scope carry-forward --------------------------------------
def test_carried_and_rescoped_supersessions_pass(graph: Driver) -> None:
    # Both legit outcomes: a successor carrying conditional (carry_conditional),
    # and an unconditional successor with a governing approving PromotionDecision
    # (explicit rescope_unconditional). Neither is flagged.
    seed(graph, fx.CONDITIONAL_CARRY_FORWARD_CONFORMANT)
    assert supersession.conditional_scope_carry_forward(graph) == []


def test_silent_default_to_unconditional_is_caught(graph: Driver) -> None:
    # A conditional predecessor superseded by an unconditional successor with NO
    # governing approving PromotionDecision — the silent default #19 cannot catch
    # (the successor is no longer marked conditional). Predecessor-keyed.
    seed(graph, fx.SILENT_DEFAULT_TO_UNCONDITIONAL)
    violations = supersession.conditional_scope_carry_forward(graph)
    assert [v.identity for v in violations] == ["pat-silent"]
    assert violations[0].invariant == "DDR-002 §7 #22"


def test_cross_origin_ingested_successor_is_caught(graph: Driver) -> None:
    # The ingestion cross-origin case: an ingested successor carries no
    # applicability_state and no re-scoping decision, so it cannot structurally
    # satisfy #22 (the gateway blocks this as SCOPE_CONFLICT; the harness catches
    # any that reached the graph).
    seed(graph, fx.CROSS_ORIGIN_INGESTED_SUCCESSOR)
    violations = supersession.conditional_scope_carry_forward(graph)
    assert [v.identity for v in violations] == ["pat-crossorigin"]


def test_unresolvable_successor_lineage_is_caught(graph: Driver) -> None:
    # A conditional predecessor whose superseded_by dangles (no retained node)
    # cannot be evaluated for carry-forward — a safety-critical check must fail
    # loud, not skip (the A-1 / A-2 fail-loud discipline; §6 atomicity means this
    # shape should never exist).
    seed(graph, fx.UNRESOLVABLE_SUPERSEDED_BY)
    violations = supersession.conditional_scope_carry_forward(graph)
    assert [v.identity for v in violations] == ["pat-dangling"]
    assert "broken lineage" in violations[0].detail


def test_rejected_rescope_decision_does_not_count_as_carry_forward(graph: Driver) -> None:
    # An unconditional successor whose only DECIDED_ON verdict is 'rejected' has
    # no *approving* re-scope — the governing verdict is non-approving, so the
    # carry-forward is not satisfied.
    seed(graph, fx.RESCOPE_DECISION_REJECTED)
    violations = supersession.conditional_scope_carry_forward(graph)
    assert [v.identity for v in violations] == ["pat-rejected"]
