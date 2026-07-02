# Module: agent_loop.gates
# Purpose: The three pure mechanical gates — build step 2. NO LLM anywhere in
#          this file. The only LLM-derived input is each finding's arbiter
#          `classification`, computed upstream and read here as data. The design
#          intent: the loop must never be able to *decide* it has converged — it
#          can only count; the router composes booleans.
# Scope:   Pure functions over ledger state. No I/O.

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal

from agent_loop.ledger import Finding, Ledger

ExitKind = Literal["CONVERGED", "CONTINUE", "HALT_DECISION"]


@dataclass
class RouterExit:
    """A router decision.

    Attributes:
        kind: One of the exactly-three exits.
        reason: For HALT_DECISION, 'oscillation' or 'decision-bearing'; else
            None.
        payload: The findings carried to the operator (unbundled, one
            escalation each on HALT).
    """

    kind: ExitKind
    reason: str | None = None
    payload: list[Finding] = field(default_factory=list)


# --- 1. convergence counter --------------------------------------------------


def open_cbm(ledger: Ledger) -> int:
    """Count open findings whose severity is in the counted set. Dumb and total."""
    counted = set(ledger.header.counted_severities)
    return sum(
        1
        for finding in ledger.findings
        if finding.status == "open" and finding.severity in counted
    )


def converged_by_count(ledger: Ledger) -> bool:
    """True iff no open counted-severity findings remain."""
    return open_cbm(ledger) == 0


# --- 2. oscillation detector (two independent triggers) ----------------------


def recurrence(ledger: Ledger) -> bool:
    """True iff some currently-open finding has recurred (was closed, came back).

    A finding that was closed and returned is, by definition, not converging by
    fixing — it is trading. Trip.
    """
    return any(
        finding.status == "open" and finding.recurrence_count >= 1
        for finding in ledger.findings
    )


def plateau(ledger: Ledger) -> bool:
    """True iff the open counted-severity count has stopped falling while positive.

    Trips when open_cbm > 0, there are at least plateau_N + 1 passes, and over
    the last plateau_N + 1 pass snapshots there is no strict decrease (every
    consecutive pair is >=, never <). The fixes are chasing their own tail.
    """
    if open_cbm(ledger) == 0:
        return False
    window_len = ledger.header.plateau_N + 1
    if len(ledger.passes) < window_len:
        return False
    window = [record.open_cbm_count for record in ledger.passes[-window_len:]]
    return all(
        current >= previous for previous, current in zip(window, window[1:])
    )


def oscillating(ledger: Ledger) -> bool:
    """True iff either oscillation trigger fires."""
    return recurrence(ledger) or plateau(ledger)


# --- payload helpers ---------------------------------------------------------


def _recurring_findings(ledger: Ledger) -> list[Finding]:
    return [
        finding
        for finding in ledger.findings
        if finding.status == "open" and finding.recurrence_count >= 1
    ]


def _plateaued_findings(ledger: Ledger) -> list[Finding]:
    counted = set(ledger.header.counted_severities)
    return [
        finding
        for finding in ledger.findings
        if finding.status == "open" and finding.severity in counted
    ]


def _open_decisions(ledger: Ledger) -> list[Finding]:
    return [
        finding
        for finding in ledger.findings
        if finding.status == "open" and finding.classification == "decision-bearing"
    ]


# --- 3. router (exactly three exits; precedence top-to-bottom) ---------------


def route(ledger: Ledger) -> RouterExit:
    """Compose the gates into exactly three exits; first match wins.

    Precedence: oscillation → decision-bearing → converged → continue. A
    decision-bearing finding halts even when open_cbm == 0 (severity-independent):
    silently auto-resolving or dropping a discovered decision is the
    manufactured-alignment failure the whole loop exists to prevent. The
    CONVERGED exit is the mechanical conjunction: open_cbm == 0 AND no open
    decision-bearing AND not oscillating.
    """
    if oscillating(ledger):
        payload = (
            _recurring_findings(ledger)
            if recurrence(ledger)
            else _plateaued_findings(ledger)
        )
        return RouterExit(kind="HALT_DECISION", reason="oscillation", payload=payload)

    open_decisions = _open_decisions(ledger)
    if open_decisions:
        return RouterExit(
            kind="HALT_DECISION", reason="decision-bearing", payload=open_decisions
        )

    if converged_by_count(ledger):
        return RouterExit(kind="CONVERGED")

    return RouterExit(kind="CONTINUE")
