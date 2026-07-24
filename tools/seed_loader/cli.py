##############################################################################
# Module: seed_loader/cli.py
# Author: Haffey Enterprises LLC
# Created: 2026-07-14 / Revised: 2026-07-14
# Description: CLI entrypoint for the seed loader. Subcommands:
#   manifest  — build/write the content-addressed manifest from a seed dir
#   verify    — re-hash a seed dir against a stored manifest (drift detection)
#   load      — MERGE the seed into Neo4j (constraints MUST be applied first),
#               then write the manifest so the seeded state is pinned
#
#   Neo4j auth comes from the environment (NEO4J_URI/NEO4J_USER/NEO4J_PASSWORD) —
#   never a flag, never committed. `--now` is an explicit ISO timestamp so a load
#   is reproducible (no hidden clock).
##############################################################################

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

from seed_loader.manifest import verify_manifest, write_manifest
from seed_loader.parser import load_seed_dir


def _driver():
    from neo4j import GraphDatabase

    uri = os.environ["NEO4J_URI"]
    user = os.environ["NEO4J_USER"]
    password = os.environ["NEO4J_PASSWORD"]
    return GraphDatabase.driver(uri, auth=(user, password))


def _cmd_manifest(args: argparse.Namespace) -> int:
    manifest = write_manifest(Path(args.seed_dir), Path(args.out))
    print(f"manifest written: {args.out}  digest={manifest['manifest_digest']}")
    return 0


def _cmd_verify(args: argparse.Namespace) -> int:
    problems = verify_manifest(Path(args.seed_dir), Path(args.manifest))
    if problems:
        print("MANIFEST DRIFT:", file=sys.stderr)
        for p in problems:
            print(f"  - {p}", file=sys.stderr)
        return 1
    print("manifest verified: seed dir matches stored manifest")
    return 0


def _cmd_load(args: argparse.Namespace) -> int:
    from seed_loader.loader import load_docs

    docs = load_seed_dir(Path(args.seed_dir))
    with _driver() as driver:
        counts = load_docs(driver, docs, now=args.now)
    print(f"loaded: {counts['nodes']} nodes, {counts['edges']} edges from {len(docs)} files")
    manifest = write_manifest(Path(args.seed_dir), Path(args.manifest))
    print(f"manifest written: {args.manifest}  digest={manifest['manifest_digest']}")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="seed-loader", description="RBT-58 KG seed loader.")
    sub = parser.add_subparsers(dest="command", required=True)

    m = sub.add_parser("manifest", help="Build the content-addressed manifest.")
    m.add_argument("--seed-dir", required=True)
    m.add_argument("--out", default="manifest.json")
    m.set_defaults(func=_cmd_manifest)

    v = sub.add_parser("verify", help="Verify a seed dir against a stored manifest.")
    v.add_argument("--seed-dir", required=True)
    v.add_argument("--manifest", default="manifest.json")
    v.set_defaults(func=_cmd_verify)

    l = sub.add_parser("load", help="Load the seed into Neo4j and pin the manifest.")
    l.add_argument("--seed-dir", required=True)
    l.add_argument("--manifest", default="manifest.json")
    l.add_argument("--now", required=True, help="ISO-8601 load instant (reproducible; no hidden clock).")
    l.set_defaults(func=_cmd_load)

    args = parser.parse_args(argv)
    return int(args.func(args))


if __name__ == "__main__":
    raise SystemExit(main())
