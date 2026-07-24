##############################################################################
# Module: test_session_trace.py
# Service: knowledge-service
# Author: Haffey Enterprises LLC
# Created: 2026-07-24
# Revised: 2026-07-24
# Description: Unit tests for session-trace (app/domain/retrieval/
#   session_trace.py, SDD-001 §3.3.9) — the audit set's third and last op:
#   full-session tree correctness (conclusions + evidence + rejected
#   alternatives + led_to adjacency), resolved-pin identity + CURRENT status
#   markers (including a now-retracted/superseded cited node still
#   surfaced), an Evidence with no SOURCED_FROM surfacing resolved_pin=None
#   rather than crashing, an out-of-map cited label surfacing node_kind/
#   version/markers with node_id=None, TARGET_NOT_FOUND on an absent
#   session only, an existing-but-empty session yielding an empty trace,
#   and the explicit assertion that this path never touches
#   apply_read_discipline or builds a CandidateNode. Runs against the
#   in-memory double — no live Neo4j (SDD-001 §6).
##############################################################################

import pytest

from app.adapters.in_memory_graph import InMemoryGraphStore
from app.domain.exceptions import GatewayError
from app.domain.retrieval.session_trace import session_trace
from app.models import CitationEntryStatus, ErrorType
from app.ports.graph_store import (
    CitedNodeRefRecord,
    LedToRecord,
    SessionTracePage,
    TraceConclusionRecord,
    TraceEvidenceRecord,
    TraceRejectedAlternativeRecord,
)

_CITED_TECH = CitedNodeRefRecord(
    node_kind="Technology",
    node_id="tech-1",
    version="1",
    is_superseded=False,
    is_retracted=False,
    is_conditional=False,
)


def _evidence(
    evidence_id: str = "ev-1", *, resolved_pin: CitedNodeRefRecord | None = _CITED_TECH
) -> TraceEvidenceRecord:
    return TraceEvidenceRecord(
        evidence_id=evidence_id,
        fact_summary="a fact",
        confidence=0.8,
        weight=1.0,
        source_node_version="1",
        observed_at="2026-07-01T00:00:00Z",
        resolved_pin=resolved_pin,
    )


def _rejected(
    rejected_id: str = "rej-1", *, would_have_used: tuple[CitedNodeRefRecord, ...] = ()
) -> TraceRejectedAlternativeRecord:
    return TraceRejectedAlternativeRecord(
        rejected_id=rejected_id,
        candidate_type="Technology",
        rejection_reason="cost",
        score_delta=-0.2,
        human_accepted=False,
        would_have_used=would_have_used,
    )


def _conclusion(
    progress_id: str = "prog-1",
    *,
    evidence: tuple[TraceEvidenceRecord, ...] = (),
    rejected_alternatives: tuple[TraceRejectedAlternativeRecord, ...] = (),
) -> TraceConclusionRecord:
    return TraceConclusionRecord(
        progress_id=progress_id,
        conclusion_type="TechnologySelection",
        reasoner_category="encoded_reasoning",
        authoritative=True,
        confidence=0.9,
        overridden_by_human=False,
        created_at="2026-07-01T00:00:00Z",
        evidence=evidence,
        rejected_alternatives=rejected_alternatives,
    )


class TestSessionTraceNotFound:
    """TARGET_NOT_FOUND fires ONLY on a truly-absent session."""

    async def test_absent_session_raises_target_not_found(self) -> None:
        # Arrange — the double defaults to session_found=False.
        graph_store = InMemoryGraphStore()

        # Act / Assert
        with pytest.raises(GatewayError) as exc_info:
            await session_trace("sess-x", graph_store)
        assert exc_info.value.error_type == ErrorType.TARGET_NOT_FOUND

    async def test_existing_but_empty_session_yields_empty_trace_no_error(self) -> None:
        # Arrange — a legal non-blocking capture state (DDR-001).
        graph_store = InMemoryGraphStore()
        graph_store.set_session_trace_result(
            SessionTracePage(session_found=True, conclusions=(), led_to=())
        )

        # Act
        result = await session_trace("sess-1", graph_store)

        # Assert
        assert result.conclusions == []
        assert result.led_to == []


class TestSessionTraceFullTree:
    """Full-session tree correctness: conclusions, evidence, rejected
    alternatives, led_to adjacency."""

    async def test_conclusion_carries_its_own_fields(self) -> None:
        # Arrange
        graph_store = InMemoryGraphStore()
        graph_store.set_session_trace_result(
            SessionTracePage(session_found=True, conclusions=(_conclusion(),), led_to=())
        )

        # Act
        result = await session_trace("sess-1", graph_store)

        # Assert
        conclusion = result.conclusions[0]
        assert conclusion.progress_id == "prog-1"
        assert conclusion.conclusion_type == "TechnologySelection"
        assert conclusion.reasoner_category == "encoded_reasoning"
        assert conclusion.authoritative is True
        assert conclusion.confidence == 0.9
        assert conclusion.overridden_by_human is False
        assert conclusion.created_at == "2026-07-01T00:00:00Z"

    async def test_conclusion_carries_its_evidence(self) -> None:
        # Arrange
        graph_store = InMemoryGraphStore()
        graph_store.set_session_trace_result(
            SessionTracePage(
                session_found=True,
                conclusions=(_conclusion(evidence=(_evidence("ev-1"), _evidence("ev-2"))),),
                led_to=(),
            )
        )

        # Act
        result = await session_trace("sess-1", graph_store)

        # Assert
        assert [e.evidence.evidence_id for e in result.conclusions[0].evidence] == [
            "ev-1",
            "ev-2",
        ]

    async def test_conclusion_carries_its_rejected_alternatives(self) -> None:
        # Arrange
        graph_store = InMemoryGraphStore()
        graph_store.set_session_trace_result(
            SessionTracePage(
                session_found=True,
                conclusions=(
                    _conclusion(rejected_alternatives=(_rejected("rej-1"), _rejected("rej-2"))),
                ),
                led_to=(),
            )
        )

        # Act
        result = await session_trace("sess-1", graph_store)

        # Assert
        assert [r.rejected_id for r in result.conclusions[0].rejected_alternatives] == [
            "rej-1",
            "rej-2",
        ]

    async def test_led_to_is_flat_adjacency_not_a_nested_tree(self) -> None:
        # Arrange
        graph_store = InMemoryGraphStore()
        graph_store.set_session_trace_result(
            SessionTracePage(
                session_found=True,
                conclusions=(_conclusion("prog-1"), _conclusion("prog-2")),
                led_to=(
                    LedToRecord(from_progress_id="prog-1", to_progress_id="prog-2"),
                    LedToRecord(from_progress_id="prog-2", to_progress_id="prog-3"),
                ),
            )
        )

        # Act
        result = await session_trace("sess-1", graph_store)

        # Assert
        assert [(link.from_progress_id, link.to_progress_id) for link in result.led_to] == [
            ("prog-1", "prog-2"),
            ("prog-2", "prog-3"),
        ]


class TestSessionTraceResolvedPin:
    """Resolved-pin identity + CURRENT status markers — the point-in-time
    fidelity point: a now-retracted/superseded cited node still surfaces."""

    async def test_resolved_pin_carries_identity(self) -> None:
        # Arrange
        graph_store = InMemoryGraphStore()
        graph_store.set_session_trace_result(
            SessionTracePage(
                session_found=True,
                conclusions=(_conclusion(evidence=(_evidence(resolved_pin=_CITED_TECH),)),),
                led_to=(),
            )
        )

        # Act
        result = await session_trace("sess-1", graph_store)

        # Assert
        pin = result.conclusions[0].evidence[0].resolved_pin
        assert pin is not None
        assert pin.node_kind == "Technology"
        assert pin.node_id == "tech-1"
        assert pin.version == "1"
        assert pin.markers == frozenset()

    async def test_now_retracted_cited_node_still_surfaces_with_its_marker(self) -> None:
        # Arrange — the citing Evidence's point-in-time pin resolves
        # regardless of the cited node's CURRENT read-discipline state.
        retracted_pin = CitedNodeRefRecord(
            node_kind="Technology",
            node_id="tech-1",
            version="1",
            is_superseded=False,
            is_retracted=True,
            is_conditional=False,
        )
        graph_store = InMemoryGraphStore()
        graph_store.set_session_trace_result(
            SessionTracePage(
                session_found=True,
                conclusions=(_conclusion(evidence=(_evidence(resolved_pin=retracted_pin),)),),
                led_to=(),
            )
        )

        # Act
        result = await session_trace("sess-1", graph_store)

        # Assert — surfaced, not excluded, marker disclosed.
        pin = result.conclusions[0].evidence[0].resolved_pin
        assert pin is not None
        assert pin.markers == {CitationEntryStatus.RETRACTED}

    async def test_now_superseded_cited_node_still_surfaces_with_its_marker(self) -> None:
        # Arrange
        superseded_pin = CitedNodeRefRecord(
            node_kind="Technology",
            node_id="tech-1",
            version="1",
            is_superseded=True,
            is_retracted=False,
            is_conditional=False,
        )
        graph_store = InMemoryGraphStore()
        graph_store.set_session_trace_result(
            SessionTracePage(
                session_found=True,
                conclusions=(_conclusion(evidence=(_evidence(resolved_pin=superseded_pin),)),),
                led_to=(),
            )
        )

        # Act
        result = await session_trace("sess-1", graph_store)

        # Assert
        pin = result.conclusions[0].evidence[0].resolved_pin
        assert pin is not None
        assert pin.markers == {CitationEntryStatus.SUPERSEDED}

    async def test_conditional_cited_node_surfaces_with_its_marker(self) -> None:
        # Arrange
        conditional_pin = CitedNodeRefRecord(
            node_kind="Technology",
            node_id="tech-1",
            version="1",
            is_superseded=False,
            is_retracted=False,
            is_conditional=True,
        )
        graph_store = InMemoryGraphStore()
        graph_store.set_session_trace_result(
            SessionTracePage(
                session_found=True,
                conclusions=(_conclusion(evidence=(_evidence(resolved_pin=conditional_pin),)),),
                led_to=(),
            )
        )

        # Act
        result = await session_trace("sess-1", graph_store)

        # Assert
        pin = result.conclusions[0].evidence[0].resolved_pin
        assert pin is not None
        assert pin.markers == {CitationEntryStatus.CONDITIONAL}

    async def test_evidence_with_no_sourced_from_surfaces_resolved_pin_none(self) -> None:
        # Arrange — schema-legal edge case, surfaced honestly, never crashed.
        graph_store = InMemoryGraphStore()
        graph_store.set_session_trace_result(
            SessionTracePage(
                session_found=True,
                conclusions=(_conclusion(evidence=(_evidence(resolved_pin=None),)),),
                led_to=(),
            )
        )

        # Act
        result = await session_trace("sess-1", graph_store)

        # Assert
        assert result.conclusions[0].evidence[0].resolved_pin is None

    async def test_out_of_map_cited_label_surfaces_identity_without_node_id(self) -> None:
        # Arrange — relay delta resolution: an out-of-scope cited label still
        # surfaces node_kind/version/markers; node_id alone goes unresolved,
        # never dropped, never guessed.
        out_of_map_pin = CitedNodeRefRecord(
            node_kind="RateCard",
            node_id=None,
            version="1",
            is_superseded=False,
            is_retracted=False,
            is_conditional=False,
        )
        graph_store = InMemoryGraphStore()
        graph_store.set_session_trace_result(
            SessionTracePage(
                session_found=True,
                conclusions=(_conclusion(evidence=(_evidence(resolved_pin=out_of_map_pin),)),),
                led_to=(),
            )
        )

        # Act
        result = await session_trace("sess-1", graph_store)

        # Assert
        pin = result.conclusions[0].evidence[0].resolved_pin
        assert pin is not None
        assert pin.node_kind == "RateCard"
        assert pin.node_id is None
        assert pin.version == "1"

    async def test_would_have_used_carries_resolved_refs(self) -> None:
        # Arrange
        used = CitedNodeRefRecord(
            node_kind="Technology",
            node_id="tech-2",
            version="1",
            is_superseded=False,
            is_retracted=False,
            is_conditional=False,
        )
        graph_store = InMemoryGraphStore()
        graph_store.set_session_trace_result(
            SessionTracePage(
                session_found=True,
                conclusions=(
                    _conclusion(rejected_alternatives=(_rejected(would_have_used=(used,)),)),
                ),
                led_to=(),
            )
        )

        # Act
        result = await session_trace("sess-1", graph_store)

        # Assert
        would_have_used = result.conclusions[0].rejected_alternatives[0].would_have_used
        assert len(would_have_used) == 1
        assert would_have_used[0].node_id == "tech-2"


class TestSessionTraceForwardsTheRequest:
    """The operation forwards the caller's session id to the port unchanged."""

    async def test_forwards_session_id(self) -> None:
        # Arrange
        graph_store = InMemoryGraphStore()
        graph_store.set_session_trace_result(
            SessionTracePage(session_found=True, conclusions=(), led_to=())
        )

        # Act
        await session_trace("sess-1", graph_store)

        # Assert
        assert graph_store.session_trace_calls == ["sess-1"]


class TestSessionTraceNeverRunsReadDiscipline:
    """Trio-free by INAPPLICABILITY (SDD-001 §3.3.9 ST-D1) — not the §1
    disclosed exception, but the same no-trio/no-CandidateNode outcome."""

    async def test_module_imports_neither_read_discipline_nor_candidate_node(self) -> None:
        # Arrange / Act
        import app.domain.retrieval.session_trace as module

        source_names = dir(module)

        # Assert
        assert "apply_read_discipline" not in source_names
        assert "CandidateNode" not in source_names

    async def test_result_carries_no_applicability_or_disclosure_surface(self) -> None:
        # Arrange
        graph_store = InMemoryGraphStore()
        graph_store.set_session_trace_result(
            SessionTracePage(session_found=True, conclusions=(_conclusion(),), led_to=())
        )

        # Act
        result = await session_trace("sess-1", graph_store)

        # Assert
        assert not hasattr(result, "admitted")
        assert not hasattr(result, "disclosures")
