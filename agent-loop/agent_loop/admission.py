# Module: agent_loop.admission
# Purpose: The mechanical admission gate + the identity/dedup rule — build
#          step 1. The gate enforces reviewer scope *structurally*: a finding
#          must carry a well-formed cited_authority or it is dropped and never
#          counted ("I'd have designed it differently is not a finding"). The
#          dedup rule assigns the stable id and decides new-record vs
#          dedup-open vs reopen, which is what makes oscillation detectable.
# Scope:   No LLM. No judgment about whether a citation is *honest* — the gate
#          can only check shape (the honest seam lives in the reviewer prompts,
#          flagged not solved).

from __future__ import annotations

from dataclasses import dataclass

from agent_loop.identity import derive_id, normalize_claim
from agent_loop.ledger import Finding, Ledger
from agent_loop.log import ActionLog

_VALID_KINDS = {"canonical", "design-intent", "coherence", "soundness"}

# Bare-preference phrasings the gate can catch when they appear literally in a
# ref. This is a courtesy catch, not a completeness claim — a reviewer can still
# dress a preference as a plausible authority ref, and that discipline lives in
# the reviewer prompt, not here.
_PREFERENCE_MARKERS = (
    "i'd have designed",
    "i would have designed",
    "i'd prefer",
    "i would prefer",
    "i'd rather",
    "personally i",
    "my preference",
)


@dataclass
class AdmissionResult:
    """Outcome of an admission attempt.

    Attributes:
        admitted: True iff a *new* record entered the ledger.
        reopened: True iff a closed id was re-admitted open.
        dropped: True iff the gate rejected the finding.
        finding_id: The derived id (empty when dropped before id derivation is
            meaningful — the id is still derived for logging).
    """

    admitted: bool = False
    reopened: bool = False
    dropped: bool = False
    finding_id: str = ""


def _citation_is_wellformed(finding: Finding) -> bool:
    """Structural check: present, valid kind, non-empty, non-preference ref."""
    authority = finding.cited_authority
    if authority is None:
        return False
    if authority.kind not in _VALID_KINDS:
        return False
    ref = authority.ref.strip()
    if not ref:
        return False
    lowered = ref.lower()
    if any(marker in lowered for marker in _PREFERENCE_MARKERS):
        return False
    return True


def _capture_claim_divergence(
    existing: Finding, incoming: Finding, finding_id: str, log: ActionLog
) -> None:
    """Preserve a materially-different claim admitting to an open id (RBT-69).

    Fires only when the incoming claim normalizes differently from the existing
    record's claim AND is not already captured (so a hat re-emitting the same
    wording each pass does not append duplicates, while a genuinely-new divergent
    variant is always retained). The record stays open; the variant is appended to
    `claim_variants`; a `claim_divergence` event carries both claims for the audit.
    """
    if normalize_claim(incoming.claim) == normalize_claim(existing.claim):
        return
    seen = {normalize_claim(variant) for variant in existing.claim_variants}
    if normalize_claim(incoming.claim) in seen:
        return
    existing.claim_variants.append(incoming.claim)
    log.emit(
        "claim_divergence",
        finding_id=finding_id,
        existing_claim=existing.claim,
        incoming_claim=incoming.claim,
    )


def admit(
    ledger: Ledger, finding: Finding, pass_number: int, log: ActionLog
) -> AdmissionResult:
    """Run one finding through the admission gate and identity/dedup rule.

    Mutates `ledger` in place. The order is: (1) structural scope check —
    dropped findings never enter and never count; (2) derive the stable id;
    (3) dedup by id — an already-open id is the same standing finding (no new
    record), a closed id is re-admitted open with recurrence_count incremented
    (a reopen — the oscillation signal), and an unseen id becomes a new open
    record.

    Args:
        ledger: The ledger to admit into (mutated).
        finding: The emitted finding record (its `id` is (re)derived here).
        pass_number: The current pass number.
        log: The structured action log (drops/dedup/reopen are all observable).

    Returns:
        An AdmissionResult describing what happened.
    """
    # Identity is stance-at-locus (RBT-69): (sorted(target), normalize_locus,
    # altitude). `altitude` is stamped from the invoked reviewer's identity at the
    # real_hats.parse_emissions seam before admission (hardcode over trust); the
    # claim is no longer identity-bearing.
    finding_id = derive_id(finding.target, finding.locus, finding.altitude)
    finding.id = finding_id

    # (1) Scope gate — structural. A dropped finding is never counted, but the
    # drop is logged so it is distinguishable from a bug.
    if not _citation_is_wellformed(finding):
        log.emit(
            "dropped",
            finding_id=finding_id,
            claim=finding.claim,
            reason="cited_authority missing or not well-formed (out of scope)",
        )
        return AdmissionResult(dropped=True, finding_id=finding_id)

    existing = ledger.find_by_id(finding_id)

    # (3a) Same id already open → the same standing finding, no new record. The
    # claim-divergence guard (RBT-69) is the safety net for the coarser key: a
    # materially-different claim admitting to the same open id is NOT hidden — the
    # finding stays open, the incoming claim is preserved in `claim_variants`, and
    # a `claim_divergence` event is emitted so the cold hand-audit can split a
    # true two-as-one. No new record; no claim discarded (ledger-schema §Identity).
    if existing is not None and existing.status == "open":
        _capture_claim_divergence(existing, finding, finding_id, log)
        log.emit("dedup_open", finding_id=finding_id)
        return AdmissionResult(finding_id=finding_id)

    # (3b) Same id previously closed → reopen. Preserve pass_raised; clear the
    # closure fields; re-judge fresh (classification back to unclassified);
    # increment recurrence_count.
    if existing is not None and existing.status == "closed":
        existing.status = "open"
        existing.pass_closed = None
        existing.resolution_note = None
        existing.classification = "unclassified"
        existing.authority_locus = None
        existing.recurrence_count += 1
        log.emit(
            "reopened",
            finding_id=finding_id,
            recurrence_count=existing.recurrence_count,
        )
        return AdmissionResult(reopened=True, finding_id=finding_id)

    # (3c) Unseen id → new open record.
    finding.status = "open"
    finding.pass_raised = pass_number
    finding.recurrence_count = 0
    finding.classification = "unclassified"
    ledger.findings.append(finding)
    log.emit("admitted", finding_id=finding_id, severity=finding.severity)
    return AdmissionResult(admitted=True, finding_id=finding_id)
