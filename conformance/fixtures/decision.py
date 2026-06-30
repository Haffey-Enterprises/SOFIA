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
