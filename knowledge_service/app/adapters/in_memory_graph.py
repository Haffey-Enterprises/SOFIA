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
#   never omitted from coverage measurement. RBT-78/R3a added find_track_record
#   and R3b adds resolve_technology_options, both as controllable candidate-
#   record stores (§4.2 A3): tests set the exact records each returns, so the
#   operation and read-discipline layers can be exercised without modelling
#   graph internals.
##############################################################################

from collections.abc import Sequence

from app.ports.graph_store import (
    ResolveTechnologyCandidateRecord,
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
