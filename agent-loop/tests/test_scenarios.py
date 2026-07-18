# Module: tests.test_scenarios
# Purpose: The acceptance suite. S1, S2 (incl. S2b), S3 (incl. S3b), and S4 each
#          assert their expected router exit deterministically. The skeleton is
#          "done" only when all are green — and green on repeated runs (the
#          determinism guarantee). These tests drive the whole plumbing through
#          a real file-backed ledger (fresh-fetched each pass).
# Scope:   End-to-end over runner.run_scenario against the dummy-case fixtures.

import pytest

from agent_loop.gates import open_cbm
from agent_loop.ledger import LedgerStore
from agent_loop.runner import run_scenario
from agent_loop.scenarios import (
    scenario_s1,
    scenario_s2,
    scenario_s2b,
    scenario_s3,
    scenario_s3b,
    scenario_s4,
)


def _store(tmp_path, name: str) -> LedgerStore:
    return LedgerStore(tmp_path / f"{name}.json")


# --- S1 ----------------------------------------------------------------------


def test_s1_converges_in_three_passes(tmp_path) -> None:
    # Act
    result = run_scenario(scenario_s1(), _store(tmp_path, "s1"))

    # Assert: CONVERGED in exactly 3 passes; final open_cbm == 0.
    assert result.exit.kind == "CONVERGED"
    assert result.passes_run == 3
    assert open_cbm(result.ledger) == 0


def test_s1_p3_never_appears_before_pass_two(tmp_path) -> None:
    # Act
    result = run_scenario(scenario_s1(), _store(tmp_path, "s1b"))

    # Assert: the coherence finding P3 (locus p3-desync) is first raised on pass 2.
    p3 = next(f for f in result.ledger.findings if f.locus == "p3-desync")
    assert p3.pass_raised == 2


# --- S2 / S2b ----------------------------------------------------------------


def test_s2_halts_on_pass_one_with_one_unbundled_escalation(tmp_path) -> None:
    # Act
    result = run_scenario(scenario_s2(), _store(tmp_path, "s2"))

    # Assert: HALT_DECISION (decision-bearing) on pass 1, exactly one escalation.
    assert result.exit.kind == "HALT_DECISION"
    assert result.exit.reason == "decision-bearing"
    assert result.passes_run == 1
    assert len(result.log.of_kind("proposed_escalation")) == 1
    # And no fix was attempted on the decision-bearing finding.
    assert result.log.of_kind("proposed_resolution") == []
    p2 = result.ledger.findings[0]
    assert p2.status == "open"


def test_s2b_decision_bearing_halts_even_when_count_is_zero(tmp_path) -> None:
    # Act
    result = run_scenario(scenario_s2b(), _store(tmp_path, "s2b"))

    # Assert: convergence-by-count does not override a decision-bearing finding.
    assert open_cbm(result.ledger) == 0
    assert result.exit.kind == "HALT_DECISION"
    assert result.exit.reason == "decision-bearing"
    assert result.passes_run == 1


# --- S3 / S3b ----------------------------------------------------------------


def test_s3_recurrence_halts_at_the_reopen(tmp_path) -> None:
    # Act
    result = run_scenario(scenario_s3(), _store(tmp_path, "s3"))

    # Assert: HALT on oscillation no later than the reopen (pass 3), and the
    # payload carries the trading id — not a convergence claim.
    assert result.exit.kind == "HALT_DECISION"
    assert result.exit.reason == "oscillation"
    assert result.passes_run == 3
    payload_loci = {f.locus for f in result.exit.payload}
    assert "p5a" in payload_loci
    reopened = next(f for f in result.ledger.findings if f.locus == "p5a")
    assert reopened.recurrence_count == 1


def test_s3b_plateau_halts_as_non_convergence_at_plateau_n_plus_one(tmp_path) -> None:
    # Act
    result = run_scenario(scenario_s3b(), _store(tmp_path, "s3b"))

    # Assert: plateau trips at plateau_N + 1 = 4 passes; no same-id reopen. RBT-69
    # Piece 3 — a plateau WITHOUT recurrence is accumulation, not trade, so the
    # disposition is `non-convergence`, NOT `oscillation` (the one dummy scenario
    # whose label legitimately changed; asserted explicitly here).
    assert result.exit.kind == "HALT_DECISION"
    assert result.exit.reason == "non-convergence"
    assert result.passes_run == 4
    assert all(f.recurrence_count == 0 for f in result.ledger.findings)
    # The flat plateau signal: open_cbm_count held at 2 across the window.
    assert [p.open_cbm_count for p in result.ledger.passes] == [2, 2, 2, 2]
    # The churn findings are resolvable (no open decision-bearing) → payload falls
    # back to the plateaued open counted set, and the context line rode the halt.
    assert {f.id for f in result.exit.payload} == {
        f.id for f in result.ledger.findings if f.status == "open"
    }
    halt = result.log.of_kind("halt")[0]
    assert halt.detail["reason"] == "non-convergence"
    assert "open_cbm plateaued at 2" in halt.detail["context"]


# --- S4 ----------------------------------------------------------------------


def test_s4_preference_is_dropped_and_ledger_converges(tmp_path) -> None:
    # Act
    result = run_scenario(scenario_s4(), _store(tmp_path, "s4"))

    # Assert: P4 absent from the ledger, not counted, and the drop is observable.
    assert result.exit.kind == "CONVERGED"
    assert result.passes_run == 1
    assert result.ledger.findings == []
    drops = result.log.of_kind("dropped")
    assert len(drops) == 1
    assert drops[0].detail["finding_id"]  # a real dropped-finding log line exists


# --- determinism across repeated runs ----------------------------------------


@pytest.mark.parametrize(
    "builder,expected_kind,expected_reason,expected_passes",
    [
        (scenario_s1, "CONVERGED", None, 3),
        (scenario_s2, "HALT_DECISION", "decision-bearing", 1),
        (scenario_s2b, "HALT_DECISION", "decision-bearing", 1),
        (scenario_s3, "HALT_DECISION", "oscillation", 3),
        (scenario_s3b, "HALT_DECISION", "non-convergence", 4),
        (scenario_s4, "CONVERGED", None, 1),
    ],
)
def test_scenarios_are_deterministic_across_repeated_runs(
    tmp_path, builder, expected_kind, expected_reason, expected_passes
) -> None:
    # Act: run the same scenario several times on fresh stores.
    outcomes = []
    for i in range(5):
        result = run_scenario(builder(), _store(tmp_path, f"{builder.__name__}-{i}"))
        outcomes.append(
            (result.exit.kind, result.exit.reason, result.passes_run)
        )

    # Assert: identical exit every time.
    assert outcomes == [
        (expected_kind, expected_reason, expected_passes)
    ] * 5
