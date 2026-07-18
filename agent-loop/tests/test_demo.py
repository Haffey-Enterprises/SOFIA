# Module: tests.test_demo
# Purpose: Cover the human-facing demo runner and confirm it reports every
#          scenario's expected exit.
# Scope:   Over demo.run_all.

from agent_loop.demo import main, run_all


def test_run_all_reports_every_scenario_exit(tmp_path) -> None:
    # Act
    lines = run_all(tmp_path)

    # Assert: one line per scenario, each carrying its expected exit.
    joined = "\n".join(lines)
    assert len(lines) == 6
    assert "S1: CONVERGED" in joined
    assert "S2: HALT_DECISION (decision-bearing)" in joined
    assert "S2b: HALT_DECISION (decision-bearing)" in joined
    assert "S3: HALT_DECISION (oscillation)" in joined
    # RBT-69 Piece 3: S3b's plateau-without-recurrence is now `non-convergence`.
    assert "S3b: HALT_DECISION (non-convergence)" in joined
    assert "S4: CONVERGED" in joined


def test_main_prints_a_summary_for_every_scenario(capsys) -> None:
    # Act
    main()

    # Assert
    out = capsys.readouterr().out
    assert out.count("\n") == 6
    assert "S1: CONVERGED" in out
