#!/usr/bin/env python3
# R-B SCRATCH PROBE — NOT part of the agent_loop package, NOT committed until fired.
# ---------------------------------------------------------------------------
# Reconstructs run-016's assembled SA (antagonist-SA) user prompt from the FROZEN
# run folder, then runs single-call counterfactual arms through the real loop
# transport to probe why the run-016 draw went all-hats-null (every hat "[]").
# Raw emissions + per-arm output-token / finding / POSITIVE counts, UNFILTERED.
#
#   ROUND 1 (fired — both SILENT):
#     B — authorities MINUS DDR-002; document untouched.
#     C — document Status cell ACCEPTED->PROPOSED; authorities untouched.
#   ROUND 2 (fired):
#     D — design-intent MINUS deliberation-record-ddr-002; authorities+doc intact.
#     E — authorities MINUS {DDR-002,SDD-001,DDR-004} + design-intent MINUS record;
#         document untouched (run-015-equivalent length).
#     F — E's trim + record restored (held; fired on D-silent AND E-wakes).
#   ROUND 3 (fired):
#     G — author-decision-record-SKILL authority swapped to the installed 1.0.0
#         cache bytes (sha256 f0ef38da…); document + rest intact.
#     H — the three 1.3.0 Change Log rows stripped from the DOCUMENT SET copy
#         (document otherwise byte-intact); authorities intact.
#     I — DOCUMENT SET copy replaced with DDR-002 v1.2.0 (git blob 8dbabefa,
#         content sha256 4a373f2e…); authorities intact (still v1.3.0).
#   ROUND 4 (fired): J (zero-narrative context — woke), K (run-015 healthy baseline — woke).
#   ROUND 5 (fired): L — full input against the gen-7 SA prompt (rule 8) — SILENT
#         (gen-7 self-terminated end_turn empty at full narrative saturation).
#   ROUND 6 (this invocation — the gen-8 remedy acceptance gate):
#     M — full, UNMODIFIED run-016 input (pre-trailer base == baseline 563415c7…)
#         against the gen-8 SA prompt: R-E1 empty-array floor (system) + R-E2
#         recency directive (assembly). PASS iff M wakes; silence => structural
#         redesign, no further prompt iteration without a ruling.
#
# Tad fires (real, paid API calls; needs ANTHROPIC_API_KEY in the shell):
#     python agent-loop/runs/run-016-ddr-002/probes/sa_probe.py
# Round-3 results MERGE into report.json (prior arms preserved; same-named arms
# replaced so a re-run is safe). No writes outside probes/; no git changes.

from __future__ import annotations

import hashlib
import json
import os
import sys
from pathlib import Path

PROBES_DIR = Path(__file__).resolve().parent            # .../run-016-ddr-002/probes
RUN_DIR = PROBES_DIR.parent                             # .../run-016-ddr-002
AGENT_LOOP_DIR = RUN_DIR.parents[1]                     # .../agent-loop
SOFIA_ROOT = RUN_DIR.parents[2]                         # repo root
sys.path.insert(0, str(AGENT_LOOP_DIR))                 # make `agent_loop` importable

from agent_loop.fetchers import RepoDocumentFetcher, RunSubstrateFetcher
from agent_loop.ledger import DEFAULT_COUNTED_SEVERITIES, Ledger, LedgerHeader
from agent_loop.log import ActionLog, JsonlFileSink
from agent_loop.real_hats import (
    _REVIEW_DIRECTIVE,
    assemble_user_prompt,
    load_system_prompt,
    parse_emissions,
)
from agent_loop.reviewers import IDENTITY_SA, DocumentSet, Substrate
from agent_loop.run_real import RUN_ONE_MAX_TOKENS, RUN_ONE_MODEL
from agent_loop.transport import build_api_emitter, build_real_transport

DOC_IDS = ["DDR-002"]
SA_PROMPT = AGENT_LOOP_DIR / "design" / "antagonist-SA.prompt.md"
_SEVERITIES = ("BLOCKING", "MATERIAL", "COSMETIC", "POSITIVE")

_SKILL_KEY = "author-decision-record-SKILL"
_SKILL_1_0_0_SHA = "f0ef38dab80b3aa4ae7e079938648b1ec1797f6c9ad0b55e633ae4b8904ff398"
_DDR002_V120_SHA = "4a373f2e9484848eca81cb79ccefe44c8f2660cb8ccd9ea93d583c9ccfc0a0bf"
_CHANGELOG_130_PREFIX = "| 1.3.0 |"

# Round 4
_RECORD_KEY = "deliberation-record-ddr-002"           # design-intent entry (E/J drop)
_E_AUTH_TRIM = {"DDR-002", "SDD-001", "DDR-004"}       # authorities E/J drop
_J_MUST_BE_ABSENT = ["ratified per item", "A-1"]       # J's zero-narrative invariant
_RUN015_DIR = "agent-loop/runs/run-015-ddr-004"        # K's healthy-baseline source
_SA_PROMPT_FILE_SHA = "e77ffbc743b86391ed1b1231c8bc6c1d4ddddfc5cb02089f07db2c6ba9bf3859"


def _sha256(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _pass_one_snapshot() -> Ledger:
    """The initial (pass-1) ledger snapshot every reviewer sees — empty findings,
    the run's header, exactly as run_real seeds it (dry mode)."""
    return Ledger(
        header=LedgerHeader(
            set=list(DOC_IDS), counted_severities=list(DEFAULT_COUNTED_SEVERITIES),
            plateau_N=3, mode="dry",
        )
    )


def _severity_breakdown(findings) -> dict[str, int]:
    counts = {sev: 0 for sev in _SEVERITIES}
    for finding in findings:
        counts[finding.severity] = counts.get(finding.severity, 0) + 1
    return counts


def _run_arm(name: str, *, records: DocumentSet, substrate: Substrate,
             system: str, transport, snapshot: Ledger | None = None,
             assert_absent: list[str] | None = None) -> dict:
    """One SA call for an arm; write raw emission + action log; return counts.

    `snapshot` overrides the default pass-1 DDR-002 snapshot (K uses run-015's
    header). `assert_absent` fails loud if any listed string is present in the
    assembled user prompt (J's zero-narrative invariant). The assembled prompt's
    sha256 is reported for every arm."""
    snap = snapshot if snapshot is not None else _pass_one_snapshot()
    user = assemble_user_prompt(records, substrate, snap)
    if assert_absent:
        present = [needle for needle in assert_absent if needle in user]
        if present:
            raise SystemExit(f"{name}: expected-absent string(s) present: {present}")
    (PROBES_DIR / f"arm-{name}.user-prompt.txt").write_text(user, encoding="utf-8")
    sink = JsonlFileSink(PROBES_DIR / f"arm-{name}.action-log.jsonl")
    log = ActionLog(sink=sink)
    try:
        emitter = build_api_emitter(
            site_label=IDENTITY_SA.label, model=RUN_ONE_MODEL,
            max_tokens=RUN_ONE_MAX_TOKENS, log=log, transport=transport,
        )
        raw = emitter(system, user)
        (PROBES_DIR / f"arm-{name}.emission.txt").write_text(raw, encoding="utf-8")
        findings = parse_emissions(IDENTITY_SA, raw, log)
    finally:
        sink.close()
    llm_calls = log.of_kind("llm_call")
    return {
        "arm": name,
        "user_sha256": _sha256(user),
        "output_tokens": llm_calls[-1].detail["output_tokens"] if llm_calls else None,
        "llm_call_count": len(llm_calls),
        "llm_retry_count": len(log.of_kind("llm_retry")),
        "parse_dropped_count": len(log.of_kind("parse_dropped")),
        "finding_count": len(findings),
        "positive_count": sum(1 for f in findings if f.severity == "POSITIVE"),
        "severity_breakdown": _severity_breakdown(findings),
    }


# --- round-3 source resolution (fail loud on any mismatch) --------------------


def _read_1_0_0_skill() -> str:
    """The installed bedrock 1.0.0 cache SKILL.md bytes (sibling of the active
    1.3.0 install), verified against its pinned sha256."""
    config = Path.home() / ".claude" / "plugins" / "installed_plugins.json"
    data = json.loads(config.read_text(encoding="utf-8"))
    install = None
    for entry in data.get("plugins", {}).get("bedrock@bedrock", []):
        path = Path(entry.get("installPath", ""))
        if path.is_dir():
            install = path
            break
    if install is None:
        raise SystemExit("G: bedrock plugin cache not resolvable")
    skill = install.parent / "1.0.0" / "skills" / "author-decision-record" / "SKILL.md"
    if not skill.is_file():
        raise SystemExit(f"G: 1.0.0 SKILL.md not found at {skill}")
    content = skill.read_text(encoding="utf-8")
    if _sha256(content) != _SKILL_1_0_0_SHA:
        raise SystemExit(f"G: 1.0.0 SKILL sha256 mismatch: {_sha256(content)}")
    return content


def _ddr002_v120_document() -> str:
    """DDR-002 v1.2.0 (git blob 8dbabefa, content sha256 4a373f2e…), sourced from
    the committed run-015 substrate copy (byte-identical), verified by hash."""
    src = SOFIA_ROOT / "agent-loop" / "runs" / "run-015-ddr-004" / "substrate" / "authorities" / "DDR-002.md"
    content = src.read_text(encoding="utf-8")
    if _sha256(content) != _DDR002_V120_SHA:
        raise SystemExit(f"I: DDR-002 v1.2.0 sha256 mismatch: {_sha256(content)}")
    return content


def _strip_130_changelog_rows(content: str) -> str:
    """Remove exactly the three `| 1.3.0 |` Change Log rows; fail loud on any
    other count. The document is otherwise byte-intact."""
    lines = content.split("\n")
    kept = [line for line in lines if not line.startswith(_CHANGELOG_130_PREFIX)]
    removed = len(lines) - len(kept)
    if removed != 3:
        raise SystemExit(f"H: expected 3 v1.3.0 Change Log rows, removed {removed}")
    return "\n".join(kept)


def _merge_into_report(new_arms: list[dict], notes: dict[str, str]) -> None:
    """Merge arm results into report.json (prior arms preserved; same-named arms
    replaced, so a re-run is idempotent)."""
    path = PROBES_DIR / "report.json"
    if path.is_file():
        report = json.loads(path.read_text(encoding="utf-8"))
    else:
        report = {
            "run_id": "run-016-ddr-002", "reviewer": IDENTITY_SA.label,
            "model": RUN_ONE_MODEL, "max_tokens": RUN_ONE_MAX_TOKENS, "arms": [],
        }
    report.setdefault("arm_notes", {}).update(notes)
    index = {arm.get("arm"): i for i, arm in enumerate(report["arms"])}
    for arm in new_arms:
        name = arm.get("arm")
        if name in index:
            report["arms"][index[name]] = arm
        else:
            report["arms"].append(arm)
    path.write_text(json.dumps(report, indent=2), encoding="utf-8")


def _run015_sa_call(system: str, transport) -> dict:
    """Arm K — reconstruct run-015's SA call byte-for-byte from its committed run
    folder (documents/, substrate/, a pass-1 snapshot with its ledger header) and
    re-fire it as-is today. The SA prompt file is verified byte-identical to the
    one run-015 recorded, so system + user + calibration all match — a true
    healthy-baseline control."""
    run015 = SOFIA_ROOT / _RUN015_DIR
    manifest = json.loads((run015 / "manifest.json").read_text(encoding="utf-8"))
    if manifest["prompt_sha256"]["antagonist-SA.prompt.md"] != _SA_PROMPT_FILE_SHA:
        raise SystemExit("K: run-015 SA prompt hash != today's — not a byte-for-byte re-fire")
    if _sha256(SA_PROMPT.read_text(encoding="utf-8")) != _SA_PROMPT_FILE_SHA:
        raise SystemExit("K: today's SA prompt file hash != run-015's recorded hash")

    header = json.loads((run015 / "ledger.json").read_text(encoding="utf-8"))["header"]
    doc_ids = list(header["set"])
    records = RepoDocumentFetcher(run015 / "documents")(doc_ids)
    substrate = RunSubstrateFetcher(run015 / "substrate")(doc_ids)
    snapshot = Ledger(header=LedgerHeader(**header))
    return _run_arm("K", records=records, substrate=substrate, system=system,
                    transport=transport, snapshot=snapshot)


# gen-8 guards (fail loud before firing if the remedy isn't actually in force):
_RE1_MARKER = "an entirely empty array is a protocol violation"   # R-E1 (SA system prompt)
_RE2_MARKER = "REVIEW DIRECTIVE (read last, applies now):"         # R-E2 (assembled user)
_BASELINE_PRE_TRAILER_SHA = "563415c7fdd266f201d109fd927d47ad35a95252de1483ccc2bc65899c639158"


def main() -> None:
    if not os.environ.get("ANTHROPIC_API_KEY"):
        raise SystemExit(
            "ANTHROPIC_API_KEY not set — this probe fires real API calls; set the "
            "key in your shell and re-run (Tad fires; key stays in his shell)."
        )

    # ROUND 6 — Arm M, the gen-8 remedy acceptance gate. Full, UNMODIFIED run-016
    # input (every narrative copy intact — the exact context that went silent
    # under gen-5 and gen-7) against the gen-8 SA prompt: R-E1 empty-array floor
    # (system) + R-E2 recency directive (assembly). PASS iff M wakes.
    records = RepoDocumentFetcher(RUN_DIR / "documents")(DOC_IDS)
    substrate = RunSubstrateFetcher(RUN_DIR / "substrate")(DOC_IDS)
    system = load_system_prompt(SA_PROMPT)

    # Guard R-E1: the empty-array floor is in the SA system prompt.
    if _RE1_MARKER not in system:
        raise SystemExit("M: SA system prompt lacks the R-E1 empty-array floor — not gen-8")
    # Guard R-E2: the recency directive is the assembled prompt's trailer.
    user = assemble_user_prompt(records, substrate, _pass_one_snapshot())
    trailer = "\n\n" + _REVIEW_DIRECTIVE
    if _RE2_MARKER not in user or not user.endswith(trailer):
        raise SystemExit("M: assembled prompt lacks the R-E2 recency directive trailer — not gen-8")
    # Guard: the pre-trailer base is byte-identical to the silent-under-gen-5/7 baseline.
    base = user[: -len(trailer)]
    base_sha = _sha256(base)
    if base_sha != _BASELINE_PRE_TRAILER_SHA:
        raise SystemExit(f"M: pre-trailer base sha {base_sha} != baseline {_BASELINE_PRE_TRAILER_SHA}")

    transport = build_real_transport()
    result = _run_arm("M", records=records, substrate=substrate, system=system, transport=transport)
    result["pre_trailer_base_sha256"] = base_sha
    result["final_assembled_sha256"] = result["user_sha256"]

    _merge_into_report([result], {
        "arm_M": "gen-8 remedy acceptance gate — full, unmodified run-016 input "
                 "(pre-trailer base == baseline 563415c7…, every narrative copy intact) "
                 "against the gen-8 SA prompt: R-E1 empty-array floor (system) + R-E2 "
                 "recency directive (assembly). PASS iff M wakes (findings >= 1, "
                 "POSITIVEs per contract); silence => structural redesign, no further "
                 "prompt iteration without a ruling.",
    })
    print(json.dumps([result], indent=2))


if __name__ == "__main__":
    main()
