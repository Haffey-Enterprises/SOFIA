##############################################################################
# Module: test_atomic_capture.py
# Service: conformance (RBT-33)
# Author: Haffey Enterprises LLC
# Created: 2026-06-22
# Revised: 2026-06-22
# Description: 1b gateway-behavioral contract for DDR-002 §7 #14 (atomic
#   capture-unit) — an Evidence node and its SOURCED_FROM edge must commit in a
#   single gateway transaction. xfail against the bare seam until RBT-15.
#
#   #14 delegated test-mechanic — atomicity-detection strategy: FAULT-INJECTION
#   over a transaction-boundary spy. The contract asserts the observable
#   all-or-nothing property — a write that cannot complete (here: a source node
#   that does not exist) must raise and leave NO partial Evidence/edge — rather
#   than spying on RBT-15's transaction internals (which would couple the
#   contract to the gateway's implementation and breach the DIRECTIVE-026 role
#   boundary). RBT-15's green run injects a mid-write fault via a wrapped driver
#   and asserts the same all-or-nothing observable.
# Standards: ENG-STD-001 v3.2.0
##############################################################################
"""#14 atomic-capture-unit contract (xfail against the GraphGateway seam)."""

import pytest

from conformance.contracts.gateway_seam import (
    SEAM_REASON,
    EvidenceWriteError,
    GraphGateway,
)


@pytest.mark.xfail(reason=SEAM_REASON, raises=NotImplementedError, strict=True)
def test_evidence_write_that_cannot_complete_is_atomic(gateway: GraphGateway) -> None:
    # Fault-injection observable: the source node does not exist, so the
    # capture-unit cannot commit; the gateway must raise and persist no partial
    # Evidence node or dangling SOURCED_FROM edge (all-or-nothing).
    with pytest.raises(EvidenceWriteError):
        gateway.write_evidence(
            source_node_id="nonexistent-kg-node",
            properties={"evidence_id": "ev-atomic"},
        )


@pytest.mark.xfail(reason=SEAM_REASON, raises=NotImplementedError, strict=True)
def test_evidence_write_with_valid_source_commits(gateway: GraphGateway) -> None:
    # The success path: a valid source node yields a committed Evidence id.
    assert gateway.write_evidence(
        source_node_id="cap-v1",
        properties={"evidence_id": "ev-ok", "source_node_version": 1},
    )
