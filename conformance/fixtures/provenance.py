##############################################################################
# Module: provenance.py
# Service: conformance (RBT-33)
# Author: Haffey Enterprises LLC
# Created: 2026-06-22
# Revised: 2026-06-22
# Description: Raw-CREATE fixtures (DDR-002 §4.2.1) for the provenance-cluster
#   graph-state assertions — DDR-002 §7 #1 (RG-provenance edges), #11 (provenance
#   distinguishability), #15 (promoted -> governing approving decision), #17
#   (ingested/distilled -> source_record_ref), and DDR-001 check 5 (Evidence
#   version-pin integrity). Each constant is a list of self-contained CREATE
#   statements; labels/properties match the committed DDR-002 v1.0.0 constants
#   (mirrored in conformance.schema_constants). No native constraints installed.
# Standards: ENG-STD-001 v3.2.0
##############################################################################
"""Conformant and violation graph fixtures for the provenance assertions."""

# --- #1 RG-provenance edges ---------------------------------------------------
# Conformant: an Evidence sourced from a provenance-bearing KG node, and a
# RejectedAlternative reached by exactly one REJECTED parent.
RG_PROVENANCE_CONFORMANT: list[str] = [
    """
    CREATE (c:Catalog:Capability {capability_id: 'cap-1', version: 1,
                                   business_key: 'cap', origin_mechanism: 'ingested',
                                   recorded_at: '2026-01-01',
                                   source_record_ref: 'cmdb:cap-1'}),
           (e:Reasoning:Evidence {evidence_id: 'ev-1', source_node_version: 1}),
           (e)-[:SOURCED_FROM]->(c)
    """,
    """
    CREATE (rp:Reasoning:ReasoningProgress {progress_id: 'rp-1',
                                            origin_mechanism: 'authored',
                                            recorded_at: '2026-01-01'}),
           (ra:Reasoning:RejectedAlternative {rejected_id: 'ra-1',
                                              origin_mechanism: 'authored',
                                              recorded_at: '2026-01-01'}),
           (rp)-[:REJECTED]->(ra)
    """,
]

# Violation: an Evidence node with no SOURCED_FROM edge at all.
EVIDENCE_WITHOUT_SOURCE: list[str] = [
    "CREATE (:Reasoning:Evidence {evidence_id: 'ev-orphan', source_node_version: 1})",
]

# Violation: Evidence sourced from a node that is not a provenance-bearing KG
# node (a ReasoningProgress carries no KG plane label and no origin_mechanism
# as a SOURCED_FROM target should).
EVIDENCE_SOURCED_FROM_NON_KG: list[str] = [
    """
    CREATE (e:Reasoning:Evidence {evidence_id: 'ev-badsrc', source_node_version: 1}),
           (x:Reasoning:ReasoningProgress {progress_id: 'rp-x',
                                           origin_mechanism: 'authored',
                                           recorded_at: '2026-01-01'}),
           (e)-[:SOURCED_FROM]->(x)
    """,
]

# Violation: a RejectedAlternative with zero REJECTED parents.
REJECTED_ALTERNATIVE_NO_PARENT: list[str] = [
    """
    CREATE (:Reasoning:RejectedAlternative {rejected_id: 'ra-orphan',
                                            origin_mechanism: 'authored',
                                            recorded_at: '2026-01-01'})
    """,
]

# --- #11 provenance distinguishability (valid origin_mechanism value) --------
# Conformant: nodes carrying valid origin_mechanism values, including both
# 'promoted' and 'ingested' so distinguishability holds (DDR-002 §7 #11, §1).
ORIGIN_MECHANISM_CONFORMANT: list[str] = [
    """
    CREATE (:Catalog:Capability {capability_id: 'cap-i', version: 1,
                                  origin_mechanism: 'ingested', recorded_at: '2026-01-01',
                                  source_record_ref: 'cmdb:cap-i'})
    """,
    """
    CREATE (:Catalog:Pattern {pattern_id: 'pat-p', version: 1, business_key: 'pat',
                              origin_mechanism: 'promoted', recorded_at: '2026-01-01',
                              applicability_state: 'unconditional'})
    """,
]

# Violation: a node whose origin_mechanism is outside {ingested, authored,
# promoted, derived}.
ORIGIN_MECHANISM_INVALID_VALUE: list[str] = [
    """
    CREATE (:Catalog:Capability {capability_id: 'cap-bad', version: 1,
                                 origin_mechanism: 'made_up', recorded_at: '2026-01-01'})
    """,
]

# Violation: a RejectedAlternative reached by two REJECTED parents.
REJECTED_ALTERNATIVE_TWO_PARENTS: list[str] = [
    """
    CREATE (rp1:Reasoning:ReasoningProgress {progress_id: 'rp-a',
                                             origin_mechanism: 'authored',
                                             recorded_at: '2026-01-01'}),
           (rp2:Reasoning:ReasoningProgress {progress_id: 'rp-b',
                                             origin_mechanism: 'authored',
                                             recorded_at: '2026-01-01'}),
           (ra:Reasoning:RejectedAlternative {rejected_id: 'ra-double',
                                              origin_mechanism: 'authored',
                                              recorded_at: '2026-01-01'}),
           (rp1)-[:REJECTED]->(ra),
           (rp2)-[:REJECTED]->(ra)
    """,
]


# --- #15 promoted -> governing approving decision -----------------------------
# Conformant cases (all pass):
#   pat-ok  : single governing decision, approved
#   pat-re  : re-approved — earlier rejected, LATER approved -> governing approved
#   pat-cond: governing decision approved_conditional
PROMOTED_GOVERNING_CONFORMANT: list[str] = [
    """
    CREATE (k:Catalog:Pattern {pattern_id: 'pat-ok', version: 1, business_key: 'pat-ok',
                               origin_mechanism: 'promoted', recorded_at: '2026-01-01',
                               applicability_state: 'unconditional'}),
           (cp:Reasoning:CandidatePromotion {candidate_id: 'cp-ok'}),
           (pd:Governance:Decision:PromotionDecision {decision_id: 'pd-ok',
                                                      decided_at: '2026-01-15'}),
           (cp)-[:PROMOTES_TO_KNOWLEDGE]->(k),
           (pd)-[:DECIDED_ON {outcome: 'approved'}]->(cp)
    """,
    """
    CREATE (k:Catalog:Pattern {pattern_id: 'pat-re', version: 1, business_key: 'pat-re',
                               origin_mechanism: 'promoted', recorded_at: '2026-01-01',
                               applicability_state: 'unconditional'}),
           (cp:Reasoning:CandidatePromotion {candidate_id: 'cp-re'}),
           (pd1:Governance:Decision:PromotionDecision {decision_id: 'pd-re1',
                                                       decided_at: '2026-01-01'}),
           (pd2:Governance:Decision:PromotionDecision {decision_id: 'pd-re2',
                                                       decided_at: '2026-02-01'}),
           (cp)-[:PROMOTES_TO_KNOWLEDGE]->(k),
           (pd1)-[:DECIDED_ON {outcome: 'rejected'}]->(cp),
           (pd2)-[:DECIDED_ON {outcome: 'approved'}]->(cp)
    """,
    """
    CREATE (k:Catalog:Pattern {pattern_id: 'pat-cond', version: 1, business_key: 'pat-cond',
                               origin_mechanism: 'promoted', recorded_at: '2026-01-01',
                               applicability_state: 'conditional'}),
           (cp:Reasoning:CandidatePromotion {candidate_id: 'cp-cond'}),
           (pd:Governance:Decision:PromotionDecision {decision_id: 'pd-cond',
                                                      decided_at: '2026-01-20'}),
           (cp)-[:PROMOTES_TO_KNOWLEDGE]->(k),
           (pd)-[:DECIDED_ON {outcome: 'approved_conditional'}]->(cp)
    """,
]

# THE TRAP — violation: governing (latest decided_at) verdict is 'rejected' even
# though an earlier, superseded verdict was 'approved'. A naive "any approving
# decision exists" check wrongly passes this; keying off the governing edge
# catches it (DDR-002 §7 #15, §2.4 verdict precedence).
PROMOTED_SUPERSEDED_APPROVAL_VIOLATION: list[str] = [
    """
    CREATE (k:Catalog:Pattern {pattern_id: 'pat-sup', version: 1, business_key: 'pat-sup',
                               origin_mechanism: 'promoted', recorded_at: '2026-01-01',
                               applicability_state: 'unconditional'}),
           (cp:Reasoning:CandidatePromotion {candidate_id: 'cp-sup'}),
           (pd1:Governance:Decision:PromotionDecision {decision_id: 'pd-sup1',
                                                       decided_at: '2026-01-01'}),
           (pd2:Governance:Decision:PromotionDecision {decision_id: 'pd-sup2',
                                                       decided_at: '2026-02-01'}),
           (cp)-[:PROMOTES_TO_KNOWLEDGE]->(k),
           (pd1)-[:DECIDED_ON {outcome: 'approved'}]->(cp),
           (pd2)-[:DECIDED_ON {outcome: 'rejected'}]->(cp)
    """,
]

# Violation: a promoted node with no governing PromotionDecision at all.
PROMOTED_NO_DECISION_VIOLATION: list[str] = [
    """
    CREATE (:Catalog:Pattern {pattern_id: 'pat-nodec', version: 1, business_key: 'pat-nodec',
                              origin_mechanism: 'promoted', recorded_at: '2026-01-01',
                              applicability_state: 'unconditional'})
    """,
]


# --- #17 ingested/distilled -> source_record_ref ------------------------------
# Conformant: an ingested node and a distilled node each carrying a
# source_record_ref, plus an 'aggregated' node WITHOUT one — aggregated derives
# from internal version-pins and is exempt (DDR-002 §7 #17, §1).
SOURCE_RECORD_REF_CONFORMANT: list[str] = [
    """
    CREATE (:Catalog:Capability {capability_id: 'cap-ok', business_key: 'cap-ok', version: 1,
                                 origin_mechanism: 'ingested', recorded_at: '2026-01-01',
                                 source_record_ref: 'cmdb:cap-ok'})
    """,
    """
    CREATE (:Operational:ObservedPattern {
        observed_pattern_id: 'op-ok', business_key: 'op-ok',
        origin_mechanism: 'derived', derivation_class: 'distilled',
        recorded_at: '2026-01-01', source_record_ref: 'telemetry:op-ok'})
    """,
    """
    CREATE (:Cost:CapabilityCostEstimate {
        estimate_id: 'est-ok', business_key: 'est-ok',
        origin_mechanism: 'derived', derivation_class: 'aggregated',
        recorded_at: '2026-01-01'})
    """,
]

# Violation: an ingested node with no source_record_ref.
INGESTED_MISSING_SOURCE_RECORD_REF: list[str] = [
    """
    CREATE (:Catalog:Capability {capability_id: 'cap-noref', business_key: 'cap-noref', version: 1,
                                 origin_mechanism: 'ingested', recorded_at: '2026-01-01'})
    """,
]

# Violation: a distilled node with no source_record_ref.
DISTILLED_MISSING_SOURCE_RECORD_REF: list[str] = [
    """
    CREATE (:Operational:ObservedPattern {
        observed_pattern_id: 'op-noref', business_key: 'op-noref',
        origin_mechanism: 'derived', derivation_class: 'distilled',
        recorded_at: '2026-01-01'})
    """,
]


# --- DDR-001 check 5: Evidence version-pin integrity (B-2-corrected) ----------
# Conformant: the lineage 'cap' has TWO retained versions (v1 superseded, v2
# active); Evidence pins source_node_version 1, which resolves to the retained
# v1 of the cited lineage — the point-in-time-explainability guarantee.
EVIDENCE_VERSION_PIN_CONFORMANT: list[str] = [
    """
    CREATE (v1:Catalog:Capability {capability_id: 'cap-v1', business_key: 'cap', version: 1,
                                   status: 'superseded', origin_mechanism: 'ingested',
                                   recorded_at: '2026-01-01', source_record_ref: 'cmdb:cap'}),
           (v2:Catalog:Capability {capability_id: 'cap-v2', business_key: 'cap', version: 2,
                                   status: 'active', origin_mechanism: 'ingested',
                                   recorded_at: '2026-02-01', source_record_ref: 'cmdb:cap'}),
           (e:Reasoning:Evidence {evidence_id: 'ev-pin', source_node_version: 1}),
           (e)-[:SOURCED_FROM]->(v1)
    """,
]

# Violation: Evidence pins source_node_version 1, but the cited lineage 'cap2'
# retains only version 2 — the pinned version is dangling (no retained v1).
EVIDENCE_DANGLING_VERSION_PIN: list[str] = [
    """
    CREATE (v2:Catalog:Capability {capability_id: 'cap2-v2', business_key: 'cap2', version: 2,
                                   status: 'active', origin_mechanism: 'ingested',
                                   recorded_at: '2026-02-01', source_record_ref: 'cmdb:cap2'}),
           (e:Reasoning:Evidence {evidence_id: 'ev-dangling', source_node_version: 1}),
           (e)-[:SOURCED_FROM]->(v2)
    """,
]
