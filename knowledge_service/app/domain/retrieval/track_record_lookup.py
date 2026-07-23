##############################################################################
# Module: app/domain/retrieval/track_record_lookup.py
# Service: knowledge-service
# Author: Haffey Enterprises LLC
# Created: 2026-07-23
# Revised: 2026-07-23
# Description: track-record-lookup (SDD-001 §3.3.3) — the first §3.3 read
#   operation. Calls the port's find_track_record traversal, maps each raw
#   record into a CandidateNode, and applies the R2 read-discipline core. The
#   read-discipline flags are FIXED, not read from the record: an
#   ObservedPattern is always origin_mechanism: derived (DDR-002 §2.3), never
#   promoted, so it structurally cannot be an un-approved CandidatePromotion
#   (#9, a distinct label), cannot carry applicability_state/HAS_CONDITION
#   (§5, exclusive to PROMOTES_TO_KNOWLEDGE-materialized nodes), and cannot be
#   a RETRACTS target (§7 #21, which un-promotes a promoted fact). Fixing the
#   flags is only sound because that invariant is CHECKED, not assumed (R3a
#   review finding): a record whose origin_mechanism disagrees is excluded,
#   fail-closed, rather than admitted with flags that would no longer be true
#   of it. Every other candidate still passes through apply_read_discipline —
#   it is never pre-excluded for any OTHER reason here (SDD-001 §4.4 is the
#   core's sole enforcement point for the read-discipline trio proper).
#   `version`/`version_pin` are None: ObservedPattern is update-in-place
#   (§2.3/§6) and carries no version property (R3a envelope correction, see
#   app.domain.shared.envelope). `confidences` carries node reliability and
#   OBSERVED_IN per-target certainty uncomposed (§3.3.3) — no rollup here.
#   Either may be null (R3a review finding): DDR-002 §7 existence constraints
#   cover only the provenance group + T1 properties, `confidence` is T2 on
#   both surfaces, and no CI check (#1-28) guarantees its presence on
#   ObservedPattern or OBSERVED_IN — unlike Evidence.confidence, which check
#   #28 exists specifically to cover. A null is carried honestly, never
#   defaulted or coerced.
##############################################################################

from collections.abc import Sequence

import structlog

from app.domain.retrieval.read_discipline import apply_read_discipline
from app.domain.retrieval.types import CandidateNode, ConsumingContext
from app.domain.shared.envelope import EnvelopeAttribution
from app.models import ReadResult
from app.ports.graph_store import GraphStoragePort, TargetEntityRef, TrackRecordCandidateRecord
from app.ports.predicate_eval import PredicateEvaluationPort

log = structlog.get_logger()

# The one origin_mechanism ObservedPattern is schema-permitted to carry
# (DDR-002 §2.3). Checked, not assumed — see _to_candidate.
_OBSERVED_PATTERN_ORIGIN_MECHANISM = "derived"


async def track_record_lookup(
    target_refs: Sequence[TargetEntityRef],
    context: ConsumingContext,
    graph_store: GraphStoragePort,
    predicate_evaluator: PredicateEvaluationPort,
) -> ReadResult:
    """Look up Operational-plane track record for the given target entities.

    Args:
        target_refs: The target entities to look up track record for.
        context: The §3.2 consuming-context payload.
        graph_store: The graph port (production: Neo4jAdapter; tests: the
            in-memory double).
        predicate_evaluator: The in-process predicate port. Never reached by
            this operation's candidates in practice — they are always
            unconditional — but still threaded through so the R2 core's
            ordered trio runs unmodified.

    Returns:
        The admitted envelopes and disclosed exclusions (SDD-001 §3.2). In
        practice this operation's candidates are always admitted: an
        `ObservedPattern` is never a pending proposal, never retracted, and
        never conditional. A record that violates the origin_mechanism
        invariant is excluded before it ever reaches the read-discipline core.
    """
    records = await graph_store.find_track_record(target_refs)
    candidates = [
        candidate
        for candidate in (_to_candidate(record) for record in records)
        if candidate is not None
    ]
    return await apply_read_discipline(candidates, context, predicate_evaluator)


def _to_candidate(record: TrackRecordCandidateRecord) -> CandidateNode | None:
    """Map one raw track-record record into a `CandidateNode`.

    The read-discipline flags below are fixed, not read from `record` — sound
    only because `origin_mechanism` is checked here first. A record that
    disagrees with the invariant this operation's fixed flags rely on is
    excluded rather than admitted with flags that would no longer be true.

    Args:
        record: The port-level structural facts for one ObservedPattern x
            target match.

    Returns:
        The `CandidateNode`, with the read-discipline flags fixed to the
        values structurally forced by `ObservedPattern`'s provenance model
        (see the module description), or `None` if the record's
        `origin_mechanism` violates that invariant — excluded, fail-closed,
        rather than admitted on flags that would no longer hold.
    """
    if record.origin_mechanism != _OBSERVED_PATTERN_ORIGIN_MECHANISM:
        log.warning(
            "track_record_candidate_excluded",
            node_id=record.node_id,
            reason="unexpected_origin_mechanism",
            origin_mechanism=record.origin_mechanism,
        )
        return None

    return CandidateNode(
        attribution=EnvelopeAttribution(
            node_id=record.node_id,
            node_kind="ObservedPattern",
            plane_labels=("Operational",),
            origin_mechanism=record.origin_mechanism,
            derivation_class=record.derivation_class,
            version=None,
            effective_from=record.first_observed_at,
            effective_to=record.last_observed_at,
            version_pin=None,
            confidences=(record.node_confidence, record.edge_confidence),
        ),
        proposal_pending=False,
        retracted=False,
        applicability_state="unconditional",
        conditions=(),
    )
