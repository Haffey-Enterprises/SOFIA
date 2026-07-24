##############################################################################
# Module: test_provenance_of.py
# Service: knowledge-service
# Author: Haffey Enterprises LLC
# Created: 2026-07-24
# Revised: 2026-07-24
# Description: Unit tests for provenance-of (app/domain/retrieval/
#   provenance_of.py, SDD-001 §3.3.8) — the audit set's second op: the
#   TARGET_NOT_FOUND raise on both an absent entry AND an existing-but-
#   never-promoted one, the frozen-fallback vs. live-overlay entry mapping,
#   frozen_layer_present=false on a broken #20 chain (never raised), the
#   inversion (a retracted/superseded promoted node still returns its
#   provenance in full), the three independent entry markers, and the
#   explicit assertion that this path never touches apply_read_discipline
#   or builds a CandidateNode. Runs against the in-memory double — no live
#   Neo4j (SDD-001 §6).
##############################################################################

import pytest

from app.adapters.in_memory_graph import InMemoryGraphStore
from app.domain.exceptions import GatewayError
from app.domain.retrieval.provenance_of import provenance_of
from app.models import CitationEntryStatus, ErrorType
from app.ports.graph_store import (
    ProvenanceOfCandidateRecord,
    ProvenanceOfFrozenEntryRecord,
    ProvenanceOfGoverningDecisionRecord,
    ProvenanceOfPage,
)

_CANDIDATE = ProvenanceOfCandidateRecord(
    candidate_id="cand-1", proposal_kind="promotion", status="promoted"
)
_DECISION = ProvenanceOfGoverningDecisionRecord(
    decision_id="dec-1", outcome="approved", decided_at="2026-07-01T00:00:00Z"
)


def _promoted_page(**overrides: object) -> ProvenanceOfPage:
    base: dict[str, object] = {
        "entry_found": True,
        "is_promoted": True,
        "origin_mechanism": "promoted",
        "is_superseded": False,
        "is_retracted": False,
        "is_conditional": False,
        "candidate": _CANDIDATE,
        "governing_decision": _DECISION,
        "frozen_layer_present": True,
        "provenance_summary_id": "summary-1",
        "entries": (),
    }
    base.update(overrides)
    return ProvenanceOfPage(**base)  # type: ignore[arg-type]


class TestProvenanceOfNotFound:
    """TARGET_NOT_FOUND fires on BOTH an absent entry AND a not-promoted one."""

    async def test_absent_entry_raises_target_not_found(self) -> None:
        # Arrange — the double defaults to entry_found=False.
        graph_store = InMemoryGraphStore()

        # Act / Assert
        with pytest.raises(GatewayError) as exc_info:
            await provenance_of("Technology", "tech-x", "1", graph_store)
        assert exc_info.value.error_type == ErrorType.TARGET_NOT_FOUND

    async def test_existing_but_not_promoted_raises_target_not_found(self) -> None:
        # Arrange — the node exists (e.g. an ingested Technology) but was
        # never promoted: no PROMOTES_TO_KNOWLEDGE chain.
        graph_store = InMemoryGraphStore()
        graph_store.set_provenance_of_result(
            _promoted_page(is_promoted=False, candidate=None, governing_decision=None)
        )

        # Act / Assert
        with pytest.raises(GatewayError) as exc_info:
            await provenance_of("Technology", "tech-1", "1", graph_store)
        assert exc_info.value.error_type == ErrorType.TARGET_NOT_FOUND

    async def test_absent_and_not_promoted_raise_distinguishable_messages(self) -> None:
        # Arrange
        graph_store = InMemoryGraphStore()

        # Act
        with pytest.raises(GatewayError) as absent_exc:
            await provenance_of("Technology", "tech-x", "1", graph_store)

        graph_store.set_provenance_of_result(
            _promoted_page(is_promoted=False, candidate=None, governing_decision=None)
        )
        with pytest.raises(GatewayError) as not_promoted_exc:
            await provenance_of("Technology", "tech-1", "1", graph_store)

        # Assert — same ErrorType (no new one), distinguishable message text.
        assert absent_exc.value.error_type == ErrorType.TARGET_NOT_FOUND
        assert not_promoted_exc.value.error_type == ErrorType.TARGET_NOT_FOUND
        assert absent_exc.value.message != not_promoted_exc.value.message


class TestProvenanceOfPortContractGuard:
    """is_promoted=True is the port's guarantee that candidate/
    origin_mechanism are populated (§5's structural invariant) — a
    violation is a gateway defect, fails loud rather than silently
    degrading. governing_decision is NOT part of this guarantee (review fix
    M3) — see TestProvenanceOfGoverningDecision below."""

    async def test_is_promoted_true_with_missing_candidate_fails_loud(self) -> None:
        # Arrange — an inconsistent port response (should be impossible by
        # §5, but this double can be misconfigured to prove the guard).
        graph_store = InMemoryGraphStore()
        graph_store.set_provenance_of_result(_promoted_page(candidate=None))

        # Act / Assert
        with pytest.raises(RuntimeError, match="port contract violation"):
            await provenance_of("Technology", "tech-1", "1", graph_store)

    async def test_is_promoted_true_with_missing_origin_mechanism_fails_loud(self) -> None:
        # Arrange
        graph_store = InMemoryGraphStore()
        graph_store.set_provenance_of_result(_promoted_page(origin_mechanism=None))

        # Act / Assert
        with pytest.raises(RuntimeError, match="port contract violation"):
            await provenance_of("Technology", "tech-1", "1", graph_store)


class TestProvenanceOfGoverningDecision:
    """Review fix M3: governing = latest decided_at, ANY outcome — never a
    promoted-node invariant. A rejected verdict is disclosed, not hidden
    behind a stale approval; a wholly-absent decision is a surfaced
    anomaly, never a raise."""

    async def test_rejected_governing_decision_surfaces_its_outcome(self) -> None:
        # Arrange — the flipped-to-rejected verdict must be visible, not
        # hidden behind an earlier stale approval (#15's own clarifying case).
        graph_store = InMemoryGraphStore()
        graph_store.set_provenance_of_result(
            _promoted_page(
                governing_decision=ProvenanceOfGoverningDecisionRecord(
                    decision_id="dec-2", outcome="rejected", decided_at="2026-07-15T00:00:00Z"
                )
            )
        )

        # Act
        result = await provenance_of("Technology", "tech-1", "1", graph_store)

        # Assert
        assert result.governing_decision is not None
        assert result.governing_decision.outcome == "rejected"
        assert result.governing_decision.decision_id == "dec-2"

    async def test_missing_governing_decision_surfaces_none_never_raises(self) -> None:
        # Arrange — a promoted node with no DECIDED_ON edge at all: a real,
        # surfaced anomaly, not a port contract violation.
        graph_store = InMemoryGraphStore()
        graph_store.set_provenance_of_result(_promoted_page(governing_decision=None))

        # Act
        result = await provenance_of("Technology", "tech-1", "1", graph_store)

        # Assert — never raises; the rest of the result is still populated.
        assert result.governing_decision is None
        assert result.candidate.candidate_id == "cand-1"


class TestProvenanceOfInversion:
    """A retracted/superseded/conditional promoted node still returns its
    provenance in full — the audit inversion (SDD-001 §1)."""

    async def test_retracted_promoted_node_still_returns_its_provenance(self) -> None:
        # Arrange
        graph_store = InMemoryGraphStore()
        graph_store.set_provenance_of_result(
            _promoted_page(
                is_retracted=True,
                entries=(
                    ProvenanceOfFrozenEntryRecord(
                        evidence_id="ev-1",
                        frozen_fact_summary="a fact",
                        frozen_source_version_pin="1",
                        frozen_source_node_ref="tech-1",
                        is_live=False,
                        live_fact_summary=None,
                        live_confidence=None,
                        live_weight=None,
                        live_source_node_version=None,
                        live_observed_at=None,
                    ),
                ),
            )
        )

        # Act
        result = await provenance_of("Technology", "tech-1", "3", graph_store)

        # Assert — provenance is NOT withheld despite the retraction marker.
        assert len(result.entries) == 1
        assert result.entry_markers == {CitationEntryStatus.RETRACTED}

    async def test_co_occurring_markers_both_survive(self) -> None:
        # Arrange — superseded AND conditional at once (independent markers).
        graph_store = InMemoryGraphStore()
        graph_store.set_provenance_of_result(
            _promoted_page(is_superseded=True, is_conditional=True)
        )

        # Act
        result = await provenance_of("Technology", "tech-1", "1", graph_store)

        # Assert
        assert result.entry_markers == {
            CitationEntryStatus.SUPERSEDED,
            CitationEntryStatus.CONDITIONAL,
        }

    async def test_no_markers_set_is_the_empty_set(self) -> None:
        # Arrange
        graph_store = InMemoryGraphStore()
        graph_store.set_provenance_of_result(_promoted_page())

        # Act
        result = await provenance_of("Technology", "tech-1", "1", graph_store)

        # Assert
        assert result.entry_markers == frozenset()


class TestProvenanceOfFrozenLayer:
    """frozen_layer_present=false is an honest anomaly signal — never raised."""

    async def test_missing_provenance_summary_returns_frozen_layer_present_false(
        self,
    ) -> None:
        # Arrange — the candidate resolves but no ProvenanceSummary exists
        # (a #20 violation reached pre-CI-catch).
        graph_store = InMemoryGraphStore()
        graph_store.set_provenance_of_result(
            _promoted_page(
                frozen_layer_present=False, provenance_summary_id=None, entries=()
            )
        )

        # Act
        result = await provenance_of("Technology", "tech-1", "1", graph_store)

        # Assert — never raises; candidate/governing_decision still populated.
        assert result.frozen_layer_present is False
        assert result.provenance_summary_id is None
        assert result.entries == []
        assert result.candidate.candidate_id == "cand-1"
        assert result.governing_decision.decision_id == "dec-1"


class TestProvenanceOfEntryMapping:
    """Frozen-vs-live entry mapping, correlated by evidence_id."""

    async def test_live_entry_carries_both_frozen_floor_and_live_overlay(self) -> None:
        # Arrange
        graph_store = InMemoryGraphStore()
        graph_store.set_provenance_of_result(
            _promoted_page(
                entries=(
                    ProvenanceOfFrozenEntryRecord(
                        evidence_id="ev-1",
                        frozen_fact_summary="frozen fact",
                        frozen_source_version_pin="1",
                        frozen_source_node_ref="tech-1",
                        is_live=True,
                        live_fact_summary="live fact",
                        live_confidence=0.9,
                        live_weight=1.0,
                        live_source_node_version="2",
                        live_observed_at="2026-07-20T00:00:00Z",
                    ),
                )
            )
        )

        # Act
        result = await provenance_of("Technology", "tech-1", "1", graph_store)

        # Assert — the frozen floor is always present; the live overlay
        # makes frozen-vs-live drift visible (frozen "1" vs live "2" pin).
        entry = result.entries[0]
        assert entry.evidence_id == "ev-1"
        assert entry.frozen_source_version_pin == "1"
        assert entry.live is True
        assert entry.live_evidence is not None
        assert entry.live_evidence.evidence_id == "ev-1"
        assert entry.live_evidence.source_node_version == "2"
        assert entry.live_evidence.fact_summary == "live fact"

    async def test_frozen_only_entry_has_no_live_evidence(self) -> None:
        # Arrange — the originating Evidence has expired out of retention.
        graph_store = InMemoryGraphStore()
        graph_store.set_provenance_of_result(
            _promoted_page(
                entries=(
                    ProvenanceOfFrozenEntryRecord(
                        evidence_id="ev-1",
                        frozen_fact_summary="frozen fact",
                        frozen_source_version_pin="1",
                        frozen_source_node_ref="tech-1",
                        is_live=False,
                        live_fact_summary=None,
                        live_confidence=None,
                        live_weight=None,
                        live_source_node_version=None,
                        live_observed_at=None,
                    ),
                )
            )
        )

        # Act
        result = await provenance_of("Technology", "tech-1", "1", graph_store)

        # Assert — frozen floor present, no live overlay, never an error.
        entry = result.entries[0]
        assert entry.evidence_id == "ev-1"
        assert entry.frozen_fact_summary == "frozen fact"
        assert entry.live is False
        assert entry.live_evidence is None

    async def test_multiple_entries_preserve_order_and_correlation(self) -> None:
        # Arrange
        graph_store = InMemoryGraphStore()
        graph_store.set_provenance_of_result(
            _promoted_page(
                entries=(
                    ProvenanceOfFrozenEntryRecord(
                        evidence_id="ev-1",
                        frozen_fact_summary="fact 1",
                        frozen_source_version_pin="1",
                        frozen_source_node_ref="tech-1",
                        is_live=True,
                        live_fact_summary="fact 1",
                        live_confidence=0.5,
                        live_weight=1.0,
                        live_source_node_version="1",
                        live_observed_at="2026-07-01T00:00:00Z",
                    ),
                    ProvenanceOfFrozenEntryRecord(
                        evidence_id="ev-2",
                        frozen_fact_summary="fact 2",
                        frozen_source_version_pin="1",
                        frozen_source_node_ref="tech-1",
                        is_live=False,
                        live_fact_summary=None,
                        live_confidence=None,
                        live_weight=None,
                        live_source_node_version=None,
                        live_observed_at=None,
                    ),
                )
            )
        )

        # Act
        result = await provenance_of("Technology", "tech-1", "1", graph_store)

        # Assert
        assert [e.evidence_id for e in result.entries] == ["ev-1", "ev-2"]
        assert result.entries[0].live is True
        assert result.entries[1].live is False

    async def test_empty_frozen_set_is_not_an_error(self) -> None:
        # Arrange — a promotion whose PROPOSED_FROM span reached no Evidence
        # (e.g. an ObservedPattern-only span, DDR-002 §5).
        graph_store = InMemoryGraphStore()
        graph_store.set_provenance_of_result(_promoted_page(entries=()))

        # Act
        result = await provenance_of("Technology", "tech-1", "1", graph_store)

        # Assert
        assert result.entries == []


class TestProvenanceOfResultFields:
    """The candidate/governing_decision/identity fields pass through."""

    async def test_result_carries_candidate_and_governing_decision(self) -> None:
        # Arrange
        graph_store = InMemoryGraphStore()
        graph_store.set_provenance_of_result(_promoted_page())

        # Act
        result = await provenance_of("Technology", "tech-1", "3", graph_store)

        # Assert
        assert result.node_kind == "Technology"
        assert result.business_key == "tech-1"
        assert result.version == "3"
        assert result.origin_mechanism == "promoted"
        assert result.candidate.candidate_id == "cand-1"
        assert result.candidate.proposal_kind == "promotion"
        assert result.candidate.status == "promoted"
        assert result.governing_decision.decision_id == "dec-1"
        assert result.governing_decision.outcome == "approved"
        assert result.provenance_summary_id == "summary-1"


class TestProvenanceOfForwardsTheRequest:
    """The operation forwards the caller's pin to the port unchanged."""

    async def test_forwards_node_kind_business_key_version(self) -> None:
        # Arrange
        graph_store = InMemoryGraphStore()
        graph_store.set_provenance_of_result(_promoted_page())

        # Act
        await provenance_of("Technology", "tech-1", "3", graph_store)

        # Assert
        assert graph_store.provenance_of_calls == [("Technology", "tech-1", "3")]


class TestProvenanceOfNeverRunsReadDiscipline:
    """The audit-posture exception (SDD-001 §1/§3.2): no trio, no CandidateNode."""

    async def test_module_imports_neither_read_discipline_nor_candidate_node(self) -> None:
        # Arrange / Act
        import app.domain.retrieval.provenance_of as module

        source_names = dir(module)

        # Assert
        assert "apply_read_discipline" not in source_names
        assert "CandidateNode" not in source_names

    async def test_result_carries_no_applicability_or_disclosure_surface(self) -> None:
        # Arrange
        graph_store = InMemoryGraphStore()
        graph_store.set_provenance_of_result(_promoted_page())

        # Act
        result = await provenance_of("Technology", "tech-1", "1", graph_store)

        # Assert
        assert not hasattr(result, "admitted")
        assert not hasattr(result, "disclosures")
