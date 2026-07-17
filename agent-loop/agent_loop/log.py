# Module: agent_loop.log
# Purpose: Structured, in-process action log. In dry mode the runner *proposes*
#          resolutions and escalations and *drops* out-of-scope findings; each
#          intended action must be observable (a silent drop is
#          indistinguishable from a bug). Events are typed records, not printed
#          strings, so tests assert on them directly.
# Scope:   No external logging sink; a single-process deterministic harness does
#          not use structlog/correlation-ids (misfit with the service
#          conventions, stated deliberately). render() emits JSON lines for a
#          human reading a run.

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable, Literal

EventKind = Literal[
    "admitted",  # new finding entered the ledger
    "reopened",  # a closed id was re-admitted open (recurrence signal)
    "dedup_open",  # emitted id already open — no new record
    "dropped",  # admission gate rejected an out-of-scope finding
    "parse_dropped",  # emission-parsing seam rejected a malformed emission (§7)
    "coherence_skip",  # runner did not schedule the coherence sweep this pass (§6)
    "classified",  # arbiter set a finding's classification
    "proposed_resolution",  # author stub proposed a fix (dry — nothing applied)
    "proposed_escalation",  # router proposed a ticket (dry — nothing opened)
    "author_edit",  # real author conformed a locus in the run's document copy (§9)
    "author_refused",  # real author declined: the authority does not determine the fix
    "author_anchor_fail",  # an edit's anchor did not match exactly once — escalated
    "author_unresolved",  # the finding's target or named authority did not resolve
    "llm_call",  # a real LLM call completed (provenance/cost — run-prep §7)
    "llm_retry",  # a real LLM call was retried (transport, content, or reviewer re-draw)
    "hat_null",  # a reviewer re-draw was empty a second time — recorded, run continues (RBT-49 Item 2)
    "run_aborted",  # a run aborted on the run path; reason logged before the raise (§7)
    "converged",
    "continue",
    "halt",
]


@dataclass
class LogEvent:
    """One structured event in a run.

    Attributes:
        kind: The event category.
        detail: Event-specific fields (finding id, reason, payload ids, etc.).
    """

    kind: EventKind
    detail: dict[str, object]


@dataclass
class ActionLog:
    """Ordered collector of run events, with an optional live sink.

    Attributes:
        events: The in-memory event list — unchanged for every existing
            consumer.
        sink: An optional callable invoked with each event as it is emitted
            (run-prep §7 live-log stream). Default None keeps behaviour
            identical to the skeleton; a not-None sink is a purely additive
            side channel that never affects the in-memory list.
    """

    events: list[LogEvent] = field(default_factory=list)
    sink: Callable[[LogEvent], None] | None = None

    def emit(self, kind: EventKind, **detail: object) -> None:
        """Append a structured event and stream it to the sink if present."""
        event = LogEvent(kind=kind, detail=detail)
        self.events.append(event)
        if self.sink is not None:
            self.sink(event)

    def of_kind(self, kind: EventKind) -> list[LogEvent]:
        """Return events of a single kind, in order."""
        return [event for event in self.events if event.kind == kind]

    def render(self) -> str:
        """Render the log as JSON lines for a human reading the run."""
        return "\n".join(_event_to_json(event) for event in self.events)


def _event_to_json(event: LogEvent) -> str:
    """Serialize one event to a single JSON line."""
    return json.dumps({"kind": event.kind, **event.detail})


class JsonlFileSink:
    """Append-per-event, flushed live sink to a `.jsonl` file (run-prep §7).

    Each emitted event is written as one JSON line and flushed immediately, so
    the attended run can be tailed live (`tail -f`). The file handle stays open
    for the run's duration; call `close()` when the run ends.
    """

    def __init__(self, path: str | Path) -> None:
        """Open the sink file for appending (creating parent dirs as needed)."""
        self._path = Path(path)
        self._path.parent.mkdir(parents=True, exist_ok=True)
        self._handle = self._path.open("a", encoding="utf-8")

    def __call__(self, event: LogEvent) -> None:
        """Write one event as a flushed JSON line."""
        self._handle.write(_event_to_json(event) + "\n")
        self._handle.flush()

    def close(self) -> None:
        """Close the underlying file handle."""
        self._handle.close()
