##############################################################################
# Module: decision.py
# Service: conformance (RBT-33)
# Author: Haffey Enterprises LLC
# Created: 2026-06-22
# Revised: 2026-06-22
# Description: Decision-subtype graph-state assertion (1a) — DDR-002 §7 #16:
#   every (:Governance:Decision) carries exactly one of {GateDecision,
#   PromotionDecision} (never bare, never both). Neo4j cannot enforce label
#   cardinality natively, so this is the CI-half.
# Standards: ENG-STD-001 v3.2.0
##############################################################################
"""Graph-state conformance assertion for Decision-subtype cardinality."""

from neo4j import Driver

from conformance import schema_constants as sc
from conformance.assertions.base import Violation, query_rows

_INV_DECISION_SUBTYPE = "DDR-002 §7 #16"

# Count how many of the recognised subtype labels each Decision carries; flag
# any Decision that does not carry exactly one (bare == 0, both == 2).
_DECISION_SUBTYPE_CARDINALITY = f"""
MATCH (d:{sc.DECISION_LABEL})
WITH d, size([l IN labels(d) WHERE l IN $subtypes]) AS subtype_count
WHERE subtype_count <> 1
RETURN d.{sc.PROP_DECISION_ID} AS identity, subtype_count
"""


def decision_subtype_cardinality(driver: Driver) -> list[Violation]:
    """DDR-002 §7 #16: every Decision carries exactly one subtype label."""
    rows = query_rows(
        driver,
        _DECISION_SUBTYPE_CARDINALITY,
        {"subtypes": sorted(sc.DECISION_SUBTYPE_LABELS)},
    )
    return [
        Violation(
            invariant=_INV_DECISION_SUBTYPE,
            identity=str(row["identity"]),
            detail=f"Decision carries {row['subtype_count']} subtype labels (must be exactly 1)",
        )
        for row in rows
    ]


# #15 companion (§2.4 per-candidate strict decided_at monotonicity): a candidate's
# inbound DECIDED_ON edges must carry DISTINCT decided_at values, so "latest
# decided_at" — the governing-verdict selector #15 keys on — is always well-
# defined (ties are structurally excluded). Scoped to PromotionDecision ->
# CandidatePromotion DECIDED_ON edges ONLY; the monotonicity rule is not extended
# to GateDecision -> Solution (SDD-001 §3.6.3, an upstream question DDR-002 does
# not answer). This is the standing 1a mirror of the gateway's write-time
# monotonicity enforcement; it detects a tie however it arrived.
_INV_DECIDED_AT_MONOTONICITY = "DDR-002 §7 #15"

# decided_at is a property of the PromotionDecision NODE (§2.4), not the
# DECIDED_ON edge (which carries {outcome}); read it from pd, matching the #15
# governing-decision assertion.
_DECIDED_AT_DUPLICATE = f"""
MATCH (pd:{sc.PROMOTION_DECISION_LABEL})-[:{sc.DECIDED_ON}]->(cp:{sc.CANDIDATE_PROMOTION_LABEL})
WITH cp, pd.{sc.PROP_DECIDED_AT} AS decided_at, count(*) AS occurrences
WHERE occurrences > 1
RETURN cp.{sc.PROP_CANDIDATE_ID} AS identity,
       decided_at AS decided_at,
       occurrences AS occurrences
"""


def decided_at_uniqueness(driver: Driver) -> list[Violation]:
    """DDR-002 §7 #15 companion: per-candidate DECIDED_ON decided_at is distinct."""
    rows = query_rows(driver, _DECIDED_AT_DUPLICATE)
    return [
        Violation(
            invariant=_INV_DECIDED_AT_MONOTONICITY,
            identity=str(row["identity"]),
            detail=(
                f"candidate has {row['occurrences']} DECIDED_ON edges sharing "
                f"decided_at={row['decided_at']!r} (per-candidate decided_at must be distinct "
                "so the governing verdict is well-defined; §2.4 monotonicity)"
            ),
        )
        for row in rows
    ]
