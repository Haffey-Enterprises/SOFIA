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
