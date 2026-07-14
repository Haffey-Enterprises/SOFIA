##############################################################################
# Module: test_register_plane.py
# Service: conformance (RBT-48 catch-up)
# Author: Haffey Enterprises LLC
# Created: 2026-07-13
# Revised: 2026-07-13
# Description: 1b gateway-behavioral contract for DDR-002 §7 #26 (basis-declaration
#   totality) — register-plane validates the confidence_basis declared totality at
#   registration and rejects a violating declaration typed (SCHEMA_VIOLATION, SDD-
#   001 §3.6.2: #26 holds by construction of this validation). The declarations are
#   the raw JSON the gateway parses, so the same duplicate-key guard the 1a parse
#   applies (A-4) belongs here: last-wins would collapse the "one basis per label"
#   rule before validation. The 1a assertion (assertions/extension.py) is the
#   standing graph-state mirror. xfail against the bare seam until RBT-15.
# Standards: ENG-STD-001 v3.2.0
##############################################################################
"""#26 register-plane totality contract (xfail against the GraphGateway seam)."""

import pytest

from conformance.contracts.gateway_seam import (
    SEAM_REASON,
    GraphGateway,
    SchemaViolationError,
)

# A totality-conformant declaration (the §2.6 cost-plane exemplar shape): equal
# label sets, valid bases, no stray operands.
_VALID_BASIS = '{"CapabilityCostEstimate": {"basis": "native_confidence"}}'
_VALID_SCHEMA = '{"CapabilityCostEstimate": {"estimate_id": "string"}}'


@pytest.mark.xfail(reason=SEAM_REASON, raises=NotImplementedError, strict=True)
def test_register_plane_with_incomplete_basis_is_rejected(gateway: GraphGateway) -> None:
    # property_schema declares a label (RateCard) confidence_basis omits — a
    # declared label with no basis; register-plane rejects it (SCHEMA_VIOLATION).
    with pytest.raises(SchemaViolationError):
        gateway.register_plane(
            plane_id="plane-incomplete",
            confidence_basis=_VALID_BASIS,
            property_schema=(
                '{"CapabilityCostEstimate": {"estimate_id": "string"}, '
                '"RateCard": {"rate_card_id": "string"}}'
            ),
        )


@pytest.mark.xfail(reason=SEAM_REASON, raises=NotImplementedError, strict=True)
def test_register_plane_with_duplicate_label_key_is_rejected(gateway: GraphGateway) -> None:
    # A-4: a duplicate label key in the raw JSON must be rejected at parse — a
    # last-wins collapse would hide the "one basis per label" violation.
    with pytest.raises(SchemaViolationError):
        gateway.register_plane(
            plane_id="plane-dup",
            confidence_basis=(
                '{"CapabilityCostEstimate": {"basis": "native_confidence"}, '
                '"CapabilityCostEstimate": {"basis": "aging"}}'
            ),
            property_schema=_VALID_SCHEMA,
        )


@pytest.mark.xfail(reason=SEAM_REASON, raises=NotImplementedError, strict=True)
def test_register_plane_with_valid_declaration_is_accepted(gateway: GraphGateway) -> None:
    assert gateway.register_plane(
        plane_id="plane-valid",
        confidence_basis=_VALID_BASIS,
        property_schema=_VALID_SCHEMA,
    )
