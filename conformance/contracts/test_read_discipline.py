##############################################################################
# Module: test_read_discipline.py
# Service: conformance (RBT-33)
# Author: Haffey Enterprises LLC
# Created: 2026-06-22
# Revised: 2026-06-22
# Description: 1b gateway-behavioral read-discipline contracts — DDR-002 §7 #9
#   (proposal-visibility: a CandidatePromotion is excluded from ground-truth
#   synthesis reads until EA-approved) and #19 (conditional-consumption: an
#   applicability_state:conditional node is admitted to a consuming context only
#   where that context satisfies its Condition). xfail against the bare seam.
#
#   #19 delegated test-mechanic — stubbed Condition verdict: the Condition
#   predicate evaluator is RBT-22's, so the contract stubs the verdict by
#   passing it in the consuming context (satisfies_condition True/False) rather
#   than evaluating a predicate. RBT-15's gateway wires the real RBT-22 evaluator
#   in place of this stub.
# Standards: ENG-STD-001 v3.2.0
##############################################################################
"""#9 / #19 read-discipline contracts (xfail against the GraphGateway seam)."""

import pytest

from conformance.contracts.gateway_seam import SEAM_REASON, GraphGateway


# --- #9 proposal-visibility ---------------------------------------------------
@pytest.mark.xfail(reason=SEAM_REASON, raises=NotImplementedError, strict=True)
def test_ground_truth_read_excludes_candidate_promotion(gateway: GraphGateway) -> None:
    # A CandidatePromotion must not surface in ground-truth synthesis until
    # EA-approved (DDR-002 §7 #9, defers to DDR-001 check #4).
    assert all(
        node.get("node_kind") != "CandidatePromotion" for node in gateway.read_ground_truth()
    )


# --- #19 conditional-consumption read-discipline ------------------------------
@pytest.mark.xfail(reason=SEAM_REASON, raises=NotImplementedError, strict=True)
def test_conditional_node_excluded_when_condition_not_satisfied(gateway: GraphGateway) -> None:
    # Stubbed Condition verdict (RBT-22 owns the real evaluator): this context
    # does NOT satisfy the node's Condition, so the conditional node must be
    # excluded (DDR-002 §7 #19).
    assert "conditional-node-1" not in {
        node.get("id") for node in gateway.read_ground_truth(context={"satisfies_condition": False})
    }


@pytest.mark.xfail(reason=SEAM_REASON, raises=NotImplementedError, strict=True)
def test_conditional_node_admitted_when_condition_satisfied(gateway: GraphGateway) -> None:
    # Stubbed Condition verdict: this context DOES satisfy the node's Condition,
    # so the conditional node is admitted — the reuse-across-qualifying-contexts
    # case (DDR-002 §2.4 / §7 #19).
    assert "conditional-node-1" in {
        node.get("id") for node in gateway.read_ground_truth(context={"satisfies_condition": True})
    }
