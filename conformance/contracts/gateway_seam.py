##############################################################################
# Module: gateway_seam.py
# Service: conformance (RBT-33)
# Author: Haffey Enterprises LLC
# Created: 2026-06-22
# Revised: 2026-06-22
# Description: The minimal GraphGateway contract seam (substrate §3.1a) the 1b
#   gateway-behavioral contracts bind to. This is the CONTRACT SURFACE, not the
#   gateway API — RBT-15 implements a conforming superset. It exposes only the
#   three behavioral surfaces the safety-critical contracts exercise: a write
#   path (author + classification), a ground-truth read path (optional consuming
#   context), and an evidence-write path (with source). A Python Protocol is not
#   callable, so UnimplementedGraphGateway raises NotImplementedError from every
#   surface — that is what makes each contract callable and meaningfully xfail
#   (DIRECTIVE-009 §9.2.1) until RBT-15 implements the seam.
# Standards: ENG-STD-001 v3.2.0
##############################################################################
"""The minimal GraphGateway contract seam + its unimplemented raising stub."""

from collections.abc import Mapping
from typing import Any, Protocol

# The xfail reason shared by every 1b contract (DIRECTIVE-009 §9.2.1 lifecycle).
SEAM_REASON = "awaiting RBT-15 gateway implementation of the GraphGateway seam"


class GatewayContractError(Exception):
    """Base for the rejections the 1b contracts require the gateway to enforce."""


class WriteAuthorityError(GatewayContractError):
    """A write is not permitted for its author/role (ADR-002 §2.6; #7)."""


class ClassificationViolationError(GatewayContractError):
    """A write's data classification is disallowed (no-PHI, R10; #13)."""


class EvidenceWriteError(GatewayContractError):
    """An evidence capture-unit write could not commit atomically (#14)."""


class FlagCategoryMismatchError(GatewayContractError):
    """A ReasoningProgress authoritative flag contradicts its reasoner_category (#23)."""


class ScopeDispositionMissingError(GatewayContractError):
    """A supersession of a conditional predecessor carries no scope disposition (#22)."""


class ScopeConflictError(GatewayContractError):
    """An ingested successor cannot satisfy a conditional predecessor's scope (#22)."""


class ProvenanceMaterializationError(GatewayContractError):
    """A promotion's ProvenanceSummary could not be built complete in-transaction (#20)."""


class GraphGateway(Protocol):
    """Minimal behavioral contract surface RBT-15's gateway must satisfy."""

    def write(
        self, *, author: str, classification: str, node_kind: str, properties: Mapping[str, Any]
    ) -> str:
        """Write a node, attributed to ``author`` and classification-checked."""
        ...

    def read_ground_truth(
        self, *, context: Mapping[str, Any] | None = None
    ) -> list[Mapping[str, Any]]:
        """Return ground-truth nodes for synthesis, scoped to an optional context."""
        ...

    def write_evidence(self, *, source_node_id: str, properties: Mapping[str, Any]) -> str:
        """Write an Evidence node and its SOURCED_FROM edge as one atomic unit."""
        ...

    def capture_conclusion(self, *, author: str, properties: Mapping[str, Any]) -> str:
        """Write a ReasoningProgress, rejecting a flag<->category mismatch (#23)."""
        ...

    def supersede(
        self,
        *,
        business_key: str,
        successor: Mapping[str, Any],
        scope_disposition: str | None = None,
    ) -> str:
        """Supersede a business key, enforcing the #22 conditional carry-forward gate."""
        ...

    def materialize_promotion(self, *, decision_id: str, candidate_id: str) -> str:
        """Materialize a promotion, building its ProvenanceSummary in-transaction (#20)."""
        ...


class UnimplementedGraphGateway:
    """The bare seam: every surface raises so contracts are meaningfully xfail.

    RBT-15 replaces this with the real gateway, at which point the contracts
    flip from xfail to xpass (the signal RBT-15 then un-marks them).
    """

    def write(
        self, *, author: str, classification: str, node_kind: str, properties: Mapping[str, Any]
    ) -> str:
        raise NotImplementedError(SEAM_REASON)

    def read_ground_truth(
        self, *, context: Mapping[str, Any] | None = None
    ) -> list[Mapping[str, Any]]:
        raise NotImplementedError(SEAM_REASON)

    def write_evidence(self, *, source_node_id: str, properties: Mapping[str, Any]) -> str:
        raise NotImplementedError(SEAM_REASON)

    def capture_conclusion(self, *, author: str, properties: Mapping[str, Any]) -> str:
        raise NotImplementedError(SEAM_REASON)

    def supersede(
        self,
        *,
        business_key: str,
        successor: Mapping[str, Any],
        scope_disposition: str | None = None,
    ) -> str:
        raise NotImplementedError(SEAM_REASON)

    def materialize_promotion(self, *, decision_id: str, candidate_id: str) -> str:
        raise NotImplementedError(SEAM_REASON)
