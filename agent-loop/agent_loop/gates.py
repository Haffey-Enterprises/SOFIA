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
        reason: For HALT_DECISION, 'oscillation', 'non-convergence', or
            'decision-bearing'; else None.
        payload: The findings carried to the operator (unbundled, one
            escalation each on HALT).
        context: A single human-readable context line, set only on the
            'non-convergence' disposition (RBT-69 Piece 3) — records that the
            resolvable surface was not exhausted and the plateaued open_cbm value.
            None on every other exit.
    """

    kind: ExitKind
    reason: str | None = None
    payload: list[Finding] = field(default_factory=list)
    context: str | None = None


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


def _open_resolvables(ledger: Ledger) -> list[Finding]:
    """Open findings the author can act on this pass (classification 'resolvable').

    The author edits only `resolvable` findings and never touches a
    decision-bearing one, so these — and only these — are the work a CONTINUE
    hands it. Mirrors `author._open_resolvable`; the router keeps its own copy so
    CONTINUE stays a pure gate concern with no import of the write path.
    """
    return [
        finding
        for finding in ledger.findings
        if finding.status == "open" and finding.classification == "resolvable"
    ]


def _non_convergence_context(ledger: Ledger) -> str:
    """The context line for a non-convergence plateau halt (RBT-69 Piece 3).

    Records the two facts that distinguish accumulation from oscillation: the
    plateaued `open_cbm` value, and that the resolvable surface was not exhausted
    (net-new findings still arriving faster than the author closes them) — no
    recurrence, so it is a pile of decisions to rule, not two altitudes trading.
    """
    return (
        f"non-convergence: open_cbm plateaued at {open_cbm(ledger)} over the last "
        f"{ledger.header.plateau_N + 1} passes with "
        f"{len(_open_resolvables(ledger))} open resolvable finding(s) still on the "
        "ledger — the resolvable surface was not exhausted (net-new still "
        "arriving), and no finding recurred (accumulation, not trade)"
    )


# --- 3. router (exactly three exits; precedence top-to-bottom) ---------------


def route(ledger: Ledger) -> RouterExit:
    """Compose the gates into exactly three exits; first match wins.

    Precedence (RBT-69 Piece 3): `[recurrence-oscillation | non-convergence-
    plateau] → open-resolvable (CONTINUE) → decision-bearing (HALT) → CONVERGED`.
    The top backstop position is unchanged; only its disposition splits — a
    non-decreasing open set now halts honestly as `non-convergence` instead of
    masquerading as `oscillation`.

    The author edits only `resolvable` findings and never touches a
    decision-bearing one, so those two concerns are independent: an open decision
    must not preempt the author from the resolvable work it can still do
    (RBT-67, after run-026 — one COSMETIC decision-bearing finding halted the
    loop over 21 real resolvables the author never got to). So an open resolvable
    outranks the decision-bearing halt: the loop CONTINUEs, the author fires on
    the resolvables, and the decision-bearing findings stay open on the ledger —
    recorded, never dropped — surfacing once the resolvables are exhausted.

    Two guarantees the reorder preserves:
      - The oscillation/non-convergence backstop still wins over everything — a
        `resolvable` that keeps reopening is trading, not converging (oscillation);
        an `open_cbm` that stops falling is accumulating (non-convergence). Either
        halts (the anti-infinite-loop backstop; plateau_N / max_passes unchanged).
      - CONVERGED is still unreachable while any decision-bearing finding is open
        (the decision-bearing branch precedes the converged one) — the change
        lets the author work while decisions wait, it does not let the run finish
        with a decision open. CONVERGED remains the mechanical conjunction:
        open_cbm == 0 AND no open decision-bearing AND not oscillating/non-converging.
    """
    # 1a. Recurrence backstop → oscillation. A closed finding that came back is
    #     real two-altitude trading; the recurring ids are the payload. Unchanged.
    if recurrence(ledger):
        return RouterExit(
            kind="HALT_DECISION", reason="oscillation", payload=_recurring_findings(ledger)
        )

    # 1b. Plateau without recurrence → non-convergence (RBT-69 Piece 3). open_cbm
    #     stopped strictly decreasing while positive: accumulation, no trade —
    #     "operator, there is a pile of decisions to rule and the surface is not
    #     exhausted." The honest disposition, split out of the oscillation label it
    #     was mislabeled under. Payload: the open decision-bearing findings the
    #     operator must rule, unbundled; falling back to the plateaued open counted
    #     findings when no decision is open (pure resolvable non-progress). A single
    #     context line records the non-exhausted resolvable surface + plateaued
    #     open_cbm. Only meaningful after Piece 1 — before the identity fix,
    #     open_cbm climbed on re-wording inflation and plateau fired on noise.
    if plateau(ledger):
        open_decisions = _open_decisions(ledger)
        payload = open_decisions if open_decisions else _plateaued_findings(ledger)
        return RouterExit(
            kind="HALT_DECISION",
            reason="non-convergence",
            payload=payload,
            context=_non_convergence_context(ledger),
        )

    # 2. Any open resolvable the author can act on → CONTINUE. Now outranks the
    #    decision-bearing halt; the open decisions ride along on the ledger.
    if _open_resolvables(ledger):
        return RouterExit(kind="CONTINUE")

    # 3. Resolvables exhausted; open decision-bearing findings remain → surface
    #    only those, unbundled (severity-independent — even a COSMETIC decision
    #    halts). Precedes CONVERGED, so a run never ends with a decision open.
    open_decisions = _open_decisions(ledger)
    if open_decisions:
        return RouterExit(
            kind="HALT_DECISION", reason="decision-bearing", payload=open_decisions
        )

    # 4. Nothing the loop can act on and no decision pending → CONVERGED, guarded
    #    on the counter. A leftover open counted finding that is neither
    #    resolvable nor decision-bearing (should not occur post-arbiter)
    #    CONTINUEs rather than falsely converging.
    if converged_by_count(ledger):
        return RouterExit(kind="CONVERGED")
    return RouterExit(kind="CONTINUE")
