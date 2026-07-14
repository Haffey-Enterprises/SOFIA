##############################################################################
# Module: test_basis_admissibility.py
# Service: conformance (RBT-48 catch-up)
# Author: Haffey Enterprises LLC
# Created: 2026-07-13
# Revised: 2026-07-13
# Description: 1b gateway-behavioral contract for DDR-002 §7 #27's capture-time
#   half — a capture-evidence citing a non_citable-basis class node is rejected
#   typed at capture (NON_CITABLE_SOURCE, DDR-002 §2.6 / SDD-001 §3.4.3): the
#   declared-contract steering rejection toward the class's purpose-built evidence
#   surface, distinct from CONFIDENCE_UNDERIVABLE. The 1a assertion
#   (assertions/extension.py) is the standing basis-admissibility half over the
#   graph. The citable success path is the #14 capture-unit contract
#   (test_atomic_capture). xfail against the bare seam until RBT-15.
# Standards: ENG-STD-001 v3.2.0
##############################################################################
"""#27 capture-time non-citable-source contract (xfail against the GraphGateway seam)."""

import pytest

from conformance.contracts.gateway_seam import (
    SEAM_REASON,
    GraphGateway,
    NonCitableSourceError,
)


@pytest.mark.xfail(reason=SEAM_REASON, raises=NotImplementedError, strict=True)
def test_capture_evidence_citing_non_citable_source_is_rejected(gateway: GraphGateway) -> None:
    # Citing a non_citable-class node (a RateCard) is rejected at capture, steering
    # to the class's purpose-built evidence surface (NON_CITABLE_SOURCE).
    with pytest.raises(NonCitableSourceError):
        gateway.write_evidence(
            source_node_id="ratecard-non-citable",
            properties={"evidence_id": "ev-inadmissible", "source_node_version": 1},
        )
