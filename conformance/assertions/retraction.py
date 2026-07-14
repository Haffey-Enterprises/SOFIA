##############################################################################
# Module: retraction.py
# Service: conformance (RBT-48 catch-up)
# Author: Haffey Enterprises LLC
# Created: 2026-07-13
# Revised: 2026-07-13
# Description: Retraction graph-state assertions (1a) — DDR-002 §7 #21
#   (retraction-gated): a RETRACTS edge is valid only from a
#   proposal_kind:retraction CandidatePromotion that traces, via DECIDED_ON, to
#   an approving PromotionDecision. The un-promotion mirror of #15: un-promotion
#   of authoritative ground truth is EA-gated, never a bare delete. Safety-
#   critical tier. Labels and property names are interpolated from
#   conformance.schema_constants (single source); values are query parameters.
#
#   Deliberate #15 asymmetry (DDR-002 §2.4, run-018): #21 traces to AN approving
#   decision, NOT the governing (latest decided_at) one. A retraction whose
#   governing verdict has since flipped to 'rejected' but retains a stale
#   approving edge is NOT flagged here — the governing-verdict-flip DETECTION for
#   executed retractions is an explicitly deferred DDR-003 gap (§2.4 names it;
#   #21 is authored to trace to an approving, not the governing, decision). This
#   assertion honours that scope; tightening it to the governing edge would
#   pre-empt a ruling the DDR routes elsewhere.
#
#   Uncovered clause (skip-path discipline): #21's "with durable rationale on the
#   audit trail" is NOT asserted here — the schema defines no dedicated rationale
#   carrier on CandidatePromotion (proposed_change is T3-opaque), so a 1a check
#   would invent a prop contract the DDR does not state; the rationale obligation
#   is procedural (EA-gate / write-time) territory. What 1a can and does verify is
#   the durable STRUCTURE the audit trail rests on: an expiry-exempt retraction
#   candidate (§6) with an append-only approving decision chain.
# Standards: ENG-STD-001 v3.2.0
##############################################################################
"""Graph-state conformance assertions for the retraction invariants."""

from neo4j import Driver

from conformance import schema_constants as sc
from conformance.assertions.base import Violation, query_rows

_INV_RETRACTION_GATED = "DDR-002 §7 #21"

# #21: for every RETRACTS edge, its source must be a proposal_kind:retraction
# CandidatePromotion tracing (via DECIDED_ON) to at least one approving
# PromotionDecision. The OPTIONAL MATCH counts approving decisions (any, not the
# governing one — the deliberate asymmetry above); count 0 == not EA-gated.
# Three violation modes: source not a CandidatePromotion; source not
# proposal_kind:retraction; no approving decision.
_RETRACTION_GATED = f"""
MATCH (src)-[:{sc.RETRACTS}]->(target)
OPTIONAL MATCH (src)<-[d:{sc.DECIDED_ON}]-(:{sc.PROMOTION_DECISION_LABEL})
  WHERE d.{sc.PROP_OUTCOME} IN $approving
WITH src, target, count(d) AS approving_count
WITH src, target, approving_count,
     ($candidate_label IN labels(src)) AS is_candidate
WHERE NOT is_candidate
   OR src.{sc.PROP_PROPOSAL_KIND} IS NULL
   OR src.{sc.PROP_PROPOSAL_KIND} <> $retraction
   OR approving_count = 0
RETURN coalesce(src.{sc.PROP_CANDIDATE_ID}, src.{sc.PROP_PROGRESS_ID}, elementId(src)) AS identity,
       is_candidate AS is_candidate,
       src.{sc.PROP_PROPOSAL_KIND} AS kind,
       approving_count AS approving_count,
       coalesce(target.{sc.PROP_BUSINESS_KEY}, elementId(target)) AS target
"""


def retraction_gated(driver: Driver) -> list[Violation]:
    """DDR-002 §7 #21: a RETRACTS edge is EA-gated from a retraction candidate."""
    rows = query_rows(
        driver,
        _RETRACTION_GATED,
        {
            "approving": sorted(sc.APPROVING_OUTCOMES),
            "candidate_label": sc.CANDIDATE_PROMOTION_LABEL,
            "retraction": sc.PROPOSAL_KIND_RETRACTION,
        },
    )
    violations: list[Violation] = []
    for row in rows:
        if not row["is_candidate"]:
            detail = f"RETRACTS to {row['target']!r} originates from a non-CandidatePromotion node"
        elif row["kind"] != sc.PROPOSAL_KIND_RETRACTION:
            detail = (
                f"RETRACTS source is proposal_kind={row['kind']!r}, not "
                f"{sc.PROPOSAL_KIND_RETRACTION!r} (only a retraction candidate may retract)"
            )
        else:
            detail = (
                f"retraction candidate retracting {row['target']!r} traces to no approving "
                "PromotionDecision (un-promotion not EA-gated)"
            )
        violations.append(
            Violation(
                invariant=_INV_RETRACTION_GATED, identity=str(row["identity"]), detail=detail
            )
        )
    return violations
