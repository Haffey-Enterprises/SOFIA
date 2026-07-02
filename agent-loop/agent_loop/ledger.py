# Module: agent_loop.ledger
# Purpose: The durable spine. Defines the finding/pass/header records and a
#          file-backed store. The ledger is the single source of continuity:
#          every agent fetches it fresh (store.load) and no agent inherits
#          another's in-memory context. Convergence counting, oscillation
#          detection, classification, and routing are all functions over this
#          state (see gates.py).
# Scope:   Data model + JSON persistence. No LLM, no gate logic here.

from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Literal

# --- constrained vocabularies (validated at admission / arbiter) -------------

Source = Literal[
    "coherence",
    "antagonist-LAA",
    "antagonist-SA",
    "antagonist-EA",
    "antagonist-stub",
    "coherence-stub",
]
Altitude = Literal["LAA", "SA", "EA", "cross-set"]
Severity = Literal["BLOCKING", "MATERIAL", "COSMETIC", "POSITIVE"]
AuthorityKind = Literal["canonical", "design-intent", "coherence", "soundness"]
Classification = Literal["unclassified", "resolvable", "decision-bearing"]
Status = Literal["open", "closed", "escalated"]
Mode = Literal["dry", "live"]

# The house `code-review` severity ladder (ratified 2026-07-01) — the single
# vocabulary across every Haffey tool; no tool defines its own set. The counted
# set for convergence is {BLOCKING, MATERIAL}: the two tiers that hold a change
# from landing. COSMETIC and POSITIVE never count and never block. POSITIVE is a
# valid tier but is unused by the dummy case. (design/ledger-schema.md §Severity)
DEFAULT_COUNTED_SEVERITIES: tuple[Severity, ...] = ("BLOCKING", "MATERIAL")


@dataclass
class CitedAuthority:
    """A finding's mandatory citation of authority.

    Attributes:
        kind: One of the four authority kinds.
        ref: A non-empty reference — named artifact + locus, quoted
            design-intent, target+locus in conflict, or named defect.
    """

    kind: AuthorityKind
    ref: str


@dataclass
class Finding:
    """A single finding record on the ledger.

    `id` is stable across passes (see identity.py). Fields are grouped by who
    sets them: reviewer (source..cited_authority), admission (id, pass_raised,
    recurrence_count), arbiter (classification, authority_locus), and
    author/router (status, pass_closed, resolution_note).
    """

    source: Source
    altitude: Altitude
    severity: Severity
    target: list[str]
    locus: str
    claim: str
    cited_authority: CitedAuthority | None
    id: str = ""
    classification: Classification = "unclassified"
    authority_locus: str | None = None
    status: Status = "open"
    pass_raised: int = 0
    pass_closed: int | None = None
    recurrence_count: int = 0
    resolution_note: str | None = None


@dataclass
class PassRecord:
    """Per-pass snapshot.

    Attributes:
        pass_number: Monotonic pass counter.
        open_cbm_count: Open counted-severity findings at routing time
            (post-admission, post-arbiter, pre-author) — the identical value the
            router reads for its convergence check. One value, no drift. It is
            the plateau signal.
        agents_run: Which agents executed this pass.
        timestamp: ISO-8601 logical timestamp (injected clock; does not affect
            any gate outcome).
    """

    pass_number: int
    open_cbm_count: int
    agents_run: list[str]
    timestamp: str


@dataclass
class DocChange:
    """A document-state change the author recorded in dry mode.

    The author-stub contract requires the fix's state change be recorded *in the
    ledger* (nothing is applied to a real document), so the coherence stub can
    react to it. The schema table did not enumerate a location for this, so the
    harness carries it here as an explicit, in-ledger change log.

    Attributes:
        doc: The document id the (proposed) fix changed.
        pass_number: The pass in which the change was recorded.
    """

    doc: str
    pass_number: int


@dataclass
class LedgerHeader:
    """Ledger header / run parameters."""

    set: list[str]
    counted_severities: list[Severity]
    plateau_N: int = 3
    mode: Mode = "dry"


@dataclass
class Ledger:
    """The whole ledger: header + findings + passes + (harness) doc changes."""

    header: LedgerHeader
    findings: list[Finding] = field(default_factory=list)
    passes: list[PassRecord] = field(default_factory=list)
    doc_changes: list[DocChange] = field(default_factory=list)

    def find_by_id(self, finding_id: str) -> Finding | None:
        """Return the finding with `finding_id`, or None if absent."""
        for finding in self.findings:
            if finding.id == finding_id:
                return finding
        return None

    def doc_changed_in_pass(self, doc: str, pass_number: int) -> bool:
        """Whether `doc` was recorded changed in exactly `pass_number`."""
        return any(
            change.doc == doc and change.pass_number == pass_number
            for change in self.doc_changes
        )


# --- persistence: fresh-fetch per agent --------------------------------------


def _finding_from_dict(data: dict) -> Finding:
    """Rehydrate a Finding, reconstructing its nested CitedAuthority."""
    payload = dict(data)
    raw_authority = payload.pop("cited_authority", None)
    authority = CitedAuthority(**raw_authority) if raw_authority else None
    return Finding(cited_authority=authority, **payload)


def _ledger_from_dict(data: dict) -> Ledger:
    """Rehydrate a Ledger from its JSON dict form."""
    return Ledger(
        header=LedgerHeader(**data["header"]),
        findings=[_finding_from_dict(f) for f in data.get("findings", [])],
        passes=[PassRecord(**p) for p in data.get("passes", [])],
        doc_changes=[DocChange(**c) for c in data.get("doc_changes", [])],
    )


class LedgerStore:
    """File-backed ledger store.

    Every agent action reads the ledger fresh via `load()` and persists via
    `save()`. Backing the store with a real file makes the "continuity lives in
    the ledger, not in any agent's context" invariant concrete and testable —
    nothing is threaded through in-memory between agents.
    """

    def __init__(self, path: str | Path) -> None:
        """Bind the store to a JSON file path (not required to exist yet)."""
        self._path = Path(path)

    def exists(self) -> bool:
        """Whether the backing file is present."""
        return self._path.exists()

    def load(self) -> Ledger:
        """Read and rehydrate the ledger from disk (a fresh fetch)."""
        with self._path.open("r", encoding="utf-8") as handle:
            return _ledger_from_dict(json.load(handle))

    def save(self, ledger: Ledger) -> None:
        """Serialize the ledger to disk as JSON."""
        with self._path.open("w", encoding="utf-8") as handle:
            json.dump(asdict(ledger), handle, indent=2, sort_keys=False)
