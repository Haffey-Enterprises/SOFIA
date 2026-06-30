##############################################################################
# Module: test_classification.py
# Service: conformance (RBT-33)
# Author: Haffey Enterprises LLC
# Created: 2026-06-22
# Revised: 2026-06-22
# Description: 1b gateway-behavioral contract for DDR-002 §7 #13 (no-PHI, R10) —
#   the gateway must reject a write whose data classification flags PHI, at the
#   write boundary. xfail against the bare seam until RBT-15 implements it.
# Standards: ENG-STD-001 v3.2.0
##############################################################################
"""#13 no-PHI classification contract (xfail against the GraphGateway seam)."""

import pytest

from conformance.contracts.gateway_seam import (
    SEAM_REASON,
    ClassificationViolationError,
    GraphGateway,
)

_ASA = "architecture-solutioning-agent"


@pytest.mark.xfail(reason=SEAM_REASON, raises=NotImplementedError, strict=True)
def test_phi_classified_write_is_rejected(gateway: GraphGateway) -> None:
    # R10: SOFIA stores no PHI data; the gateway rejects it at the write boundary.
    with pytest.raises(ClassificationViolationError):
        gateway.write(
            author=_ASA,
            classification="phi",
            node_kind="ReasoningProgress",
            properties={"progress_id": "rp-phi"},
        )


@pytest.mark.xfail(reason=SEAM_REASON, raises=NotImplementedError, strict=True)
def test_non_phi_classified_write_is_permitted(gateway: GraphGateway) -> None:
    assert gateway.write(
        author=_ASA,
        classification="internal",
        node_kind="ReasoningProgress",
        properties={"progress_id": "rp-ok"},
    )
