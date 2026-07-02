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
from typing import Literal

EventKind = Literal[
    "admitted",  # new finding entered the ledger
    "reopened",  # a closed id was re-admitted open (recurrence signal)
    "dedup_open",  # emitted id already open — no new record
    "dropped",  # admission gate rejected an out-of-scope finding
    "parse_dropped",  # emission-parsing seam rejected a malformed emission (§7)
    "coherence_skip",  # runner did not schedule the coherence sweep this pass (§6)
    "classified",  # arbiter set a finding's classification
    "proposed_resolution",  # author proposed a fix (dry — nothing applied)
    "proposed_escalation",  # router proposed a ticket (dry — nothing opened)
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
    """Ordered collector of run events."""

    events: list[LogEvent] = field(default_factory=list)

    def emit(self, kind: EventKind, **detail: object) -> None:
        """Append a structured event."""
        self.events.append(LogEvent(kind=kind, detail=detail))

    def of_kind(self, kind: EventKind) -> list[LogEvent]:
        """Return events of a single kind, in order."""
        return [event for event in self.events if event.kind == kind]

    def render(self) -> str:
        """Render the log as JSON lines for a human reading the run."""
        return "\n".join(
            json.dumps({"kind": event.kind, **event.detail}) for event in self.events
        )
