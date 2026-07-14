##############################################################################
# Module: test_monotonicity.py
# Service: conformance (RBT-48 catch-up)
# Author: Haffey Enterprises LLC
# Created: 2026-07-13
# Revised: 2026-07-13
# Description: 1b gateway-behavioral contract for the DDR-002 §7 #15 companion —
#   per-candidate strict decided_at monotonicity on DECIDED_ON writes (DDR-002
#   §2.4; SDD-001 §3.5.2's write contract). A new DECIDED_ON edge on a candidate
#   must carry decided_at strictly greater than any existing edge's on that
#   candidate, else MONOTONICITY_VIOLATION — which is what keeps "latest
#   decided_at" (the #15 governing selector) well-defined. Scoped to the
#   PromotionDecision -> CandidatePromotion edge (SDD-001 §3.6.3 declines
#   extending it to GateDecision). The 1a assertion (assertions/decision.py) is
#   the standing no-duplicate-decided_at half. xfail against the bare seam.
# Standards: ENG-STD-001 v3.2.0
##############################################################################
"""#15-companion monotonicity contract (xfail against the GraphGateway seam)."""

import pytest

from conformance.contracts.gateway_seam import (
    SEAM_REASON,
    GraphGateway,
    MonotonicityViolationError,
)


@pytest.mark.xfail(reason=SEAM_REASON, raises=NotImplementedError, strict=True)
def test_strictly_greater_decided_at_is_accepted(gateway: GraphGateway) -> None:
    # A re-decision with decided_at strictly greater than the candidate's existing
    # DECIDED_ON edges is the legitimate append-only re-decision (§2.4).
    assert gateway.record_promotion_decision(
        decision_id="pd-2", candidate_id="cp-1", decided_at="2026-01-02", outcome="approved"
    )


@pytest.mark.xfail(reason=SEAM_REASON, raises=NotImplementedError, strict=True)
def test_non_increasing_decided_at_is_rejected(gateway: GraphGateway) -> None:
    # A decided_at not strictly greater than an existing edge's on the same
    # candidate is rejected — ties/regressions are structurally excluded so the
    # governing verdict never underdetermines (MONOTONICITY_VIOLATION).
    with pytest.raises(MonotonicityViolationError):
        gateway.record_promotion_decision(
            decision_id="pd-3", candidate_id="cp-1", decided_at="2026-01-02", outcome="rejected"
        )
