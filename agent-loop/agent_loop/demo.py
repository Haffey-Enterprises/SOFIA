# Module: agent_loop.demo
# Purpose: A human-facing dry-run of all dummy scenarios. Prints each scenario's
#          router exit and the structured action log (drops, classifications,
#          proposed resolutions, proposed escalations) so the dry-mode behavior
#          is observable — nothing is applied to a document, no ticket is opened.
# Scope:   Thin presentation over runner.run_scenario. No gate logic here.

from __future__ import annotations

import tempfile
from pathlib import Path

from agent_loop.gates import open_cbm
from agent_loop.ledger import LedgerStore
from agent_loop.runner import run_scenario
from agent_loop.scenarios import ALL_SCENARIOS


def run_all(workdir: str | Path) -> list[str]:
    """Run every scenario in a scratch dir and return per-scenario summary lines.

    Args:
        workdir: Directory to hold the per-scenario ledger files.

    Returns:
        One human-readable summary line per scenario (id → exit + pass count).
    """
    lines: list[str] = []
    for name, builder in ALL_SCENARIOS.items():
        store = LedgerStore(Path(workdir) / f"{name}.json")
        result = run_scenario(builder(), store)
        reason = f" ({result.exit.reason})" if result.exit.reason else ""
        remaining = open_cbm(result.ledger)
        lines.append(
            f"{name}: {result.exit.kind}{reason} in {result.passes_run} "
            f"pass(es); open_cbm={remaining}"
        )
    return lines


def main() -> None:
    """Print a dry-run summary of all scenarios to stdout."""
    with tempfile.TemporaryDirectory() as workdir:
        for line in run_all(workdir):
            print(line)


if __name__ == "__main__":  # pragma: no cover
    main()
