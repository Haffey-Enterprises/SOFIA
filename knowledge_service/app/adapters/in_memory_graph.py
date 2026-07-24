##############################################################################
# Module: in_memory_graph.py
# Service: knowledge-service
# Author: Haffey Enterprises LLC
# Created: 2026-07-21
# Revised: 2026-07-23
# Description: In-memory GraphStoragePort implementation — the double every
#   knowledge-service test runs against (SDD-001 §4.2, §6). It is a first-class
#   implementation of the port, not a mock: keeping it a true substitute is
#   what lets the domain suite verify behavior without a live Neo4j, and it is
#   never omitted from coverage measurement. RBT-78/R3a added find_track_record,
#   R3b added resolve_technology_options, and R3c adds select_patterns — all
#   controllable candidate-record stores (§4.2 A3): tests set the exact records
#   each returns, so the operation and read-discipline layers can be exercised
#   without modelling graph internals. R6a's citation_lookup is DIFFERENT: it
#   is the first paginated method, and keyset-pagination correctness (no dup,
#   no skip across pages, cap honored) is genuine behavior under test — so
#   this double performs REAL keyset pagination over the configured citation
#   sequence rather than returning it unconditionally. The caller supplies the
#   full unpaginated set, pre-sorted by evidence_id; that ordering is a test
#   setup responsibility, not something this double re-derives (it has no
#   graph to derive it from).
##############################################################################

from collections.abc import Sequence

from app.ports.graph_store import (
    CitationEntryStatusRecord,
    CitationLookupPage,
    CitationMode,
    CitationRecord,
    FindPrecedentsCandidateRecord,
    FindPrecedentsCriteria,
    ObligationCandidateRecord,
    ReadAsOfNodeKind,
    ReadAsOfResolvedRecord,
    ResolveTechnologyCandidateRecord,
    SelectPatternsCandidateRecord,
    TargetEntityRef,
    TrackRecordCandidateRecord,
)


class InMemoryGraphStore:
    """A controllable in-memory implementation of `GraphStoragePort`.

    At RBT-77 the port's surface was the connectivity verdict alone. It grows
    in step with the port: when a read operation adds a method, it is
    implemented here in the same story as in the Neo4j adapter — a port
    method implemented on only one side would silently break substitutability.

    The connectivity verdict is settable in both directions so the SDD-001
    §3.1 readiness check can be exercised ready *and* not-ready without a
    database.
    """

    def __init__(self, *, connectivity_healthy: bool = True) -> None:
        """Create the double.

        Args:
            connectivity_healthy: The verdict `check_connectivity` reports
                until `set_connectivity` changes it. Defaults to healthy.
        """
        self._connectivity_healthy = connectivity_healthy
        self._check_connectivity_calls = 0
        self._track_record_candidates: list[TrackRecordCandidateRecord] = []
        self._find_track_record_calls: list[Sequence[TargetEntityRef]] = []
        self._technology_option_candidates: list[ResolveTechnologyCandidateRecord] = []
        self._resolve_technology_options_calls: list[str] = []
        self._pattern_candidates: list[SelectPatternsCandidateRecord] = []
        self._select_patterns_calls: list[Sequence[str]] = []
        self._obligation_candidates: list[ObligationCandidateRecord] = []
        self._obligation_context_calls: list[str] = []
        self._precedent_candidates: list[FindPrecedentsCandidateRecord] = []
        self._find_precedents_calls: list[FindPrecedentsCriteria] = []
        self._read_as_of_result: ReadAsOfResolvedRecord | None = None
        self._read_as_of_calls: list[tuple[ReadAsOfNodeKind, str, str]] = []
        self._citation_entry_found = False
        self._citation_entry_statuses: list[CitationEntryStatusRecord] = []
        self._citation_all_citations: list[CitationRecord] = []
        self._citation_lookup_calls: list[
            tuple[ReadAsOfNodeKind, str, str | None, CitationMode, str | None, int]
        ] = []

    @property
    def check_connectivity_calls(self) -> int:
        """How many times `check_connectivity` has been awaited.

        Lets a readiness test assert the check was genuinely consumed rather
        than short-circuited around.
        """
        return self._check_connectivity_calls

    @property
    def find_track_record_calls(self) -> list[Sequence[TargetEntityRef]]:
        """The `target_refs` argument of every `find_track_record` call.

        Lets a test assert the operation forwarded the caller's target
        entities rather than dropping or substituting them.
        """
        return self._find_track_record_calls

    @property
    def resolve_technology_options_calls(self) -> list[str]:
        """The `capability_id` argument of every `resolve_technology_options` call.

        Lets a test assert the operation forwarded the caller's capability id
        rather than dropping or substituting it.
        """
        return self._resolve_technology_options_calls

    @property
    def select_patterns_calls(self) -> list[Sequence[str]]:
        """The `capability_ids` argument of every `select_patterns` call.

        Lets a test assert the operation forwarded the caller's required
        capabilities rather than dropping or substituting them.
        """
        return self._select_patterns_calls

    @property
    def obligation_context_calls(self) -> list[str]:
        """The `solution_id` argument of every `obligation_context` call.

        Lets a test assert the operation forwarded the caller's solution id
        rather than dropping or substituting it.
        """
        return self._obligation_context_calls

    @property
    def find_precedents_calls(self) -> list[FindPrecedentsCriteria]:
        """The `criteria` argument of every `find_precedents` call.

        Lets a test assert the operation forwarded the caller's structural
        match criteria rather than dropping or substituting them.
        """
        return self._find_precedents_calls

    @property
    def read_as_of_calls(self) -> list[tuple[ReadAsOfNodeKind, str, str]]:
        """The `(node_kind, business_key, version)` argument of every
        `read_as_of` call.

        Lets a test assert the operation forwarded the caller's pin rather
        than dropping or substituting it.
        """
        return self._read_as_of_calls

    @property
    def citation_lookup_calls(
        self,
    ) -> list[tuple[ReadAsOfNodeKind, str, str | None, CitationMode, str | None, int]]:
        """The `(node_kind, business_key, version, mode, after_evidence_id,
        limit)` argument tuple of every `citation_lookup` call.

        Lets a test assert the operation forwarded the caller's pin/mode/page
        rather than dropping or substituting them — including the
        already-resolved `limit` the API layer computed.
        """
        return self._citation_lookup_calls

    def set_connectivity(self, *, healthy: bool) -> None:
        """Set the verdict subsequent connectivity checks will report.

        Args:
            healthy: True to report the store reachable and authenticated,
                False to report it unavailable.
        """
        self._connectivity_healthy = healthy

    def set_track_record_candidates(self, candidates: Sequence[TrackRecordCandidateRecord]) -> None:
        """Set the candidate records subsequent `find_track_record` calls return.

        Args:
            candidates: The records to return, unconditionally on the
                requested `target_refs` — this is a controllable record store
                (SDD-001 §4.2 A3), not a graph-internals model.
        """
        self._track_record_candidates = list(candidates)

    def set_technology_option_candidates(
        self, candidates: Sequence[ResolveTechnologyCandidateRecord]
    ) -> None:
        """Set the candidate records subsequent `resolve_technology_options` calls return.

        Args:
            candidates: The records to return, unconditionally on the
                requested `capability_id` — this is a controllable record
                store (SDD-001 §4.2 A3), not a graph-internals model.
        """
        self._technology_option_candidates = list(candidates)

    def set_pattern_candidates(self, candidates: Sequence[SelectPatternsCandidateRecord]) -> None:
        """Set the candidate records subsequent `select_patterns` calls return.

        Args:
            candidates: The records to return, unconditionally on the
                requested `capability_ids` — this is a controllable record
                store (SDD-001 §4.2 A3), not a graph-internals model.
        """
        self._pattern_candidates = list(candidates)

    def set_obligation_candidates(self, candidates: Sequence[ObligationCandidateRecord]) -> None:
        """Set the candidate records subsequent `obligation_context` calls return.

        Args:
            candidates: The records to return, unconditionally on the
                requested `solution_id` — this is a controllable record
                store (SDD-001 §4.2 A3), not a graph-internals model.
        """
        self._obligation_candidates = list(candidates)

    def set_precedent_candidates(self, candidates: Sequence[FindPrecedentsCandidateRecord]) -> None:
        """Set the candidate records subsequent `find_precedents` calls return.

        Args:
            candidates: The records to return, unconditionally on the
                requested `criteria` — this is a controllable record store
                (SDD-001 §4.2 A3), not a graph-internals model. The AND-
                across/OR-within linkage matching is a graph-traversal
                concern (the Neo4j adapter's Cypher query); this double
                simply reports whatever was configured.
        """
        self._precedent_candidates = list(candidates)

    def set_read_as_of_result(self, record: ReadAsOfResolvedRecord | None) -> None:
        """Set the record (or resolution miss) subsequent `read_as_of` calls return.

        Args:
            record: The record to return, unconditionally on the requested
                `(node_kind, business_key, version)` — this is a controllable
                record store (SDD-001 §4.2 A3), not a graph-internals model.
                `None` stands in for a resolution miss (the pin resolves
                nothing).
        """
        self._read_as_of_result = record

    def set_citation_lookup_result(
        self,
        *,
        entry_found: bool,
        entry_statuses: Sequence[CitationEntryStatusRecord] = (),
        citations: Sequence[CitationRecord] = (),
    ) -> None:
        """Configure the full, unpaginated dataset `citation_lookup` draws from.

        Unlike the other doubles' unconditional-return pattern, `citations`
        IS filtered/paginated by subsequent `citation_lookup` calls — that
        pagination behavior (keyset cursor, no dup, no skip, cap) is itself
        under test here, not graph-internals modelling. Callers must supply
        `citations` pre-sorted by `evidence_id` ascending; this double does
        not re-sort (a real Neo4j `ORDER BY evidence_id` would, but sorting
        here would mask a caller building an unsorted fixture by accident).

        Args:
            entry_found: Whether the entry node(s) exist at all. `False`
                stands in for a truly-absent entry (the operation raises
                `TARGET_NOT_FOUND`); `citations`/`entry_statuses` are ignored
                in that case.
            entry_statuses: The per-version audit-disclosure marker facts —
                0-or-1 for `per_version`, 0-or-more for `business_key_wide`.
            citations: The full citation set, pre-sorted by `evidence_id`.
        """
        self._citation_entry_found = entry_found
        self._citation_entry_statuses = list(entry_statuses)
        self._citation_all_citations = list(citations)

    async def check_connectivity(self) -> bool:
        """Report the configured connectivity verdict.

        Returns:
            The verdict currently set on this double.
        """
        self._check_connectivity_calls += 1
        return self._connectivity_healthy

    async def find_track_record(
        self, target_refs: Sequence[TargetEntityRef]
    ) -> Sequence[TrackRecordCandidateRecord]:
        """Report the configured candidate records.

        Args:
            target_refs: Recorded for test assertion; does not filter the
                configured candidates (a faithful port-level substitute per
                §4.2 need not model graph internals).

        Returns:
            The candidates currently set on this double.
        """
        self._find_track_record_calls.append(target_refs)
        return list(self._track_record_candidates)

    async def resolve_technology_options(
        self, capability_id: str
    ) -> Sequence[ResolveTechnologyCandidateRecord]:
        """Report the configured Technology option candidate records.

        Args:
            capability_id: Recorded for test assertion; does not filter the
                configured candidates (a faithful port-level substitute per
                §4.2 need not model graph internals).

        Returns:
            The candidates currently set on this double.
        """
        self._resolve_technology_options_calls.append(capability_id)
        return list(self._technology_option_candidates)

    async def select_patterns(
        self, capability_ids: Sequence[str]
    ) -> Sequence[SelectPatternsCandidateRecord]:
        """Report the configured candidate Pattern records.

        Args:
            capability_ids: Recorded for test assertion; does not filter the
                configured candidates (a faithful port-level substitute per
                §4.2 need not model graph internals).

        Returns:
            The candidates currently set on this double.
        """
        self._select_patterns_calls.append(capability_ids)
        return list(self._pattern_candidates)

    async def obligation_context(self, solution_id: str) -> Sequence[ObligationCandidateRecord]:
        """Report the configured obligation candidate records.

        Args:
            solution_id: Recorded for test assertion; does not filter the
                configured candidates (a faithful port-level substitute per
                §4.2 need not model graph internals).

        Returns:
            The candidates currently set on this double.
        """
        self._obligation_context_calls.append(solution_id)
        return list(self._obligation_candidates)

    async def find_precedents(
        self, criteria: FindPrecedentsCriteria
    ) -> Sequence[FindPrecedentsCandidateRecord]:
        """Report the configured precedent candidate records.

        Args:
            criteria: Recorded for test assertion; does not filter the
                configured candidates (a faithful port-level substitute per
                §4.2 need not model graph internals).

        Returns:
            The candidates currently set on this double.
        """
        self._find_precedents_calls.append(criteria)
        return list(self._precedent_candidates)

    async def read_as_of(
        self,
        node_kind: ReadAsOfNodeKind,
        business_key: str,
        version: str,
    ) -> ReadAsOfResolvedRecord | None:
        """Report the configured record, or None for a resolution miss.

        Args:
            node_kind: Recorded for test assertion; does not affect the
                configured result (a faithful port-level substitute per §4.2
                need not model graph internals).
            business_key: Recorded for test assertion; does not affect the
                configured result.
            version: Recorded for test assertion; does not affect the
                configured result.

        Returns:
            The record currently set on this double, or `None`.
        """
        self._read_as_of_calls.append((node_kind, business_key, version))
        return self._read_as_of_result

    async def citation_lookup(
        self,
        node_kind: ReadAsOfNodeKind,
        business_key: str,
        version: str | None,
        mode: CitationMode,
        after_evidence_id: str | None,
        limit: int,
    ) -> CitationLookupPage:
        """Report a real keyset page over the configured citation sequence.

        Args:
            node_kind: Recorded for test assertion; does not affect the
                configured result (a faithful port-level substitute per §4.2
                need not model graph internals).
            business_key: Recorded for test assertion; does not affect the
                configured result.
            version: Recorded for test assertion; does not affect the
                configured result.
            mode: Recorded for test assertion; does not affect the configured
                result — mode/version pairing validation is the operation's
                job (SDD-001 §3.3.7 D3), not this double's.
            after_evidence_id: The keyset cursor — genuinely filters the
                configured sequence to strictly-greater `evidence_id`s.
            limit: The page size — genuinely caps the returned page, with a
                real `next_cursor` when more remain.

        Returns:
            `entry_found=False` (citations/entry_statuses empty) when the
            double was configured not-found; otherwise a real page of the
            configured citation sequence.
        """
        self._citation_lookup_calls.append(
            (node_kind, business_key, version, mode, after_evidence_id, limit)
        )
        if not self._citation_entry_found:
            return CitationLookupPage(
                entry_found=False, entry_statuses=(), citations=(), next_cursor=None
            )

        pool = self._citation_all_citations
        if after_evidence_id is not None:
            pool = [c for c in pool if c.evidence_id > after_evidence_id]
        fetched = pool[: limit + 1]
        has_more = len(fetched) > limit
        page = fetched[:limit]
        next_cursor = page[-1].evidence_id if has_more and page else None
        return CitationLookupPage(
            entry_found=True,
            entry_statuses=tuple(self._citation_entry_statuses),
            citations=tuple(page),
            next_cursor=next_cursor,
        )
