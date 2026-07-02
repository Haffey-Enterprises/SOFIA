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


def test_router_plateau_payload_is_open_counted_set() -> None:
    ledger = Ledger(
        header=_header(plateau_n=3),
        findings=[_finding("a"), _finding("b")],
        passes=_passes([2, 2, 2, 2]),
    )
    exit_ = route(ledger)
    assert exit_.kind == "HALT_DECISION"
    assert exit_.reason == "oscillation"
    assert {f.id for f in exit_.payload} == {"a", "b"}
