##############################################################################
# Module: retraction.py
# Service: conformance (RBT-48 catch-up)
# Author: Haffey Enterprises LLC
# Created: 2026-07-13
# Revised: 2026-07-13
# Description: Raw-CREATE fixtures (DDR-002 §4.2.1) for the retraction graph-state
#   assertions — DDR-002 §7 #21 (retraction-gated). Labels/properties match the
#   committed DDR-002 v1.3.0 constants (mirrored in conformance.schema_constants).
#   No native constraints installed.
# Standards: ENG-STD-001 v3.2.0
##############################################################################
"""Conformant and violation graph fixtures for the retraction assertions."""

# --- #21 retraction-gated -----------------------------------------------------
# Conformant: two retraction candidates, each EA-gated — one approved, one
# approved_conditional — with a RETRACTS edge to a (formerly promoted) KG node.
RETRACTION_GATED_CONFORMANT: list[str] = [
    """
    CREATE (cp:Reasoning:CandidatePromotion {candidate_id: 'cp-ret-approved',
                                             proposal_kind: 'retraction', status: 'promoted'}),
           (pd:Governance:Decision:PromotionDecision {decision_id: 'pd-ret-approved',
                                                      decided_at: '2026-01-02',
                                                      origin_mechanism: 'authored',
                                                      recorded_at: '2026-01-02'}),
           (k:Catalog:Pattern {pattern_id: 'pat-ret-a', business_key: 'pat-ret-a', version: 1,
                               origin_mechanism: 'promoted', recorded_at: '2026-01-01',
                               applicability_state: 'unconditional'}),
           (pd)-[:DECIDED_ON {outcome: 'approved'}]->(cp),
           (cp)-[:RETRACTS]->(k)
    """,
    """
    CREATE (cp:Reasoning:CandidatePromotion {candidate_id: 'cp-ret-cond',
                                             proposal_kind: 'retraction', status: 'promoted'}),
           (pd:Governance:Decision:PromotionDecision {decision_id: 'pd-ret-cond',
                                                      decided_at: '2026-01-02',
                                                      origin_mechanism: 'authored',
                                                      recorded_at: '2026-01-02'}),
           (k:Catalog:Pattern {pattern_id: 'pat-ret-c', business_key: 'pat-ret-c', version: 1,
                               origin_mechanism: 'promoted', recorded_at: '2026-01-01',
                               applicability_state: 'conditional'}),
           (pd)-[:DECIDED_ON {outcome: 'approved_conditional'}]->(cp),
           (cp)-[:RETRACTS]->(k)
    """,
]

# Conformant (deliberate #15 asymmetry): a retraction with an early 'approved'
# and a later 'rejected' verdict still has AN approving DECIDED_ON, so #21 does
# not flag it. The governing-verdict-flip detection for executed retractions is a
# deferred DDR-003 gap (DDR-002 §2.4); #21 traces to an approving, not the
# governing, decision.
RETRACTS_STALE_APPROVING_NOT_GOVERNING: list[str] = [
    """
    CREATE (cp:Reasoning:CandidatePromotion {candidate_id: 'cp-stale',
                                             proposal_kind: 'retraction', status: 'promoted'}),
           (pd1:Governance:Decision:PromotionDecision {decision_id: 'pd-early',
                                                       decided_at: '2026-01-01',
                                                       origin_mechanism: 'authored',
                                                       recorded_at: '2026-01-01'}),
           (pd2:Governance:Decision:PromotionDecision {decision_id: 'pd-late',
                                                       decided_at: '2026-01-05',
                                                       origin_mechanism: 'authored',
                                                       recorded_at: '2026-01-05'}),
           (k:Catalog:Pattern {pattern_id: 'pat-stale', business_key: 'pat-stale', version: 1,
                               origin_mechanism: 'promoted', recorded_at: '2026-01-01',
                               applicability_state: 'unconditional'}),
           (pd1)-[:DECIDED_ON {outcome: 'approved'}]->(cp),
           (pd2)-[:DECIDED_ON {outcome: 'rejected'}]->(cp),
           (cp)-[:RETRACTS]->(k)
    """,
]

# Violation: a RETRACTS edge from a proposal_kind:promotion candidate (with an
# approving decision) — only a retraction candidate may retract.
RETRACTS_FROM_PROMOTION_KIND: list[str] = [
    """
    CREATE (cp:Reasoning:CandidatePromotion {candidate_id: 'cp-wrongkind',
                                             proposal_kind: 'promotion', status: 'promoted'}),
           (pd:Governance:Decision:PromotionDecision {decision_id: 'pd-wrongkind',
                                                      decided_at: '2026-01-02',
                                                      origin_mechanism: 'authored',
                                                      recorded_at: '2026-01-02'}),
           (k:Catalog:Pattern {pattern_id: 'pat-wk', business_key: 'pat-wk', version: 1,
                               origin_mechanism: 'promoted', recorded_at: '2026-01-01',
                               applicability_state: 'unconditional'}),
           (pd)-[:DECIDED_ON {outcome: 'approved'}]->(cp),
           (cp)-[:RETRACTS]->(k)
    """,
]

# Violation: a retraction candidate with NO DECIDED_ON at all — un-promotion not
# EA-gated (the bare-delete-equivalent).
RETRACTS_WITHOUT_APPROVING_DECISION: list[str] = [
    """
    CREATE (cp:Reasoning:CandidatePromotion {candidate_id: 'cp-unapproved',
                                             proposal_kind: 'retraction', status: 'promoted'}),
           (k:Catalog:Pattern {pattern_id: 'pat-un', business_key: 'pat-un', version: 1,
                               origin_mechanism: 'promoted', recorded_at: '2026-01-01',
                               applicability_state: 'unconditional'}),
           (cp)-[:RETRACTS]->(k)
    """,
]

# Violation: a retraction candidate whose only DECIDED_ON verdict is 'rejected'
# — a non-approving decision does not gate the un-promotion.
RETRACTS_ONLY_REJECTED: list[str] = [
    """
    CREATE (cp:Reasoning:CandidatePromotion {candidate_id: 'cp-rejonly',
                                             proposal_kind: 'retraction', status: 'rejected'}),
           (pd:Governance:Decision:PromotionDecision {decision_id: 'pd-rejonly',
                                                      decided_at: '2026-01-02',
                                                      origin_mechanism: 'authored',
                                                      recorded_at: '2026-01-02'}),
           (k:Catalog:Pattern {pattern_id: 'pat-rej', business_key: 'pat-rej', version: 1,
                               origin_mechanism: 'promoted', recorded_at: '2026-01-01',
                               applicability_state: 'unconditional'}),
           (pd)-[:DECIDED_ON {outcome: 'rejected'}]->(cp),
           (cp)-[:RETRACTS]->(k)
    """,
]

# Violation: a RETRACTS edge originating from a non-CandidatePromotion node —
# malformed (DDR-002 §5: RETRACTS originates from a CandidatePromotion).
RETRACTS_FROM_NON_CANDIDATE: list[str] = [
    """
    CREATE (rp:Reasoning:ReasoningProgress {progress_id: 'rp-not-a-candidate',
                                            reasoner_category: 'encoded_reasoning',
                                            authoritative: true, origin_mechanism: 'authored',
                                            recorded_at: '2026-01-01'}),
           (k:Catalog:Pattern {pattern_id: 'pat-nc', business_key: 'pat-nc', version: 1,
                               origin_mechanism: 'promoted', recorded_at: '2026-01-01',
                               applicability_state: 'unconditional'}),
           (rp)-[:RETRACTS]->(k)
    """,
]

# --- #25 proposal_kind <-> RETRACTS (executed-proposal scope, v1.3.0) ----------
# Conformant, three consistent cases:
#   cp-exec  — proposal_kind:retraction at terminal status:promoted WITH a RETRACTS
#              edge (the executed un-promotion);
#   cp-unexec — proposal_kind:retraction not yet executed (status:approved) with NO
#              RETRACTS edge (the edge-writing is the materialization act);
#   cp-promo — a promotion candidate with no RETRACTS edge (not a #25 subject).
PROPOSAL_KIND_RETRACTS_CONFORMANT: list[str] = [
    """
    CREATE (cp:Reasoning:CandidatePromotion {candidate_id: 'cp-exec',
                                             proposal_kind: 'retraction', status: 'promoted'}),
           (k:Catalog:Pattern {pattern_id: 'pat-exec', business_key: 'pat-exec', version: 1,
                               origin_mechanism: 'promoted', recorded_at: '2026-01-01',
                               applicability_state: 'unconditional'}),
           (cp)-[:RETRACTS]->(k)
    """,
    """
    CREATE (:Reasoning:CandidatePromotion {candidate_id: 'cp-unexec',
                                           proposal_kind: 'retraction', status: 'approved'})
    """,
    """
    CREATE (:Reasoning:CandidatePromotion {candidate_id: 'cp-promo',
                                           proposal_kind: 'promotion', status: 'promoted'})
    """,
]

# Violation (forward): an executed retraction (terminal status:promoted) with NO
# RETRACTS edge.
EXECUTED_RETRACTION_MISSING_EDGE: list[str] = [
    """
    CREATE (:Reasoning:CandidatePromotion {candidate_id: 'cp-executed-noedge',
                                           proposal_kind: 'retraction', status: 'promoted'})
    """,
]

# Violation (reverse): a RETRACTS edge from a proposal_kind:promotion candidate.
RETRACTS_FROM_PROMOTION_KIND_25: list[str] = [
    """
    CREATE (cp:Reasoning:CandidatePromotion {candidate_id: 'cp-promo-retracts',
                                             proposal_kind: 'promotion', status: 'promoted'}),
           (k:Catalog:Pattern {pattern_id: 'pat-pr', business_key: 'pat-pr', version: 1,
                               origin_mechanism: 'promoted', recorded_at: '2026-01-01',
                               applicability_state: 'unconditional'}),
           (cp)-[:RETRACTS]->(k)
    """,
]

# Violation (pre-execution): a retraction proposal before materialization
# (status:approved, not promoted) that already carries a RETRACTS edge.
UNEXECUTED_RETRACTION_WITH_EDGE: list[str] = [
    """
    CREATE (cp:Reasoning:CandidatePromotion {candidate_id: 'cp-premature-edge',
                                             proposal_kind: 'retraction', status: 'approved'}),
           (k:Catalog:Pattern {pattern_id: 'pat-pm', business_key: 'pat-pm', version: 1,
                               origin_mechanism: 'promoted', recorded_at: '2026-01-01',
                               applicability_state: 'unconditional'}),
           (cp)-[:RETRACTS]->(k)
    """,
]

# Conformant (rejected retraction — the Touch-1 acceptance walkthrough shape): a
# proposal_kind:retraction at terminal status:rejected with NO RETRACTS edge. The
# old unscoped #25 produced a permanent false positive here (it demanded the edge
# unconditionally); the v1.3.0 executed-proposal scope passes it — forward needs
# status:promoted, reverse and pre-execution both need an edge. Ties the harness
# to the RBT-54 Touch-1 acceptance record by name.
REJECTED_RETRACTION_CONFORMANT: list[str] = [
    """
    CREATE (:Reasoning:CandidatePromotion {candidate_id: 'cp-rejected-ret',
                                           proposal_kind: 'retraction', status: 'rejected'})
    """,
]

# Violation (reverse, null-kind): a RETRACTS edge from a CandidatePromotion that
# carries NO proposal_kind. proposal_kind is T2 — no DB existence constraint forces
# it — so the reverse predicate must flag the null-kind source (IS NULL branch),
# not null-skip it (A-3). An edge whose source cannot vouch for its kind is exactly
# what the reverse direction exists to catch.
RETRACTS_FROM_KINDLESS_CANDIDATE: list[str] = [
    """
    CREATE (cp:Reasoning:CandidatePromotion {candidate_id: 'cp-kindless',
                                             status: 'promoted'}),
           (k:Catalog:Pattern {pattern_id: 'pat-kl', business_key: 'pat-kl', version: 1,
                               origin_mechanism: 'promoted', recorded_at: '2026-01-01',
                               applicability_state: 'unconditional'}),
           (cp)-[:RETRACTS]->(k)
    """,
]
