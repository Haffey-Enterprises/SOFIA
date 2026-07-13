# Module: agent_loop.real_hats
# Purpose: The real-reviewer machinery specified by runner-real-hats.contract.md
#          §4–§7: load a reviewer's prompt as data, assemble its per-pass User
#          block, parse+stamp its JSON emissions, and schedule the sweep. NO real
#          LLM is invoked here — reviewers compose an injected emitter callable;
#          first dry runs of the real hats are a separate, supervised session.
# Scope:   Prompt loading, input assembly (§5), the emission-parsing seam (§7),
#          the real-hat pass plan + coherence scheduling (§6). Admission,
#          arbiter, gates, router, author, and mode are untouched (§8).

from __future__ import annotations

import json
import re
from dataclasses import asdict
from pathlib import Path
from typing import Callable

# A well-defined opening code-fence line: ``` optionally followed by a `json`
# language tag (case-insensitive). Nothing else counts as a fence.
_FENCE_OPEN = re.compile(r"^```(?:json)?$", re.IGNORECASE)


def strip_code_fences(text: str) -> str:
    """Strip a well-defined markdown code fence around an emission.

    Removes an opening ``` / ```json line and a closing ``` line (plus
    surrounding whitespace) — transport unwrapping only, applied when BOTH a
    matching open and close fence are present. No other tolerance: prose
    preambles, trailing commentary, or malformed structure are left intact and
    still fail parsing (runner-real-hats.contract.md §7, amended 2026-07-02).
    """
    stripped = text.strip()
    lines = stripped.split("\n")
    if (
        len(lines) >= 2
        and _FENCE_OPEN.match(lines[0].strip())
        and lines[-1].strip() == "```"
    ):
        return "\n".join(lines[1:-1]).strip()
    return stripped

from agent_loop.ledger import CitedAuthority, Finding, Ledger
from agent_loop.log import ActionLog
from agent_loop.reviewers import (
    IDENTITY_COHERENCE,
    IDENTITY_EA,
    IDENTITY_LAA,
    IDENTITY_SA,
    DocumentSet,
    Plan,
    ReviewerIdentity,
    ScheduledReviewer,
    Substrate,
)

_VALID_KINDS = {"canonical", "design-intent", "coherence", "soundness"}
_VALID_SEVERITIES = {"BLOCKING", "MATERIAL", "COSMETIC", "POSITIVE"}
_REQUIRED_FIELDS = ("severity", "target", "locus", "claim", "cited_authority")

# An LLM emitter: given the system + user prompts, return the model's raw text
# (a JSON array of findings). Not invoked in this task — real wiring is a
# separate supervised session; tests inject fakes.
LlmEmitter = Callable[[str, str], str]


# --- §4: prompt loading (## System block, loaded as data) --------------------


def load_system_prompt(prompt_path: str | Path) -> str:
    """Extract the `## System` block from a reviewer prompt file.

    The block runs from the `## System` heading to the next top-level (`## `)
    heading (the `## User` template, which the runner assembles itself per §5).

    Args:
        prompt_path: Path to the reviewer's `.prompt.md` (loaded as data — the
            file content is never edited).

    Returns:
        The system prompt text, stripped.

    Raises:
        ValueError: If the file has no `## System` section.
    """
    text = Path(prompt_path).read_text(encoding="utf-8")
    lines = text.splitlines()
    collected: list[str] = []
    in_system = False
    for line in lines:
        if line.strip() == "## System":
            in_system = True
            continue
        if in_system and line.startswith("## "):
            break
        if in_system:
            collected.append(line)
    if not in_system:
        raise ValueError(f"no '## System' section in {prompt_path}")
    return "\n".join(collected).strip()


# --- §5: input assembly (runner is the fetch point) --------------------------


def assemble_user_prompt(
    records: DocumentSet, substrate: Substrate, snapshot: Ledger
) -> str:
    """Assemble the reviewer's `## User` block from the fetched-fresh inputs.

    Args:
        records: The document set under review.
        substrate: Ratified authorities + design intent in scope.
        snapshot: The immutable prior-pass ledger snapshot (§2).

    Returns:
        The assembled user-prompt text.
    """
    docs = "\n".join(
        f"### {doc_id}\n{content}" for doc_id, content in sorted(records.documents.items())
    )
    authorities = (
        "\n".join(f"- {k}: {v}" for k, v in sorted(substrate.authorities.items()))
        or "(none in scope)"
    )
    design_intent = (
        "\n".join(f"- {k}: {v}" for k, v in sorted(substrate.design_intent.items()))
        or "(none in scope)"
    )
    snapshot_json = json.dumps(asdict(snapshot), indent=2, sort_keys=False)
    return (
        "DOCUMENT SET (fetched fresh):\n"
        f"{docs}\n\n"
        "SUBSTRATE (fetched fresh):\n"
        f"Authorities:\n{authorities}\n"
        f"Design intent:\n{design_intent}\n\n"
        "LEDGER SNAPSHOT (immutable, prior-pass):\n"
        f"{snapshot_json}"
    )


# --- §7: emission-parsing seam (validate, construct, stamp, drop) ------------


def _valid_cited_authority(raw: object) -> bool:
    """Shape/vocabulary check for a cited_authority payload (not scope/honesty).

    A `null` authority is a *valid shape* here — it passes parse and is dropped
    at admission as out-of-scope, keeping drop-at-parse distinct from
    drop-at-admission. A present authority must be a dict with a valid `kind`
    enum and a string `ref`.
    """
    if raw is None:
        return True
    if not isinstance(raw, dict):
        return False
    if raw.get("kind") not in _VALID_KINDS:
        return False
    return isinstance(raw.get("ref"), str)


def parse_emissions(
    identity: ReviewerIdentity,
    raw_text: str,
    log: ActionLog,
    emission_path: str | None = None,
) -> list[Finding]:
    """Parse one reviewer's raw JSON emission into stamped Finding templates.

    Fence-unwraps the raw text, then validates shape and vocabulary, constructs
    Finding templates, and **stamps `source`/`altitude` from the invoked
    reviewer's identity, ignoring whatever the model emitted** (§7; ledger-schema
    §Identity — hardcode over trust). A malformed emission (bad JSON, not an
    array, missing field, invalid enum) is dropped with an observable
    `parse_dropped` line referencing the captured raw file — never silently,
    never by crashing the pass. Scope drops (null/bare authority) remain
    admission's job.

    Args:
        identity: The invoking reviewer's identity (source/altitude to stamp).
        raw_text: The model's raw output (expected: a JSON array of findings).
        log: The structured action log.
        emission_path: Path to the captured raw emission, referenced on a drop.

    Returns:
        The list of well-formed, stamped Finding templates (possibly empty).
    """
    text = strip_code_fences(raw_text)
    try:
        data = json.loads(text)
    except json.JSONDecodeError:
        log.emit(
            "parse_dropped",
            reviewer=identity.label,
            reason="invalid JSON",
            emission_path=emission_path,
        )
        return []
    if not isinstance(data, list):
        log.emit(
            "parse_dropped",
            reviewer=identity.label,
            reason="emission is not a JSON array",
            emission_path=emission_path,
        )
        return []

    findings: list[Finding] = []
    for index, item in enumerate(data):
        reason = _emission_defect(item)
        if reason is not None:
            log.emit(
                "parse_dropped",
                reviewer=identity.label,
                index=index,
                reason=reason,
                emission_path=emission_path,
            )
            continue
        raw_authority = item["cited_authority"]
        authority = (
            None
            if raw_authority is None
            else CitedAuthority(kind=raw_authority["kind"], ref=raw_authority["ref"])
        )
        findings.append(
            Finding(
                # Stamped from identity — emitted source/altitude are ignored.
                source=identity.source,
                altitude=identity.altitude,
                severity=item["severity"],
                target=list(item["target"]),
                locus=item["locus"],
                claim=item["claim"],
                cited_authority=authority,
            )
        )
    return findings


def _emission_defect(item: object) -> str | None:
    """Return a reason string if `item` is a malformed emission, else None."""
    if not isinstance(item, dict):
        return "emission is not an object"
    for field_name in _REQUIRED_FIELDS:
        if field_name not in item:
            return f"missing field '{field_name}'"
    if item["severity"] not in _VALID_SEVERITIES:
        return f"invalid severity {item['severity']!r}"
    if not isinstance(item["target"], list) or not all(
        isinstance(t, str) for t in item["target"]
    ):
        return "target must be a list of strings"
    if not isinstance(item["locus"], str):
        return "locus must be a string"
    if not isinstance(item["claim"], str):
        return "claim must be a string"
    if not _valid_cited_authority(item["cited_authority"]):
        return "cited_authority malformed (bad kind or ref shape)"
    return None


# --- §4/§5: build a real reviewer (LLM call + parse seam) --------------------

# The ratified POSITIVE floor: a compliant emission owes its strongest survived
# attacks, so fewer than this many POSITIVEs is malformed-by-calibration — a
# legitimate empty result is structurally impossible under it (RBT-49 Item 2,
# run-009 audit §5b). Below the floor triggers exactly one reviewer re-draw.
_POSITIVE_FLOOR = 2


def _positive_count(findings: list[Finding]) -> int:
    """Count POSITIVE (survived-attack) findings in an emission."""
    return sum(1 for finding in findings if finding.severity == "POSITIVE")


def build_real_reviewer(
    identity: ReviewerIdentity,
    prompt_path: str | Path,
    emitter: LlmEmitter,
    capture: object | None = None,
    *,
    redraw: bool = True,
    brief_addendum: str | None = None,
) -> ScheduledReviewer:
    """Compose a real reviewer: load prompt, assemble User, emit, parse+stamp.

    The returned ScheduledReviewer runs in its own context per invocation (§4):
    the system prompt is loaded from the file, the user block is assembled from
    the fetched-fresh inputs and the frozen snapshot, the injected emitter is
    called, and the raw output is parsed and stamped. No conversation or context
    is shared between reviewers.

    When a raw-emission `capture` is supplied, the reviewer sets the capture's
    `current_pass` before emitting (so the emitter writes the raw under the right
    pass, and the arbiter — running later this pass — inherits it) and references
    the captured file path on any parse drop.

    Empty-emission re-draw (RBT-49 Item 2): when `redraw` is set, an emission
    below the 2-POSITIVE floor triggers exactly one re-draw of this hat — the
    reviewer-side analog of the arbiter's content retry. This is on by default
    (the real-run behavior, per run_real); the deterministic parse-seam and
    machinery tests pass `redraw=False` to exercise a single emission in
    isolation.

    Args:
        identity: The reviewer's canonical identity.
        prompt_path: Path to its `.prompt.md`.
        emitter: The LLM emitter (injected; a fake in tests).
        capture: Optional EmissionCapture (raw-emission provenance).
        redraw: Whether a below-floor emission triggers one re-draw.
        brief_addendum: Optional run-scoped text appended verbatim to this hat's
            assembled User block (RBT-54 R-C) — the coherence brief's ratified
            seam list is threaded here for the coherence hat only. None (default)
            appends nothing; the assembled prompt is byte-identical to before.

    Returns:
        A ScheduledReviewer ready for the runner's plan.
    """
    system_prompt = load_system_prompt(prompt_path)

    def _emit_and_parse(user_prompt: str, log: ActionLog) -> list[Finding]:
        raw_text = emitter(system_prompt, user_prompt)
        emission_path = (
            capture.last_path.get(identity.label) if capture is not None else None  # type: ignore[attr-defined]
        )
        return parse_emissions(identity, raw_text, log, emission_path=emission_path)

    def run(
        pass_number: int,
        snapshot: Ledger,
        records: DocumentSet,
        substrate: Substrate,
        log: ActionLog,
    ) -> list[Finding]:
        if capture is not None:
            capture.current_pass = pass_number  # type: ignore[attr-defined]
        user_prompt = assemble_user_prompt(records, substrate, snapshot)
        if brief_addendum:
            user_prompt = (
                f"{user_prompt}\n\n"
                "COHERENCE BRIEF ADDENDUM (ratified seam list):\n"
                f"{brief_addendum}"
            )
        drops_at_start = len(log.of_kind("parse_dropped"))
        findings = _emit_and_parse(user_prompt, log)
        if not redraw or _positive_count(findings) >= _POSITIVE_FLOOR:
            return findings

        # Below the floor: malformed-by-calibration, not a legitimate result.
        # Exactly one re-draw of this hat, logged as a retry-species event with
        # the detection reason (the reviewer-side analog of the arbiter's content
        # retry). The re-draw uses the same inputs — variance-to-zero is a
        # draw-level degeneracy, not a fixable prompt defect, so a fresh
        # identical draw is the recovery.
        log.emit(
            "llm_retry",
            site=identity.label,
            retry_kind="reviewer_redraw",
            reason="emission below the 2-POSITIVE floor",
            positive_count=_positive_count(findings),
            finding_count=len(findings),
        )
        redraw_findings = _emit_and_parse(user_prompt, log)
        total_drops = len(log.of_kind("parse_dropped")) - drops_at_start
        if not redraw_findings and total_drops == 0:
            # Second consecutive clean-empty draw (the observed variance-to-zero
            # mode): record hat_null and continue the run — a reviewer null
            # degrades recall, recoverable via union-over-runs; an arbiter null
            # corrupts the ledger and is correctly fatal (ApiArbiter aborts). The
            # asymmetry justifies the different terminal behavior. A malformed
            # draw (total_drops > 0) is not a clean null: no hat_null, and the
            # instrument-compromised guard fails loud on the parse storm as
            # before.
            log.emit(
                "hat_null",
                reviewer=identity.label,
                pass_number=pass_number,
                reason="re-draw emitted no findings after a below-floor emission",
            )
        # Otherwise admit the re-draw's emission: meets floor → admit normally;
        # non-empty but still below floor (Rb) → real content, degraded recall,
        # admitted with the below-floor fact visible via the re-draw event above
        # (hat_null is reserved for the empty case; no new event species).
        return redraw_findings

    return ScheduledReviewer(identity, run)


# --- §6: coherence scheduling (runner-scheduled, not self-gating) ------------


def _coherence_due(pass_number: int, snapshot: Ledger) -> bool:
    """Whether the real coherence sweep runs this pass.

    Pass 1 always (initial sweep); thereafter iff any document in the set was
    recorded changed in the immediately preceding pass (fire-on-trigger).
    """
    if pass_number == 1:
        return True
    return any(
        snapshot.doc_changed_in_pass(doc, pass_number - 1)
        for doc in snapshot.header.set
    )


def real_hat_plan(
    laa: ScheduledReviewer,
    sa: ScheduledReviewer,
    ea: ScheduledReviewer,
    coherence: ScheduledReviewer,
) -> Plan:
    """Build the real-hat pass plan: three hats every pass; coherence per §6.

    The coherence sweep is runner-scheduled (each real invocation costs an LLM
    call): invoked on pass 1 and on any pass after a recorded document change;
    otherwise skipped, and the skip is logged (a silent skip is
    indistinguishable from a bug).
    """

    def plan(
        pass_number: int, snapshot: Ledger, log: ActionLog
    ) -> list[ScheduledReviewer]:
        scheduled = [laa, sa, ea]
        if _coherence_due(pass_number, snapshot):
            scheduled.append(coherence)
        else:
            log.emit(
                "coherence_skip",
                pass_number=pass_number,
                reason="no document change recorded in the prior pass",
            )
        return scheduled

    return plan


def build_real_hat_plan(
    prompt_dir: str | Path,
    emitter: LlmEmitter,
    capture: object | None = None,
    *,
    coherence_addendum: str | None = None,
) -> Plan:
    """Convenience: build the real-hat plan from the four prompt files.

    Loads antagonist-LAA/SA/EA and coherence-sweep prompts from `prompt_dir` and
    wires each to `emitter` (and the optional raw-emission `capture`). Provided so
    a supervised real run has one entry point; not exercised against a real LLM
    in this task. `coherence_addendum` (RBT-54 R-C) is threaded to the coherence
    hat ALONE — the antagonist hats never receive it.
    """
    directory = Path(prompt_dir)
    return real_hat_plan(
        build_real_reviewer(IDENTITY_LAA, directory / "antagonist-LAA.prompt.md", emitter, capture),
        build_real_reviewer(IDENTITY_SA, directory / "antagonist-SA.prompt.md", emitter, capture),
        build_real_reviewer(IDENTITY_EA, directory / "antagonist-EA.prompt.md", emitter, capture),
        build_real_reviewer(
            IDENTITY_COHERENCE, directory / "coherence-sweep.prompt.md", emitter, capture,
            brief_addendum=coherence_addendum,
        ),
    )
