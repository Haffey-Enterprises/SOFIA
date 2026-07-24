##############################################################################
# Module: test_ports.py
# Service: knowledge-service
# Author: Haffey Enterprises LLC
# Created: 2026-07-21
# Revised: 2026-07-21
# Description: Tests for the port declarations (SDD-001 §4.2). These are pure
#   Protocols with no behavior of their own, so what is asserted here is the
#   seam itself: that each port is structurally checkable, and that an object
#   missing the contract does not satisfy it. That last point is what stops a
#   later adapter from being wired in half-implemented. GraphStoragePort grows
#   additively (RBT-78/R3a find_track_record, R3b resolve_technology_options,
#   R3c select_patterns, R4a obligation_context, R4b find_precedents, R5a
#   read_as_of, R6a citation_lookup, R6b provenance_of, R6c session_trace —
#   the ninth and last read op) — the minimal fixture below grows with it,
#   since isinstance() against a runtime_checkable Protocol checks every
#   declared member, not just the ones a test happens to exercise.
##############################################################################

from collections.abc import Mapping, Sequence

from app.ports.graph_store import (
    CitationLookupPage,
    CitationMode,
    FindPrecedentsCandidateRecord,
    FindPrecedentsCriteria,
    GraphStoragePort,
    ObligationCandidateRecord,
    ProvenanceOfPage,
    ReadAsOfNodeKind,
    ReadAsOfResolvedRecord,
    ResolveTechnologyCandidateRecord,
    SelectPatternsCandidateRecord,
    SessionTracePage,
    TargetEntityRef,
    TrackRecordCandidateRecord,
)
from app.ports.predicate_eval import PredicateEvaluationPort


class TestGraphStoragePortDeclaration:
    """The substitution seam admits only objects carrying its surface."""

    def test_object_without_check_connectivity_does_not_satisfy_the_port(self) -> None:
        # Arrange
        class NotAGraphStore:
            pass

        # Act / Assert
        assert not isinstance(NotAGraphStore(), GraphStoragePort)

    def test_object_missing_resolve_technology_options_does_not_satisfy_the_port(
        self,
    ) -> None:
        # Arrange — R3b grew the port again; find_track_record alone no
        # longer suffices.
        class PartialGraphStore:
            async def check_connectivity(self) -> bool:
                return True

            async def find_track_record(
                self, target_refs: Sequence[TargetEntityRef]
            ) -> Sequence[TrackRecordCandidateRecord]:
                return []

        # Act / Assert
        assert not isinstance(PartialGraphStore(), GraphStoragePort)

    def test_object_missing_select_patterns_does_not_satisfy_the_port(self) -> None:
        # Arrange — R3c grew the port again; resolve_technology_options alone
        # no longer suffices.
        class PartialGraphStore:
            async def check_connectivity(self) -> bool:
                return True

            async def find_track_record(
                self, target_refs: Sequence[TargetEntityRef]
            ) -> Sequence[TrackRecordCandidateRecord]:
                return []

            async def resolve_technology_options(
                self, capability_id: str
            ) -> Sequence[ResolveTechnologyCandidateRecord]:
                return []

        # Act / Assert
        assert not isinstance(PartialGraphStore(), GraphStoragePort)

    def test_object_missing_obligation_context_does_not_satisfy_the_port(self) -> None:
        # Arrange — R4a grew the port again; select_patterns alone no longer
        # suffices.
        class PartialGraphStore:
            async def check_connectivity(self) -> bool:
                return True

            async def find_track_record(
                self, target_refs: Sequence[TargetEntityRef]
            ) -> Sequence[TrackRecordCandidateRecord]:
                return []

            async def resolve_technology_options(
                self, capability_id: str
            ) -> Sequence[ResolveTechnologyCandidateRecord]:
                return []

            async def select_patterns(
                self, capability_ids: Sequence[str]
            ) -> Sequence[SelectPatternsCandidateRecord]:
                return []

        # Act / Assert
        assert not isinstance(PartialGraphStore(), GraphStoragePort)

    def test_object_missing_find_precedents_does_not_satisfy_the_port(self) -> None:
        # Arrange — R4b grew the port again; obligation_context alone no
        # longer suffices.
        class PartialGraphStore:
            async def check_connectivity(self) -> bool:
                return True

            async def find_track_record(
                self, target_refs: Sequence[TargetEntityRef]
            ) -> Sequence[TrackRecordCandidateRecord]:
                return []

            async def resolve_technology_options(
                self, capability_id: str
            ) -> Sequence[ResolveTechnologyCandidateRecord]:
                return []

            async def select_patterns(
                self, capability_ids: Sequence[str]
            ) -> Sequence[SelectPatternsCandidateRecord]:
                return []

            async def obligation_context(
                self, solution_id: str
            ) -> Sequence[ObligationCandidateRecord]:
                return []

        # Act / Assert
        assert not isinstance(PartialGraphStore(), GraphStoragePort)

    def test_object_missing_read_as_of_does_not_satisfy_the_port(self) -> None:
        # Arrange — R5a grew the port again; find_precedents alone no longer
        # suffices.
        class PartialGraphStore:
            async def check_connectivity(self) -> bool:
                return True

            async def find_track_record(
                self, target_refs: Sequence[TargetEntityRef]
            ) -> Sequence[TrackRecordCandidateRecord]:
                return []

            async def resolve_technology_options(
                self, capability_id: str
            ) -> Sequence[ResolveTechnologyCandidateRecord]:
                return []

            async def select_patterns(
                self, capability_ids: Sequence[str]
            ) -> Sequence[SelectPatternsCandidateRecord]:
                return []

            async def obligation_context(
                self, solution_id: str
            ) -> Sequence[ObligationCandidateRecord]:
                return []

            async def find_precedents(
                self, criteria: FindPrecedentsCriteria
            ) -> Sequence[FindPrecedentsCandidateRecord]:
                return []

        # Act / Assert
        assert not isinstance(PartialGraphStore(), GraphStoragePort)

    def test_object_missing_citation_lookup_does_not_satisfy_the_port(self) -> None:
        # Arrange — R6a grew the port again; read_as_of alone no longer
        # suffices.
        class PartialGraphStore:
            async def check_connectivity(self) -> bool:
                return True

            async def find_track_record(
                self, target_refs: Sequence[TargetEntityRef]
            ) -> Sequence[TrackRecordCandidateRecord]:
                return []

            async def resolve_technology_options(
                self, capability_id: str
            ) -> Sequence[ResolveTechnologyCandidateRecord]:
                return []

            async def select_patterns(
                self, capability_ids: Sequence[str]
            ) -> Sequence[SelectPatternsCandidateRecord]:
                return []

            async def obligation_context(
                self, solution_id: str
            ) -> Sequence[ObligationCandidateRecord]:
                return []

            async def find_precedents(
                self, criteria: FindPrecedentsCriteria
            ) -> Sequence[FindPrecedentsCandidateRecord]:
                return []

            async def read_as_of(
                self, node_kind: ReadAsOfNodeKind, business_key: str, version: str
            ) -> ReadAsOfResolvedRecord | None:
                return None

        # Act / Assert
        assert not isinstance(PartialGraphStore(), GraphStoragePort)

    def test_object_missing_provenance_of_does_not_satisfy_the_port(self) -> None:
        # Arrange — R6b grew the port again; citation_lookup alone no longer
        # suffices.
        class PartialGraphStore:
            async def check_connectivity(self) -> bool:
                return True

            async def find_track_record(
                self, target_refs: Sequence[TargetEntityRef]
            ) -> Sequence[TrackRecordCandidateRecord]:
                return []

            async def resolve_technology_options(
                self, capability_id: str
            ) -> Sequence[ResolveTechnologyCandidateRecord]:
                return []

            async def select_patterns(
                self, capability_ids: Sequence[str]
            ) -> Sequence[SelectPatternsCandidateRecord]:
                return []

            async def obligation_context(
                self, solution_id: str
            ) -> Sequence[ObligationCandidateRecord]:
                return []

            async def find_precedents(
                self, criteria: FindPrecedentsCriteria
            ) -> Sequence[FindPrecedentsCandidateRecord]:
                return []

            async def read_as_of(
                self, node_kind: ReadAsOfNodeKind, business_key: str, version: str
            ) -> ReadAsOfResolvedRecord | None:
                return None

            async def citation_lookup(
                self,
                node_kind: ReadAsOfNodeKind,
                business_key: str,
                version: str | None,
                mode: CitationMode,
                after_evidence_id: str | None,
                limit: int,
            ) -> CitationLookupPage:
                return CitationLookupPage(
                    entry_found=False, entry_statuses=(), citations=(), next_cursor=None
                )

        # Act / Assert
        assert not isinstance(PartialGraphStore(), GraphStoragePort)

    def test_object_missing_session_trace_does_not_satisfy_the_port(self) -> None:
        # Arrange — R6c grew the port again; provenance_of alone no longer
        # suffices.
        class PartialGraphStore:
            async def check_connectivity(self) -> bool:
                return True

            async def find_track_record(
                self, target_refs: Sequence[TargetEntityRef]
            ) -> Sequence[TrackRecordCandidateRecord]:
                return []

            async def resolve_technology_options(
                self, capability_id: str
            ) -> Sequence[ResolveTechnologyCandidateRecord]:
                return []

            async def select_patterns(
                self, capability_ids: Sequence[str]
            ) -> Sequence[SelectPatternsCandidateRecord]:
                return []

            async def obligation_context(
                self, solution_id: str
            ) -> Sequence[ObligationCandidateRecord]:
                return []

            async def find_precedents(
                self, criteria: FindPrecedentsCriteria
            ) -> Sequence[FindPrecedentsCandidateRecord]:
                return []

            async def read_as_of(
                self, node_kind: ReadAsOfNodeKind, business_key: str, version: str
            ) -> ReadAsOfResolvedRecord | None:
                return None

            async def citation_lookup(
                self,
                node_kind: ReadAsOfNodeKind,
                business_key: str,
                version: str | None,
                mode: CitationMode,
                after_evidence_id: str | None,
                limit: int,
            ) -> CitationLookupPage:
                return CitationLookupPage(
                    entry_found=False, entry_statuses=(), citations=(), next_cursor=None
                )

            async def provenance_of(
                self, node_kind: ReadAsOfNodeKind, business_key: str, version: str
            ) -> ProvenanceOfPage:
                return ProvenanceOfPage(
                    entry_found=False,
                    is_promoted=False,
                    origin_mechanism=None,
                    is_superseded=False,
                    is_retracted=False,
                    is_conditional=False,
                    candidate=None,
                    governing_decision=None,
                    frozen_layer_present=False,
                    provenance_summary_id=None,
                    entries=(),
                )

        # Act / Assert
        assert not isinstance(PartialGraphStore(), GraphStoragePort)

    def test_object_with_the_full_surface_satisfies_the_port(self) -> None:
        # Arrange
        class MinimalGraphStore:
            async def check_connectivity(self) -> bool:
                return True

            async def find_track_record(
                self, target_refs: Sequence[TargetEntityRef]
            ) -> Sequence[TrackRecordCandidateRecord]:
                return []

            async def resolve_technology_options(
                self, capability_id: str
            ) -> Sequence[ResolveTechnologyCandidateRecord]:
                return []

            async def select_patterns(
                self, capability_ids: Sequence[str]
            ) -> Sequence[SelectPatternsCandidateRecord]:
                return []

            async def obligation_context(
                self, solution_id: str
            ) -> Sequence[ObligationCandidateRecord]:
                return []

            async def find_precedents(
                self, criteria: FindPrecedentsCriteria
            ) -> Sequence[FindPrecedentsCandidateRecord]:
                return []

            async def read_as_of(
                self, node_kind: ReadAsOfNodeKind, business_key: str, version: str
            ) -> ReadAsOfResolvedRecord | None:
                return None

            async def citation_lookup(
                self,
                node_kind: ReadAsOfNodeKind,
                business_key: str,
                version: str | None,
                mode: CitationMode,
                after_evidence_id: str | None,
                limit: int,
            ) -> CitationLookupPage:
                return CitationLookupPage(
                    entry_found=False, entry_statuses=(), citations=(), next_cursor=None
                )

            async def provenance_of(
                self, node_kind: ReadAsOfNodeKind, business_key: str, version: str
            ) -> ProvenanceOfPage:
                return ProvenanceOfPage(
                    entry_found=False,
                    is_promoted=False,
                    origin_mechanism=None,
                    is_superseded=False,
                    is_retracted=False,
                    is_conditional=False,
                    candidate=None,
                    governing_decision=None,
                    frozen_layer_present=False,
                    provenance_summary_id=None,
                    entries=(),
                )

            async def session_trace(self, session_id: str) -> SessionTracePage:
                return SessionTracePage(session_found=False, conclusions=(), led_to=())

        # Act / Assert
        assert isinstance(MinimalGraphStore(), GraphStoragePort)


class TestPredicateEvaluationPortDeclaration:
    """Declared at RBT-77, implemented nowhere — DDR-003 owns the grammar."""

    def test_object_without_evaluate_does_not_satisfy_the_port(self) -> None:
        # Arrange
        class NotAnEvaluator:
            pass

        # Act / Assert
        assert not isinstance(NotAnEvaluator(), PredicateEvaluationPort)

    def test_object_with_evaluate_satisfies_the_port(self) -> None:
        # Arrange
        class MinimalEvaluator:
            async def evaluate(
                self,
                predicate: Mapping[str, object],
                context: Mapping[str, object],
            ) -> bool:
                return False

        # Act / Assert
        assert isinstance(MinimalEvaluator(), PredicateEvaluationPort)

    def test_no_predicate_evaluation_adapter_ships_in_this_service_yet(self) -> None:
        # Arrange / Act — an implementation before DDR-003's vocabulary is
        # ratified would be a gateway-local fork of predicate semantics, which
        # SDD-001 §4.2 prohibits.
        import app.adapters as adapters_package

        module_names = dir(adapters_package)

        # Assert
        assert not any("predicate" in name.lower() for name in module_names)
