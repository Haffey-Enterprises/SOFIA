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
# The `close_satisfied` required keys are only the always-present three. The two
# evidence fields (`evidence_present`, `evidence_absent`) are individually
# nullable — either may be null so long as at least one is supplied — so their
# presence is enforced as a construction invariant (§at-least-one), not as a
# missing-key parse check.
_SATISFIED_KEYS = ("authority_satisfied", "rationale", "confidence")

# The anchor-fail storm threshold (§9: "abort only on an anchor-fail storm").
# A single anchor fail is a finding-level defect — logged, escalated, not looped
# on. A pass in which at least this many edits were attempted and EVERY one
# anchor-failed (nothing applied) is the author-side analog of a parse-drop
# storm: a prompt or assembly defect, not a finding-level one. Fail loud.
_ANCHOR_STORM_MIN = 2

# The parse-fail storm threshold (RBT-67, run-027). A single parse-fail after a
# content retry is a finding-level defect — logged, escalated (Change 3), the
# run continues on the pass's other resolvables. A pass in which at least this
# many findings parse-failed and none applied is the same prompt/assembly-defect
# signal as the anchor storm, so it reuses the anchor-storm threshold.
_PARSE_STORM_MIN = _ANCHOR_STORM_MIN

# The productive outcomes for the storm guards' "nothing applied" conjunction. A
# storm (anchor or parse) fires only when at least the threshold of failures
# occurred AND nothing was applied this pass. A satisfied-close is productive —
# it closes a finding on mechanically-verified evidence, exactly as an edit does
# — so a pass of valid satisfied-closes is not a storm (RBT-71 Piece A).
_PRODUCTIVE_OUTCOMES = frozenset({"edit", "satisfied"})


class AuthorParseStormError(RuntimeError):
    """Enough findings this pass produced unparseable output that none applied.

    The parse-side twin of `AuthorAnchorStormError` (RBT-67, run-027, where the
    first live author-fire aborted the whole run on one finding's malformed
    envelope). A single parse-fail is now escalated per finding and the run
    continues; only a pass-wide storm — at least `_PARSE_STORM_MIN` parse-fails
    with nothing applied — aborts, because that is a prompt or assembly defect,
    not a finding-level one, and continuing would burn passes producing nothing.
    """


class AuthorAnchorStormError(RuntimeError):
    """Every edit attempted this pass failed its anchor check (§9).

    The author-side analog of the instrument-compromised guard: one anchor fail
    is escalated per finding, but an all-fail pass means the prompt or the
    assembly is broken, and continuing would burn passes producing nothing.
    """


# --- the three author actions (invariants enforced at construction) ----------


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
        rationale: One terse sentence (<=~30 words).
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


@dataclass(frozen=True)
class AuthorSatisfied:
    """A satisfied-close: the finding's demand is already met by the current text.

    The author's third action (RBT-71 Piece A), lawful only when the conforming
    state is *quotable* verbatim from the current document (or the offending text
    is verifiably absent). The closure is accepted only after a mechanical
    evidence check in `_apply_satisfied`; on any failure it degrades to today's
    escalate, closing nothing. Construction enforces the prompt's invariants so a
    malformed satisfied-close can never reach the apply path:
      - at least one evidence field must be supplied (non-null and non-empty) —
        a satisfied-close with no quotable evidence is exactly the interpretive
        close the bias rule forbids, so it is a construction error, not a close;
      - `confidence` must be `high` or `medium` — a `low`-confidence close is a
        contradiction with the bias rule (unsure means refuse), exactly as for
        an `AuthorEdit`;
      - `authority_satisfied` must be non-empty — the closure names the authority
        + locus the current text already conforms to.

    Attributes:
        finding_id: The finding this closes (stamped from the ledger).
        evidence_present: A verbatim substring of the current document showing the
            conformed state — checked to occur >= 1 time — or None.
        evidence_absent: The offending string the finding targets, checked to occur
            0 times in the current document — or None.
        authority_satisfied: The authority + locus the current text conforms to.
        rationale: One terse sentence (<=~30 words).
        confidence: 'high' | 'medium'.
    """

    finding_id: str
    evidence_present: str | None
    evidence_absent: str | None
    authority_satisfied: str
    rationale: str
    confidence: str

    def __post_init__(self) -> None:
        if not (self.evidence_present or self.evidence_absent):
            raise ValueError(
                "a satisfied-close must supply at least one non-empty evidence "
                "field (evidence_present and/or evidence_absent) — an unquotable "
                "satisfaction is a refusal, not a close"
            )
        if self.confidence not in ("high", "medium"):
            raise ValueError(
                "a satisfied-close's confidence must be 'high' or 'medium' — a "
                "low-confidence close is forbidden (bias rule), got "
                f"{self.confidence!r}"
            )
        if not self.authority_satisfied.strip():
            raise ValueError(
                "a satisfied-close must name the authority its text conforms to"
            )


# --- parse seam: envelope-tolerant, schema-strict, never fabricate -----------


def _balanced_object_span(text: str, start: int) -> int | None:
    """End index (exclusive) of the balanced `{...}` beginning at `text[start]`.

    String- and escape-aware, so a brace inside a JSON string value (a `{` in the
    document text an edit carries, say) does not throw off the depth count.
    Returns None if the object never closes (a truncated tail).
    """
    depth = 0
    in_string = False
    escaped = False
    for i in range(start, len(text)):
        ch = text[i]
        if in_string:
            if escaped:
                escaped = False
            elif ch == "\\":
                escaped = True
            elif ch == '"':
                in_string = False
            continue
        if ch == '"':
            in_string = True
        elif ch == "{":
            depth += 1
        elif ch == "}":
            depth -= 1
            if depth == 0:
                return i + 1
    return None


def _extract_json_object(raw_text: str) -> tuple[str | None, bool]:
    """The first balanced, JSON-parseable `{...}` in the fence-stripped text.

    Defense-in-depth for run-027 (RBT-67): the first live author-fire aborted
    because the model narrated ~1,900 characters of reasoning before an otherwise
    valid JSON edit, and the strict whole-string parse failed at character 0. The
    prompt (gen-10) forbids that preamble; this salvages the edit when it slips
    through anyway, and the caller logs that it had to (so the prompt fix's
    residual rate stays observable rather than silently masked).

    Fence-unwraps first (transport unwrapping), then scans each `{` in turn and
    returns the first balanced span that `json.loads` accepts — trying successive
    braces makes it robust to a stray `{` in the prose preamble. Returns
    `(object_text, had_surrounding_text)`, or `(None, False)` when the text holds
    no parseable object (genuinely malformed — the caller escalates it).
    """
    text = strip_code_fences(raw_text)
    for start, ch in enumerate(text):
        if ch != "{":
            continue
        end = _balanced_object_span(text, start)
        if end is None:
            continue
        candidate = text[start:end]
        try:
            json.loads(candidate)
        except json.JSONDecodeError:
            continue
        had_surround = bool(text[:start].strip()) or bool(text[end:].strip())
        return candidate, had_surround
    return None, False


def _parse_author_output(
    raw_text: str, finding_id: str, log: ActionLog | None = None
) -> AuthorEdit | AuthorRefusal | AuthorSatisfied | None:
    """Parse author output into one action, or None if malformed.

    The action must be one of the three schema objects with all its fields and
    valid vocabulary — every invariant above is enforced by construction.
    `finding_id` is stamped from the actual finding, never trusted from the
    model's echo. Any defect returns None (a content malformation), never a
    fabricated edit.

    Tolerant on the envelope only, not the schema (RBT-67, run-027): the JSON
    object is extracted from any surrounding prose (`_extract_json_object`), so a
    leading reasoning preamble no longer defeats an otherwise-valid edit; when a
    preamble had to be stripped and the object parses, an
    `author_output_preamble_stripped` event is logged (if a `log` is given) so
    the residual rate stays visible. The schema check that follows is unchanged
    and strict.
    """
    obj_text, had_surround = _extract_json_object(raw_text)
    if obj_text is None:
        return None
    try:
        data = json.loads(obj_text)
        action = data["action"]
        if action == "edit":
            result: AuthorEdit | AuthorRefusal | AuthorSatisfied = AuthorEdit(
                finding_id=finding_id,
                target=data["target"],
                old_string=data["old_string"],
                new_string=data["new_string"],
                authority_conformed=data["authority_conformed"],
                rationale=data["rationale"],
                confidence=data["confidence"],
            )
        elif action == "refuse":
            result = AuthorRefusal(
                finding_id=finding_id,
                reason=data["reason"],
                confidence=data["confidence"],
            )
        elif action == "close_satisfied":
            # The two evidence fields are individually nullable — an omitted key
            # reads as null (the AuthorSatisfied construction invariant enforces
            # at-least-one-supplied), so they are fetched leniently while the
            # always-present keys stay strict, mirroring the edit/refuse idiom.
            result = AuthorSatisfied(
                finding_id=finding_id,
                evidence_present=data.get("evidence_present"),
                evidence_absent=data.get("evidence_absent"),
                authority_satisfied=data["authority_satisfied"],
                rationale=data["rationale"],
                confidence=data["confidence"],
            )
        else:
            return None
    except (json.JSONDecodeError, KeyError, TypeError, ValueError):
        return None
    if had_surround and log is not None:
        log.emit("author_output_preamble_stripped", finding_id=finding_id)
    return result


def _diagnose_author_defect(raw_text: str) -> str:
    """Name why author output failed to parse, for a corrective retry message.

    Read-only diagnosis mirroring `_parse_author_output`'s checks WITHOUT
    changing the parser's strictness — including its envelope tolerance, so the
    retry names the real defect (a missing key, not "not JSON", when a parseable
    object was present all along).
    """
    obj_text, _ = _extract_json_object(raw_text)
    if obj_text is None:
        return "the previous output contained no parseable JSON object"
    # `_extract_json_object` returns only a `{...}` span that already parsed, so
    # this reparse cannot fail and yields a dict — the remaining defects are
    # schema (wrong action, missing key, bad vocabulary), not envelope.
    data = json.loads(obj_text)
    action = data.get("action")
    if action not in ("edit", "refuse", "close_satisfied"):
        return (
            "the previous output's 'action' was not 'edit', 'refuse', or "
            "'close_satisfied'"
        )
    required = {
        "edit": _EDIT_KEYS,
        "refuse": _REFUSE_KEYS,
        "close_satisfied": _SATISFIED_KEYS,
    }[action]
    missing = [key for key in required if key not in data]
    if missing:
        return "the previous output was missing required key(s): " + ", ".join(missing)
    return (
        "the previous output used an invalid vocabulary value (an 'edit' needs a "
        "non-empty target and a non-empty old_string, and confidence 'high' or "
        "'medium' — never 'low'; a 'refuse' needs a non-empty reason and "
        "confidence 'high', 'medium', or 'low'; a 'close_satisfied' needs a "
        "non-empty authority_satisfied, at least one non-empty evidence field "
        "(evidence_present and/or evidence_absent), and confidence 'high' or "
        "'medium' — never 'low')"
    )


def _author_repair_suffix(defect: str) -> str:
    """The corrective instruction appended to the user block on the content retry.

    Names the diagnosed defect, then restates the Output-section contract so the
    second attempt is corrected rather than blindly re-prompted.
    """
    return (
        f"\n\nYOUR PREVIOUS RESPONSE COULD NOT BE PARSED: {defect}. "
        "Emit the complete raw JSON object per the Output section — exactly one "
        "of the edit, refusal, or satisfied-close objects, with all of its "
        "fields, no fences, first character {."
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


# The heading that opens the author's per-finding-variable tail. `_assemble_author_user`
# leads with the stable run document(s) so that block can be cached; everything
# from this heading on (the finding, the resolved determining authority) varies
# per finding and stays uncached (RBT-69 Piece 2). Defined once and used by both
# the assembler and `author_cache_prefix` so the boundary cannot diverge.
_AUTHOR_VARIABLE_HEADING = "RESOLVABLE FINDING:\n"


def _assemble_author_user(
    finding: Finding,
    reference: str,
    authority_texts: dict[str, str],
    documents: dict[str, str],
) -> str:
    """Assemble the author's `## User` block per its prompt template.

    Order (RBT-69 Piece 2): the stable run document(s) lead so that block — the
    single largest input sink, re-sent per finding (run-028: 2.12M input tokens,
    59 calls) — becomes the cacheable leading prefix. The per-finding-variable
    portion (the finding verbatim and the specific resolved determining authority)
    trails as the uncached tail. Exact split per the spec's leave-to-Code note:
    the run document is cached; the finding and *all* resolved authority stay in
    the tail (a content-neutral split that does not attempt to sub-partition
    authority into shared-vs-per-finding, which is not mechanically determinable
    from the resolver). Byte-identical to the pre-reorder assembly's *content*;
    only section order changed.
    """
    authority = "\n\n".join(
        f"### {name}\n{text}" for name, text in authority_texts.items()
    )
    docs = "\n\n".join(
        f"### {doc_id}\n{documents[doc_id]}" for doc_id in sorted(finding.target)
    )
    return (
        "CURRENT DOCUMENT (fetched fresh):\n"
        f"{docs}\n\n"
        f"{_AUTHOR_VARIABLE_HEADING}"
        f"{json.dumps(asdict(finding), indent=2)}\n\n"
        "DETERMINING AUTHORITY (fetched fresh):\n"
        f"Named as determining the fix: {reference}\n\n"
        f"{authority}"
    )


def author_cache_prefix(user: str) -> str | None:
    """The leading stable-run-document slice of an assembled author `## User` block.

    Returns `user` up to (not including) the `RESOLVABLE FINDING` heading — the
    run document(s), stable per run (unchanging in dry mode; content-addressed so
    a real edit in live mode simply refreshes the cache) — so the author
    transport can cache it (RBT-69 Piece 2). Sliced from the call's own `user`, so
    the cached head is byte-identical to the sent bytes by construction. Returns
    `None` when the heading is absent or at position 0, so no user-level caching
    is requested — a valid prefix or nothing, never the per-finding tail.
    """
    index = user.find(_AUTHOR_VARIABLE_HEADING)
    return user[:index] if index > 0 else None


# --- the escalation transition (D3) ------------------------------------------


def _escalate(finding: Finding) -> None:
    """Route a finding the author could not conform to the operator (D3).

    The transition is re-classification to `decision-bearing`, status left
    `open`. That is the one transition that composes with `gates.route` as it
    stands: the router halts, unbundled, on open decision-bearing findings
    regardless of severity once a pass's resolvable work is exhausted (RBT-67
    reorder — an open resolvable now outranks the decision halt), so the refused
    finding is never dropped; it surfaces to the operator on the routing after
    the last resolvable is closed, and waits, still open, while any resolvable
    remains. It also leaves oscillation accounting intact — the finding stays
    open, so `open_cbm` does not fall and
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
    second attempt's user block names the actual defect (logged) — then the
    finding is escalated to the operator, never fabricated (Change 3, RBT-67); a
    pass-wide storm of such give-ups aborts (`AuthorParseStormError`).
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
            AuthorAnchorStormError: When every attempted edit anchor-failed.
            AuthorParseStormError: When `_PARSE_STORM_MIN`+ findings produced
                unparseable output and none applied.
        """
        outcomes = [
            self._author_one(ledger, finding, pass_number, log)
            for finding in _open_resolvable(ledger)
        ]
        applied = bool(set(outcomes) & _PRODUCTIVE_OUTCOMES)
        anchor_fails = outcomes.count("anchor_fail")
        if anchor_fails >= _ANCHOR_STORM_MIN and not applied:
            raise AuthorAnchorStormError(
                f"pass {pass_number}: {anchor_fails} attempted edits all failed "
                "their exact-single-match anchor check and none applied — the "
                "author prompt or its assembly is defective, refusing to burn "
                "further passes"
            )
        # Parse-fail storm (RBT-67, run-027): a single parse-fail is escalated
        # per finding in `_author_one` and the pass continues; only a pass-wide
        # storm with nothing applied aborts — the parse-side twin of the anchor
        # storm above, reusing its threshold.
        parse_fails = outcomes.count("parse_fail")
        if parse_fails >= _PARSE_STORM_MIN and not applied:
            raise AuthorParseStormError(
                f"pass {pass_number}: {parse_fails} findings produced output that "
                "could not be parsed after a content retry and none applied — the "
                "author prompt or its assembly is defective, refusing to burn "
                "further passes"
            )

    def _author_one(
        self, ledger: Ledger, finding: Finding, pass_number: int, log: ActionLog
    ) -> str:
        """Author one finding.

        Returns the outcome:
        edit/satisfied/refused/satisfied_evidence_fail/anchor_fail/parse_fail/unresolved.
        """
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
        if action is None:
            # Malformed after one content retry (Change 3, RBT-67): escalate this
            # one finding, never fabricate — and let the pass continue on its
            # other resolvables. A pass-wide storm is caught back in `__call__`.
            log.emit(
                "author_parse_fail",
                finding_id=finding.id,
                reason="author output could not be parsed after one content retry",
                authority_locus=finding.authority_locus,
            )
            _escalate(finding)
            return "parse_fail"
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
        if isinstance(action, AuthorSatisfied):
            return self._apply_satisfied(
                ledger, finding, action, documents, pass_number, log
            )
        return self._apply(ledger, finding, action, documents, pass_number, log)

    def _call(
        self, finding: Finding, base_user: str, log: ActionLog
    ) -> AuthorEdit | AuthorRefusal | AuthorSatisfied | None:
        """One author call with one corrective content retry.

        Mirrors `ApiArbiter.classify` for the transport retry and the parse seam;
        only the retry's user block is made corrective. Returns the parsed action,
        or None when both attempts are malformed — the caller escalates that one
        finding rather than fabricating an edit (Change 3, RBT-67); a pass-wide
        storm of such give-ups aborts in `__call__`.
        """
        user = base_user
        for attempt in (1, 2):
            raw_text = self._emitter(self._system, user)
            parsed = _parse_author_output(raw_text, finding.id, log)
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
        return None

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

    def _apply_satisfied(
        self,
        ledger: Ledger,
        finding: Finding,
        action: AuthorSatisfied,
        documents: dict[str, str],
        pass_number: int,
        log: ActionLog,
    ) -> str:
        """Close a finding that the current text already satisfies, or escalate (RBT-71).

        The satisfied-close writes no document and records no DocChange — its
        whole act is a mechanically-verified ledger transition. The evidence is
        checked against the current text of the finding's target document(s)
        (all present in `documents` by construction — `_author_one` escalated any
        unknown target before this point):
          - `evidence_present` supplied → must occur at least once, verbatim
            (presence, not uniqueness — this is evidence, not an edit anchor);
          - `evidence_absent` supplied → must occur zero times;
          - both supplied → both must hold.
        On verify: the finding is closed (`status`, `pass_closed`,
        `resolution_note`) and `author_satisfied` is emitted. On any failure:
        `author_satisfied_evidence_fail` is emitted with which check failed and
        the match counts, and the finding is escalated exactly as today — a
        malformed or unverified satisfied-close can never close a finding.
        """
        present_count: int | None = None
        absent_count: int | None = None
        present_ok = True
        absent_ok = True
        if action.evidence_present:
            present_count = sum(
                documents[doc].count(action.evidence_present) for doc in finding.target
            )
            present_ok = present_count >= 1
        if action.evidence_absent:
            absent_count = sum(
                documents[doc].count(action.evidence_absent) for doc in finding.target
            )
            absent_ok = absent_count == 0

        if not (present_ok and absent_ok):
            failed = []
            if action.evidence_present and not present_ok:
                failed.append("evidence_present")
            if action.evidence_absent and not absent_ok:
                failed.append("evidence_absent")
            log.emit(
                "author_satisfied_evidence_fail",
                finding_id=finding.id,
                failed=failed,
                evidence_present_count=present_count,
                evidence_absent_count=absent_count,
            )
            _escalate(finding)
            return "satisfied_evidence_fail"

        kinds = [
            kind
            for kind, supplied in (
                ("present", bool(action.evidence_present)),
                ("absent", bool(action.evidence_absent)),
            )
            if supplied
        ]
        finding.status = "closed"
        finding.pass_closed = pass_number
        finding.resolution_note = (
            f"satisfied: already conforms to {action.authority_satisfied}"
        )
        log.emit(
            "author_satisfied",
            finding_id=finding.id,
            evidence=kinds,
            authority_satisfied=action.authority_satisfied,
            confidence=action.confidence,
        )
        return "satisfied"
