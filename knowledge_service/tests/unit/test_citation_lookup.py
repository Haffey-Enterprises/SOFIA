##############################################################################
# Module: test_citation_lookup.py
# Service: knowledge-service
# Author: Haffey Enterprises LLC
# Created: 2026-07-24
# Revised: 2026-07-24
# Description: Unit tests for citation-lookup (app/domain/retrieval/
#   citation_lookup.py, SDD-001 §3.3.7) — the platform's first AUDIT-posture
#   read op: mode/version pairing validation (SCHEMA_VIOLATION), the
#   TARGET_NOT_FOUND raise on a truly-absent entry (never on a
#   retracted/superseded/conditional-but-existing one — the inversion),
#   pagination pass-through, multi-owner Evidence, and the explicit assertion
#   that this path never touches apply_read_discipline or builds a
#   CandidateNode. Runs against the in-memory double — no live Neo4j
#   (SDD-001 §6).
##############################################################################

import pytest

from app.adapters.in_memory_graph import InMemoryGraphStore
from app.domain.exceptions import GatewayError
from app.domain.retrieval.citation_lookup import citation_lookup
from app.domain.retrieval.types import CitationPage
from app.models import CitationEntryStatus, ErrorType
from app.ports.graph_store import CitationEntryStatusRecord, CitationOwnerRecord, CitationRecord

_DEFAULT_PAGE = CitationPage(after_evidence_id=None, limit=50)


_DEFAULT_OWNERS = (
    CitationOwnerRecord(
        progress_id="prog-1",
        conclusion_type="TechnologySelection",
        reasoner_category="encoded_reasoning",
        authoritative=True,
        progress_confidence=0.9,
        session_id="sess-1",
    ),
)


def _citation(
    evidence_id: str = "ev-1", *, owners: tuple[CitationOwnerRecord, ...] | None = None
) -> CitationRecord:
    return CitationRecord(
        evidence_id=evidence_id,
        fact_summary="a fact",
        confidence=0.8,
        weight=1.0,
        source_node_version="1",
        observed_at="2026-07-24T00:00:00Z",
        owners=_DEFAULT_OWNERS if owners is None else owners,
    )


class TestCitationLookupModeVersionPairing:
    """D3's presence-mismatch rule — the sole domain SCHEMA_VIOLATION on this op."""

    async def test_per_version_without_version_raises_schema_violation(self) -> None:
        # Arrange
        graph_store = InMemoryGraphStore()

        # Act / Assert
        with pytest.raises(GatewayError) as exc_info:
            await citation_lookup(
                "Technology", "tech-1", None, "per_version", _DEFAULT_PAGE, graph_store
            )
        assert exc_info.value.error_type == ErrorType.SCHEMA_VIOLATION

    async def test_business_key_wide_with_version_raises_schema_violation(self) -> None:
        # Arrange
        graph_store = InMemoryGraphStore()

        # Act / Assert
        with pytest.raises(GatewayError) as exc_info:
            await citation_lookup(
                "Technology", "tech-1", "3", "business_key_wide", _DEFAULT_PAGE, graph_store
            )
        assert exc_info.value.error_type == ErrorType.SCHEMA_VIOLATION

    async def test_valid_pairings_do_not_raise(self) -> None:
        # Arrange
        graph_store = InMemoryGraphStore()
        graph_store.set_citation_lookup_result(entry_found=True, citations=())

        # Act / Assert — neither call raises.
        await citation_lookup(
            "Technology", "tech-1", "3", "per_version", _DEFAULT_PAGE, graph_store
        )
        await citation_lookup(
            "Technology", "tech-1", None, "business_key_wide", _DEFAULT_PAGE, graph_store
        )


class TestCitationLookupNotFound:
    """TARGET_NOT_FOUND fires ONLY on a truly-absent entry."""

    async def test_truly_absent_entry_raises_target_not_found(self) -> None:
        # Arrange — the double defaults to not-found.
        graph_store = InMemoryGraphStore()

        # Act / Assert
        with pytest.raises(GatewayError) as exc_info:
            await citation_lookup(
                "Technology", "tech-x", "1", "per_version", _DEFAULT_PAGE, graph_store
            )
        assert exc_info.value.error_type == ErrorType.TARGET_NOT_FOUND

    async def test_existing_entry_with_zero_citations_does_not_raise(self) -> None:
        # Arrange — the node exists but nothing cites it.
        graph_store = InMemoryGraphStore()
        graph_store.set_citation_lookup_result(entry_found=True, citations=())

        # Act
        result = await citation_lookup(
            "Technology", "tech-1", "1", "per_version", _DEFAULT_PAGE, graph_store
        )

        # Assert
        assert result.citations == []
        assert result.next_cursor is None


class TestCitationLookupInversion:
    """A retracted/superseded/conditional-but-EXISTING entry still returns its
    citations in full — the audit inversion (SDD-001 §1)."""

    async def test_retracted_entry_still_returns_its_citations(self) -> None:
        # Arrange
        graph_store = InMemoryGraphStore()
        graph_store.set_citation_lookup_result(
            entry_found=True,
            entry_statuses=[
                CitationEntryStatusRecord(
                    version="1", is_superseded=False, is_retracted=True, is_conditional=False
                )
            ],
            citations=[_citation("ev-1")],
        )

        # Act
        result = await citation_lookup(
            "Technology", "tech-1", "1", "per_version", _DEFAULT_PAGE, graph_store
        )

        # Assert — citations are NOT excluded despite the retraction marker.
        assert len(result.citations) == 1
        assert result.citations[0].evidence.evidence_id == "ev-1"
        assert result.entry_status[0].markers == {CitationEntryStatus.RETRACTED}

    async def test_co_occurring_markers_both_survive(self) -> None:
        # Arrange — superseded AND conditional at once (independent markers,
        # R6a delta A3): applicability_state is per-version, so a superseded
        # version can independently carry its own conditional scope.
        graph_store = InMemoryGraphStore()
        graph_store.set_citation_lookup_result(
            entry_found=True,
            entry_statuses=[
                CitationEntryStatusRecord(
                    version="1", is_superseded=True, is_retracted=False, is_conditional=True
                )
            ],
            citations=[_citation("ev-1")],
        )

        # Act
        result = await citation_lookup(
            "Technology", "tech-1", "1", "per_version", _DEFAULT_PAGE, graph_store
        )

        # Assert — both markers present, citations untouched.
        assert result.entry_status[0].markers == {
            CitationEntryStatus.SUPERSEDED,
            CitationEntryStatus.CONDITIONAL,
        }
        assert len(result.citations) == 1

    async def test_no_markers_set_is_the_empty_set_not_an_active_member(self) -> None:
        # Arrange
        graph_store = InMemoryGraphStore()
        graph_store.set_citation_lookup_result(
            entry_found=True,
            entry_statuses=[
                CitationEntryStatusRecord(
                    version="1", is_superseded=False, is_retracted=False, is_conditional=False
                )
            ],
            citations=(),
        )

        # Act
        result = await citation_lookup(
            "Technology", "tech-1", "1", "per_version", _DEFAULT_PAGE, graph_store
        )

        # Assert
        assert result.entry_status[0].markers == frozenset()


class TestCitationLookupBusinessKeyWide:
    """business_key_wide unions citations across the version chain, per-version status."""

    async def test_business_key_wide_returns_per_version_status_list(self) -> None:
        # Arrange
        graph_store = InMemoryGraphStore()
        graph_store.set_citation_lookup_result(
            entry_found=True,
            entry_statuses=[
                CitationEntryStatusRecord(
                    version="1", is_superseded=True, is_retracted=False, is_conditional=False
                ),
                CitationEntryStatusRecord(
                    version="2", is_superseded=False, is_retracted=False, is_conditional=False
                ),
            ],
            citations=[_citation("ev-1"), _citation("ev-2")],
        )

        # Act
        result = await citation_lookup(
            "Technology", "tech-1", None, "business_key_wide", _DEFAULT_PAGE, graph_store
        )

        # Assert
        assert result.mode == "business_key_wide"
        assert result.version is None
        assert [e.version for e in result.entry_status] == ["1", "2"]
        assert result.entry_status[0].markers == {CitationEntryStatus.SUPERSEDED}
        assert result.entry_status[1].markers == frozenset()
        assert len(result.citations) == 2


class TestCitationLookupOwners:
    """Multi-owner Evidence surfaces every owning ReasoningProgress/Session."""

    async def test_evidence_supporting_two_conclusions_surfaces_both_owners(self) -> None:
        # Arrange
        owners = (
            CitationOwnerRecord(
                progress_id="prog-1",
                conclusion_type="TechnologySelection",
                reasoner_category="encoded_reasoning",
                authoritative=True,
                progress_confidence=0.9,
                session_id="sess-1",
            ),
            CitationOwnerRecord(
                progress_id="prog-2",
                conclusion_type="RiskSignal",
                reasoner_category="llm_advisory",
                authoritative=False,
                progress_confidence=None,
                session_id="sess-2",
            ),
        )
        graph_store = InMemoryGraphStore()
        graph_store.set_citation_lookup_result(
            entry_found=True, citations=[_citation("ev-1", owners=owners)]
        )

        # Act
        result = await citation_lookup(
            "Technology", "tech-1", "1", "per_version", _DEFAULT_PAGE, graph_store
        )

        # Assert
        entry = result.citations[0]
        assert len(entry.owners) == 2
        assert {o.progress.progress_id for o in entry.owners} == {"prog-1", "prog-2"}
        assert {o.session.session_id for o in entry.owners} == {"sess-1", "sess-2"}

    async def test_evidence_with_no_owners_surfaces_an_empty_owner_list(self) -> None:
        # Arrange — Evidence exists but nothing SUPPORTED_BY-references it yet.
        graph_store = InMemoryGraphStore()
        graph_store.set_citation_lookup_result(
            entry_found=True, citations=[_citation("ev-1", owners=())]
        )

        # Act
        result = await citation_lookup(
            "Technology", "tech-1", "1", "per_version", _DEFAULT_PAGE, graph_store
        )

        # Assert
        assert result.citations[0].owners == []

    async def test_owner_with_no_resolvable_session_surfaces_session_id_none(self) -> None:
        # Arrange — review fix M1: the traversal's OPTIONAL MATCH to the
        # owning session resolved nothing; this must surface, never 500.
        owners = (
            CitationOwnerRecord(
                progress_id="prog-1",
                conclusion_type="TechnologySelection",
                reasoner_category="encoded_reasoning",
                authoritative=True,
                progress_confidence=0.9,
                session_id=None,
            ),
        )
        graph_store = InMemoryGraphStore()
        graph_store.set_citation_lookup_result(
            entry_found=True, citations=[_citation("ev-1", owners=owners)]
        )

        # Act
        result = await citation_lookup(
            "Technology", "tech-1", "1", "per_version", _DEFAULT_PAGE, graph_store
        )

        # Assert
        assert result.citations[0].owners[0].session.session_id is None

    async def test_owner_with_null_attribution_fields_surfaces_them_as_none(self) -> None:
        # Arrange — review fix M1: a malformed/incomplete ReasoningProgress
        # (the exact kind this audit op is built to reach) must surface
        # honestly, never crash — only progress_id (T1 PK) is required.
        owners = (
            CitationOwnerRecord(
                progress_id="prog-1",
                conclusion_type=None,
                reasoner_category=None,
                authoritative=None,
                progress_confidence=None,
                session_id="sess-1",
            ),
        )
        graph_store = InMemoryGraphStore()
        graph_store.set_citation_lookup_result(
            entry_found=True, citations=[_citation("ev-1", owners=owners)]
        )

        # Act
        result = await citation_lookup(
            "Technology", "tech-1", "1", "per_version", _DEFAULT_PAGE, graph_store
        )

        # Assert
        owner = result.citations[0].owners[0]
        assert owner.progress.progress_id == "prog-1"
        assert owner.progress.conclusion_type is None
        assert owner.progress.reasoner_category is None
        assert owner.progress.authoritative is None


class TestCitationLookupPagination:
    """The page/cursor pass through to the port and back onto the result."""

    async def test_forwards_the_page_to_the_graph_store(self) -> None:
        # Arrange
        graph_store = InMemoryGraphStore()
        graph_store.set_citation_lookup_result(entry_found=True, citations=())
        page = CitationPage(after_evidence_id="ev-5", limit=25)

        # Act
        await citation_lookup("Technology", "tech-1", "1", "per_version", page, graph_store)

        # Assert
        assert graph_store.citation_lookup_calls == [
            ("Technology", "tech-1", "1", "per_version", "ev-5", 25)
        ]

    async def test_result_carries_the_next_cursor_from_the_port(self) -> None:
        # Arrange
        graph_store = InMemoryGraphStore()
        graph_store.set_citation_lookup_result(
            entry_found=True, citations=[_citation("ev-1"), _citation("ev-2")]
        )

        # Act
        result = await citation_lookup(
            "Technology",
            "tech-1",
            "1",
            "per_version",
            CitationPage(after_evidence_id=None, limit=1),
            graph_store,
        )

        # Assert
        assert result.next_cursor == "ev-1"


class TestCitationLookupNeverRunsReadDiscipline:
    """The audit-posture exception (SDD-001 §1/§3.2): no trio, no CandidateNode."""

    async def test_module_imports_neither_read_discipline_nor_candidate_node(self) -> None:
        # Arrange / Act
        import app.domain.retrieval.citation_lookup as module

        source_names = dir(module)

        # Assert — this path never calls apply_read_discipline and never
        # builds a CandidateNode: neither name is bound in the module at all.
        assert "apply_read_discipline" not in source_names
        assert "CandidateNode" not in source_names

    async def test_result_carries_no_applicability_or_disclosure_surface(self) -> None:
        # Arrange
        graph_store = InMemoryGraphStore()
        graph_store.set_citation_lookup_result(entry_found=True, citations=[_citation("ev-1")])

        # Act
        result = await citation_lookup(
            "Technology", "tech-1", "1", "per_version", _DEFAULT_PAGE, graph_store
        )

        # Assert — the result type itself carries none of the §3.2 envelope
        # surfaces (no `admitted`/`disclosures`/`applicability` fields).
        assert not hasattr(result, "admitted")
        assert not hasattr(result, "disclosures")
        assert not hasattr(result.citations[0], "applicability")
