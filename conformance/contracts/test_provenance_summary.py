##############################################################################
# Module: test_provenance_summary.py
# Service: conformance (RBT-48 catch-up)
# Author: Haffey Enterprises LLC
# Created: 2026-07-13
# Revised: 2026-07-13
# Description: 1b gateway-behavioral contract for DDR-002 §7 #20 (at-promotion
#   ProvenanceSummary materialization). The materialize-promotion transaction
#   builds the ProvenanceSummary in the SAME transaction as the promotion
#   (SDD-001 §3.5.3), so the build-before-Evidence-expiry ordering holds by
#   construction — it is not a later sweep racing retention. The behavioral
#   observables: a successful materialize-promotion returns the promoted node id
#   (its at-promotion summary written and bound); a materialization whose §5-span
#   closure cannot be computed complete raises and commits nothing (atomicity,
#   parallel to #14). The 1a assertion (assertions/provenance.py) is the standing
#   existence+completeness half. xfail against the bare seam until RBT-15.
# Standards: ENG-STD-001 v3.2.0
##############################################################################
"""#20 at-promotion materialization contract (xfail against the GraphGateway seam)."""

import pytest

from conformance.contracts.gateway_seam import (
    SEAM_REASON,
    GraphGateway,
    ProvenanceMaterializationError,
)


@pytest.mark.xfail(reason=SEAM_REASON, raises=NotImplementedError, strict=True)
def test_materialize_promotion_binds_provenance_summary_at_promotion(
    gateway: GraphGateway,
) -> None:
    # Success path: materialize-promotion returns the promoted node id, its
    # ProvenanceSummary written and bound (MATERIALIZES_PROVENANCE_OF) within the
    # same transaction — at-promotion, before any Evidence can expire.
    assert gateway.materialize_promotion(decision_id="pd-1", candidate_id="cp-1")


@pytest.mark.xfail(reason=SEAM_REASON, raises=NotImplementedError, strict=True)
def test_materialize_promotion_incomplete_closure_does_not_commit(gateway: GraphGateway) -> None:
    # If the §5-span closure cannot be computed complete, the transaction raises
    # and commits no partial promotion or incomplete summary (all-or-nothing).
    with pytest.raises(ProvenanceMaterializationError):
        gateway.materialize_promotion(decision_id="pd-broken", candidate_id="cp-broken")
