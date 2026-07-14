##############################################################################
# Module: reasoning.py
# Service: conformance (RBT-48 catch-up)
# Author: Haffey Enterprises LLC
# Created: 2026-07-13
# Revised: 2026-07-13
# Description: Reasoning-Graph conclusion graph-state assertions (1a) — DDR-002
#   §7 #23 (flag<->category consistency: every ReasoningProgress carries an
#   authoritative value matching the fixed reasoner_category mapping,
#   llm_advisory -> false / all other categories -> true). Safety-critical tier:
#   guards against wrong-consumption of non-authoritative content as
#   authoritative (the ADR-001 §5.2 read-discipline surface). Labels and property
#   names are interpolated from conformance.schema_constants (single source);
#   values are passed as query parameters.
# Standards: ENG-STD-001 v3.2.0
##############################################################################
"""Graph-state conformance assertions for Reasoning-Graph conclusions."""

from neo4j import Driver

from conformance import schema_constants as sc
from conformance.assertions.base import Violation, query_rows

_INV_FLAG_CATEGORY = "DDR-002 §7 #23"

# #23 quantifies over EVERY ReasoningProgress (DDR-002 §4/§7 #23). It is NOT
# scoped to nodes that carry a reasoner_category: that property is T2, and §7's
# DB-enforced existence constraints cover only the provenance group + T1 required
# props — nothing forces reasoner_category to be present. So a category-absent
# node (worst shape: authoritative:true with no category) is a violation the
# fixed mapping cannot vouch for, and 1a graph-state exists precisely to catch
# nodes that arrived outside the mediated (1b) write path. Three violation modes:
#   (i)  category absent      -> the mapping cannot derive an expected flag;
#   (ii) flag absent          -> present category, no flag to check against;
#   (iii) flag <> expected    -> both mismatch directions of the fixed mapping,
#         where expected = (reasoner_category <> 'llm_advisory').
_FLAG_CATEGORY_MISMATCH = f"""
MATCH (rp:{sc.RG_LABEL}:{sc.REASONING_PROGRESS_LABEL})
WITH rp, CASE
    WHEN rp.{sc.PROP_REASONER_CATEGORY} IS NULL THEN null
    ELSE rp.{sc.PROP_REASONER_CATEGORY} <> $non_authoritative
END AS expected
WHERE rp.{sc.PROP_REASONER_CATEGORY} IS NULL
   OR rp.{sc.PROP_AUTHORITATIVE} IS NULL
   OR rp.{sc.PROP_AUTHORITATIVE} <> expected
RETURN rp.{sc.PROP_PROGRESS_ID} AS identity,
       rp.{sc.PROP_REASONER_CATEGORY} AS category,
       rp.{sc.PROP_AUTHORITATIVE} AS flag,
       expected AS expected
"""


def flag_category_consistency(driver: Driver) -> list[Violation]:
    """DDR-002 §7 #23: authoritative matches the fixed reasoner_category mapping."""
    rows = query_rows(
        driver,
        _FLAG_CATEGORY_MISMATCH,
        {"non_authoritative": sc.NON_AUTHORITATIVE_CATEGORY},
    )
    violations: list[Violation] = []
    for row in rows:
        if row["category"] is None:
            detail = (
                "ReasoningProgress carries no reasoner_category; the fixed mapping "
                f"cannot vouch for authoritative={row['flag']!r}"
            )
        else:
            detail = (
                f"reasoner_category {row['category']!r} requires authoritative="
                f"{row['expected']}, but node carries {row['flag']!r}"
            )
        violations.append(
            Violation(invariant=_INV_FLAG_CATEGORY, identity=str(row["identity"]), detail=detail)
        )
    return violations
