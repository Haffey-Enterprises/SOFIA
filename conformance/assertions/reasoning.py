##############################################################################
# Module: reasoning.py
# Service: conformance (RBT-48 catch-up)
# Author: Haffey Enterprises LLC
# Created: 2026-07-13
# Revised: 2026-07-13
# Description: Reasoning-Graph conclusion graph-state assertions (1a) — DDR-002
#   §7 #23 (flag<->category consistency: every ReasoningProgress carries an
#   authoritative value matching the fixed reasoner_category mapping,
#   llm_advisory -> false / all other categories -> true; safety-critical tier,
#   guarding wrong-consumption of non-authoritative content as authoritative — the
#   ADR-001 §5.2 read-discipline surface), #24 (rollup upper bound: a conclusion's
#   confidence <= its strongest supporting Evidence path; follow tier), and #28
#   (Evidence.confidence presence: every (:Reasoning:Evidence) carries a non-null
#   confidence; follow tier, the out-of-path presence backstop). Labels and
#   property names are interpolated from conformance.schema_constants (single
#   source); values are passed as query parameters.
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


_INV_ROLLUP_CEILING = "DDR-002 §7 #24"

# #24 (follow tier, graph-state only): ReasoningProgress.confidence <=
# max(SUPPORTED_BY Evidence.confidence) — a conclusion is no more confident than
# its strongest evidence path (DDR-002 §4). Scoped to conclusions WITH supporting
# evidence: the MATCH requires a SUPPORTED_BY edge, so a zero-evidence conclusion
# produces no row (that case is SDD-routed, §4). This is 1a-only by ruling — #24
# is not checkable at conclusion-write time (evidence attaches later, SDD-001
# §3.4.2), so there is no 1b write contract. The comparator is bound to §4's canon
# (ceiling = max supporting Evidence.confidence); it amends with the SDD's rollup
# function if that redefines path strength.
#
# Skip-path (honest floor): when every supporting Evidence carries a null
# confidence, max() is null and the ceiling is undefined — such a conclusion is
# NOT flagged here. That is an evidence-confidence-presence concern owned by #28
# (evidence_confidence_presence), not the #24 rollup comparator; the two concerns
# stay distinct (comparator vs. presence, DDR-002 §7 #24/#28). #28 catches the
# null Evidence directly, so the all-null supporting set #24 skips by construction
# is covered — no open gap. #24 is a follow-tier reasoning-quality check.
# Mixed-null direction: Neo4j's max() ignores nulls, so a conclusion with SOME
# null-confidence evidence takes its ceiling from the non-null subset only — which
# under-states the true ceiling and therefore TIGHTENS (never loosens) the check.
# The conservative direction is stated, not silent. (Presence is #28's, obs O-1.)
_ROLLUP_CEILING_EXCEEDED = f"""
MATCH (rp:{sc.RG_LABEL}:{sc.REASONING_PROGRESS_LABEL})
      -[:{sc.SUPPORTED_BY}]->(e:{sc.RG_LABEL}:{sc.EVIDENCE_LABEL})
WITH rp, max(e.{sc.PROP_CONFIDENCE}) AS ceiling
WHERE rp.{sc.PROP_CONFIDENCE} IS NOT NULL
  AND ceiling IS NOT NULL
  AND rp.{sc.PROP_CONFIDENCE} > ceiling
RETURN rp.{sc.PROP_PROGRESS_ID} AS identity,
       rp.{sc.PROP_CONFIDENCE} AS confidence,
       ceiling AS ceiling
"""


def rollup_upper_bound(driver: Driver) -> list[Violation]:
    """DDR-002 §7 #24: a conclusion's confidence <= its strongest evidence path."""
    rows = query_rows(driver, _ROLLUP_CEILING_EXCEEDED)
    return [
        Violation(
            invariant=_INV_ROLLUP_CEILING,
            identity=str(row["identity"]),
            detail=(
                f"ReasoningProgress confidence {row['confidence']} exceeds the ceiling "
                f"{row['ceiling']} (max supporting Evidence.confidence)"
            ),
        )
        for row in rows
    ]


_INV_EVIDENCE_CONFIDENCE = "DDR-002 §7 #28"

# #28 (follow tier, graph-state only): every (:Reasoning:Evidence) node carries a
# non-null confidence (DDR-002 §7 #28). confidence is T2, so the DB-existence
# constraints (provenance group + T1 required props) do not force it; the mediated
# capture path guarantees a value by construction — DDR-004's derive-or-reject
# totality computes the inherited value or rejects the citation typed (incl. the
# branch-(i) null-native reject, DDR-004 §1), never defaulting a null — but no
# graph-state check verifies presence on an Evidence node that arrived OUTSIDE
# that path. #28 is that out-of-path presence backstop: the #23 pattern applied to
# the confidence surface (as #23 backstops the authoritative flag despite the
# sole-writer gateway), a fortiori proportionate as a follow-tier check.
#
# Quantified over ALL Evidence, NOT gated on SUPPORTED_BY: per DDR-002 §7 #28 the
# check fires "independent of whether it yet supports any conclusion" — schema-
# legal unlinked Evidence exists (§4), and an unlinked null-confidence node is
# exactly the out-of-path shape 1a exists to catch. This also closes the
# interaction #24 names: an all-null supporting set leaves #24's max() ceiling
# undefined so #24 skips that conclusion by construction, while #28 catches the
# null Evidence directly. 1a-only by ruling: the write-time guarantee is subsumed
# by DDR-004's (now null-safe) derive-or-reject totality, so #28 carries no
# separate 1b write contract of its own.
_EVIDENCE_CONFIDENCE_ABSENT = f"""
MATCH (e:{sc.RG_LABEL}:{sc.EVIDENCE_LABEL})
WHERE e.{sc.PROP_CONFIDENCE} IS NULL
RETURN e.{sc.PROP_EVIDENCE_ID} AS identity
"""


def evidence_confidence_presence(driver: Driver) -> list[Violation]:
    """DDR-002 §7 #28: every Evidence node carries a non-null confidence."""
    rows = query_rows(driver, _EVIDENCE_CONFIDENCE_ABSENT)
    return [
        Violation(
            invariant=_INV_EVIDENCE_CONFIDENCE,
            identity=str(row["identity"]),
            detail=(
                "Evidence carries a null confidence; the mediated capture path derives "
                "or rejects (never defaults a null), so this node arrived outside it"
            ),
        )
        for row in rows
    ]
