#!/usr/bin/env python3
##############################################################################
# Module: run_conformance_1a.py
# Author: Haffey Enterprises LLC
# Created: 2026-07-14 / Revised: 2026-07-14
# Description: Run the conformance 1a GRAPH-STATE assertions against the SEEDED
#   Neo4j instance (the acceptance leg: "conformance harness 1a green against the
#   seeded instance"). The assertions in conformance/assertions/*.py are read-only
#   Cypher that take a Driver and return list[Violation]; this thin runner points
#   them at the live seeded instance rather than the ephemeral fixture harness.
#
#   Scope: 1a (graph-state) ONLY. The 1b gateway-behavioral contracts stay xfail
#   until RBT-15 (the gateway build) — RBT-58 does not flip them, so this runner
#   does not touch contracts/.
#
#   FRESH-FETCH NOTE: this runner DISCOVERS assertion functions by introspection
#   (public module-level callables taking a single `driver` arg). Before relying
#   on it, confirm against the harness's actual public API on disk — if
#   conformance/assertions exposes a canonical registry, prefer that over
#   introspection. Do not trust this list from memory.
##############################################################################

from __future__ import annotations

import importlib
import inspect
import os
import sys
from typing import Any

# The 1a graph-state assertion modules (exclude base.py — helpers, not assertions).
_ASSERTION_MODULES = [
    "conformance.assertions.provenance",
    "conformance.assertions.decision",
    "conformance.assertions.reasoning",
    "conformance.assertions.supersession",
    "conformance.assertions.retraction",
    "conformance.assertions.extension",
]


def _driver():
    from neo4j import GraphDatabase

    return GraphDatabase.driver(
        os.environ["NEO4J_URI"],
        auth=(os.environ["NEO4J_USER"], os.environ["NEO4J_PASSWORD"]),
    )


def _assertion_callables(module: Any) -> list[Any]:
    found = []
    for name, fn in inspect.getmembers(module, inspect.isfunction):
        if name.startswith("_") or fn.__module__ != module.__name__:
            continue
        params = list(inspect.signature(fn).parameters)
        if params == ["driver"]:
            found.append(fn)
    return found


def main() -> int:
    total_violations = 0
    ran = 0
    skipped: list[str] = []
    with _driver() as driver:
        for mod_name in _ASSERTION_MODULES:
            try:
                module = importlib.import_module(mod_name)
            except ModuleNotFoundError as exc:
                skipped.append(f"{mod_name} ({exc})")
                continue
            for fn in _assertion_callables(module):
                violations = fn(driver)
                ran += 1
                for v in violations:
                    total_violations += 1
                    print(f"  VIOLATION [{fn.__name__}] {v}")

    print(
        f"\nassertion modules expected: {len(_ASSERTION_MODULES)}; "
        f"loaded: {len(_ASSERTION_MODULES) - len(skipped)}; assertions run: {ran}; "
        f"violations: {total_violations}"
    )

    # Fail loud: a skipped module or zero assertions must NEVER read as GREEN.
    # (A swallowed import producing a spurious green is the exact failure the
    # acceptance gate cannot afford — the `conformance` package must be importable;
    # see the Code execution prompt step 6.)
    if skipped:
        print("RESULT: NOT GREEN — assertion module(s) failed to import:", file=sys.stderr)
        for s in skipped:
            print(f"  - {s}", file=sys.stderr)
        return 2
    if ran == 0:
        print("RESULT: NOT GREEN — zero assertions ran; refusing to greenlight.", file=sys.stderr)
        return 2
    if total_violations:
        print("RESULT: NOT GREEN — seed is non-conformant; fix before closing RBT-58.")
        return 1
    print("RESULT: GREEN — 1a graph-state assertions pass against the seeded instance.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
