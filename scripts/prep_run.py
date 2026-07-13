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
# Which substrate recipe is used is selected by the reviewed doctype, read off
# the document id (SDD-001 -> the SDD recipe; DDR-004 -> the DDR recipe) — no
# flag to get wrong (RBT-57). An unknown doctype fails loud.
#
# Why the run folder and not the working tree: a review has to be reproducible
# from the run folder plus its manifests alone. If the runner re-read the working
# tree each pass, an edit mid-run would silently change what was reviewed. Prep
# freezes the bytes once; the run folder is the record.
#
# Usage:
#   scripts/prep_run.py <run-id> <doc-id> [<doc-id> ...] [--from-run <run-id>]
#                       [--draws <run-id> ...] [--sofia-root <path>]
#                       [--bedrock-cache-root <path>]
#                       [--accept-stale-authority <id> --reason <text>]...
#                       [--extra-canon <doc-id>]...
#
# --from-run carries forward the substrate the runner cannot re-fetch and that
# is not forward-verifiable (the Notion vision block), asserting each carried
# file's hash against the prior draw's pin. Bedrock authorities (RBT-54 F4) are
# NOT carried forward: they are sourced from the installed plugin cache
# (discovered from the plugin registry, or --bedrock-cache-root) and verified
# pin-vs-installed; a drifted cache fails loud unless sanctioned with
# --accept-stale-authority <id> --reason <text> (repeatable, order-matched).
# --draws prepares several draws that differ only in run_id (the two-draw
# verification standard).
#
# Provenance: this tool is authored for RBT-52 and cited to that ticket alone.

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from datetime import date
from pathlib import Path

# scripts/ is not a package; make the agent-loop package importable.
_AGENT_LOOP = Path(__file__).resolve().parents[1] / "agent-loop"
sys.path.insert(0, str(_AGENT_LOOP))

from agent_loop.prep import (  # noqa: E402
    SubstrateSpec,
    prep_draws,
    prep_run,
    resolve_document,
)


def _git_head(sofia_root: Path) -> str:
    """`git rev-parse HEAD` — the working-tree commit the snapshot was taken at."""
    completed = subprocess.run(
        ["git", "-C", str(sofia_root), "rev-parse", "HEAD"],
        capture_output=True,
        text=True,
        check=True,
    )
    return completed.stdout.strip()


def _resolve_bedrock_cache_root() -> Path:  # pragma: no cover
    """Discover the installed bedrock plugin cache root from Claude's plugin
    registry (`~/.claude/plugins/installed_plugins.json` ->
    plugins['bedrock@bedrock'][*].installPath — the version-pinned cache dir).
    Discovered, not hardcoded; fails loud if the plugin isn't installed, since
    the DDR recipe's F4 currency check has nothing to verify against."""
    config = Path.home() / ".claude" / "plugins" / "installed_plugins.json"
    if not config.is_file():
        raise SystemExit(f"bedrock plugin registry not found: {config}")
    data = json.loads(config.read_text(encoding="utf-8"))
    for entry in data.get("plugins", {}).get("bedrock@bedrock", []):
        path = Path(entry.get("installPath", ""))
        if path.is_dir():
            return path
    raise SystemExit(
        "bedrock plugin not installed or its cache root is unresolvable "
        "(no plugins['bedrock@bedrock'] installPath exists)"
    )


def main(argv: list[str] | None = None) -> None:  # pragma: no cover
    """CLI entry: stamp HEAD SHA + retrieval date, then prepare the run folder(s)."""
    parser = argparse.ArgumentParser(
        description=(
            "Prepare a supervised-run folder: freeze the reviewed documents and "
            "substrate, with hashed provenance manifests."
        )
    )
    parser.add_argument("run_id")
    parser.add_argument("doc_ids", nargs="+", help="e.g. SDD-001 or DDR-004")
    parser.add_argument("--from-run", default=None, help="prior draw to carry substrate forward from")
    parser.add_argument("--draws", nargs="+", default=None, help="run-ids for N draws (differ only in run_id)")
    parser.add_argument("--sofia-root", default=str(Path(__file__).resolve().parents[1]))
    parser.add_argument(
        "--bedrock-cache-root", default=None,
        help="installed bedrock plugin cache root (default: discovered from the plugin registry)",
    )
    parser.add_argument(
        "--accept-stale-authority", action="append", default=[], metavar="ID",
        help="sanction a bedrock pin mismatch for <ID> (needs a matching --reason)",
    )
    parser.add_argument(
        "--reason", action="append", default=[],
        help="reason for the corresponding --accept-stale-authority (order-matched)",
    )
    parser.add_argument(
        "--extra-canon", action="append", default=[], metavar="DOC-ID",
        help="fold an extra landing-state authority (by doc-id) into this run's "
             "substrate without widening the recipe (RBT-54 S-2 / E2')",
    )
    args = parser.parse_args(argv)

    sofia_root = Path(args.sofia_root)
    runs_root = sofia_root / "agent-loop" / "runs"
    head_sha = _git_head(sofia_root)
    retrieved = date.today().isoformat()
    verified_at = retrieved  # F4 currency check runs at this same prep instant

    # S-2 (E2'): resolve each --extra-canon doc-id to a repo-canonical authority.
    extra_specs = []
    for doc_id in args.extra_canon:
        path = resolve_document(sofia_root / "docs", doc_id)
        relpath = str(path.relative_to(sofia_root))
        extra_specs.append(
            SubstrateSpec(
                doc_id, "authorities",
                {"source": "sofia-repo", "path": relpath},
                repo_relpath=relpath,
            )
        )
        print(f"extra-canon: {doc_id} -> {relpath}")

    # F4: bedrock authorities are verified pin-vs-installed against the cache.
    bedrock_cache_root = (
        Path(args.bedrock_cache_root) if args.bedrock_cache_root
        else _resolve_bedrock_cache_root()
    )
    print(f"bedrock cache root: {bedrock_cache_root}")
    if len(args.accept_stale_authority) != len(args.reason):
        parser.error("each --accept-stale-authority needs exactly one matching --reason")
    accept_stale = dict(zip(args.accept_stale_authority, args.reason))

    if args.draws:
        folders = prep_draws(
            args.draws, args.doc_ids, sofia_root=sofia_root, runs_root=runs_root,
            sofia_head_sha=head_sha, retrieved=retrieved, from_run=args.from_run,
            bedrock_cache_root=bedrock_cache_root, accept_stale=accept_stale,
            verified_at=verified_at, extra_specs=extra_specs,
        )
    else:
        folders = [
            prep_run(
                args.run_id, args.doc_ids, sofia_root=sofia_root, runs_root=runs_root,
                sofia_head_sha=head_sha, retrieved=retrieved, from_run=args.from_run,
                bedrock_cache_root=bedrock_cache_root, accept_stale=accept_stale,
                verified_at=verified_at, extra_specs=extra_specs,
            )
        ]
    for folder in folders:
        print(f"prepared {folder}")


if __name__ == "__main__":  # pragma: no cover
    main()
