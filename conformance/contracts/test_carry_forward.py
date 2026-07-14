##############################################################################
# Module: test_carry_forward.py
# Service: conformance (RBT-48 catch-up)
# Author: Haffey Enterprises LLC
# Created: 2026-07-13
# Revised: 2026-07-13
# Description: 1b gateway-behavioral contracts for DDR-002 §7 #22 (conditional-
#   scope carry-forward on supersession). Two write paths per SDD-001 §3.5.4:
#   the promotion path requires an explicit scope disposition (carry_conditional
#   / rescope_unconditional), and an absent disposition is rejected
#   (SCOPE_DISPOSITION_MISSING); the ingestion cross-origin case is blocked
#   (SCOPE_CONFLICT), because an ingested successor cannot structurally satisfy
#   the carry-forward. The 1a assertion (assertions/supersession.py) is the
#   standing graph-state half. xfail against the bare seam until RBT-15.
# Standards: ENG-STD-001 v3.2.0
##############################################################################
"""#22 carry-forward write-time contracts (xfail against the GraphGateway seam)."""

import pytest

from conformance.contracts.gateway_seam import (
    SEAM_REASON,
    GraphGateway,
    ScopeConflictError,
    ScopeDispositionMissingError,
)

# A promoted, unconditional successor over a conditional predecessor (the lineage
# whose predecessor is applicability_state:conditional — the gateway reads that
# state from the graph; here it is named by the business key under test).
_PROMOTED_SUCCESSOR = {"origin_mechanism": "promoted", "applicability_state": "unconditional"}
_INGESTED_SUCCESSOR = {"origin_mechanism": "ingested"}


@pytest.mark.xfail(reason=SEAM_REASON, raises=NotImplementedError, strict=True)
def test_supersession_without_scope_disposition_is_rejected(gateway: GraphGateway) -> None:
    # Promotion path: superseding a conditional predecessor with no scope
    # disposition is rejected — the silent default is unexpressible, not merely
    # detectable (SDD-001 §3.5.4; SCOPE_DISPOSITION_MISSING).
    with pytest.raises(ScopeDispositionMissingError):
        gateway.supersede(business_key="pat-conditional", successor=_PROMOTED_SUCCESSOR)


@pytest.mark.xfail(reason=SEAM_REASON, raises=NotImplementedError, strict=True)
def test_cross_origin_ingested_supersession_is_blocked(gateway: GraphGateway) -> None:
    # Ingestion path: an ingested successor cannot structurally satisfy #22, so
    # the supersession is blocked as a scope-conflict (SDD-001 §3.5.4;
    # SCOPE_CONFLICT), never silent admission of ingested reality over an EA scope.
    with pytest.raises(ScopeConflictError):
        gateway.supersede(business_key="pat-conditional", successor=_INGESTED_SUCCESSOR)


@pytest.mark.xfail(reason=SEAM_REASON, raises=NotImplementedError, strict=True)
def test_supersession_with_carry_conditional_disposition_commits(gateway: GraphGateway) -> None:
    # carry_conditional: the successor keeps the EA-set scope; the gateway
    # verifies a Condition is linked via the approving decision and commits.
    assert gateway.supersede(
        business_key="pat-conditional",
        successor=_PROMOTED_SUCCESSOR,
        scope_disposition="carry_conditional",
    )


@pytest.mark.xfail(reason=SEAM_REASON, raises=NotImplementedError, strict=True)
def test_supersession_with_rescope_unconditional_disposition_commits(
    gateway: GraphGateway,
) -> None:
    # rescope_unconditional: the EA explicitly re-scopes to unconditional; the
    # gateway verifies the approving decision carries no HAS_CONDITION and commits.
    assert gateway.supersede(
        business_key="pat-conditional",
        successor=_PROMOTED_SUCCESSOR,
        scope_disposition="rescope_unconditional",
    )
