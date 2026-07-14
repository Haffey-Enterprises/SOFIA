##############################################################################
# Module: extension.py
# Service: conformance (RBT-48 catch-up)
# Author: Haffey Enterprises LLC
# Created: 2026-07-13
# Revised: 2026-07-13
# Description: Extension-registry graph-state assertions (1a) — DDR-002 §7 #26
#   (basis-declaration totality): every PlaneDefinition declares exactly one
#   confidence-derivation basis per declared node-label, with confidence_basis's
#   label set equal to property_schema's (no label without a basis, no basis for
#   an undeclared label), and a freshness operand present iff — and only iff — the
#   basis is aging. Follow tier: a plane that slipped registration without a basis
#   yields fail-closed capture rejections, not ground-truth corruption; this is
#   the graph-state mirror of the gateway's register-plane validation.
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
"""Graph-state conformance assertions for the Extension registry (#26)."""

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
