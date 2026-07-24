##############################################################################
# Module: reasoning.py
# Service: conformance (RBT-48 catch-up)
# Author: Haffey Enterprises LLC
# Created: 2026-07-13
# Revised: 2026-07-13
# Description: Raw-CREATE fixtures (DDR-002 §4.2.1) for the Reasoning-Graph
#   conclusion assertions — DDR-002 §7 #23 (flag<->category consistency), #24
#   (rollup upper bound), and #28 (Evidence.confidence presence). Each constant is
#   a list of self-contained CREATE statements; labels/properties match the
#   committed DDR-002 v1.4.0 constants (mirrored in conformance.schema_constants).
#   No native constraints installed.
# Standards: ENG-STD-001 v3.2.0
##############################################################################
"""Conformant and violation graph fixtures for the RG-conclusion assertions."""

# --- #23 flag<->category consistency ------------------------------------------
# Conformant: every reasoner_category maps to its correct authoritative value —
# llm_advisory -> false, all other categories -> true (DDR-002 §4, §7 #23).
FLAG_CATEGORY_CONFORMANT: list[str] = [
    """
    CREATE (:Reasoning:ReasoningProgress {progress_id: 'rp-encoded',
                                          reasoner_category: 'encoded_reasoning',
                                          authoritative: true,
                                          origin_mechanism: 'authored',
                                          recorded_at: '2026-01-01'})
    """,
    """
    CREATE (:Reasoning:ReasoningProgress {progress_id: 'rp-agent',
                                          reasoner_category: 'specialized_agent',
                                          reasoner_ref: 'detection-agent',
                                          authoritative: true,
                                          origin_mechanism: 'authored',
                                          recorded_at: '2026-01-01'})
    """,
    """
    CREATE (:Reasoning:ReasoningProgress {progress_id: 'rp-human',
                                          reasoner_category: 'human_override',
                                          authoritative: true,
                                          origin_mechanism: 'authored',
                                          recorded_at: '2026-01-01'})
    """,
    """
    CREATE (:Reasoning:ReasoningProgress {progress_id: 'rp-llm',
                                          reasoner_category: 'llm_advisory',
                                          authoritative: false,
                                          origin_mechanism: 'authored',
                                          recorded_at: '2026-01-01'})
    """,
]

# Violation: llm_advisory content marked authoritative (must be false) — the
# wrong-consumption-of-non-authoritative-as-authoritative hole #23 guards.
LLM_ADVISORY_MARKED_AUTHORITATIVE: list[str] = [
    """
    CREATE (:Reasoning:ReasoningProgress {progress_id: 'rp-llm-auth',
                                          reasoner_category: 'llm_advisory',
                                          authoritative: true,
                                          origin_mechanism: 'authored',
                                          recorded_at: '2026-01-01'})
    """,
]

# Violation: a non-llm_advisory category (encoded_reasoning) marked
# non-authoritative (must be true).
AUTHORITATIVE_CATEGORY_MARKED_NON_AUTHORITATIVE: list[str] = [
    """
    CREATE (:Reasoning:ReasoningProgress {progress_id: 'rp-encoded-nonauth',
                                          reasoner_category: 'encoded_reasoning',
                                          authoritative: false,
                                          origin_mechanism: 'authored',
                                          recorded_at: '2026-01-01'})
    """,
]

# Violation: a present category with no authoritative flag at all — cannot be
# consistent with the mapping.
CATEGORY_WITHOUT_AUTHORITATIVE: list[str] = [
    """
    CREATE (:Reasoning:ReasoningProgress {progress_id: 'rp-noflag',
                                          reasoner_category: 'encoded_reasoning',
                                          origin_mechanism: 'authored',
                                          recorded_at: '2026-01-01'})
    """,
]

# Violation: reasoner_category absent entirely. reasoner_category is T2, so no
# DB existence constraint forces its presence (§7 covers the provenance group +
# T1 props only). The worst shape (rp-nocat-auth) carries authoritative:true with
# no category — an authoritative-flagged conclusion the fixed mapping cannot
# vouch for, arrived outside the mediated write path; rp-bare carries neither.
# #23 quantifies over every ReasoningProgress, so both are caught.
CATEGORY_ABSENT: list[str] = [
    """
    CREATE (:Reasoning:ReasoningProgress {progress_id: 'rp-nocat-auth',
                                          authoritative: true,
                                          origin_mechanism: 'authored',
                                          recorded_at: '2026-01-01'})
    """,
    """
    CREATE (:Reasoning:ReasoningProgress {progress_id: 'rp-bare',
                                          origin_mechanism: 'authored',
                                          recorded_at: '2026-01-01'})
    """,
]

# --- #24 rollup upper bound ----------------------------------------------------
# Conformant, three cases:
#   rp-below   — confidence 0.7 <= ceiling max(0.8, 0.6) = 0.8;
#   rp-equal   — confidence 0.8 == ceiling 0.8 (the boundary is <=, not <);
#   rp-noev    — a zero-evidence conclusion (confidence 0.99, no SUPPORTED_BY):
#                out of #24's scope (the zero-evidence case is SDD-routed, §4).
ROLLUP_CEILING_CONFORMANT: list[str] = [
    """
    CREATE (rp:Reasoning:ReasoningProgress {progress_id: 'rp-below',
                                            reasoner_category: 'encoded_reasoning',
                                            authoritative: true, confidence: 0.7,
                                            origin_mechanism: 'authored',
                                            recorded_at: '2026-01-01'}),
           (e1:Reasoning:Evidence {evidence_id: 'ev-b1', confidence: 0.8, source_node_version: 1}),
           (e2:Reasoning:Evidence {evidence_id: 'ev-b2', confidence: 0.6, source_node_version: 1}),
           (rp)-[:SUPPORTED_BY]->(e1),
           (rp)-[:SUPPORTED_BY]->(e2)
    """,
    """
    CREATE (rp:Reasoning:ReasoningProgress {progress_id: 'rp-equal',
                                            reasoner_category: 'encoded_reasoning',
                                            authoritative: true, confidence: 0.8,
                                            origin_mechanism: 'authored',
                                            recorded_at: '2026-01-01'}),
           (e:Reasoning:Evidence {evidence_id: 'ev-eq', confidence: 0.8, source_node_version: 1}),
           (rp)-[:SUPPORTED_BY]->(e)
    """,
    """
    CREATE (:Reasoning:ReasoningProgress {progress_id: 'rp-noev',
                                          reasoner_category: 'encoded_reasoning',
                                          authoritative: true, confidence: 0.99,
                                          origin_mechanism: 'authored', recorded_at: '2026-01-01'})
    """,
]

# Violation: a conclusion (0.95) more confident than its strongest supporting
# evidence (ceiling max(0.8, 0.6) = 0.8).
ROLLUP_CEILING_EXCEEDED: list[str] = [
    """
    CREATE (rp:Reasoning:ReasoningProgress {progress_id: 'rp-overconfident',
                                            reasoner_category: 'encoded_reasoning',
                                            authoritative: true, confidence: 0.95,
                                            origin_mechanism: 'authored',
                                            recorded_at: '2026-01-01'}),
           (e1:Reasoning:Evidence {evidence_id: 'ev-o1', confidence: 0.8, source_node_version: 1}),
           (e2:Reasoning:Evidence {evidence_id: 'ev-o2', confidence: 0.6, source_node_version: 1}),
           (rp)-[:SUPPORTED_BY]->(e1),
           (rp)-[:SUPPORTED_BY]->(e2)
    """,
]

# --- #28 Evidence.confidence presence -----------------------------------------
# Conformant: every (:Reasoning:Evidence) carries a non-null confidence (DDR-002
# §7 #28). Two shapes both present a value — a SUPPORTED_BY-linked Evidence and an
# unlinked (standalone) one — so #28, which quantifies over ALL Evidence
# regardless of SUPPORTED_BY, finds nothing to flag.
EVIDENCE_CONFIDENCE_CONFORMANT: list[str] = [
    """
    CREATE (rp:Reasoning:ReasoningProgress {progress_id: 'rp-ec-ok',
                                            reasoner_category: 'encoded_reasoning',
                                            authoritative: true, confidence: 0.7,
                                            origin_mechanism: 'authored',
                                            recorded_at: '2026-01-01'}),
           (e:Reasoning:Evidence {evidence_id: 'ev-ec-linked', confidence: 0.8,
                                  source_node_version: 1}),
           (rp)-[:SUPPORTED_BY]->(e)
    """,
    """
    CREATE (:Reasoning:Evidence {evidence_id: 'ev-ec-unlinked', confidence: 0.5,
                                 source_node_version: 1})
    """,
]

# Violation: a SUPPORTED_BY-linked Evidence with confidence omitted (null in
# Neo4j). confidence is T2 — no DB-existence constraint forces it — and the
# mediated capture path derives-or-rejects, never defaulting a null (DDR-004 §1),
# so a null-confidence Evidence arrived outside that path: the shape #28 catches.
EVIDENCE_CONFIDENCE_ABSENT: list[str] = [
    """
    CREATE (rp:Reasoning:ReasoningProgress {progress_id: 'rp-ec-null',
                                            reasoner_category: 'encoded_reasoning',
                                            authoritative: true, confidence: 0.7,
                                            origin_mechanism: 'authored',
                                            recorded_at: '2026-01-01'}),
           (e:Reasoning:Evidence {evidence_id: 'ev-null-linked', source_node_version: 1}),
           (rp)-[:SUPPORTED_BY]->(e)
    """,
]

# Violation (out-of-path shape): an UNLINKED (no SUPPORTED_BY) Evidence with
# confidence omitted. Per §7 #28 the check fires independent of whether the node
# yet supports any conclusion — schema-legal unlinked Evidence exists (§4) — so an
# unlinked null-confidence node is flagged directly, not skipped the way #24's
# ceiling comparator skips an all-null supporting set (§7 #24/#28).
EVIDENCE_CONFIDENCE_ABSENT_UNLINKED: list[str] = [
    """
    CREATE (:Reasoning:Evidence {evidence_id: 'ev-null-unlinked', source_node_version: 1})
    """,
]
