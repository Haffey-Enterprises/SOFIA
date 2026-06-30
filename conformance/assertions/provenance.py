##############################################################################
# Module: provenance.py
# Service: conformance (RBT-33)
# Author: Haffey Enterprises LLC
# Created: 2026-06-22
# Revised: 2026-06-22
# Description: Provenance-cluster graph-state assertions (1a) — DDR-002 §7 #1
#   (RG-provenance edges), #11 (provenance distinguishability), #15 (promoted ->
#   governing approving decision), #17 (ingested/distilled -> source_record_ref),
#   and DDR-001 check 5 (Evidence version-pin integrity). Labels and edge types
#   are interpolated from conformance.schema_constants (single source); property
#   values are passed as query parameters.
# Standards: ENG-STD-001 v3.2.0
##############################################################################
"""Graph-state conformance assertions for the provenance cluster."""

from neo4j import Driver

from conformance import schema_constants as sc
from conformance.assertions.base import Violation, query_rows

_INV_RG_PROVENANCE = "DDR-002 §7 #1"

# (a) An Evidence node must have a SOURCED_FROM edge to a provenance-bearing KG
# node — a node carrying a KG plane label AND the origin_mechanism provenance
# property (DDR-002 §1, §5). Flags Evidence with no SOURCED_FROM and Evidence
# whose target is not a provenance-bearing KG node (e.g. an RG node).
_EVIDENCE_MISSING_SOURCE = f"""
MATCH (e:{sc.RG_LABEL}:{sc.EVIDENCE_LABEL})
WHERE NOT EXISTS {{
    MATCH (e)-[:{sc.SOURCED_FROM}]->(k)
    WHERE k.{sc.PROP_ORIGIN_MECHANISM} IS NOT NULL
      AND any(lbl IN labels(k) WHERE lbl IN $plane_labels)
}}
RETURN e.{sc.PROP_EVIDENCE_ID} AS identity
"""

# (b) A RejectedAlternative must be reached by exactly one parent REJECTED edge
# (DDR-002 §7 #1 — per-conclusion rejection rationale). Flags zero or many.
_REJECTED_PARENT_CARDINALITY = f"""
MATCH (r:{sc.RG_LABEL}:{sc.REJECTED_ALTERNATIVE_LABEL})
WITH r, COUNT {{ (r)<-[:{sc.REJECTED}]-() }} AS parents
WHERE parents <> 1
RETURN r.{sc.PROP_REJECTED_ID} AS identity, parents
"""


def evidence_missing_sourced_from(driver: Driver) -> list[Violation]:
    """DDR-002 §7 #1 (a): every Evidence has a SOURCED_FROM to a KG node."""
    rows = query_rows(driver, _EVIDENCE_MISSING_SOURCE, {"plane_labels": list(sc.KG_PLANE_LABELS)})
    return [
        Violation(
            invariant=_INV_RG_PROVENANCE,
            identity=str(row["identity"]),
            detail="Evidence lacks a SOURCED_FROM edge to a provenance-bearing KG node",
        )
        for row in rows
    ]


def rejected_alternative_parent_cardinality(driver: Driver) -> list[Violation]:
    """DDR-002 §7 #1 (b): every RejectedAlternative has exactly one REJECTED parent."""
    rows = query_rows(driver, _REJECTED_PARENT_CARDINALITY)
    return [
        Violation(
            invariant=_INV_RG_PROVENANCE,
            identity=str(row["identity"]),
            detail=f"RejectedAlternative has {row['parents']} REJECTED parents (must be exactly 1)",
        )
        for row in rows
    ]


_INV_PROVENANCE_DISTINGUISHABILITY = "DDR-002 §7 #11"

# #11: presence of origin_mechanism is DB-enforced; CI checks the value is one
# of the valid set (DDR-002 §1) — which is also what keeps 'promoted'
# distinguishable from 'ingested'. Any node carrying an out-of-set value fails.
_ORIGIN_MECHANISM_INVALID = f"""
MATCH (n)
WHERE n.{sc.PROP_ORIGIN_MECHANISM} IS NOT NULL
  AND NOT n.{sc.PROP_ORIGIN_MECHANISM} IN $valid
RETURN elementId(n) AS identity, n.{sc.PROP_ORIGIN_MECHANISM} AS value
"""


def origin_mechanism_invalid_value(driver: Driver) -> list[Violation]:
    """DDR-002 §7 #11: every origin_mechanism value is in the valid set."""
    valid = sorted(sc.ORIGIN_MECHANISMS)
    rows = query_rows(driver, _ORIGIN_MECHANISM_INVALID, {"valid": valid})
    return [
        Violation(
            invariant=_INV_PROVENANCE_DISTINGUISHABILITY,
            identity=str(row["identity"]),
            detail=f"origin_mechanism {row['value']!r} is not one of {valid}",
        )
        for row in rows
    ]


_INV_PROMOTED_GOVERNING = "DDR-002 §7 #15"

# Correct — key off the GOVERNING decision: per promoted node, collect the
# DECIDED_ON outcomes ordered by their PromotionDecision's decided_at DESC, take
# the latest (governing) verdict, and flag the node unless that verdict is
# approving. A node with no decision chain collects [] -> governing NULL ->
# flagged. This catches a node whose governing verdict has flipped to 'rejected'
# despite a stale earlier 'approved' (DDR-002 §7 #15, §2.4 verdict precedence).
_PROMOTED_GOVERNING = f"""
MATCH (k)
WHERE k.{sc.PROP_ORIGIN_MECHANISM} = $promoted
OPTIONAL MATCH (k)<-[:{sc.PROMOTES_TO_KNOWLEDGE}]-(:{sc.CANDIDATE_PROMOTION_LABEL})
              <-[d:{sc.DECIDED_ON}]-(pd:{sc.PROMOTION_DECISION_LABEL})
WITH k, d.{sc.PROP_OUTCOME} AS outcome, pd.{sc.PROP_DECIDED_AT} AS decided_at
ORDER BY decided_at DESC
WITH k, collect(outcome) AS outcomes
WITH k, head(outcomes) AS governing
WHERE governing IS NULL OR NOT governing IN $approving
RETURN k.{sc.PROP_BUSINESS_KEY} AS identity, governing AS governing_outcome
"""


def promoted_without_governing_approval(driver: Driver) -> list[Violation]:
    """DDR-002 §7 #15: a promoted node's governing decision must be approving."""
    rows = query_rows(
        driver,
        _PROMOTED_GOVERNING,
        {"promoted": sc.PROMOTED_ORIGIN, "approving": sorted(sc.APPROVING_OUTCOMES)},
    )
    return [
        Violation(
            invariant=_INV_PROMOTED_GOVERNING,
            identity=str(row["identity"]),
            detail=(
                "promoted node's governing PromotionDecision verdict is "
                f"{row['governing_outcome']!r} (must be approving)"
            ),
        )
        for row in rows
    ]


_INV_SOURCE_RECORD_REF = "DDR-002 §7 #17"

# A node must carry source_record_ref if it is origin_mechanism 'ingested' OR
# derivation_class 'distilled'. 'aggregated' (internal version-pins) is exempt
# by not matching either branch (DDR-002 §7 #17, §1).
_MISSING_SOURCE_RECORD_REF = f"""
MATCH (n)
WHERE (n.{sc.PROP_ORIGIN_MECHANISM} = $ingested
       OR n.{sc.PROP_DERIVATION_CLASS} = $distilled)
  AND n.{sc.PROP_SOURCE_RECORD_REF} IS NULL
RETURN n.{sc.PROP_BUSINESS_KEY} AS identity,
       n.{sc.PROP_ORIGIN_MECHANISM} AS origin_mechanism,
       n.{sc.PROP_DERIVATION_CLASS} AS derivation_class
"""


def missing_source_record_ref(driver: Driver) -> list[Violation]:
    """DDR-002 §7 #17: ingested and distilled nodes carry a source_record_ref."""
    rows = query_rows(
        driver,
        _MISSING_SOURCE_RECORD_REF,
        {
            "ingested": sc.ORIGIN_REQUIRES_SOURCE_RECORD_REF,
            "distilled": sc.DERIVATION_REQUIRES_SOURCE_RECORD_REF,
        },
    )
    return [
        Violation(
            invariant=_INV_SOURCE_RECORD_REF,
            identity=str(row["identity"]),
            detail=(
                "node (origin_mechanism="
                f"{row['origin_mechanism']!r}, derivation_class={row['derivation_class']!r}) "
                "lacks a required source_record_ref"
            ),
        )
        for row in rows
    ]


_INV_EVIDENCE_VERSION_PIN = "DDR-001 check 5"

# B-2-corrected shape: traverse SOURCED_FROM to the cited KG node, then verify
# the pinned source_node_version resolves to a RETAINED version node of that
# lineage (matched by business_key + version). No phantom source_business_key —
# the lineage key is read off the SOURCED_FROM target (DDR-002 §4/§5/§6). A pin
# with no retained matching version is a dangling pin.
_EVIDENCE_DANGLING_VERSION_PIN = f"""
MATCH (e:{sc.RG_LABEL}:{sc.EVIDENCE_LABEL})-[:{sc.SOURCED_FROM}]->(k)
WHERE e.{sc.PROP_SOURCE_NODE_VERSION} IS NOT NULL
  AND NOT EXISTS {{
    MATCH (kv)
    WHERE kv.{sc.PROP_BUSINESS_KEY} = k.{sc.PROP_BUSINESS_KEY}
      AND kv.{sc.PROP_VERSION} = e.{sc.PROP_SOURCE_NODE_VERSION}
  }}
RETURN e.{sc.PROP_EVIDENCE_ID} AS identity,
       e.{sc.PROP_SOURCE_NODE_VERSION} AS pinned_version,
       k.{sc.PROP_BUSINESS_KEY} AS lineage
"""


def evidence_dangling_version_pin(driver: Driver) -> list[Violation]:
    """DDR-001 check 5: Evidence's source_node_version resolves to a retained version."""
    rows = query_rows(driver, _EVIDENCE_DANGLING_VERSION_PIN)
    return [
        Violation(
            invariant=_INV_EVIDENCE_VERSION_PIN,
            identity=str(row["identity"]),
            detail=(
                f"Evidence pins version {row['pinned_version']} of lineage "
                f"{row['lineage']!r}, which has no retained version node"
            ),
        )
        for row in rows
    ]
