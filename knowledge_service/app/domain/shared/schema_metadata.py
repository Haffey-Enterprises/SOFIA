##############################################################################
# Module: app/domain/shared/schema_metadata.py
# Service: knowledge-service
# Author: Haffey Enterprises LLC
# Created: 2026-07-23
# Revised: 2026-07-23
# Description: The in-process schema-metadata registry (SDD-001 §3.1 check 2,
#   §4.1, §4.5) — the PlaneDefinition registry and core-plane validation
#   metadata the gateway loads at startup and the write paths enforce against.
#   RBT-78 stands up the core half in-process from the declared descriptor
#   (core_schema.py); the Extension half is graph-resident (register-plane,
#   RBT-81) and legitimately empty until then, so startup stays graph-
#   independent (ADR-004 §2.2, "start against an empty instance"). Loading is
#   parse-and-verify: the descriptor must present exactly the five core planes,
#   each with a ratified basis, under the expected DDR-002 authority pin — else
#   the registry loads not-ready and /readyz check 2 answers 503 rather than the
#   process serving writes it cannot validate. Per §4.5 the registry is a
#   write-through cache home; no ground-truth result is cached.
##############################################################################

from collections.abc import Mapping

import structlog

from app.domain.shared.core_schema import (
    CORE_SCHEMA_DESCRIPTOR,
    DDR_002_AUTHORITY,
    CoreSchemaDescriptor,
)

log = structlog.get_logger()

# The four ratified confidence bases (DDR-002 §2). A core plane must declare one.
_RATIFIED_BASES: frozenset[str] = frozenset(
    {"native_confidence", "flat_base", "aging", "non_citable"}
)

# The five DDR-001 core KG planes the descriptor must present — exactly these,
# no more, no fewer (DDR-002 Decision.2: five core planes; Extension/Cost are
# not core and are graph-resident, so absent from the static descriptor).
_EXPECTED_CORE_PLANES: frozenset[str] = frozenset(
    {"Catalog", "Environment", "Operational", "Governance", "Standards"}
)


class SchemaMetadataError(Exception):
    """The declared core-schema descriptor failed parse-and-verify at load."""


class SchemaRegistry:
    """The gateway's loaded schema-metadata registry (SDD-001 §4.1, §4.5).

    Holds the verified core-plane metadata (the static half) and, in later
    stories, the graph-resident Extension PlaneDefinitions (empty at RBT-78).
    `is_ready` is the verdict SDD-001 §3.1 check 2 reports: the metadata the
    write paths enforce against is present and verified. A registry that failed
    to verify at load is published not-ready, so /readyz answers 503 rather than
    the process serving writes it cannot validate.
    """

    def __init__(self, *, core_plane_bases: Mapping[str, str], authority: str, ready: bool) -> None:
        """Construct a registry over a verified (or empty, not-ready) basis map.

        Args:
            core_plane_bases: The verified plane -> confidence-basis mapping;
                empty on a not-ready registry.
            authority: The DDR-002 authority pin the metadata conforms to.
            ready: Whether the metadata loaded and verified (check 2's verdict).
        """
        self._core_plane_bases = dict(core_plane_bases)
        self._authority = authority
        self._ready = ready

    def is_ready(self) -> bool:
        """Report whether the schema metadata loaded and verified (check 2)."""
        return self._ready

    @property
    def authority(self) -> str:
        """The DDR-002 authority pin the loaded metadata conforms to."""
        return self._authority

    def core_planes(self) -> frozenset[str]:
        """The set of core plane names the registry verified."""
        return frozenset(self._core_plane_bases)

    def basis_for_plane(self, plane: str) -> str:
        """The declared confidence basis for a verified core plane (DDR-002 §2)."""
        return self._core_plane_bases[plane]


def _verified_core_plane_bases(descriptor: CoreSchemaDescriptor) -> dict[str, str]:
    """Parse and verify the descriptor's core-plane basis map.

    Args:
        descriptor: The declared core-schema descriptor.

    Returns:
        The verified plane -> basis mapping.

    Raises:
        SchemaMetadataError: If the authority pin, the plane set, or any basis
            fails verification — the gateway must not report ready against
            metadata it could not verify.
    """
    if descriptor.authority != DDR_002_AUTHORITY:
        raise SchemaMetadataError(f"authority pin mismatch: descriptor={descriptor.authority!r}")

    planes = frozenset(descriptor.plane_bases)
    if planes != _EXPECTED_CORE_PLANES:
        missing = sorted(_EXPECTED_CORE_PLANES - planes)
        unexpected = sorted(planes - _EXPECTED_CORE_PLANES)
        raise SchemaMetadataError(
            f"core-plane set mismatch: missing={missing}, unexpected={unexpected}"
        )

    for plane, basis in descriptor.plane_bases.items():
        if basis not in _RATIFIED_BASES:
            raise SchemaMetadataError(f"unratified basis for {plane!r}: {basis!r}")

    return dict(descriptor.plane_bases)


def load_core_registry(
    descriptor: CoreSchemaDescriptor = CORE_SCHEMA_DESCRIPTOR,
) -> SchemaRegistry:
    """Load the schema-metadata registry from the declared descriptor.

    Total by construction: on a verified descriptor the registry is ready; on a
    verification failure it is published *not-ready* (logged) rather than
    raising, so startup completes and /readyz reports check 2 unavailable (503)
    — the readiness contract, not a process crash (SDD-001 §3.1).

    Args:
        descriptor: The core-schema descriptor to load; defaults to the ratified
            CORE_SCHEMA_DESCRIPTOR.

    Returns:
        A ready registry when the descriptor verifies, else a not-ready one.
    """
    try:
        bases = _verified_core_plane_bases(descriptor)
    except SchemaMetadataError as exc:
        log.error("schema_metadata_unavailable", reason=str(exc))
        return SchemaRegistry(core_plane_bases={}, authority=descriptor.authority, ready=False)

    return SchemaRegistry(core_plane_bases=bases, authority=descriptor.authority, ready=True)
