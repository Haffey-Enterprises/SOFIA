##############################################################################
# Module: app/domain/shared/core_schema.py
# Service: knowledge-service
# Author: Haffey Enterprises LLC
# Created: 2026-07-23
# Revised: 2026-07-23
# Description: The declared core-plane schema descriptor (SDD-001 §3.1 check 2 /
#   §4.1 schema_metadata) — the static, in-process half of the validation
#   metadata the gateway loads at startup. It carries the five DDR-001 core KG
#   planes mapped to their DDR-002 §2 confidence-derivation basis (the plane a
#   write path resolves a citation's basis from — #27 / DDR-004), the one §2.2
#   per-label override, and the DDR-002 authority version+hash the values are
#   transcribed from. It is a vendored snapshot of DDR-002 v1.4.0 §2, parallel
#   to conformance/schema_constants.py (per-service packaging forbids importing
#   that module across the package boundary); a currency check keys on the
#   authority pin, and the schema_metadata parity test asserts these values
#   against the canonical DDR-002 §2 map. The Extension half of the registry is
#   graph-resident (register-plane, RBT-81) and empty until then, so startup
#   stays graph-independent (ADR-004 §2.2). No entity-label snapshot lives here
#   by design — that second drift surface waits for its write-path consumer
#   (RBT-79), which also extends this descriptor with property validation.
##############################################################################

from collections.abc import Mapping
from dataclasses import dataclass
from types import MappingProxyType

# The DDR-002 authority these values are transcribed from — version + content
# hash of docs/ddr/DDR-002-graph-schema.md. A currency check keys on this pin;
# re-fetch and re-verify before any refresh (the schema_constants.py / F4
# discipline). It matches conformance/schema_constants.py's pin.
DDR_002_AUTHORITY: str = (
    "DDR-002 v1.4.0 (sha256 2fdd403b6b5ee0477ffa2f9ab8cc7f4ef43601e413c38ed08202e9e74deaa32e)"
)


@dataclass(frozen=True)
class CoreSchemaDescriptor:
    """The declared core-plane validation metadata loaded at startup.

    Immutable by construction: the mappings are read-only proxies, so a loaded
    descriptor cannot be mutated by a caller. `plane_bases` maps each of the
    five DDR-001 core KG planes to its DDR-002 §2 confidence basis;
    `label_basis_overrides` carries the §2.2 per-label exceptions; `authority`
    pins the DDR-002 version and hash the values conform to.
    """

    authority: str
    plane_bases: Mapping[str, str]
    label_basis_overrides: Mapping[str, str]


# The ratified descriptor (DDR-002 v1.4.0 §2.1-§2.6; the CORE_PLANE_BASIS map).
# Catalog/Standards are versioned authoritative ground truth (flat_base);
# Environment ages on observed_at (aging), except the structurally-stable
# DeploymentEnvironment (flat_base override, §2.2); Operational carries lesson
# reliability (native_confidence); Governance is immutable append-only
# (flat_base). Extension/Cost are NOT core — their basis is declared per
# PlaneDefinition in the graph (§2.6), so they are absent here.
CORE_SCHEMA_DESCRIPTOR: CoreSchemaDescriptor = CoreSchemaDescriptor(
    authority=DDR_002_AUTHORITY,
    plane_bases=MappingProxyType(
        {
            "Catalog": "flat_base",
            "Environment": "aging",
            "Operational": "native_confidence",
            "Governance": "flat_base",
            "Standards": "flat_base",
        }
    ),
    label_basis_overrides=MappingProxyType(
        {
            "DeploymentEnvironment": "flat_base",
        }
    ),
)
