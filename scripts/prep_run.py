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
#                       [--docs-root <path>]
#                       [--extra-design-intent <path>[:<logical_id>]]...
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


_SANDBOX_PREFIX = "agent-loop/sandbox/"


def _extra_origin(relpath: str) -> dict:  # pragma: no cover
    """The origin block for an extra substrate file, by where it lives.

    A sandbox fixture's own substrate records a FIXTURE-relative origin path:
    the fixture root is the provenance boundary for a sandbox run exactly as the
    repo root is for a canonical one, so the origin stays meaningful if the
    fixture is moved or archived wholesale. Anything outside
    `agent-loop/sandbox/` is repo-canonical and records its repo-relative path.
    """
    if relpath.startswith(_SANDBOX_PREFIX):
        _fixture, _, inner = relpath[len(_SANDBOX_PREFIX):].partition("/")
        if inner:
            return {"source": "sandbox", "path": inner}
    return {"source": "sofia-repo", "path": relpath}


def _split_logical_id(item: str) -> tuple[str, str]:  # pragma: no cover
    """Split `PATH[:logical_id]`; the id is optional and never contains a slash."""
    head, sep, tail = item.rpartition(":")
    if sep and tail and "/" not in tail:
        return head, tail
    return item, ""


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
    parser.add_argument(
        "--docs-root", default=None, metavar="PATH",
        help="resolve/snapshot the REVIEWED document from this root instead of "
             "<sofia-root>/docs (RBT-67 sandbox ingest, e.g. "
             "agent-loop/sandbox/adr-003-fixture/docs). Authorities still come "
             "from the canonical docs/",
    )
    parser.add_argument(
        "--extra-design-intent", action="append", default=[], metavar="PATH[:ID]",
        help="fold an extra design-intent authority (by repo-relative path, with "
             "an optional :logical_id overriding the filename stem) into this "
             "run's substrate without widening the recipe (RBT-67 rule-and-resume: "
             "operator rulings enter as ratified design intent, which is what "
             "turns a decision-bearing finding resolvable)",
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

    # RBT-67 rule-and-resume: an operator ruling enters the run as ratified
    # design intent. That is the whole pivot — a decision-bearing finding is one
    # whose fix authority does not yet exist; once the ruling IS substrate, the
    # arbiter can name it, the finding classifies resolvable, and the author can
    # conform to it. No recipe change: the ruling rides extra_specs, per-run.
    for item in args.extra_design_intent:
        raw, override_id = _split_logical_id(item)
        path = (sofia_root / raw).resolve()
        if not path.is_file():
            parser.error(f"--extra-design-intent path not found: {path}")
        relpath = str(path.relative_to(sofia_root.resolve()))
        logical_id = override_id or path.stem
        extra_specs.append(
            SubstrateSpec(
                logical_id, "design-intent",
                _extra_origin(relpath),
                repo_relpath=relpath,
            )
        )
        print(f"extra-design-intent: {logical_id} -> {relpath}")

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
        if args.docs_root:
            parser.error("--docs-root is a single-run sandbox ingest; not supported with --draws")
        folders = prep_draws(
            args.draws, args.doc_ids, sofia_root=sofia_root, runs_root=runs_root,
            sofia_head_sha=head_sha, retrieved=retrieved, from_run=args.from_run,
            bedrock_cache_root=bedrock_cache_root, accept_stale=accept_stale,
            verified_at=verified_at, extra_specs=extra_specs,
        )
    else:
        if args.docs_root:
            print(f"sandbox ingest: reviewed document from {args.docs_root}")
        folders = [
            prep_run(
                args.run_id, args.doc_ids, sofia_root=sofia_root, runs_root=runs_root,
                sofia_head_sha=head_sha, retrieved=retrieved, from_run=args.from_run,
                bedrock_cache_root=bedrock_cache_root, accept_stale=accept_stale,
                verified_at=verified_at, extra_specs=extra_specs,
                docs_root=args.docs_root,
            )
        ]
    for folder in folders:
        print(f"prepared {folder}")


if __name__ == "__main__":  # pragma: no cover
    main()
