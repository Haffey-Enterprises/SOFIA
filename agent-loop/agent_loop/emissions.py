# Module: agent_loop.emissions
# Purpose: Raw-emission capture (run-prep.contract.md §7, amended 2026-07-02).
#          Every LLM response body — reviewer and arbiter, parse success or
#          failure — is written verbatim to disk BEFORE any parsing, so a
#          parse-drop storm is diagnosable after the fact (run-003 discarded all
#          first-run output undiagnosably). Files are named
#          pass<NN>-<site>-<seq>.txt; `seq` is a per-pass, per-site call counter
#          (the arbiter makes multiple calls per pass).
# Scope:   Filesystem write + naming/seq bookkeeping. No LLM, no parsing.

from __future__ import annotations

from pathlib import Path


class EmissionCapture:
    """Writes raw LLM response bodies to a run's `emissions/` folder.

    `current_pass` is set by the runner's reviewers (which know the pass number)
    before each emit; the arbiter — which runs after the reviewers within the
    same pass and cannot take a pass number through its frozen port — writes
    under that same `current_pass`. `last_path` records the most recent file per
    site so the parse seam can reference it on a drop.
    """

    def __init__(self, emissions_dir: str | Path) -> None:
        """Create the emissions folder and initialise bookkeeping."""
        self._dir = Path(emissions_dir)
        self._dir.mkdir(parents=True, exist_ok=True)
        self._seq: dict[tuple[int, str], int] = {}
        self.current_pass: int = 0
        self.last_path: dict[str, str] = {}

    def write(self, site: str, raw: str) -> str:
        """Write one raw emission verbatim; return its path.

        Args:
            site: The call-site label (`antagonist-LAA` … `coherence`, `arbiter`).
            raw: The verbatim response body (before any fence-strip or parse).

        Returns:
            The written file path as a string.
        """
        key = (self.current_pass, site)
        seq = self._seq.get(key, 0) + 1
        self._seq[key] = seq
        path = self._dir / f"pass{self.current_pass:02d}-{site}-{seq}.txt"
        path.write_text(raw, encoding="utf-8")
        self.last_path[site] = str(path)
        return str(path)
