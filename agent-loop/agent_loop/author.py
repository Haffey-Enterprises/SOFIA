# Module: agent_loop.author
# Purpose: The author port — the fix step of the design-review loop, built to
#          `design/author.prompt.md` and the sandbox-apply semantics of
#          `run-supervision.protocol.md` §9. Runs on CONTINUE, after routing, per
#          open `resolvable` finding, one finding per LLM call, in admission
#          order, severity-blind. It derives one minimal conforming edit and
#          applies it as an exact find-replace to the run's OWN document copy
#          (`runs/<run-id>/documents/`) — or it refuses, and the refused finding
#          is routed to the operator rather than re-attempted forever.
# Scope:   Assembly (the runner is the fetch point), the parse seam, the
#          scoped apply, and the escalation transition. No classification (the
#          arbiter's), no convergence judgment (the mechanical gate's). Every
#          write is bounded to the run folder by construction: paths are resolved
#          through the run's snapshot fetcher, never `docs/`, never a ticket,
#          never the network (D4 / §9).

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Callable

from agent_loop.fetchers import RepoDocumentFetcher
from agent_loop.ledger import DocChange, Finding, Ledger
from agent_loop.log import ActionLog
from agent_loop.real_hats import LlmEmitter, load_system_prompt, strip_code_fences
from agent_loop.reviewers import Substrate, SubstrateFetcher

# The author port. Same shape as the canned `stubs.author_pass` minus its fix-
# change map: the runner hands the author the ledger it just routed, the pass
# number, and the log. `run_loop` injects the stub path's behaviour when no port
# is supplied, so the stub path is byte-identical (D1).
AuthorPort = Callable[[Ledger, int, ActionLog], None]

_CONFIDENCE_VALUES = ("high", "medium", "low")
_EDIT_KEYS = (
    "target",
    "old_string",
    "new_string",
    "authority_conformed",
    "rationale",
    "confidence",
)
_REFUSE_KEYS = ("reason", "confidence")

# The anchor-fail storm threshold (§9: "abort only on an anchor-fail storm").
# A single anchor fail is a finding-level defect — logged, escalated, not looped
# on. A pass in which at least this many edits were attempted and EVERY one
# anchor-failed (nothing applied) is the author-side analog of a parse-drop
# storm: a prompt or assembly defect, not a finding-level one. Fail loud.
_ANCHOR_STORM_MIN = 2


class AuthorParseError(RuntimeError):
    """The author output could not be parsed after its one content retry.

    Mirrors `ArbiterParseError`: aborting is correct because the alternative is
    fabricating an edit, and an edit lands on the write path.
    """


class AuthorAnchorStormError(RuntimeError):
    """Every edit attempted this pass failed its anchor check (§9).

    The author-side analog of the instrument-compromised guard: one anchor fail
    is escalated per finding, but an all-fail pass means the prompt or the
    assembly is broken, and continuing would burn passes producing nothing.
    """


# --- the two author actions (invariants enforced at construction) ------------


@dataclass(frozen=True)
class AuthorEdit:
    """A single minimal conforming edit, expressed as an exact find-replace.

    Construction enforces the prompt's own invariants so a malformed action can
    never reach the apply path:
      - `confidence` must be `high` or `medium` — a `low`-confidence edit is a
        contradiction with the bias rule (low confidence means unsure, and
        unsure means refuse), exactly as a low-confidence `resolvable` is for
        the arbiter;
      - `target` and `old_string` must be non-empty — an empty anchor matches
        everywhere and is never a unique substring.

    Attributes:
        finding_id: The finding this edit resolves (stamped from the ledger).
        target: The single document id the edit applies to.
        old_string: The verbatim, unique anchor in the current document.
        new_string: The conformed replacement.
        authority_conformed: The authority + locus the edit derives from.
        rationale: One or two sentences.
        confidence: 'high' | 'medium'.
    """

    finding_id: str
    target: str
    old_string: str
    new_string: str
    authority_conformed: str
    rationale: str
    confidence: str

    def __post_init__(self) -> None:
        if self.confidence not in ("high", "medium"):
            raise ValueError(
                "an edit's confidence must be 'high' or 'medium' — a "
                f"low-confidence edit is forbidden (bias rule), got "
                f"{self.confidence!r}"
            )
        if not self.target.strip():
            raise ValueError("an edit must name the target document it applies to")
        if not self.old_string:
            raise ValueError("an edit's old_string must be a non-empty anchor")


@dataclass(frozen=True)
class AuthorRefusal:
    """A refusal: the named authority does not uniquely determine the edit.

    Attributes:
        finding_id: The finding refused (stamped from the ledger).
        reason: Why the authority does not determine the edit.
        confidence: 'high' | 'medium' | 'low' — all three are lawful here; a
            low-confidence refusal is exactly what the bias rule asks for.
    """

    finding_id: str
    reason: str
    confidence: str

    def __post_init__(self) -> None:
        if self.confidence not in _CONFIDENCE_VALUES:
            raise ValueError(f"invalid confidence {self.confidence!r}")
        if not self.reason.strip():
            raise ValueError("a refusal must give a reason")


# --- parse seam: strict, never fabricate -------------------------------------


def _parse_author_output(raw_text: str, finding_id: str) -> AuthorEdit | AuthorRefusal | None:
    """Parse author output into one action, or None if malformed.

    Strict, mirroring `_parse_arbiter_output`: the action must be one of the two
    schema objects with all its fields and valid vocabulary — every invariant
    above is enforced by construction. `finding_id` is stamped from the actual
    finding, never trusted from the model's echo. Any defect returns None (a
    content malformation), never a fabricated edit. The raw text is
    fence-unwrapped first (transport unwrapping only).
    """
    try:
        data = json.loads(strip_code_fences(raw_text))
        action = data["action"]
        if action == "edit":
            return AuthorEdit(
                finding_id=finding_id,
                target=data["target"],
                old_string=data["old_string"],
                new_string=data["new_string"],
                authority_conformed=data["authority_conformed"],
                rationale=data["rationale"],
                confidence=data["confidence"],
            )
        if action == "refuse":
            return AuthorRefusal(
                finding_id=finding_id,
                reason=data["reason"],
                confidence=data["confidence"],
            )
        return None
    except (json.JSONDecodeError, KeyError, TypeError, ValueError):
        return None


def _diagnose_author_defect(raw_text: str) -> str:
    """Name why author output failed to parse, for a corrective retry message.

    Read-only diagnosis mirroring `_parse_author_output`'s checks WITHOUT
    changing the parser's strictness.
    """
    try:
        data = json.loads(strip_code_fences(raw_text))
    except json.JSONDecodeError:
        return "the previous output was not valid JSON"
    if not isinstance(data, dict):
        return "the previous output was not a JSON object"
    action = data.get("action")
    if action not in ("edit", "refuse"):
        return "the previous output's 'action' was not 'edit' or 'refuse'"
    required = _EDIT_KEYS if action == "edit" else _REFUSE_KEYS
    missing = [key for key in required if key not in data]
    if missing:
        return "the previous output was missing required key(s): " + ", ".join(missing)
    return (
        "the previous output used an invalid vocabulary value (an 'edit' needs a "
        "non-empty target and a non-empty old_string, and confidence 'high' or "
        "'medium' — never 'low'; a 'refuse' needs a non-empty reason and "
        "confidence 'high', 'medium', or 'low')"
    )


def _author_repair_suffix(defect: str) -> str:
    """The corrective instruction appended to the user block on the content retry.

    Names the diagnosed defect, then restates the Output-section contract so the
    second attempt is corrected rather than blindly re-prompted.
    """
    return (
        f"\n\nYOUR PREVIOUS RESPONSE COULD NOT BE PARSED: {defect}. "
        "Emit the complete raw JSON object per the Output section — exactly one "
        "of the edit or refusal objects, with all of its fields, no fences, "
        "first character {."
    )


# --- assembly: the runner is the fetch point, fetched fresh per finding -------


def _authority_reference(finding: Finding) -> str:
    """The text naming the determining authority: the arbiter's locus + the citation.

    The arbiter's `authority_locus` is the determining name (it is mandatory on a
    `resolvable` classification); the reviewer's `cited_authority.ref` is carried
    with it because a coherence or soundness finding names its authority there.
    Both are shown to the author and both are matched against when resolving the
    authority text.
    """
    parts = [finding.authority_locus or ""]
    if finding.cited_authority is not None:
        parts.append(f"{finding.cited_authority.kind}: {finding.cited_authority.ref}")
    return "\n".join(part for part in parts if part)


def _resolve_authority_texts(
    reference: str, substrate: Substrate, documents: dict[str, str]
) -> dict[str, str]:
    """Resolve the named authority to its full text, from the run's frozen inputs.

    The named authority is matched by logical id — a substrate file's stem, or a
    doc-id in the run's set — appearing in the reference text. Documents are
    candidates alongside substrate because a `coherence` finding's determining
    authority is frequently a sibling record in the set, not a substrate file;
    resolving only against `substrate/` would make every such finding
    unresolvable and silently disable the author for cross-document work. On an
    id present in both, the run's document wins (it is the text under review).

    Returns:
        Map of logical id → full text, for every authority the reference names
        (empty when the reference names nothing the run froze).
    """
    lowered = reference.lower()
    candidates: dict[str, str] = {}
    candidates.update(substrate.authorities)
    candidates.update(substrate.design_intent)
    candidates.update(documents)
    return {
        name: text
        for name, text in sorted(candidates.items())
        if name.lower() in lowered
    }


def _assemble_author_user(
    finding: Finding,
    reference: str,
    authority_texts: dict[str, str],
    documents: dict[str, str],
) -> str:
    """Assemble the author's `## User` block per its prompt template."""
    authority = "\n\n".join(
        f"### {name}\n{text}" for name, text in authority_texts.items()
    )
    docs = "\n\n".join(
        f"### {doc_id}\n{documents[doc_id]}" for doc_id in sorted(finding.target)
    )
    return (
        "RESOLVABLE FINDING:\n"
        f"{json.dumps(asdict(finding), indent=2)}\n\n"
        "DETERMINING AUTHORITY (fetched fresh):\n"
        f"Named as determining the fix: {reference}\n\n"
        f"{authority}\n\n"
        "CURRENT DOCUMENT (fetched fresh):\n"
        f"{docs}"
    )


# --- the escalation transition (D3) ------------------------------------------


def _escalate(finding: Finding) -> None:
    """Route a finding the author could not conform to the operator (D3).

    The transition is re-classification to `decision-bearing`, status left
    `open`. That is the one transition that composes with `gates.route` as it
    stands: the router already halts, unbundled, on any open decision-bearing
    finding regardless of severity, so the refused finding reaches the operator
    at the next pass's routing with no gate change. It also leaves oscillation
    accounting intact — the finding stays open, so `open_cbm` does not fall and
    plateau still measures real progress, whereas `status="escalated"` would
    drop it out of the count (reading as progress) and out of the router's view
    (which only sees open findings) — a silent drop of a discovered decision.

    The arbiter's `authority_locus` is deliberately preserved: it is the exact
    claim the author could not conform, and the operator ruling the escalation
    needs to see the seam between the two judgments.
    """
    finding.classification = "decision-bearing"


def _open_resolvable(ledger: Ledger) -> list[Finding]:
    """The open resolvable findings this pass, in admission order (D1).

    Ledger order IS admission order — `admission.admit` appends in the runner's
    fixed rank order (LAA, SA, EA, coherence), emission order preserved within a
    reviewer — so iterating the list mirrors admission determinism without a
    second ordering rule. Severity-blind: a resolvable COSMETIC is processed
    exactly like a resolvable MATERIAL.
    """
    return [
        finding
        for finding in ledger.findings
        if finding.status == "open" and finding.classification == "resolvable"
    ]


class LlmAuthor:
    """The real author over the API — the sole LLM on the write path.

    Loads `author.prompt.md`'s `## System` as data and, per open resolvable
    finding, assembles its user block from inputs fetched fresh: the finding
    verbatim (including the arbiter's `authority_locus`), the determining
    authority resolved from the run's frozen substrate and document snapshot,
    and the current text of the finding's target document(s) from the run's own
    `documents/` copy. Malformed output gets ONE corrective content retry — the
    second attempt's user block names the actual defect (logged) — then aborts.
    """

    def __init__(
        self,
        *,
        prompt_path: str | Path,
        emitter: LlmEmitter,
        documents_root: str | Path,
        substrate_fetcher: SubstrateFetcher,
        doc_ids: list[str],
    ) -> None:
        """Load the author prompt and bind the run's emitter and fetch points.

        Args:
            prompt_path: Path to `author.prompt.md` (loaded as data).
            emitter: The per-call-site LLM emitter (site label `author`), which
                carries the §5 transport, the §6 call policy (one transport
                retry then abort), and the `llm_call` / raw-capture provenance.
            documents_root: The run's `documents/` snapshot — the only place the
                author reads or writes (D4 / §9).
            substrate_fetcher: The run's substrate fetcher, invoked per finding.
            doc_ids: The run's document set (the ledger header `set`).
        """
        self._system = load_system_prompt(prompt_path)
        self._emitter = emitter
        self._fetcher = RepoDocumentFetcher(documents_root)
        self._substrate_fetcher = substrate_fetcher
        self._doc_ids = list(doc_ids)

    def __call__(self, ledger: Ledger, pass_number: int, log: ActionLog) -> None:
        """Run the fix step over this pass's open resolvable findings.

        One finding per call, sequential, in admission order, severity-blind.
        Mutates the ledger (closures, doc-changes, escalations) and the run's
        document copies; the caller persists the ledger.

        Raises:
            AuthorParseError: On malformed output after one content retry.
            AuthorAnchorStormError: When every attempted edit anchor-failed.
        """
        outcomes = [
            self._author_one(ledger, finding, pass_number, log)
            for finding in _open_resolvable(ledger)
        ]
        anchor_fails = outcomes.count("anchor_fail")
        if anchor_fails >= _ANCHOR_STORM_MIN and "edit" not in outcomes:
            raise AuthorAnchorStormError(
                f"pass {pass_number}: {anchor_fails} attempted edits all failed "
                "their exact-single-match anchor check and none applied — the "
                "author prompt or its assembly is defective, refusing to burn "
                "further passes"
            )

    def _author_one(
        self, ledger: Ledger, finding: Finding, pass_number: int, log: ActionLog
    ) -> str:
        """Author one finding. Returns the outcome: edit/refused/anchor_fail/unresolved."""
        # Fetched fresh per finding: an earlier finding's edit this same pass is
        # visible here, so anchors are checked against the text as it now stands.
        documents = self._fetcher(self._doc_ids).documents
        substrate = self._substrate_fetcher(self._doc_ids)

        unknown = [target for target in finding.target if target not in documents]
        if not finding.target or unknown:
            log.emit(
                "author_unresolved",
                finding_id=finding.id,
                cause="target",
                detail=(
                    f"finding target {finding.target} is not in the run's document "
                    f"set {self._doc_ids} — no document to conform"
                ),
            )
            _escalate(finding)
            return "unresolved"

        reference = _authority_reference(finding)
        authority_texts = _resolve_authority_texts(reference, substrate, documents)
        if not authority_texts:
            log.emit(
                "author_unresolved",
                finding_id=finding.id,
                cause="authority",
                detail=(
                    "no substrate file or document in the run resolves the named "
                    f"authority: {reference!r}"
                ),
            )
            _escalate(finding)
            return "unresolved"

        action = self._call(
            finding, _assemble_author_user(finding, reference, authority_texts, documents), log
        )
        if isinstance(action, AuthorRefusal):
            log.emit(
                "author_refused",
                finding_id=finding.id,
                reason=action.reason,
                confidence=action.confidence,
                authority_locus=finding.authority_locus,
            )
            _escalate(finding)
            return "refused"
        return self._apply(ledger, finding, action, documents, pass_number, log)

    def _call(
        self, finding: Finding, base_user: str, log: ActionLog
    ) -> AuthorEdit | AuthorRefusal:
        """One author call with one corrective content retry, then abort.

        Mirrors `ApiArbiter.classify`: the transport retry, the abort behaviour,
        and the parser's strictness are the emitter's and the parse seam's; only
        the retry's user block is made corrective.
        """
        user = base_user
        for attempt in (1, 2):
            raw_text = self._emitter(self._system, user)
            parsed = _parse_author_output(raw_text, finding.id)
            if parsed is not None:
                return parsed
            if attempt == 1:
                defect = _diagnose_author_defect(raw_text)
                log.emit(
                    "llm_retry",
                    site="author",
                    retry_kind="content",
                    reason="malformed author output",
                    defect=defect,
                )
                user = base_user + _author_repair_suffix(defect)
        raise AuthorParseError(
            f"author output for finding {finding.id!r} malformed after one "
            "content retry — aborting rather than fabricating an edit"
        )

    def _apply(
        self,
        ledger: Ledger,
        finding: Finding,
        edit: AuthorEdit,
        documents: dict[str, str],
        pass_number: int,
        log: ActionLog,
    ) -> str:
        """Apply one edit as a scoped find-replace, or fail loud on the anchor (D2).

        The anchor is (target, old_string) and both halves are checked: the
        target must be one the finding names (an edit outside the finding's locus
        is not this author's to make), and `old_string` must match exactly once
        in that document. Zero matches or more than one is an anchor fail —
        logged, observable, nothing written, and the finding routed to the
        operator rather than re-attempted forever.
        """
        if edit.target not in finding.target:
            log.emit(
                "author_anchor_fail",
                finding_id=finding.id,
                doc=edit.target,
                match_count=0,
                reason=(
                    f"edit target {edit.target!r} is outside the finding's target "
                    f"set {finding.target}"
                ),
            )
            _escalate(finding)
            return "anchor_fail"

        text = documents[edit.target]
        match_count = text.count(edit.old_string)
        if match_count != 1:
            log.emit(
                "author_anchor_fail",
                finding_id=finding.id,
                doc=edit.target,
                match_count=match_count,
                reason="old_string must match exactly once in the target document",
            )
            _escalate(finding)
            return "anchor_fail"

        # Sandbox apply (D4 / §9): the path is resolved inside the run's own
        # document snapshot, so the write cannot reach `docs/` by construction.
        path = self._fetcher.resolve(edit.target)
        path.write_text(text.replace(edit.old_string, edit.new_string), encoding="utf-8")
        # The coherence sweep fires on the doc-change recorded in the prior pass.
        ledger.doc_changes.append(DocChange(doc=edit.target, pass_number=pass_number))
        finding.status = "closed"
        finding.pass_closed = pass_number
        finding.resolution_note = f"conformed to {edit.authority_conformed}"
        log.emit(
            "author_edit",
            finding_id=finding.id,
            doc=edit.target,
            authority_conformed=edit.authority_conformed,
            confidence=edit.confidence,
            path=str(path),
        )
        return "edit"
