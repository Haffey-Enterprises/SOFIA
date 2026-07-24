##############################################################################
# Module: supersession.py
# Service: conformance (RBT-48 catch-up)
# Author: Haffey Enterprises LLC
# Created: 2026-07-13
# Revised: 2026-07-13
# Description: Raw-CREATE fixtures (DDR-002 §4.2.1) for the supersession graph-
#   state assertions — DDR-002 §7 #22 (conditional-scope carry-forward on
#   supersession, predecessor-keyed). Supersession is modelled per DDR-002 §6:
#   the predecessor carries superseded_by = the successor's version, resolved
#   within the shared business_key lineage (the version-in-lineage convention the
#   Evidence version-pin assertion also uses). Labels/properties match the
#   committed DDR-002 v1.3.0 constants (mirrored in conformance.schema_constants).
#   No native constraints installed.
# Standards: ENG-STD-001 v3.2.0
##############################################################################
"""Conformant and violation graph fixtures for the supersession assertions."""

# --- #22 conditional-scope carry-forward --------------------------------------
# Conformant, two legit outcomes:
#   (A) carry_conditional  — pat-carry: v1 conditional superseded by v2, which
#       itself carries conditional (the EA-set scope is preserved);
#   (B) rescope_unconditional — pat-rescope: v1 conditional superseded by v2,
#       which is unconditional AND traces to a governing approving
#       PromotionDecision (the explicit EA re-scope act).
CONDITIONAL_CARRY_FORWARD_CONFORMANT: list[str] = [
    # (A) carry_conditional
    """
    CREATE (:Catalog:Pattern {pattern_id: 'pat-carry-v1', business_key: 'pat-carry',
                              version: 1, origin_mechanism: 'promoted',
                              recorded_at: '2026-01-01', applicability_state: 'conditional',
                              status: 'superseded', superseded_by: 2})
    """,
    """
    CREATE (:Catalog:Pattern {pattern_id: 'pat-carry-v2', business_key: 'pat-carry',
                              version: 2, origin_mechanism: 'promoted',
                              recorded_at: '2026-01-02', applicability_state: 'conditional',
                              status: 'active'})
    """,
    # (B) rescope_unconditional — the successor is unconditional but has a
    # governing approving PromotionDecision, so the re-scope is explicit.
    """
    CREATE (p1:Catalog:Pattern {pattern_id: 'pat-rescope-v1', business_key: 'pat-rescope',
                                version: 1, origin_mechanism: 'promoted',
                                recorded_at: '2026-01-01', applicability_state: 'conditional',
                                status: 'superseded', superseded_by: 2}),
           (p2:Catalog:Pattern {pattern_id: 'pat-rescope-v2', business_key: 'pat-rescope',
                                version: 2, origin_mechanism: 'promoted',
                                recorded_at: '2026-01-02', applicability_state: 'unconditional',
                                status: 'active'}),
           (cp:Reasoning:CandidatePromotion {candidate_id: 'cp-rescope',
                                             proposal_kind: 'promotion', status: 'promoted'}),
           (pd:Governance:Decision:PromotionDecision {decision_id: 'pd-rescope',
                                                      decided_at: '2026-01-02',
                                                      origin_mechanism: 'authored',
                                                      recorded_at: '2026-01-02'}),
           (cp)-[:PROMOTES_TO_KNOWLEDGE]->(p2),
           (pd)-[:DECIDED_ON {outcome: 'approved'}]->(cp)
    """,
]

# Violation: a conditional predecessor superseded by an unconditional successor
# with NO governing approving PromotionDecision — the silent default.
SILENT_DEFAULT_TO_UNCONDITIONAL: list[str] = [
    """
    CREATE (:Catalog:Pattern {pattern_id: 'pat-silent-v1', business_key: 'pat-silent',
                              version: 1, origin_mechanism: 'promoted',
                              recorded_at: '2026-01-01', applicability_state: 'conditional',
                              status: 'superseded', superseded_by: 2}),
           (:Catalog:Pattern {pattern_id: 'pat-silent-v2', business_key: 'pat-silent',
                              version: 2, origin_mechanism: 'promoted',
                              recorded_at: '2026-01-02', applicability_state: 'unconditional',
                              status: 'active'})
    """,
]

# Violation: the ingestion cross-origin case — an ingested successor carries no
# applicability_state and no re-scoping decision.
CROSS_ORIGIN_INGESTED_SUCCESSOR: list[str] = [
    """
    CREATE (:Catalog:Pattern {pattern_id: 'pat-crossorigin-v1',
                              business_key: 'pat-crossorigin', version: 1,
                              origin_mechanism: 'promoted', recorded_at: '2026-01-01',
                              applicability_state: 'conditional', status: 'superseded',
                              superseded_by: 2}),
           (:Catalog:Pattern {pattern_id: 'pat-crossorigin-v2',
                              business_key: 'pat-crossorigin', version: 2,
                              origin_mechanism: 'ingested', recorded_at: '2026-01-02',
                              source_record_ref: 'cmdb:pat-crossorigin', status: 'active'})
    """,
]

# Violation: unresolvable lineage — a conditional predecessor whose superseded_by
# points at a version with no retained node (dangling). §6's atomic supersession
# means this should never exist, so the check must fail loud rather than skip a
# safety-critical predecessor whose carry-forward can no longer be evaluated.
UNRESOLVABLE_SUPERSEDED_BY: list[str] = [
    """
    CREATE (:Catalog:Pattern {pattern_id: 'pat-dangling-v1', business_key: 'pat-dangling',
                              version: 1, origin_mechanism: 'promoted',
                              recorded_at: '2026-01-01', applicability_state: 'conditional',
                              status: 'superseded', superseded_by: 2})
    """,
]

# Violation: an unconditional successor whose only DECIDED_ON verdict is
# 'rejected' — a non-approving governing verdict is not an EA re-scope.
RESCOPE_DECISION_REJECTED: list[str] = [
    """
    CREATE (p1:Catalog:Pattern {pattern_id: 'pat-rejected-v1', business_key: 'pat-rejected',
                                version: 1, origin_mechanism: 'promoted',
                                recorded_at: '2026-01-01', applicability_state: 'conditional',
                                status: 'superseded', superseded_by: 2}),
           (p2:Catalog:Pattern {pattern_id: 'pat-rejected-v2', business_key: 'pat-rejected',
                                version: 2, origin_mechanism: 'promoted',
                                recorded_at: '2026-01-02', applicability_state: 'unconditional',
                                status: 'active'}),
           (cp:Reasoning:CandidatePromotion {candidate_id: 'cp-rejected',
                                             proposal_kind: 'promotion', status: 'rejected'}),
           (pd:Governance:Decision:PromotionDecision {decision_id: 'pd-rejected',
                                                      decided_at: '2026-01-02',
                                                      origin_mechanism: 'authored',
                                                      recorded_at: '2026-01-02'}),
           (cp)-[:PROMOTES_TO_KNOWLEDGE]->(p2),
           (pd)-[:DECIDED_ON {outcome: 'rejected'}]->(cp)
    """,
]
