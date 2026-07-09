#!/usr/bin/env python3
# Tool: prep_run — supervised-run prep (RBT-52).
#
# What it does, in plain language: before a supervised design-review run, this
# tool builds the run's folder so the run reviews a FROZEN copy of the documents
# and authorities, not whatever happens to be in the working tree at run time.
# It resolves each document id to its file, copies those files into the run
# folder's documents/, copies the ratified authorities and design-intent into
# substrate/, and records the exact SHA-256 of every copied file. The runner
# later verifies those hashes and refuses to start if anything is missing or
# changed. Nothing here calls an LLM, the network, or git that would cost money
# or mutate state — it copies files and writes manifests, and that is all.
#
# Why the run folder and not the working tree: a review has to be reproducible
# from the run folder plus its manifests alone. If the runner re-read the working
# tree each pass, an edit mid-run would silently change what was reviewed. Prep
# freezes the bytes once; the run folder is the record.
#
# Usage:
#   scripts/prep_run.py <run-id> <doc-id> [<doc-id> ...] [--from-run <run-id>]
#                       [--draws <run-id> ...] [--sofia-root <path>]
#
# --from-run carries forward the substrate the runner cannot re-fetch (the
# bedrock templates/skills and the Notion vision block), asserting each carried
# file's hash against the prior draw's pin. --draws prepares several draws that
# differ only in run_id (the two-draw verification standard).
#
# Provenance: this tool is authored for RBT-52 and cited to that ticket alone.

from __future__ import annotations

import argparse
import subprocess
import sys
from datetime import date
from pathlib import Path

# scripts/ is not a package; make the agent-loop package importable.
_AGENT_LOOP = Path(__file__).resolve().parents[1] / "agent-loop"
sys.path.insert(0, str(_AGENT_LOOP))

from agent_loop.prep import prep_draws, prep_run  # noqa: E402


def _git_head(sofia_root: Path) -> str:
    """`git rev-parse HEAD` — the working-tree commit the snapshot was taken at."""
    completed = subprocess.run(
        ["git", "-C", str(sofia_root), "rev-parse", "HEAD"],
        capture_output=True,
        text=True,
        check=True,
    )
    return completed.stdout.strip()


def main(argv: list[str] | None = None) -> None:  # pragma: no cover
    """CLI entry: stamp HEAD SHA + retrieval date, then prepare the run folder(s)."""
    parser = argparse.ArgumentParser(
        description=(
            "Prepare a supervised-run folder: freeze the reviewed documents and "
            "substrate, with hashed provenance manifests."
        )
    )
    parser.add_argument("run_id")
    parser.add_argument("doc_ids", nargs="+", help="e.g. SDD-001")
    parser.add_argument("--from-run", default=None, help="prior draw to carry substrate forward from")
    parser.add_argument("--draws", nargs="+", default=None, help="run-ids for N draws (differ only in run_id)")
    parser.add_argument("--sofia-root", default=str(Path(__file__).resolve().parents[1]))
    args = parser.parse_args(argv)

    sofia_root = Path(args.sofia_root)
    runs_root = sofia_root / "agent-loop" / "runs"
    head_sha = _git_head(sofia_root)
    retrieved = date.today().isoformat()

    if args.draws:
        folders = prep_draws(
            args.draws, args.doc_ids, sofia_root=sofia_root, runs_root=runs_root,
            sofia_head_sha=head_sha, retrieved=retrieved, from_run=args.from_run,
        )
    else:
        folders = [
            prep_run(
                args.run_id, args.doc_ids, sofia_root=sofia_root, runs_root=runs_root,
                sofia_head_sha=head_sha, retrieved=retrieved, from_run=args.from_run,
            )
        ]
    for folder in folders:
        print(f"prepared {folder}")


if __name__ == "__main__":  # pragma: no cover
    main()
