##############################################################################
# Module: test_retraction.py
# Service: conformance (RBT-48 catch-up)
# Author: Haffey Enterprises LLC
# Created: 2026-07-13
# Revised: 2026-07-13
# Description: Validator-correctness tests for the retraction graph-state
#   assertions — DDR-002 §7 #21 (retraction-gated: a RETRACTS edge is valid only
#   from a proposal_kind:retraction CandidatePromotion that traces via DECIDED_ON
#   to an approving PromotionDecision). Each assertion is exercised against its
#   conformant + violation fixtures.
# Standards: ENG-STD-001 v3.2.0
##############################################################################
"""Tests: the retraction assertions vs. their conformant / violation fixtures."""

from neo4j import Driver

from conformance.assertions import retraction
from conformance.fixtures import retraction as fx
from conformance.fixtures.seeding import seed


# --- #21 retraction-gated -----------------------------------------------------
def test_ea_gated_retractions_pass(graph: Driver) -> None:
    # A retraction candidate with an approving DECIDED_ON (approved and
    # approved_conditional variants) is a valid EA-gated un-promotion.
    seed(graph, fx.RETRACTION_GATED_CONFORMANT)
    assert retraction.retraction_gated(graph) == []


def test_stale_approving_not_governing_still_passes(graph: Driver) -> None:
    # #21 traces to AN approving decision, not the GOVERNING one (DDR-002 §2.4:
    # the governing-flip detection for executed retractions is a deferred DDR-003
    # gap). A retraction with an early 'approved' and a later 'rejected' verdict
    # still has an approving edge, so #21 does NOT flag it — the deliberate
    # asymmetry with #15. This test locks that semantics against a future tighten.
    seed(graph, fx.RETRACTS_STALE_APPROVING_NOT_GOVERNING)
    assert retraction.retraction_gated(graph) == []


def test_retracts_from_non_retraction_kind_is_caught(graph: Driver) -> None:
    seed(graph, fx.RETRACTS_FROM_PROMOTION_KIND)
    violations = retraction.retraction_gated(graph)
    assert [v.identity for v in violations] == ["cp-wrongkind"]
    assert violations[0].invariant == "DDR-002 §7 #21"


def test_retracts_without_approving_decision_is_caught(graph: Driver) -> None:
    # A retraction candidate with no approving DECIDED_ON — the bare-delete-
    # equivalent #21 guards against.
    seed(graph, fx.RETRACTS_WITHOUT_APPROVING_DECISION)
    violations = retraction.retraction_gated(graph)
    assert [v.identity for v in violations] == ["cp-unapproved"]


def test_retracts_with_only_rejected_verdict_is_caught(graph: Driver) -> None:
    # A rejected DECIDED_ON is not approving — no EA gate.
    seed(graph, fx.RETRACTS_ONLY_REJECTED)
    violations = retraction.retraction_gated(graph)
    assert [v.identity for v in violations] == ["cp-rejonly"]


def test_retracts_from_non_candidate_node_is_caught(graph: Driver) -> None:
    # A RETRACTS edge must originate from a CandidatePromotion (DDR-002 §5).
    seed(graph, fx.RETRACTS_FROM_NON_CANDIDATE)
    violations = retraction.retraction_gated(graph)
    assert [v.identity for v in violations] == ["rp-not-a-candidate"]
