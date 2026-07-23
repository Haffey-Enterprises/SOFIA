##############################################################################
# Module: app/domain/shared/read_discipline_guard.py
# Service: knowledge-service
# Author: Haffey Enterprises LLC
# Created: 2026-07-23
# Revised: 2026-07-23
# Description: The promoted-only-state contradiction guard (DDR-002 §5 / §7 #21)
#   — a pure predicate shared by every Catalog read op (SDD-001 §3.3). DDR-002
#   §5 makes applicability_state / Condition exclusive to nodes materialized via
#   PROMOTES_TO_KNOWLEDGE, and §7 #21 makes RETRACTS un-promote a PROMOTED fact,
#   so a node carrying a promoted-only read-discipline state (retracted, or
#   applicability_state == "conditional") whose origin_mechanism is not
#   "promoted" is a data-integrity contradiction. The caller excludes such a
#   record fail-closed, BEFORE the read-discipline core — never admitted, and
#   never trusted to the core's ordinary exclusion path on a broken assumption
#   about what only a promoted-origin node may carry. Extracted from
#   resolve_technology (RBT-78 R3b) so resolve-technology and select-patterns
#   (R3c) — and every future Catalog read op — share one home for the rule
#   (RBT-78 R3c ruling #7). Side-effect-free by design: each caller logs its own
#   exclusion event, so the predicate stays a pure, isolately-testable boolean.
##############################################################################

# The one origin_mechanism that may carry applicability_state: conditional or a
# governing RETRACTS edge (DDR-002 §5 / §7 #21). Checked, never assumed.
_PROMOTED_ONLY_ORIGIN_MECHANISM = "promoted"


def is_promoted_only_state_contradiction(
    *,
    origin_mechanism: str,
    retracted: bool,
    applicability_state: str,
) -> bool:
    """Report whether a record claims a promoted-only state on a non-promoted origin.

    A `retracted` flag or `applicability_state == "conditional"` is a state only
    a `promoted`-origin node may carry (DDR-002 §5 / §7 #21). A record carrying
    either on any other `origin_mechanism` is a data-integrity contradiction the
    caller must exclude fail-closed, before the read-discipline core.

    Args:
        origin_mechanism: The candidate record's origin_mechanism.
        retracted: Whether the traversal resolved a governing RETRACTS edge.
        applicability_state: The candidate record's applicability_state.

    Returns:
        True iff the record claims a promoted-only state but is not
        promoted-origin — the caller excludes it, fail-closed. False otherwise.
    """
    claims_promoted_only_state = retracted or applicability_state == "conditional"
    return claims_promoted_only_state and origin_mechanism != _PROMOTED_ONLY_ORIGIN_MECHANISM
