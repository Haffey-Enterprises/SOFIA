##############################################################################
# Module: test_schema_metadata.py
# Service: knowledge-service
# Author: Haffey Enterprises LLC
# Created: 2026-07-23
# Revised: 2026-07-23
# Description: Unit tests for the in-process schema-metadata registry
#   (app/domain/shared/schema_metadata.py) and its parse-and-verify load. Covers
#   the ready path (the declared descriptor verifies), the parity of the loaded
#   plane -> basis map against the canonical DDR-002 §2 values, and each
#   not-ready trigger (authority-pin mismatch, core-plane-set mismatch,
#   unratified basis) — the load is total, publishing a not-ready registry on
#   failure so /readyz answers 503 rather than the process crashing.
##############################################################################

import pytest

from app.domain.shared.core_schema import CORE_SCHEMA_DESCRIPTOR, CoreSchemaDescriptor
from app.domain.shared.schema_metadata import (
    SchemaMetadataError,
    SchemaRegistry,
    _verified_core_plane_bases,
    load_core_registry,
)

# The canonical DDR-002 §2 plane -> basis map, transcribed here as the parity
# floor (matches conformance/schema_constants.py CORE_PLANE_BASIS; the
# cross-package CI parity check is the noted follow-up).
_CANONICAL_CORE_PLANE_BASIS = {
    "Catalog": "flat_base",
    "Environment": "aging",
    "Operational": "native_confidence",
    "Governance": "flat_base",
    "Standards": "flat_base",
}


def _descriptor(**overrides: object) -> CoreSchemaDescriptor:
    """Build a descriptor from the ratified one with selective field overrides."""
    fields: dict[str, object] = {
        "authority": CORE_SCHEMA_DESCRIPTOR.authority,
        "plane_bases": dict(CORE_SCHEMA_DESCRIPTOR.plane_bases),
        "label_basis_overrides": dict(CORE_SCHEMA_DESCRIPTOR.label_basis_overrides),
    }
    fields.update(overrides)
    return CoreSchemaDescriptor(**fields)  # type: ignore[arg-type]


class TestLoadCoreRegistry:
    """load_core_registry: ready on the declared descriptor, not-ready on failure."""

    def test_load_from_declared_descriptor_is_ready(self) -> None:
        # Act
        registry = load_core_registry()

        # Assert
        assert registry.is_ready() is True
        assert registry.core_planes() == frozenset(_CANONICAL_CORE_PLANE_BASIS)
        assert registry.authority == CORE_SCHEMA_DESCRIPTOR.authority

    def test_load_basis_for_each_core_plane_matches_ddr_002(self) -> None:
        # Arrange
        registry = load_core_registry()

        # Act / Assert — the parity floor: every core plane's declared basis
        # equals the canonical DDR-002 §2 value.
        for plane, basis in _CANONICAL_CORE_PLANE_BASIS.items():
            assert registry.basis_for_plane(plane) == basis

    def test_load_with_authority_mismatch_is_not_ready(self) -> None:
        # Arrange
        descriptor = _descriptor(authority="DDR-002 v0.0.0 (sha256 deadbeef)")

        # Act
        registry = load_core_registry(descriptor)

        # Assert
        assert registry.is_ready() is False
        assert registry.core_planes() == frozenset()

    def test_load_with_a_missing_core_plane_is_not_ready(self) -> None:
        # Arrange — drop Standards.
        bases = dict(CORE_SCHEMA_DESCRIPTOR.plane_bases)
        del bases["Standards"]
        descriptor = _descriptor(plane_bases=bases)

        # Act
        registry = load_core_registry(descriptor)

        # Assert
        assert registry.is_ready() is False

    def test_load_with_an_unratified_basis_is_not_ready(self) -> None:
        # Arrange
        bases = dict(CORE_SCHEMA_DESCRIPTOR.plane_bases)
        bases["Catalog"] = "made_up_basis"
        descriptor = _descriptor(plane_bases=bases)

        # Act
        registry = load_core_registry(descriptor)

        # Assert
        assert registry.is_ready() is False


class TestVerifiedCorePlaneBases:
    """The verifier raises a typed error on each failure and returns on success."""

    def test_verify_returns_the_basis_map_on_a_valid_descriptor(self) -> None:
        # Act
        bases = _verified_core_plane_bases(CORE_SCHEMA_DESCRIPTOR)

        # Assert
        assert bases == _CANONICAL_CORE_PLANE_BASIS

    def test_verify_raises_on_authority_mismatch(self) -> None:
        # Arrange / Act / Assert
        with pytest.raises(SchemaMetadataError, match="authority"):
            _verified_core_plane_bases(_descriptor(authority="wrong"))

    def test_verify_raises_on_core_plane_set_mismatch(self) -> None:
        # Arrange
        descriptor = _descriptor(plane_bases={"Catalog": "flat_base"})

        # Act / Assert
        with pytest.raises(SchemaMetadataError, match="core-plane set"):
            _verified_core_plane_bases(descriptor)

    def test_verify_raises_on_unratified_basis(self) -> None:
        # Arrange
        bases = dict(CORE_SCHEMA_DESCRIPTOR.plane_bases)
        bases["Governance"] = "not_a_basis"

        # Act / Assert
        with pytest.raises(SchemaMetadataError, match="unratified basis"):
            _verified_core_plane_bases(_descriptor(plane_bases=bases))


class TestSchemaRegistry:
    """The registry's accessors over a verified — and a not-ready — state."""

    def test_ready_registry_exposes_planes_and_basis_lookup(self) -> None:
        # Arrange / Act
        registry = SchemaRegistry(
            core_plane_bases={"Catalog": "flat_base"}, authority="a", ready=True
        )

        # Assert
        assert registry.is_ready() is True
        assert registry.core_planes() == frozenset({"Catalog"})
        assert registry.basis_for_plane("Catalog") == "flat_base"
        assert registry.authority == "a"

    def test_not_ready_registry_reports_not_ready_and_no_planes(self) -> None:
        # Arrange / Act
        registry = SchemaRegistry(core_plane_bases={}, authority="a", ready=False)

        # Assert
        assert registry.is_ready() is False
        assert registry.core_planes() == frozenset()
