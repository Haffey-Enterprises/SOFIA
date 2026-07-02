# Module: agent_loop.stubs
# Purpose: Canned reviewer/author emitters — build step 4. These are NOT
#          judgment agents: the antagonist and coherence stubs emit fixed
#          planted findings, and the author stub proposes resolutions in dry
#          mode without touching any real document. Determinism here is what
#          makes every gate outcome assertable.
# Scope:   No LLM. Emission discipline (ledger-schema §Identity + author-stub
#          contract): each planted finding fires on an emission predicate —
#          seeds fire once (pass 1); coherence/trading findings fire on a
#          doc-change trigger the author recorded in the prior pass. A stub MUST
#          NOT re-emit a finding whose id is already closed (that would falsely
#          trip recurrence); fire-once / fire-on-trigger is the rule that keeps
#          S1 and S3 from false-tripping.

from __future__ import annotations

import copy
from dataclasses import dataclass
from typing import Callable

from agent_loop.arbiter import ArbiterResult
from agent_loop.identity import derive_id
from agent_loop.ledger import Classification, DocChange, Finding, Ledger
from agent_loop.log import ActionLog

# A reviewer stub: given the pass number and a freshly-fetched ledger, return
# the finding records to emit this pass (templates; admission derives their id).
Reviewer = Callable[[int, Ledger], list[Finding]]


@dataclass
class EmitContext:
    """Context a plant's emission predicate reads."""

    pass_number: int
    ledger: Ledger

    def doc_changed_in_prev_pass(self, doc: str) -> bool:
        """Whether `doc` was recorded changed in the immediately preceding pass."""
        return self.ledger.doc_changed_in_pass(doc, self.pass_number - 1)


@dataclass
class Plant:
    """A planted finding plus its emission predicate and downstream effects.

    Attributes:
        label: Human tag from the dummy case (e.g. 'P1', 'P5a').
        finding: The finding template emitted when the predicate fires.
        emit: Predicate over EmitContext — fire-once or fire-on-trigger.
        classification: The planted expected arbiter verdict for this finding.
        authority_locus: For a 'resolvable' verdict, the naming authority+locus.
        fix_changes_doc: If set, closing this finding records that doc changed
            (so the coherence stub can react). Omit for findings with no
            downstream trigger — recording a spurious change would false-trip.
        confidence: The planted verdict confidence.
        rationale: The planted verdict rationale.
    """

    label: str
    finding: Finding
    emit: Callable[[EmitContext], bool]
    classification: Classification
    authority_locus: str | None = None
    fix_changes_doc: str | None = None
    confidence: str = "high"
    rationale: str = ""

    def plant_id(self) -> str:
        """The stable id this plant's finding will derive at admission."""
        return derive_id(self.finding.target, self.finding.locus, self.finding.claim)


def plant_emitter(plants: list[Plant]) -> Reviewer:
    """Build a reviewer stub that emits each plant whose predicate fires.

    A deep copy of the template is emitted so admission mutating id/status never
    corrupts the plant.
    """

    def emit(pass_number: int, ledger: Ledger) -> list[Finding]:
        context = EmitContext(pass_number=pass_number, ledger=ledger)
        return [
            copy.deepcopy(plant.finding) for plant in plants if plant.emit(context)
        ]

    return emit


def no_reviewer(pass_number: int, ledger: Ledger) -> list[Finding]:
    """A reviewer stub that emits nothing (e.g. the antagonist in a coherence-only
    scenario)."""
    return []


def verdicts_for(plants: list[Plant]) -> dict[str, ArbiterResult]:
    """Build the canned arbiter verdict table keyed by each plant's derived id."""
    table: dict[str, ArbiterResult] = {}
    for plant in plants:
        finding_id = plant.plant_id()
        table[finding_id] = ArbiterResult(
            finding_id=finding_id,
            classification=plant.classification,
            authority_locus=plant.authority_locus,
            rationale=plant.rationale or f"planted verdict for {plant.label}",
            confidence=plant.confidence,
        )
    return table


def fix_changes_for(plants: list[Plant]) -> dict[str, str]:
    """Map finding id → doc changed on close, for plants that declare one."""
    return {
        plant.plant_id(): plant.fix_changes_doc
        for plant in plants
        if plant.fix_changes_doc is not None
    }


def author_pass(
    ledger: Ledger,
    pass_number: int,
    fix_changes: dict[str, str],
    log: ActionLog,
) -> None:
    """Author stub (canned, dry): close open resolvable findings, propose fixes.

    For each open `resolvable` finding it records a *proposed* resolution and
    marks the finding closed — nothing is applied to a real document. If the
    finding is mapped in `fix_changes`, it also records that doc-state change in
    the ledger so the coherence stub can react. It never touches a
    `decision-bearing` finding.

    Args:
        ledger: The ledger to act on (mutated).
        pass_number: The current pass number.
        fix_changes: Map finding id → doc changed on close.
        log: The structured action log.
    """
    for finding in ledger.findings:
        if finding.status != "open" or finding.classification != "resolvable":
            continue
        finding.status = "closed"
        finding.pass_closed = pass_number
        finding.resolution_note = (
            f"proposed (dry): conform to {finding.authority_locus}"
        )
        log.emit(
            "proposed_resolution",
            finding_id=finding.id,
            authority_locus=finding.authority_locus,
        )
        changed_doc = fix_changes.get(finding.id)
        if changed_doc is not None:
            ledger.doc_changes.append(
                DocChange(doc=changed_doc, pass_number=pass_number)
            )
