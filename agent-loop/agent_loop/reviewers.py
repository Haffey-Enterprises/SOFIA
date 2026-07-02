# Module: agent_loop.reviewers
# Purpose: The reviewer port and its supporting types — the seam the runner
#          schedules against, shared by the canned stub path and the real-hat
#          path (runner-real-hats.contract.md §1, §5). A ScheduledReviewer pairs
#          a reviewer's identity (source/altitude to stamp, admission rank) with
#          a run function that takes the frozen prior-pass snapshot and the
#          fetched-fresh inputs and returns Finding templates.
# Scope:   Port + input types + canonical identities + the stub adapter. No LLM,
#          no admission, no gate logic here.

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

from agent_loop.ledger import Altitude, Finding, Ledger, Source
from agent_loop.log import ActionLog


# --- §5 input types (assembled fresh by the runner, per pass) ----------------


@dataclass(frozen=True)
class DocumentSet:
    """The full document set under review, per the ledger header `set`.

    Attributes:
        documents: Map of document id → content. In the dry harness the content
            is a placeholder — no real ADR/DDR is touched — but the structure is
            real so the runner remains the single fetch point (§5): reviewers do
            not fetch for themselves.
    """

    documents: dict[str, str]


@dataclass(frozen=True)
class Substrate:
    """The ratified substrate in scope for the set.

    Attributes:
        authorities: Ratified canonical authorities (id → content).
        design_intent: Stated design intent (id → content).
    """

    authorities: dict[str, str]
    design_intent: dict[str, str]


def default_document_fetcher(doc_ids: list[str]) -> DocumentSet:
    """Placeholder document fetch for the dry harness (no real documents).

    A real deployment injects a fetcher that loads document content; here the
    content is a marker so the assembly path is exercised without touching a
    real artifact.
    """
    return DocumentSet(
        documents={doc_id: f"<{doc_id}: content not materialised in dry harness>" for doc_id in doc_ids}
    )


def default_substrate_fetcher(doc_ids: list[str]) -> Substrate:
    """Placeholder substrate fetch for the dry harness (empty scope)."""
    return Substrate(authorities={}, design_intent={})


DocumentFetcher = Callable[[list[str]], DocumentSet]
SubstrateFetcher = Callable[[list[str]], Substrate]


# --- reviewer identity + the scheduled-reviewer port -------------------------


@dataclass(frozen=True)
class ReviewerIdentity:
    """A reviewer's runner-side identity.

    Attributes:
        label: Human tag used in `agents_run` and skip/parse logs.
        source: The `source` the runner stamps on this reviewer's findings
            (real path — §7); for canned stubs the finding already carries its
            own source and is admitted as-is.
        altitude: The `altitude` the runner stamps (real path — §7).
        admission_rank: Fixed admission order — LAA(0), SA(1), EA(2),
            coherence(3). Determinism keeps ids, dedup, and logs reproducible.
    """

    label: str
    source: Source
    altitude: Altitude
    admission_rank: int


# The run function receives the frozen prior-pass snapshot and fetched-fresh
# inputs (never the mutating in-pass ledger) and returns Finding templates.
# `log` is passed so a real reviewer's parse seam can record parse-drops (§7).
ReviewerRun = Callable[[int, Ledger, DocumentSet, Substrate, ActionLog], list[Finding]]


@dataclass
class ScheduledReviewer:
    """A reviewer scheduled to run this pass: its identity + its run function."""

    identity: ReviewerIdentity
    run: ReviewerRun


# A pass plan: given the pass number and the frozen snapshot, decide which
# reviewers run this pass (and log any skip — §6). The plan owns scheduling;
# the runner owns gather-then-admit.
Plan = Callable[[int, Ledger, ActionLog], list[ScheduledReviewer]]


# --- canonical real-hat + coherence identities (admission order) -------------

IDENTITY_LAA = ReviewerIdentity("antagonist-LAA", "antagonist-LAA", "LAA", 0)
IDENTITY_SA = ReviewerIdentity("antagonist-SA", "antagonist-SA", "SA", 1)
IDENTITY_EA = ReviewerIdentity("antagonist-EA", "antagonist-EA", "EA", 2)
IDENTITY_COHERENCE = ReviewerIdentity("coherence", "coherence", "cross-set", 3)

# Stub identities preserve the current `agents_run` labels and the current
# admission order (antagonist before coherence). Their source/altitude are
# unused by the engine — canned findings carry their own, set by the scenario.
IDENTITY_ANTAGONIST_STUB = ReviewerIdentity(
    "antagonist-stub", "antagonist-stub", "LAA", 0
)
IDENTITY_COHERENCE_STUB = ReviewerIdentity(
    "coherence-stub", "coherence-stub", "cross-set", 3
)


# --- stub adapter: canned Reviewer -> ScheduledReviewer path -----------------

# The canned stub port (agent_loop.stubs.Reviewer) is Callable[[int, Ledger],
# list[Finding]]. It is adapted to the ScheduledReviewer run signature here; the
# stub reads only prior-pass state, so handing it the frozen snapshot is
# behaviour-preserving.
StubReviewer = Callable[[int, Ledger], list[Finding]]


def stub_plan(antagonist: StubReviewer, coherence: StubReviewer) -> Plan:
    """Build the stub-path plan: antagonist + coherence, every pass.

    This preserves the skeleton's every-pass behaviour (the coherence stub
    self-gates internally via its emission predicates — §6 keeps that on the
    stub path only). Both reviewers receive the frozen snapshot.
    """

    def plan(pass_number: int, snapshot: Ledger, log: ActionLog) -> list[ScheduledReviewer]:
        return [
            ScheduledReviewer(
                IDENTITY_ANTAGONIST_STUB,
                lambda pn, snap, recs, sub, lg, _r=antagonist: _r(pn, snap),
            ),
            ScheduledReviewer(
                IDENTITY_COHERENCE_STUB,
                lambda pn, snap, recs, sub, lg, _r=coherence: _r(pn, snap),
            ),
        ]

    return plan
