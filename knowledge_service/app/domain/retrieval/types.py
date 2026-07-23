##############################################################################
# Module: app/domain/retrieval/types.py
# Service: knowledge-service
# Author: Haffey Enterprises LLC
# Created: 2026-07-23
# Revised: 2026-07-23
# Description: The read-discipline core's input shapes (SDD-001 §3.2, §4.4).
#   `CandidateNode` is the structural-fact bundle a §3.3 retrieval operation
#   supplies per node — the #9/#21 exclusion indicators, the applicability
#   marker, its resolved `HAS_CONDITION` set, and the envelope attribution
#   (app.domain.shared.envelope) — so the read-discipline core never touches
#   the graph itself; operations do the traversal (R3+) and hand candidates in.
#   `ConsumingContext` is the §3.2 consuming-context payload. Pure data — no
#   behavior lives here.
##############################################################################

from collections.abc import Mapping
from dataclasses import dataclass, field
from typing import Literal

from app.domain.shared.envelope import EnvelopeAttribution


@dataclass(frozen=True)
class ConsumingContext:
    """The §3.2 consuming-context payload a ground-truth read carries.

    `declared_fields` holds the manifest-declared fields the conditions in
    scope require — introspected from the `Condition.dependency_manifest`
    (§3.2), not the full graph-wide field superset.
    """

    environment_class: str
    data_classification: str
    declared_fields: Mapping[str, object] = field(default_factory=dict)


@dataclass(frozen=True)
class ConditionRef:
    """One resolved `HAS_CONDITION` path — a predicate + its required fields.

    `required_context_fields` is introspected from the `Condition`'s
    `dependency_manifest` (§3.2) — the fields a `ConsumingContext` must supply
    before the predicate can even be attempted.
    """

    predicate: Mapping[str, object]
    required_context_fields: frozenset[str]


@dataclass(frozen=True)
class CandidateNode:
    """One retrieval candidate, as read-discipline (SDD-001 §4.4) needs it.

    `conditions` holds every `HAS_CONDITION` path resolved for this node —
    empty for an unconditional node, one for the ordinary conditional case,
    and more than one only in the DDR-002 multi-condition named-gap case
    (structurally one node reached by multiple promotion decisions).

    `applicability_state` is the **authoritative** conditional marker — not a
    derived echo of `conditions`. The read-discipline core fails closed on any
    inconsistency between the two: `"conditional"` with empty `conditions`
    (a resolution defect — the marker says a `Condition` governs this node but
    none was resolved) excludes rather than falling through to an unconditional
    admit.
    """

    attribution: EnvelopeAttribution
    proposal_pending: bool
    retracted: bool
    applicability_state: Literal["unconditional", "conditional"]
    conditions: tuple[ConditionRef, ...] = ()
