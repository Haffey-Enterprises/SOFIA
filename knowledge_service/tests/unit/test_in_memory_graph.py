##############################################################################
# Module: test_in_memory_graph.py
# Service: knowledge-service
# Author: Haffey Enterprises LLC
# Created: 2026-07-21
# Revised: 2026-07-21
# Description: Unit tests for InMemoryGraphStore — the GraphStoragePort double
#   every service test runs against (SDD-001 §6, no test depends on live
#   Neo4j). The double is real behavior and is covered as such: its
#   controllable connectivity verdict is what makes the §3.1 readiness check
#   testable in both directions, and its controllable candidate-record lists
#   (RBT-78/R3a track-record, R3b resolve-technology, R3c select-patterns) are
#   what make read-discipline exercisable without modelling graph internals
#   (§4.2 A3).
##############################################################################

from app.adapters.in_memory_graph import InMemoryGraphStore
from app.ports.graph_store import (
    CitationEntryStatusRecord,
    CitationOwnerRecord,
    CitationRecord,
    CitedNodeRefRecord,
    FindPrecedentsCandidateRecord,
    FindPrecedentsCriteria,
    GraphStoragePort,
    LedToRecord,
    ObligationCandidateRecord,
    ProvenanceOfCandidateRecord,
    ProvenanceOfFrozenEntryRecord,
    ProvenanceOfGoverningDecisionRecord,
    ProvenanceOfPage,
    ReadAsOfResolvedRecord,
    ResolveTechnologyCandidateRecord,
    SelectPatternsCandidateRecord,
    SessionTracePage,
    TargetEntityRef,
    TraceConclusionRecord,
    TraceEvidenceRecord,
    TraceRejectedAlternativeRecord,
    TrackRecordCandidateRecord,
)


def _citation(evidence_id: str) -> CitationRecord:
    return CitationRecord(
        evidence_id=evidence_id,
        fact_summary="a fact",
        confidence=0.8,
        weight=1.0,
        source_node_version="1",
        observed_at="2026-07-24T00:00:00Z",
        owners=(
            CitationOwnerRecord(
                progress_id="prog-1",
                conclusion_type="TechnologySelection",
                reasoner_category="encoded_reasoning",
                authoritative=True,
                progress_confidence=0.9,
                session_id="sess-1",
            ),
        ),
    )


class TestInMemoryGraphStoreSubstitutability:
    """The double must satisfy the port it substitutes for."""

    def test_in_memory_store_satisfies_the_graph_storage_port(self) -> None:
        # Arrange
        store = InMemoryGraphStore()

        # Act / Assert
        assert isinstance(store, GraphStoragePort)


class TestInMemoryGraphStoreConnectivity:
    """Connectivity is controllable in both directions, and observable."""

    async def test_check_connectivity_when_store_is_healthy_returns_true(self) -> None:
        # Arrange
        store = InMemoryGraphStore()

        # Act
        result = await store.check_connectivity()

        # Assert
        assert result is True

    async def test_check_connectivity_when_constructed_unhealthy_returns_false(self) -> None:
        # Arrange
        store = InMemoryGraphStore(connectivity_healthy=False)

        # Act
        result = await store.check_connectivity()

        # Assert
        assert result is False

    async def test_set_connectivity_flips_the_reported_verdict(self) -> None:
        # Arrange
        store = InMemoryGraphStore()

        # Act
        store.set_connectivity(healthy=False)
        after_failure = await store.check_connectivity()
        store.set_connectivity(healthy=True)
        after_recovery = await store.check_connectivity()

        # Assert
        assert after_failure is False
        assert after_recovery is True

    async def test_check_connectivity_records_how_many_times_it_was_consumed(self) -> None:
        # Arrange
        store = InMemoryGraphStore()

        # Act
        await store.check_connectivity()
        await store.check_connectivity()

        # Assert — lets a readiness test prove the check was exercised, not
        # short-circuited around.
        assert store.check_connectivity_calls == 2


class TestInMemoryGraphStoreFindTrackRecord:
    """The controllable candidate-record store (§4.2 A3)."""

    async def test_find_track_record_with_no_candidates_set_returns_empty(self) -> None:
        # Arrange
        store = InMemoryGraphStore()

        # Act
        result = await store.find_track_record(
            [TargetEntityRef(entity_kind="Technology", entity_id="t")]
        )

        # Assert
        assert result == []

    async def test_find_track_record_returns_the_configured_candidates(self) -> None:
        # Arrange
        store = InMemoryGraphStore()
        candidate = TrackRecordCandidateRecord(
            node_id="op-1",
            origin_mechanism="derived",
            derivation_class="distilled",
            node_confidence=0.8,
            edge_confidence=0.6,
            first_observed_at="2026-01-01T00:00:00Z",
            last_observed_at="2026-06-01T00:00:00Z",
        )
        store.set_track_record_candidates([candidate])

        # Act
        result = await store.find_track_record(
            [TargetEntityRef(entity_kind="Technology", entity_id="t")]
        )

        # Assert
        assert result == [candidate]

    async def test_find_track_record_records_the_requested_target_refs(self) -> None:
        # Arrange
        store = InMemoryGraphStore()
        refs = [TargetEntityRef(entity_kind="Pattern", entity_id="p-1")]

        # Act
        await store.find_track_record(refs)

        # Assert — lets a test prove the operation forwarded the caller's
        # target entities rather than dropping or substituting them.
        assert store.find_track_record_calls == [refs]


class TestInMemoryGraphStoreResolveTechnologyOptions:
    """The controllable candidate-record store (§4.2 A3)."""

    async def test_resolve_technology_options_with_no_candidates_set_returns_empty(
        self,
    ) -> None:
        # Arrange
        store = InMemoryGraphStore()

        # Act
        result = await store.resolve_technology_options("cap-1")

        # Assert
        assert result == []

    async def test_resolve_technology_options_returns_the_configured_candidates(
        self,
    ) -> None:
        # Arrange
        store = InMemoryGraphStore()
        candidate = ResolveTechnologyCandidateRecord(
            node_id="tech-1",
            version="1",
            origin_mechanism="ingested",
            derivation_class="primary",
            tier_applicability=("production",),
            approved_data_classifications=("internal",),
            applicability_state="unconditional",
            retracted=False,
            conditions=(),
        )
        store.set_technology_option_candidates([candidate])

        # Act
        result = await store.resolve_technology_options("cap-1")

        # Assert
        assert result == [candidate]

    async def test_resolve_technology_options_records_the_requested_capability_id(
        self,
    ) -> None:
        # Arrange
        store = InMemoryGraphStore()

        # Act
        await store.resolve_technology_options("cap-42")

        # Assert — lets a test prove the operation forwarded the caller's
        # capability id rather than dropping or substituting it.
        assert store.resolve_technology_options_calls == ["cap-42"]


class TestInMemoryGraphStoreSelectPatterns:
    """The controllable candidate-record store (§4.2 A3)."""

    async def test_select_patterns_with_no_candidates_set_returns_empty(self) -> None:
        # Arrange
        store = InMemoryGraphStore()

        # Act
        result = await store.select_patterns(["cap-1"])

        # Assert
        assert result == []

    async def test_select_patterns_returns_the_configured_candidates(self) -> None:
        # Arrange
        store = InMemoryGraphStore()
        candidate = SelectPatternsCandidateRecord(
            node_id="pattern-1",
            version="1",
            origin_mechanism="ingested",
            derivation_class="primary",
            applicability_state="unconditional",
            retracted=False,
            conditions=(),
            capabilities=(),
            preferred_over=(),
        )
        store.set_pattern_candidates([candidate])

        # Act
        result = await store.select_patterns(["cap-1"])

        # Assert
        assert result == [candidate]

    async def test_select_patterns_records_the_requested_capability_ids(self) -> None:
        # Arrange
        store = InMemoryGraphStore()

        # Act
        await store.select_patterns(["cap-a", "cap-b"])

        # Assert — lets a test prove the operation forwarded the caller's
        # required capabilities rather than dropping or substituting them.
        assert store.select_patterns_calls == [["cap-a", "cap-b"]]


class TestInMemoryGraphStoreObligationContext:
    """The controllable candidate-record store (§4.2 A3)."""

    async def test_obligation_context_with_no_candidates_set_returns_empty(self) -> None:
        # Arrange
        store = InMemoryGraphStore()

        # Act
        result = await store.obligation_context("sol-1")

        # Assert
        assert result == []

    async def test_obligation_context_returns_the_configured_candidates(self) -> None:
        # Arrange
        store = InMemoryGraphStore()
        candidate = ObligationCandidateRecord(
            node_id="rule-1",
            version="1",
            origin_mechanism="ingested",
            derivation_class="primary",
            applicability_state="unconditional",
            retracted=False,
            conditions=(),
            statement="Data at rest must be encrypted.",
            rule_definition="IF classification == 'restricted' THEN require(encryption)",
            dependency_manifest=("Technology",),
            enforcement_level="hard",
            enforced_at_gate="architecture_review",
            domain="security",
        )
        store.set_obligation_candidates([candidate])

        # Act
        result = await store.obligation_context("sol-1")

        # Assert
        assert result == [candidate]

    async def test_obligation_context_records_the_requested_solution_id(self) -> None:
        # Arrange
        store = InMemoryGraphStore()

        # Act
        await store.obligation_context("sol-42")

        # Assert — lets a test prove the operation forwarded the caller's
        # solution id rather than dropping or substituting it.
        assert store.obligation_context_calls == ["sol-42"]


class TestInMemoryGraphStoreFindPrecedents:
    """The controllable candidate-record store (§4.2 A3)."""

    async def test_find_precedents_with_no_candidates_set_returns_empty(self) -> None:
        # Arrange
        store = InMemoryGraphStore()
        criteria = FindPrecedentsCriteria(
            capability_ids=(),
            pattern_ids=(),
            technology_ids=("tech-1",),
            target_environment=None,
            gate_outcome=None,
        )

        # Act
        result = await store.find_precedents(criteria)

        # Assert
        assert result == []

    async def test_find_precedents_returns_the_configured_candidates(self) -> None:
        # Arrange
        store = InMemoryGraphStore()
        candidate = FindPrecedentsCandidateRecord(
            node_id="sol-1",
            version="1",
            origin_mechanism="authored",
            target_environment="production",
            gate_decisions=(),
        )
        store.set_precedent_candidates([candidate])
        criteria = FindPrecedentsCriteria(
            capability_ids=(),
            pattern_ids=(),
            technology_ids=("tech-1",),
            target_environment=None,
            gate_outcome=None,
        )

        # Act
        result = await store.find_precedents(criteria)

        # Assert
        assert result == [candidate]

    async def test_find_precedents_records_the_requested_criteria(self) -> None:
        # Arrange
        store = InMemoryGraphStore()
        criteria = FindPrecedentsCriteria(
            capability_ids=("cap-1",),
            pattern_ids=(),
            technology_ids=(),
            target_environment="production",
            gate_outcome="approved",
        )

        # Act
        await store.find_precedents(criteria)

        # Assert — lets a test prove the operation forwarded the caller's
        # criteria rather than dropping or substituting them.
        assert store.find_precedents_calls == [criteria]


class TestInMemoryGraphStoreReadAsOf:
    """The controllable single-record store (§4.2 A3)."""

    async def test_read_as_of_with_no_result_set_returns_none(self) -> None:
        # Arrange — a resolution miss.
        store = InMemoryGraphStore()

        # Act
        result = await store.read_as_of("Technology", "tech-1", "1")

        # Assert
        assert result is None

    async def test_read_as_of_returns_the_configured_record(self) -> None:
        # Arrange
        store = InMemoryGraphStore()
        record = ReadAsOfResolvedRecord(
            node_id="tech-1",
            plane_labels=("Catalog",),
            version="3",
            origin_mechanism="ingested",
            derivation_class="primary",
            effective_from=None,
            effective_to=None,
            applicability_state="unconditional",
            retracted=False,
            conditions=(),
        )
        store.set_read_as_of_result(record)

        # Act
        result = await store.read_as_of("Technology", "tech-1", "3")

        # Assert
        assert result == record

    async def test_read_as_of_records_the_requested_pin(self) -> None:
        # Arrange
        store = InMemoryGraphStore()

        # Act
        await store.read_as_of("Technology", "tech-42", "2")

        # Assert — lets a test prove the operation forwarded the caller's
        # pin rather than dropping or substituting it.
        assert store.read_as_of_calls == [("Technology", "tech-42", "2")]


class TestInMemoryGraphStoreCitationLookup:
    """R6a: the ONE double with real behavior — genuine keyset pagination
    (§4.2 A3 note: pagination correctness is under test, not graph-internals
    modelling, so this double must actually paginate)."""

    async def test_not_found_reports_entry_found_false(self) -> None:
        # Arrange — the double defaults to not-found until configured.
        store = InMemoryGraphStore()

        # Act
        page = await store.citation_lookup("Technology", "tech-x", "1", "per_version", None, 50)

        # Assert
        assert page.entry_found is False
        assert page.citations == ()
        assert page.entry_statuses == ()
        assert page.next_cursor is None

    async def test_found_with_zero_citations_is_not_an_error(self) -> None:
        # Arrange
        store = InMemoryGraphStore()
        store.set_citation_lookup_result(entry_found=True, citations=())

        # Act
        page = await store.citation_lookup("Technology", "tech-1", "1", "per_version", None, 50)

        # Assert
        assert page.entry_found is True
        assert page.citations == ()
        assert page.next_cursor is None

    async def test_page_under_the_limit_has_no_next_cursor(self) -> None:
        # Arrange
        store = InMemoryGraphStore()
        store.set_citation_lookup_result(
            entry_found=True, citations=[_citation("ev-1"), _citation("ev-2")]
        )

        # Act
        page = await store.citation_lookup("Technology", "tech-1", "1", "per_version", None, 50)

        # Assert
        assert [c.evidence_id for c in page.citations] == ["ev-1", "ev-2"]
        assert page.next_cursor is None

    async def test_pagination_across_pages_has_no_duplication_and_no_skip(self) -> None:
        # Arrange — 5 citations, page size 2: exercises the full keyset walk.
        store = InMemoryGraphStore()
        all_ids = ["ev-1", "ev-2", "ev-3", "ev-4", "ev-5"]
        store.set_citation_lookup_result(
            entry_found=True, citations=[_citation(eid) for eid in all_ids]
        )

        # Act — walk every page via the returned cursor.
        collected: list[str] = []
        cursor: str | None = None
        for _ in range(10):  # bounded: a stuck cursor must not hang the test
            page = await store.citation_lookup(
                "Technology", "tech-1", "1", "per_version", cursor, 2
            )
            collected.extend(c.evidence_id for c in page.citations)
            if page.next_cursor is None:
                break
            cursor = page.next_cursor

        # Assert — every id exactly once, in order: no dup, no skip.
        assert collected == all_ids

    async def test_limit_caps_the_returned_page_and_sets_next_cursor(self) -> None:
        # Arrange
        store = InMemoryGraphStore()
        store.set_citation_lookup_result(
            entry_found=True, citations=[_citation("ev-1"), _citation("ev-2"), _citation("ev-3")]
        )

        # Act
        page = await store.citation_lookup("Technology", "tech-1", "1", "per_version", None, 2)

        # Assert
        assert [c.evidence_id for c in page.citations] == ["ev-1", "ev-2"]
        assert page.next_cursor == "ev-2"

    async def test_after_evidence_id_filters_to_strictly_greater_ids(self) -> None:
        # Arrange
        store = InMemoryGraphStore()
        store.set_citation_lookup_result(
            entry_found=True, citations=[_citation("ev-1"), _citation("ev-2"), _citation("ev-3")]
        )

        # Act
        page = await store.citation_lookup(
            "Technology", "tech-1", "1", "per_version", "ev-1", 50
        )

        # Assert
        assert [c.evidence_id for c in page.citations] == ["ev-2", "ev-3"]

    async def test_reports_the_configured_entry_statuses(self) -> None:
        # Arrange
        store = InMemoryGraphStore()
        statuses = [
            CitationEntryStatusRecord(
                version="2", is_superseded=True, is_retracted=False, is_conditional=True
            )
        ]
        store.set_citation_lookup_result(entry_found=True, entry_statuses=statuses, citations=())

        # Act
        page = await store.citation_lookup(
            "Technology", "tech-1", "2", "per_version", None, 50
        )

        # Assert — co-occurring markers both survive; nothing excludes.
        assert page.entry_statuses == tuple(statuses)
        assert page.citations == ()

    async def test_records_the_requested_pin_mode_and_page(self) -> None:
        # Arrange
        store = InMemoryGraphStore()

        # Act
        await store.citation_lookup(
            "PolicyRule", "rule-1", None, "business_key_wide", "ev-9", 10
        )

        # Assert — lets a test prove the operation forwarded the caller's
        # pin/mode/page rather than dropping or substituting them.
        assert store.citation_lookup_calls == [
            ("PolicyRule", "rule-1", None, "business_key_wide", "ev-9", 10)
        ]


class TestInMemoryGraphStoreProvenanceOf:
    """The controllable single-page store (§4.2 A3) — R6b, single-subject,
    unpaginated."""

    async def test_default_reports_entry_found_false(self) -> None:
        # Arrange — no configuration yet.
        store = InMemoryGraphStore()

        # Act
        page = await store.provenance_of("Technology", "tech-1", "1")

        # Assert
        assert page.entry_found is False
        assert page.is_promoted is False

    async def test_returns_the_configured_page(self) -> None:
        # Arrange
        store = InMemoryGraphStore()
        page = ProvenanceOfPage(
            entry_found=True,
            is_promoted=True,
            origin_mechanism="promoted",
            is_superseded=False,
            is_retracted=False,
            is_conditional=False,
            candidate=ProvenanceOfCandidateRecord(
                candidate_id="cand-1", proposal_kind="promotion", status="promoted"
            ),
            governing_decision=ProvenanceOfGoverningDecisionRecord(
                decision_id="dec-1", outcome="approved", decided_at="2026-07-01T00:00:00Z"
            ),
            frozen_layer_present=True,
            provenance_summary_id="summary-1",
            entries=(
                ProvenanceOfFrozenEntryRecord(
                    evidence_id="ev-1",
                    frozen_fact_summary="a fact",
                    frozen_source_version_pin="1",
                    frozen_source_node_ref="tech-1",
                    is_live=True,
                    live_fact_summary="a fact",
                    live_confidence=0.8,
                    live_weight=1.0,
                    live_source_node_version="1",
                    live_observed_at="2026-07-01T00:00:00Z",
                ),
            ),
        )
        store.set_provenance_of_result(page)

        # Act
        result = await store.provenance_of("Technology", "tech-1", "1")

        # Assert
        assert result == page

    async def test_records_the_requested_pin(self) -> None:
        # Arrange
        store = InMemoryGraphStore()

        # Act
        await store.provenance_of("Technology", "tech-42", "2")

        # Assert — lets a test prove the operation forwarded the caller's
        # pin rather than dropping or substituting it.
        assert store.provenance_of_calls == [("Technology", "tech-42", "2")]


class TestInMemoryGraphStoreSessionTrace:
    """The controllable single-page store (§4.2 A3) — R6c, single-subject,
    unpaginated."""

    async def test_default_reports_session_found_false(self) -> None:
        # Arrange — no configuration yet.
        store = InMemoryGraphStore()

        # Act
        page = await store.session_trace("sess-1")

        # Assert
        assert page.session_found is False
        assert page.conclusions == ()

    async def test_returns_the_configured_page(self) -> None:
        # Arrange
        store = InMemoryGraphStore()
        page = SessionTracePage(
            session_found=True,
            conclusions=(
                TraceConclusionRecord(
                    progress_id="prog-1",
                    conclusion_type="TechnologySelection",
                    reasoner_category="encoded_reasoning",
                    authoritative=True,
                    confidence=0.9,
                    overridden_by_human=False,
                    created_at="2026-07-01T00:00:00Z",
                    evidence=(
                        TraceEvidenceRecord(
                            evidence_id="ev-1",
                            fact_summary="a fact",
                            confidence=0.8,
                            weight=1.0,
                            source_node_version="1",
                            observed_at="2026-07-01T00:00:00Z",
                            resolved_pin=CitedNodeRefRecord(
                                node_kind="Technology",
                                node_id="tech-1",
                                version="1",
                                is_superseded=False,
                                is_retracted=False,
                                is_conditional=False,
                            ),
                        ),
                    ),
                    rejected_alternatives=(
                        TraceRejectedAlternativeRecord(
                            rejected_id="rej-1",
                            candidate_type="Technology",
                            rejection_reason="cost",
                            score_delta=-0.2,
                            human_accepted=False,
                            would_have_used=(
                                CitedNodeRefRecord(
                                    node_kind="Technology",
                                    node_id="tech-2",
                                    version="1",
                                    is_superseded=False,
                                    is_retracted=False,
                                    is_conditional=False,
                                ),
                            ),
                        ),
                    ),
                ),
            ),
            led_to=(LedToRecord(from_progress_id="prog-1", to_progress_id="prog-2"),),
        )
        store.set_session_trace_result(page)

        # Act
        result = await store.session_trace("sess-1")

        # Assert
        assert result == page

    async def test_records_the_requested_session_id(self) -> None:
        # Arrange
        store = InMemoryGraphStore()

        # Act
        await store.session_trace("sess-42")

        # Assert — lets a test prove the operation forwarded the caller's
        # session id rather than dropping or substituting it.
        assert store.session_trace_calls == ["sess-42"]
