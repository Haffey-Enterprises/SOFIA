##############################################################################
# Module: supersession.py
# Service: conformance (RBT-48 catch-up)
# Author: Haffey Enterprises LLC
# Created: 2026-07-13
# Revised: 2026-07-13
# Description: Supersession graph-state assertions (1a) — DDR-002 §7 #22
#   (conditional-scope carry-forward on supersession, predecessor-keyed).
#   Safety-critical tier: guards conditional knowledge against over-admission
#   past an EA-set scope. Labels and property names are interpolated from
#   conformance.schema_constants (single source); values are query parameters.
#
#   Supersession modelling (DDR-002 §6): the predecessor carries superseded_by =
#   the successor's version, resolved within the shared business_key lineage
#   (the version-in-lineage convention the Evidence version-pin assertion uses;
#   the real-schema representation binds at RBT-15).
#
#   Structure vs. deliberateness (honest floor): for a promoted successor this
#   1a assertion proves STRUCTURE — an approving governing decision exists (which
#   catches the ingested cross-origin shape, the rejected-verdict shape, and the
#   unresolvable-lineage shape) — but NOT deliberateness: graph-state cannot
#   distinguish a conscious EA re-scope from an approval that never engaged the
#   condition (both look identical). Deliberateness is carried by the 1b
#   SCOPE_DISPOSITION_MISSING contract, which is why both halves are needed; 1a
#   alone does not discharge #22.
# Standards: ENG-STD-001 v3.2.0
##############################################################################
"""Graph-state conformance assertions for the supersession invariants."""

from neo4j import Driver

from conformance import schema_constants as sc
from conformance.assertions.base import Violation, query_rows

_INV_CARRY_FORWARD = "DDR-002 §7 #22"

# #22 predecessor-keyed: for every superseded applicability_state:conditional
# predecessor, resolve its successor (same business_key, version = superseded_by)
# and flag it unless the EA-set scope carried forward. Legit successor outcomes:
# (a) the successor carries conditional; (b) the successor is non-conditional
# (unconditional or absent) BUT traces to a governing approving PromotionDecision
# — the explicit EA re-scope. Three violation modes:
#   (i)  unresolvable lineage — superseded_by resolves to NO retained node; the
#        carry-forward can no longer be evaluated, so a safety-critical check must
#        fail LOUD (§6's atomic supersession means this shape should never exist).
#        The successor is OPTIONAL-matched precisely so a null resolution flags
#        rather than silently drops the predecessor.
#   (ii) silent default — non-conditional successor with no governing approving
#        decision (the case #19 cannot catch, the successor no longer conditional).
#   (iii) cross-origin — an ingested successor carries neither applicability_state
#        nor a decision; the same no-governing-approving-decision branch catches it.
# The governing verdict is keyed off the latest decided_at (§2.4), mirroring #15;
# a successor with no decision chain collects [] -> governing NULL -> flagged.
_CONDITIONAL_CARRY_FORWARD = f"""
MATCH (pred)
WHERE pred.{sc.PROP_APPLICABILITY_STATE} = $conditional
  AND pred.{sc.PROP_SUPERSEDED_BY} IS NOT NULL
OPTIONAL MATCH (succ)
  WHERE succ.{sc.PROP_BUSINESS_KEY} = pred.{sc.PROP_BUSINESS_KEY}
    AND succ.{sc.PROP_VERSION} = pred.{sc.PROP_SUPERSEDED_BY}
OPTIONAL MATCH (succ)<-[:{sc.PROMOTES_TO_KNOWLEDGE}]-(:{sc.CANDIDATE_PROMOTION_LABEL})
              <-[d:{sc.DECIDED_ON}]-(pd:{sc.PROMOTION_DECISION_LABEL})
WITH pred, succ, d.{sc.PROP_OUTCOME} AS outcome, pd.{sc.PROP_DECIDED_AT} AS decided_at
ORDER BY decided_at DESC
WITH pred, succ, collect(outcome) AS outcomes
WITH pred, succ, head(outcomes) AS governing
WHERE succ IS NULL
   OR ((succ.{sc.PROP_APPLICABILITY_STATE} IS NULL
        OR succ.{sc.PROP_APPLICABILITY_STATE} <> $conditional)
       AND (governing IS NULL OR NOT governing IN $approving))
RETURN pred.{sc.PROP_BUSINESS_KEY} AS identity,
       pred.{sc.PROP_VERSION} AS pred_version,
       pred.{sc.PROP_SUPERSEDED_BY} AS superseded_by,
       succ.{sc.PROP_VERSION} AS succ_version,
       succ.{sc.PROP_APPLICABILITY_STATE} AS succ_state,
       governing AS governing
"""


def conditional_scope_carry_forward(driver: Driver) -> list[Violation]:
    """DDR-002 §7 #22: a superseded conditional node's scope carries forward."""
    rows = query_rows(
        driver,
        _CONDITIONAL_CARRY_FORWARD,
        {
            "conditional": sc.APPLICABILITY_STATE_CONDITIONAL,
            "approving": sorted(sc.APPROVING_OUTCOMES),
        },
    )
    violations: list[Violation] = []
    for row in rows:
        if row["succ_version"] is None:
            detail = (
                f"conditional v{row['pred_version']} has superseded_by="
                f"{row['superseded_by']} that resolves to no retained version node "
                "(broken lineage; carry-forward unevaluatable)"
            )
        else:
            detail = (
                f"conditional v{row['pred_version']} superseded by non-conditional "
                f"v{row['succ_version']} (applicability_state={row['succ_state']!r}) with no "
                f"governing approving re-scope decision (governing verdict={row['governing']!r})"
            )
        violations.append(
            Violation(invariant=_INV_CARRY_FORWARD, identity=str(row["identity"]), detail=detail)
        )
    return violations
