##############################################################################
# Module: test_reasoning.py
# Service: conformance (RBT-48 catch-up)
# Author: Haffey Enterprises LLC
# Created: 2026-07-13
# Revised: 2026-07-13
# Description: Validator-correctness tests for the Reasoning-Graph conclusion
#   assertions — DDR-002 §7 #23 (flag<->category consistency: every
#   ReasoningProgress carries an authoritative value matching the fixed
#   reasoner_category mapping, llm_advisory -> false / all others -> true).
#   Each assertion is exercised against its conformant + violation fixtures.
# Standards: ENG-STD-001 v3.2.0
##############################################################################
"""Tests: the RG-conclusion assertions vs. their conformant / violation fixtures."""

from neo4j import Driver

from conformance.assertions import reasoning
from conformance.fixtures import reasoning as fx
from conformance.fixtures.seeding import seed


# --- #23 flag<->category consistency ------------------------------------------
def test_consistent_flag_category_conclusions_pass(graph: Driver) -> None:
    seed(graph, fx.FLAG_CATEGORY_CONFORMANT)
    assert reasoning.flag_category_consistency(graph) == []


def test_llm_advisory_marked_authoritative_is_caught(graph: Driver) -> None:
    # llm_advisory must map to authoritative False; a True flag is the wrong-
    # consumption hole #23 guards (DDR-002 §7 #23).
    seed(graph, fx.LLM_ADVISORY_MARKED_AUTHORITATIVE)
    violations = reasoning.flag_category_consistency(graph)
    assert [v.identity for v in violations] == ["rp-llm-auth"]
    assert violations[0].invariant == "DDR-002 §7 #23"


def test_authoritative_category_marked_non_authoritative_is_caught(graph: Driver) -> None:
    # A non-llm_advisory category must map to authoritative True; a False flag
    # is the other direction of the mismatch.
    seed(graph, fx.AUTHORITATIVE_CATEGORY_MARKED_NON_AUTHORITATIVE)
    violations = reasoning.flag_category_consistency(graph)
    assert [v.identity for v in violations] == ["rp-encoded-nonauth"]


def test_missing_authoritative_flag_is_caught(graph: Driver) -> None:
    # A present category with an absent flag cannot be consistent — flagged.
    seed(graph, fx.CATEGORY_WITHOUT_AUTHORITATIVE)
    violations = reasoning.flag_category_consistency(graph)
    assert [v.identity for v in violations] == ["rp-noflag"]


def test_absent_category_is_caught(graph: Driver) -> None:
    # reasoner_category is T2 — no DB existence constraint forces it, so #23's
    # 1a half must catch a category-absent node (incl. the worst shape:
    # authoritative:true with no category) that escaped the mediated write path.
    seed(graph, fx.CATEGORY_ABSENT)
    violations = reasoning.flag_category_consistency(graph)
    assert sorted(v.identity for v in violations) == ["rp-bare", "rp-nocat-auth"]
    assert all(v.invariant == "DDR-002 §7 #23" for v in violations)
