##############################################################################
# Module: decision.py
# Service: conformance (RBT-33)
# Author: Haffey Enterprises LLC
# Created: 2026-06-22
# Revised: 2026-06-22
# Description: Raw-CREATE fixtures (DDR-002 §4.2.1) for the Decision-subtype
#   graph-state assertion — DDR-002 §7 #16 (every Decision carries exactly one of
#   {GateDecision, PromotionDecision}; never bare, never both).
# Standards: ENG-STD-001 v3.2.0
##############################################################################
"""Conformant and violation fixtures for the Decision-subtype assertion."""

# Conformant: one GateDecision and one PromotionDecision, each with exactly one
# subtype label.
DECISION_SUBTYPE_CONFORMANT: list[str] = [
    "CREATE (:Governance:Decision:GateDecision {decision_id: 'gd-1'})",
    "CREATE (:Governance:Decision:PromotionDecision {decision_id: 'pd-1'})",
]

# Violation: a bare Decision with no subtype label.
DECISION_BARE_VIOLATION: list[str] = [
    "CREATE (:Governance:Decision {decision_id: 'dec-bare'})",
]

# Violation: a Decision carrying both subtype labels.
DECISION_BOTH_SUBTYPES_VIOLATION: list[str] = [
    "CREATE (:Governance:Decision:GateDecision:PromotionDecision {decision_id: 'dec-both'})",
]

# --- #15 companion: per-candidate decided_at uniqueness -----------------------
# Conformant: a candidate with two DECIDED_ON edges from distinct PromotionDecisions
# carrying distinct decided_at (a legitimate append-only re-decision, §2.4).
DECIDED_AT_DISTINCT_CONFORMANT: list[str] = [
    """
    CREATE (cp:Reasoning:CandidatePromotion {candidate_id: 'cp-mono',
                                             proposal_kind: 'promotion', status: 'promoted'}),
           (pd1:Governance:Decision:PromotionDecision {decision_id: 'pd-mono-1',
                                                       decided_at: '2026-01-01',
                                                       origin_mechanism: 'authored',
                                                       recorded_at: '2026-01-01'}),
           (pd2:Governance:Decision:PromotionDecision {decision_id: 'pd-mono-2',
                                                       decided_at: '2026-01-02',
                                                       origin_mechanism: 'authored',
                                                       recorded_at: '2026-01-02'}),
           (pd1)-[:DECIDED_ON {outcome: 'rejected'}]->(cp),
           (pd2)-[:DECIDED_ON {outcome: 'approved'}]->(cp)
    """,
]

# Violation: two DECIDED_ON edges on one candidate sharing decided_at — a tie the
# governing-verdict selector cannot resolve.
DECIDED_AT_DUPLICATE: list[str] = [
    """
    CREATE (cp:Reasoning:CandidatePromotion {candidate_id: 'cp-dup',
                                             proposal_kind: 'promotion', status: 'promoted'}),
           (pd1:Governance:Decision:PromotionDecision {decision_id: 'pd-dup-1',
                                                       decided_at: '2026-01-03',
                                                       origin_mechanism: 'authored',
                                                       recorded_at: '2026-01-03'}),
           (pd2:Governance:Decision:PromotionDecision {decision_id: 'pd-dup-2',
                                                       decided_at: '2026-01-03',
                                                       origin_mechanism: 'authored',
                                                       recorded_at: '2026-01-03'}),
           (pd1)-[:DECIDED_ON {outcome: 'approved'}]->(cp),
           (pd2)-[:DECIDED_ON {outcome: 'rejected'}]->(cp)
    """,
]

# Conformant (scoping proof): a Solution with two GateDecision DECIDED_ON edges
# sharing decided_at is NOT flagged — monotonicity is scoped to
# PromotionDecision -> CandidatePromotion, not GateDecision -> Solution (SDD §3.6.3).
GATE_DECISION_DUPLICATE_DECIDED_AT: list[str] = [
    """
    CREATE (s:Artifact:Solution {artifact_id: 'sol-1', artifact_type: 'solution', version: 1,
                                 origin_mechanism: 'authored', recorded_at: '2026-01-01'}),
           (gd1:Governance:Decision:GateDecision {decision_id: 'gd-1', decided_at: '2026-01-04',
                                                  origin_mechanism: 'ingested',
                                                  recorded_at: '2026-01-04',
                                                  source_record_ref: 'gate:gd-1'}),
           (gd2:Governance:Decision:GateDecision {decision_id: 'gd-2', decided_at: '2026-01-04',
                                                  origin_mechanism: 'ingested',
                                                  recorded_at: '2026-01-04',
                                                  source_record_ref: 'gate:gd-2'}),
           (gd1)-[:DECIDED_ON {outcome: 'approved'}]->(s),
           (gd2)-[:DECIDED_ON {outcome: 'rejected'}]->(s)
    """,
]
