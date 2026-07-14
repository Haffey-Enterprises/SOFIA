##############################################################################
# Module: test_flag_category.py
# Service: conformance (RBT-48 catch-up)
# Author: Haffey Enterprises LLC
# Created: 2026-07-13
# Revised: 2026-07-13
# Description: 1b gateway-behavioral contract for DDR-002 §7 #23 (flag<->category
#   consistency) — the gateway rejects a capture-conclusion write whose
#   authoritative flag contradicts the fixed reasoner_category mapping, at the
#   write boundary (SDD-001 §3.4.2: #23 rejected at write, not merely
#   CI-detected). The 1a assertion (assertions/reasoning.py) is the standing
#   graph-state half; this is the write-time half. xfail against the bare seam
#   until RBT-15 implements it.
# Standards: ENG-STD-001 v3.2.0
##############################################################################
"""#23 flag<->category write-time contract (xfail against the GraphGateway seam)."""

import pytest

from conformance.contracts.gateway_seam import (
    SEAM_REASON,
    FlagCategoryMismatchError,
    GraphGateway,
)

_ASA = "architecture-solutioning-agent"


@pytest.mark.xfail(reason=SEAM_REASON, raises=NotImplementedError, strict=True)
def test_llm_advisory_marked_authoritative_is_rejected(gateway: GraphGateway) -> None:
    # llm_advisory must map to authoritative False; a True flag is rejected at
    # write (FLAG_CATEGORY_MISMATCH per SDD-001 §3.2 / §3.4.2).
    with pytest.raises(FlagCategoryMismatchError):
        gateway.capture_conclusion(
            author=_ASA,
            properties={
                "progress_id": "rp-llm-auth",
                "reasoner_category": "llm_advisory",
                "authoritative": True,
            },
        )


@pytest.mark.xfail(reason=SEAM_REASON, raises=NotImplementedError, strict=True)
def test_authoritative_category_marked_non_authoritative_is_rejected(
    gateway: GraphGateway,
) -> None:
    # A non-llm_advisory category must map to authoritative True; a False flag
    # is the other direction of the rejected mismatch.
    with pytest.raises(FlagCategoryMismatchError):
        gateway.capture_conclusion(
            author=_ASA,
            properties={
                "progress_id": "rp-encoded-nonauth",
                "reasoner_category": "encoded_reasoning",
                "authoritative": False,
            },
        )


@pytest.mark.xfail(reason=SEAM_REASON, raises=NotImplementedError, strict=True)
def test_consistent_flag_category_conclusion_is_captured(gateway: GraphGateway) -> None:
    # The success path: a consistent flag<->category conclusion returns an id.
    assert gateway.capture_conclusion(
        author=_ASA,
        properties={
            "progress_id": "rp-llm-ok",
            "reasoner_category": "llm_advisory",
            "authoritative": False,
        },
    )
