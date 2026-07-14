##############################################################################
# Module: test_retraction_read_discipline.py
# Service: conformance (RBT-48 catch-up)
# Author: Haffey Enterprises LLC
# Created: 2026-07-13
# Revised: 2026-07-13
# Description: 1b gateway-behavioral contract for DDR-002 §7 #21's read-discipline
#   half — a KG node carrying an inbound RETRACTS edge from an EA-approved
#   reversing CandidatePromotion is excluded from ground-truth synthesis
#   traversals (DDR-002 §5; parallel to #9 proposal-visibility and #19
#   conditional-consumption). The 1a assertion (assertions/retraction.py) is the
#   structural retraction-gating half; this is the read-exclusion half. xfail
#   against the bare seam until RBT-15.
# Standards: ENG-STD-001 v3.2.0
##############################################################################
"""#21 retracted-node read-exclusion contract (xfail against the GraphGateway seam)."""

import pytest

from conformance.contracts.gateway_seam import SEAM_REASON, GraphGateway


@pytest.mark.xfail(reason=SEAM_REASON, raises=NotImplementedError, strict=True)
def test_retracted_node_excluded_from_ground_truth(gateway: GraphGateway) -> None:
    # A KG node with an EA-approved inbound RETRACTS edge must not surface in
    # ground-truth synthesis (DDR-002 §5 / §7 #21; the retracted node stays
    # retained and audit-reachable, but read-excluded).
    assert "retracted-node-1" not in {
        node.get("id") for node in gateway.read_ground_truth()
    }
