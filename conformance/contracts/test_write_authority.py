##############################################################################
# Module: test_write_authority.py
# Service: conformance (RBT-33)
# Author: Haffey Enterprises LLC
# Created: 2026-06-22
# Revised: 2026-06-22
# Description: 1b gateway-behavioral contract for DDR-002 §7 #7 (ADR-002 §2.6
#   write-authority) — the gateway must reject a ReasoningProgress write not
#   attributed to the ASA, and confine the AOE to ReasoningSession lifecycle.
#   xfail against the bare seam (stub raises NotImplementedError); RBT-15
#   implements the seam and flips these to xpass.
# Standards: ENG-STD-001 v3.2.0
##############################################################################
"""#7 write-authority contract (xfail against the GraphGateway seam)."""

import pytest

from conformance.contracts.gateway_seam import (
    SEAM_REASON,
    GraphGateway,
    WriteAuthorityError,
)

_ASA = "architecture-solutioning-agent"
_AOE = "agent-orchestration-engine"


@pytest.mark.xfail(reason=SEAM_REASON, raises=NotImplementedError, strict=True)
def test_non_asa_reasoning_progress_write_is_rejected(gateway: GraphGateway) -> None:
    # ADR-002 §2.6: only the ASA authors ReasoningProgress.
    with pytest.raises(WriteAuthorityError):
        gateway.write(
            author=_AOE,
            classification="internal",
            node_kind="ReasoningProgress",
            properties={"progress_id": "rp-unauthorised"},
        )


@pytest.mark.xfail(reason=SEAM_REASON, raises=NotImplementedError, strict=True)
def test_asa_reasoning_progress_write_is_permitted(gateway: GraphGateway) -> None:
    # The ASA is the authorised author; the gateway must accept and return an id.
    assert gateway.write(
        author=_ASA,
        classification="internal",
        node_kind="ReasoningProgress",
        properties={"progress_id": "rp-1"},
    )
