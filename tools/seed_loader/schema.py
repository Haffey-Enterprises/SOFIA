##############################################################################
# Module: seed_loader/schema.py
# Author: Haffey Enterprises LLC
# Created: 2026-07-14 / Revised: 2026-07-14
# Description: The label->PK map and the versioned-ground-truth set the loader
#   keys on. Sourced from DDR-002 v1.3.0 §2 (PK per entity) and §6 (versioned
#   set) — the same authority conformance/schema_constants.py pins. Kept here
#   (not re-derived at runtime) so a schema change is a single, reviewable edit.
##############################################################################

from typing import Final

# Most-specific entity label -> primary-key property (DDR-002 §2, §4, §5).
# GateDecision/PromotionDecision share decision_id on the :Decision supertype;
# Solution's PK is the Artifact-family artifact_id.
PK_BY_LABEL: Final[dict[str, str]] = {
    "Pattern": "pattern_id",
    "Capability": "capability_id",
    "Technology": "technology_id",
    "IacTemplate": "iac_template_id",
    "DeployedService": "deployed_service_id",
    "DeploymentEnvironment": "environment_id",
    "ConfigurationItem": "ci_id",
    "ObservedPattern": "observed_pattern_id",
    "Decision": "decision_id",
    "GateDecision": "decision_id",
    "PromotionDecision": "decision_id",
    "Actor": "actor_id",
    "Role": "role_id",
    "Attestation": "attestation_id",
    "Condition": "condition_id",
    "Standard": "standard_id",
    "PolicyRule": "policy_rule_id",
    "ComplianceControl": "control_id",
    "PlaneDefinition": "plane_id",
    "RateCard": "rate_card_id",
    "CostFactor": "cost_factor_id",
    "CapabilityCostEstimate": "estimate_id",
    "Solution": "artifact_id",
}

# Versioned-ground-truth types — carry (business_key, version); supersede, never
# age (DDR-002 §6). These are the only types the loader runs supersession for.
VERSIONED_GROUND_TRUTH: Final[frozenset[str]] = frozenset(
    {
        "Pattern",
        "Capability",
        "Technology",
        "IacTemplate",
        "Standard",
        "PolicyRule",
        "RateCard",
        "CostFactor",
        "PlaneDefinition",
    }
)


def pk_for(labels: list[str]) -> tuple[str, str]:
    """Return (entity_label, pk_property) for a node's label list.

    The entity label is the most-specific known label (last match in PK_BY_LABEL);
    raises if none is recognised — a seed node with an unmapped label is a defect,
    surfaced loudly rather than silently skipped.
    """
    for label in reversed(labels):
        if label in PK_BY_LABEL:
            return label, PK_BY_LABEL[label]
    raise ValueError(f"no known PK for labels {labels!r}")
