# Module: tests.test_gates
# Purpose: Specify the three pure mechanical gates — counter, oscillation
#          detector (both triggers), router (three exits, precedence). No LLM
#          input here except the arbiter's per-finding classification, read as
#          data. These tests pin the ratified guarantee: the loop can only
#          count, never *decide* it is done.
# Scope:   Unit tests over gates.* against hand-built ledgers.

from agent_loop.gates import (
    converged_by_count,
    open_cbm,
    oscillating,
    plateau,
    recurrence,
    route,
)
from agent_loop.ledger import (
    CitedAuthority,
    Finding,
    Ledger,
    LedgerHeader,
    PassRecord,
)


def _header(plateau_n: int = 3) -> LedgerHeader:
    return LedgerHeader(
        set=["DOC-A", "DOC-B"],
        counted_severities=["BLOCKING", "MATERIAL"],
        plateau_N=plateau_n,
    )


def _finding(fid: str, **overrides: object) -> Finding:
    base: dict[str, object] = dict(
        source="antagonist-stub",
        altitude="LAA",
        severity="MATERIAL",
        target=["DOC-A"],
        locus="l",
        claim=f"claim-{fid}",
        cited_authority=CitedAuthority(kind="canonical", ref="AUTH-1"),
        id=fid,
        classification="resolvable",
        authority_locus="AUTH-1 §2",
        status="open",
    )
    base.update(overrides)
    return Finding(**base)  # type: ignore[arg-type]


def _passes(counts: list[int]) -> list[PassRecord]:
    return [
        PassRecord(pass_number=i + 1, open_cbm_count=c, agents_run=[], timestamp="t")
        for i, c in enumerate(counts)
    ]


# --- counter -----------------------------------------------------------------


def test_open_cbm_counts_only_open_counted_severities() -> None:
    ledger = Ledger(
        header=_header(),
        findings=[
            _finding("a", severity="MATERIAL", status="open"),
            _finding("b", severity="BLOCKING", status="open"),
            _finding("c", severity="COSMETIC", status="open"),  # not counted
            _finding("d", severity="MATERIAL", status="closed"),  # not open
        ],
    )
    assert open_cbm(ledger) == 2


def test_converged_by_count_true_only_when_zero_open_counted() -> None:
    empty = Ledger(header=_header())
    assert converged_by_count(empty) is True

    with_open = Ledger(header=_header(), findings=[_finding("a")])
    assert converged_by_count(with_open) is False


# --- oscillation: recurrence -------------------------------------------------


def test_recurrence_trips_when_open_finding_has_recurred() -> None:
    ledger = Ledger(
        header=_header(),
        findings=[_finding("a", status="open", recurrence_count=1)],
    )
    assert recurrence(ledger) is True


def test_recurrence_ignores_closed_recurred_findings() -> None:
    ledger = Ledger(
        header=_header(),
        findings=[_finding("a", status="closed", recurrence_count=2)],
    )
    assert recurrence(ledger) is False


# --- oscillation: plateau ----------------------------------------------------


def test_plateau_trips_when_flat_and_positive_over_window() -> None:
    # plateau_N=3 → needs plateau_N+1 = 4 passes, all >= (never strictly down).
    ledger = Ledger(
        header=_header(plateau_n=3),
        findings=[_finding("a"), _finding("b")],  # open_cbm == 2 > 0
        passes=_passes([2, 2, 2, 2]),
    )
    assert plateau(ledger) is True


def test_plateau_does_not_trip_before_window_is_full() -> None:
    ledger = Ledger(
        header=_header(plateau_n=3),
        findings=[_finding("a"), _finding("b")],
        passes=_passes([2, 2, 2]),  # only 3 passes
    )
    assert plateau(ledger) is False


def test_plateau_does_not_trip_when_count_strictly_decreased_in_window() -> None:
    ledger = Ledger(
        header=_header(plateau_n=3),
        findings=[_finding("a"), _finding("b")],
        passes=_passes([2, 2, 1, 2]),  # a strict decrease exists
    )
    assert plateau(ledger) is False


def test_plateau_does_not_trip_when_no_open_counted_findings() -> None:
    ledger = Ledger(
        header=_header(plateau_n=3),
        findings=[_finding("a", status="closed")],  # open_cbm == 0
        passes=_passes([0, 0, 0, 0]),
    )
    assert plateau(ledger) is False


def test_plateau_trips_when_count_diverges_across_window() -> None:
    # Characterization (design review): the non-decreasing rule includes strict
    # DIVERGENCE, not just a flat line. A rising open_cbm_count ([2,3,4,5]) has
    # no strict decrease, so the fixes are still not converging → plateau trips.
    # Pins the rising branch of the >= comparison.
    ledger = Ledger(
        header=_header(plateau_n=3),
        findings=[_finding("a"), _finding("b")],  # open_cbm == 2 > 0
        passes=_passes([2, 3, 4, 5]),
    )
    assert plateau(ledger) is True


def test_oscillating_is_disjunction_of_recurrence_and_plateau() -> None:
    only_recurrence = Ledger(
        header=_header(),
        findings=[_finding("a", recurrence_count=1)],
    )
    assert oscillating(only_recurrence) is True


# --- router: three exits, precedence -----------------------------------------


def test_router_oscillation_takes_precedence_over_decision_bearing() -> None:
    ledger = Ledger(
        header=_header(),
        findings=[
            _finding("a", recurrence_count=1),  # oscillation
            _finding("b", classification="decision-bearing"),  # would also halt
        ],
    )
    exit_ = route(ledger)
    assert exit_.kind == "HALT_DECISION"
    assert exit_.reason == "oscillation"
    assert [f.id for f in exit_.payload] == ["a"]  # trading id is the payload


def test_router_decision_bearing_halts_even_when_count_is_zero() -> None:
    # S2b at the unit level: a COSMETIC (uncounted) decision-bearing finding.
    ledger = Ledger(
        header=_header(),
        findings=[
            _finding("b", severity="COSMETIC", classification="decision-bearing"),
        ],
    )
    assert open_cbm(ledger) == 0
    exit_ = route(ledger)
    assert exit_.kind == "HALT_DECISION"
    assert exit_.reason == "decision-bearing"
    assert [f.id for f in exit_.payload] == ["b"]


def test_router_converged_when_no_open_no_decision_not_oscillating() -> None:
    ledger = Ledger(header=_header(), findings=[_finding("a", status="closed")])
    assert route(ledger).kind == "CONVERGED"


def test_router_continue_when_open_resolvable_and_no_other_trigger() -> None:
    ledger = Ledger(header=_header(), findings=[_finding("a", classification="resolvable")])
    assert route(ledger).kind == "CONTINUE"


def test_router_plateau_without_recurrence_is_non_convergence_not_oscillation() -> None:
    # RBT-69 Piece 3: a flat, positive open_cbm with NO reopen is accumulation, not
    # trade — it now halts honestly as `non-convergence` (was mislabeled
    # `oscillation`). All findings here are resolvable (no open decision-bearing),
    # so the payload falls back to the plateaued open counted set, and the context
    # line is set.
    ledger = Ledger(
        header=_header(plateau_n=3),
        findings=[_finding("a"), _finding("b")],
        passes=_passes([2, 2, 2, 2]),
    )
    exit_ = route(ledger)
    assert exit_.kind == "HALT_DECISION"
    assert exit_.reason == "non-convergence"
    assert {f.id for f in exit_.payload} == {"a", "b"}
    assert exit_.context is not None
    assert "open_cbm plateaued at 2" in exit_.context


# --- router: open-resolvable outranks the decision-bearing halt (RBT-67) ------
#
# After run-026: a lone COSMETIC, arbiter-variance decision-bearing finding
# tripped HALT_DECISION and preempted the author from firing on 21 open
# resolvables. The author only ever edits resolvable findings and never touches
# a decision-bearing one, so no decision-bearing finding should block it. The
# reorder makes an open resolvable outrank the decision halt; the invariants
# (convergence needs zero open decisions; oscillation still wins) hold.


def test_router_continue_when_open_resolvable_and_open_decision_bearing() -> None:
    # The run-026 shape at the unit level: resolvable work AND an open decision.
    # CONTINUE so the author can fire; the decision-bearing finding is recorded
    # and surfaced later, not dropped.
    ledger = Ledger(
        header=_header(),
        findings=[
            _finding("r", classification="resolvable"),
            _finding("d", severity="COSMETIC", classification="decision-bearing"),
        ],
    )
    exit_ = route(ledger)
    assert exit_.kind == "CONTINUE"
    assert exit_.payload == []  # CONTINUE surfaces nothing to the operator
    # The decision-bearing finding is untouched on the ledger — still open, still
    # decision-bearing — so a later pass surfaces it once resolvables are gone.
    d = next(f for f in ledger.findings if f.id == "d")
    assert d.status == "open" and d.classification == "decision-bearing"


def test_router_halt_decision_when_resolvables_exhausted() -> None:
    # Resolvable closed (author acted a prior pass); the open decision remains →
    # HALT_DECISION with exactly the decision-bearing findings in the payload.
    ledger = Ledger(
        header=_header(),
        findings=[
            _finding("r", classification="resolvable", status="closed"),
            _finding("d", classification="decision-bearing"),
        ],
    )
    exit_ = route(ledger)
    assert exit_.kind == "HALT_DECISION"
    assert exit_.reason == "decision-bearing"
    assert [f.id for f in exit_.payload] == ["d"]


def test_router_oscillating_resolvable_halts_over_continue() -> None:
    # The anti-infinite-loop backstop is intact after the reorder: a resolvable
    # that reopens (recurrence >= threshold) HALTs even though, absent the guard,
    # its open-resolvable status would route CONTINUE.
    ledger = Ledger(
        header=_header(),
        findings=[_finding("a", classification="resolvable", recurrence_count=1)],
    )
    exit_ = route(ledger)
    assert exit_.kind == "HALT_DECISION"
    assert exit_.reason == "oscillation"
    assert [f.id for f in exit_.payload] == ["a"]


def test_router_converged_only_when_nothing_open_and_never_with_open_decision() -> None:
    # Nothing open → CONVERGED.
    converged = Ledger(header=_header(), findings=[_finding("a", status="closed")])
    assert route(converged).kind == "CONVERGED"
    # CONVERGED is never returned while a decision-bearing finding is open, even
    # with every counted finding resolved (open_cbm == 0 via COSMETIC).
    with_open_decision = Ledger(
        header=_header(),
        findings=[
            _finding("a", status="closed"),
            _finding("d", severity="COSMETIC", classification="decision-bearing"),
        ],
    )
    assert open_cbm(with_open_decision) == 0
    assert route(with_open_decision).kind != "CONVERGED"
    assert route(with_open_decision).kind == "HALT_DECISION"


def test_router_open_cosmetic_resolvable_continues_severity_blind() -> None:
    # An open COSMETIC (uncounted) resolvable must still route CONTINUE so the
    # severity-blind author fixes it — open_cbm == 0 alone must not converge past
    # open resolvable work.
    ledger = Ledger(
        header=_header(),
        findings=[_finding("a", severity="COSMETIC", classification="resolvable")],
    )
    assert open_cbm(ledger) == 0
    assert route(ledger).kind == "CONTINUE"


def test_router_open_counted_unclassified_continues_not_converged() -> None:
    # Defensive branch: an open counted finding that is neither resolvable nor
    # decision-bearing (should not occur post-arbiter) CONTINUEs rather than
    # falsely converging — the CONVERGED conjunction stays honest.
    ledger = Ledger(
        header=_header(),
        findings=[_finding("u", classification="unclassified")],
    )
    assert open_cbm(ledger) == 1
    assert route(ledger).kind == "CONTINUE"


# --- RBT-69 Piece 3 clean-stop suite (S1–S5) ---------------------------------
#
# The non-recurrence plateau is split out of `oscillation` into `non-convergence`.
# Precedence unchanged: [recurrence-oscillation | non-convergence-plateau] →
# open-resolvable (CONTINUE) → decision-bearing (HALT) → CONVERGED.


def test_s1_recurrence_still_halts_as_oscillation() -> None:
    # S1 — a reopened finding is real trade → oscillation, payload = recurring ids.
    # The recurrence branch is untouched by the split.
    ledger = Ledger(
        header=_header(),
        findings=[_finding("a", recurrence_count=1)],
    )
    exit_ = route(ledger)
    assert exit_.kind == "HALT_DECISION"
    assert exit_.reason == "oscillation"
    assert [f.id for f in exit_.payload] == ["a"]
    assert exit_.context is None  # context line is a non-convergence-only affordance


def test_s2_accumulation_is_non_convergence_with_decisions_unbundled() -> None:
    # S2 (run-028-shaped, unit level) — a monotonic open_cbm climb with NO reopen
    # and an open decision-bearing backlog dry mode never drains. Plateau (no
    # strict decrease) trips at the top precedence → non-convergence, NOT
    # oscillation. Payload = the open decision-bearing findings, unbundled; the
    # context line records the non-exhausted surface.
    ledger = Ledger(
        header=_header(plateau_n=3),
        findings=[
            # Counted, open, still-accumulating resolvable surface (not exhausted).
            _finding("r1", classification="resolvable"),
            _finding("r2", classification="resolvable"),
            # The decision-bearing backlog the operator must rule.
            _finding("d1", classification="decision-bearing", authority_locus=None),
            _finding("d2", classification="decision-bearing", authority_locus=None),
        ],
        passes=_passes([18, 24, 41, 55]),  # the run-028 shape: climbing, zero recurrence
    )
    assert all(f.recurrence_count == 0 for f in ledger.findings)
    exit_ = route(ledger)
    assert exit_.kind == "HALT_DECISION"
    assert exit_.reason == "non-convergence"
    assert {f.id for f in exit_.payload} == {"d1", "d2"}  # decisions unbundled
    assert exit_.context is not None
    assert "resolvable surface was not exhausted" in exit_.context
    assert "no finding recurred" in exit_.context


def test_s3_clean_decision_halt_unchanged() -> None:
    # S3 — resolvables exhausted (closed a prior pass), an open decision remains,
    # no plateau → the run-025/026 clean decision-bearing halt, unchanged.
    ledger = Ledger(
        header=_header(),
        findings=[
            _finding("r", classification="resolvable", status="closed"),
            _finding("d", classification="decision-bearing"),
        ],
    )
    exit_ = route(ledger)
    assert exit_.kind == "HALT_DECISION"
    assert exit_.reason == "decision-bearing"
    assert [f.id for f in exit_.payload] == ["d"]
    assert exit_.context is None


def test_s4_converged_unchanged() -> None:
    # S4 — the CONVERGED conjunction is untouched: open_cbm == 0, no open
    # decision-bearing, and not oscillating/non-converging.
    ledger = Ledger(header=_header(), findings=[_finding("a", status="closed")])
    exit_ = route(ledger)
    assert exit_.kind == "CONVERGED"
    assert exit_.reason is None


def test_s5_escalated_resolvable_surfaces_never_dropped_never_status_escalated() -> None:
    # S5 — the author refuses a resolvable → `_escalate` re-classifies it
    # decision-bearing with status LEFT open (never status="escalated", which would
    # drop it out of open_cbm and the router's open-only view). It then surfaces —
    # here in the non-convergence payload — and is never dropped.
    from agent_loop.author import _escalate

    refused = _finding("x", classification="resolvable")
    _escalate(refused)
    assert refused.status == "open"  # NOT "escalated"
    assert refused.classification == "decision-bearing"

    # Composed into a plateau: the escalated finding is an open decision-bearing at
    # a non-convergence plateau → it is in the payload, still open.
    ledger = Ledger(
        header=_header(plateau_n=3),
        findings=[refused, _finding("r", classification="resolvable")],
        passes=_passes([2, 2, 2, 2]),
    )
    exit_ = route(ledger)
    assert exit_.kind == "HALT_DECISION"
    assert exit_.reason == "non-convergence"
    assert "x" in {f.id for f in exit_.payload}
    assert refused.status == "open"
