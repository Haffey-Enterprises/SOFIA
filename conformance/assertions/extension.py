##############################################################################
# Module: extension.py
# Service: conformance (RBT-48 catch-up)
# Author: Haffey Enterprises LLC
# Created: 2026-07-13
# Revised: 2026-07-13
# Description: Extension-registry / confidence-basis graph-state assertions (1a) —
#   DDR-002 §7 #26 (basis-declaration totality) and #27 (basis-admissibility),
#   both follow tier.
#   #26: every PlaneDefinition declares exactly one confidence-derivation basis
#   per declared node-label, with confidence_basis's label set equal to
#   property_schema's (no label without a basis, no basis for an undeclared
#   label), and a freshness operand present iff — and only iff — the basis is
#   aging. The graph-state mirror of the gateway's register-plane validation.
#   #27: every SOURCED_FROM edge terminates at a node whose class resolves to a
#   citable basis (native_confidence / flat_base / aging); a non_citable class
#   carries no inbound SOURCED_FROM. A plane that slipped registration yields
#   fail-closed capture rejections, not ground-truth corruption.
#
#   Modelling: confidence_basis / property_schema are T2 "structured, validator-
#   consumable" declarations. §2.6 fixes them as "declarations (properties), not
#   edges-to-labels" — so child-node modelling is text-foreclosed, and since Neo4j
#   properties cannot nest maps, a JSON-string serialization is the only faithful
#   representation. Both are T2 (no DB existence constraint), so an absent,
#   unparseable, or duplicate-keyed declaration is unverifiable for totality and is
#   FLAGGED (fail loud — the A-1/A-3 pattern), never skipped. Duplicate label keys
#   in particular would silently collapse under json.loads (last-wins), hiding an
#   "exactly one basis per label" violation in the stored bytes, so the parse
#   rejects them via an object_pairs_hook (A-4). The wire format binds at RBT-15.
# Standards: ENG-STD-001 v3.2.0
##############################################################################
"""Graph-state conformance assertions for the confidence-basis contract (#26, #27)."""

import json
from typing import Any

from neo4j import Driver

from conformance import schema_constants as sc
from conformance.assertions.base import Violation, query_rows

_INV_BASIS_TOTALITY = "DDR-002 §7 #26"

_PLANE_DEFINITIONS = f"""
MATCH (pd:{sc.PLANE_DEFINITION_LABEL})
RETURN pd.{sc.PROP_PLANE_ID} AS identity,
       pd.{sc.PROP_CONFIDENCE_BASIS} AS confidence_basis,
       pd.{sc.PROP_PROPERTY_SCHEMA} AS property_schema
"""


class _DeclarationError(ValueError):
    """A declaration is structurally malformed (e.g. a duplicate label key)."""


def _reject_duplicate_keys(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    """object_pairs_hook: raise on a duplicate key rather than silently last-wins."""
    seen: dict[str, Any] = {}
    for key, value in pairs:
        if key in seen:
            raise _DeclarationError(f"duplicate key {key!r}")
        seen[key] = value
    return seen


def _parse_declaration(raw: Any) -> tuple[dict[str, Any] | None, str | None]:
    """Parse a JSON-string declaration; return (dict, None) or (None, reason)."""
    if raw is None:
        return None, "absent"
    if not isinstance(raw, str):
        return None, "not a string"
    try:
        parsed = json.loads(raw, object_pairs_hook=_reject_duplicate_keys)
    except _DeclarationError as exc:
        return None, str(exc)
    except ValueError:
        return None, "unparseable"
    if not isinstance(parsed, dict):
        return None, "not a JSON object"
    return parsed, None


def basis_declaration_totality(driver: Driver) -> list[Violation]:
    """DDR-002 §7 #26: a PlaneDefinition's confidence-basis declaration is total."""
    rows = query_rows(driver, _PLANE_DEFINITIONS)
    violations: list[Violation] = []
    for row in rows:
        plane_id = str(row["identity"])
        confidence_basis, cb_reason = _parse_declaration(row["confidence_basis"])
        property_schema, ps_reason = _parse_declaration(row["property_schema"])

        if confidence_basis is None or property_schema is None:
            reason = cb_reason if confidence_basis is None else ps_reason
            violations.append(
                Violation(
                    invariant=_INV_BASIS_TOTALITY,
                    identity=plane_id,
                    detail=(
                        f"confidence_basis/property_schema declaration invalid ({reason}); "
                        "totality unverifiable"
                    ),
                )
            )
            continue

        # (1) key-set equality between confidence_basis and property_schema.
        basis_labels = set(confidence_basis)
        schema_labels = set(property_schema)
        if basis_labels != schema_labels:
            violations.append(
                Violation(
                    invariant=_INV_BASIS_TOTALITY,
                    identity=plane_id,
                    detail=(
                        "confidence_basis/property_schema label-set mismatch (labels without a "
                        f"basis={sorted(schema_labels - basis_labels)}, basis for undeclared "
                        f"label={sorted(basis_labels - schema_labels)})"
                    ),
                )
            )

        # (2) exactly one valid basis per label + (3) freshness operand iff aging.
        for label, declaration in confidence_basis.items():
            if not isinstance(declaration, dict):
                violations.append(
                    Violation(
                        invariant=_INV_BASIS_TOTALITY,
                        identity=plane_id,
                        detail=f"label {label!r} basis declaration is malformed",
                    )
                )
                continue
            basis = declaration.get("basis")
            if basis not in sc.CONFIDENCE_BASES:
                violations.append(
                    Violation(
                        invariant=_INV_BASIS_TOTALITY,
                        identity=plane_id,
                        detail=(
                            f"label {label!r} declares basis {basis!r}, not one of the four bases"
                        ),
                    )
                )
                continue
            operand = declaration.get("freshness_operand")
            if basis == sc.AGING_BASIS and operand is None:
                violations.append(
                    Violation(
                        invariant=_INV_BASIS_TOTALITY,
                        identity=plane_id,
                        detail=f"aging label {label!r} carries no freshness operand",
                    )
                )
            elif basis != sc.AGING_BASIS and operand is not None:
                violations.append(
                    Violation(
                        invariant=_INV_BASIS_TOTALITY,
                        identity=plane_id,
                        detail=(
                            f"non-aging label {label!r} (basis {basis!r}) carries a stray "
                            f"freshness operand {operand!r}"
                        ),
                    )
                )
    return violations


_INV_BASIS_ADMISSIBILITY = "DDR-002 §7 #27"

# PlaneDefinition is an Option-A versioned type (§6), so supersession RETAINS the
# old version node. #27's basis resolution must key off the ACTIVE version per
# business_key (§6's one-active-per-business_key is what makes that well-defined);
# a superseded declaration must not contribute to the citation-governing map. So
# the ext-map build filters to status = active (A-5, version-filtering).
_ACTIVE_PLANE_DEFINITIONS = f"""
MATCH (pd:{sc.PLANE_DEFINITION_LABEL})
WHERE pd.{sc.PROP_STATUS} = $active
RETURN pd.{sc.PROP_PLANE_ID} AS identity,
       pd.{sc.PROP_CONFIDENCE_BASIS} AS confidence_basis
"""

_SOURCED_FROM_TARGETS = f"""
MATCH (e:{sc.RG_LABEL}:{sc.EVIDENCE_LABEL})-[:{sc.SOURCED_FROM}]->(t)
RETURN e.{sc.PROP_EVIDENCE_ID} AS evidence_id,
       labels(t) AS target_labels,
       coalesce(t.{sc.PROP_BUSINESS_KEY}, elementId(t)) AS target_id
"""


def _extension_basis_map(driver: Driver) -> tuple[dict[str, str], set[str]]:
    """Build node-label -> basis from every ACTIVE PlaneDefinition's confidence_basis.

    Returns (resolved, conflicts). A label declared by more than one active plane
    is a conflict (A-5): last-write-wins would let the map-build eat the ambiguity
    before the check sees it, so such labels are removed from the resolved map and
    surfaced as conflicts (fail loud). A None/unparseable confidence_basis is
    skipped here, but that degrades to a downstream fail-loud — the basis-less
    plane's labels become unresolvable and #27 flags any citation of them, while
    #26 separately flags the plane itself.
    """
    resolved: dict[str, str] = {}
    conflicts: set[str] = set()
    for row in query_rows(driver, _ACTIVE_PLANE_DEFINITIONS, {"active": sc.VERSION_STATUS_ACTIVE}):
        confidence_basis, _ = _parse_declaration(row["confidence_basis"])
        if confidence_basis is None:
            continue
        for label, declaration in confidence_basis.items():
            if not isinstance(declaration, dict):
                continue
            basis = declaration.get("basis")
            if not isinstance(basis, str):
                continue
            if label in resolved or label in conflicts:
                conflicts.add(label)
            else:
                resolved[label] = basis
    for label in conflicts:
        resolved.pop(label, None)
    return resolved, conflicts


def _resolve_basis(labels: list[str], extension_basis: dict[str, str]) -> str | None:
    """Resolve a node's confidence-derivation basis from its labels, or None.

    Order: per-label override (e.g. DeploymentEnvironment) → an active Extension
    PlaneDefinition declaration (keyed by node-label) → the core-plane basis.
    """
    for label in labels:
        if label in sc.NODE_LABEL_BASIS_OVERRIDES:
            return sc.NODE_LABEL_BASIS_OVERRIDES[label]
    for label in labels:
        if label in extension_basis:
            return extension_basis[label]
    for label in labels:
        if label in sc.CORE_PLANE_BASIS:
            return sc.CORE_PLANE_BASIS[label]
    return None


def basis_admissibility(driver: Driver) -> list[Violation]:
    """DDR-002 §7 #27: every SOURCED_FROM target resolves to a citable basis.

    A non_citable-class target is an inadmissible citation; a target whose class
    declares no resolvable basis — or a conflicting one across active planes — is
    unverifiable and is FLAGGED (fail loud — the A-1/A-5 pattern), never skipped.
    Core-plane bases are all citable; only an Extension/Cost registration can
    declare non_citable (e.g. RateCard). Resolution keys off the ACTIVE plane
    version (§6), so a superseded declaration cannot govern a citation.
    """
    extension_basis, conflicts = _extension_basis_map(driver)
    violations: list[Violation] = []
    for row in query_rows(driver, _SOURCED_FROM_TARGETS):
        labels = list(row["target_labels"])
        conflicted = sorted(label for label in labels if label in conflicts)
        if conflicted:
            detail = (
                f"SOURCED_FROM target {row['target_id']!r} class label(s) {conflicted} carry "
                "conflicting basis declarations across active PlaneDefinitions "
                "(ambiguous; admissibility unverifiable)"
            )
        else:
            basis = _resolve_basis(labels, extension_basis)
            if basis is None:
                detail = (
                    f"SOURCED_FROM target {row['target_id']!r} (labels {sorted(labels)}) resolves "
                    "to no declared basis (admissibility unverifiable)"
                )
            elif basis not in sc.CITABLE_BASES:
                detail = (
                    f"SOURCED_FROM target {row['target_id']!r} resolves to non-citable basis "
                    f"{basis!r} (inadmissible citation)"
                )
            else:
                continue
        violations.append(
            Violation(
                invariant=_INV_BASIS_ADMISSIBILITY,
                identity=str(row["evidence_id"]),
                detail=detail,
            )
        )
    return violations
