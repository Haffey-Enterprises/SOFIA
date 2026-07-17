# Module: tests.test_author
# Purpose: The author step (design/author.prompt.md; run-supervision.protocol.md
#          §9): parse+apply, anchor fidelity, refuse→escalate, one-per-call
#          ordering and severity-blindness, the content retry, the emitter's
#          transport policy at the author call site, and the multi-pass
#          edit→doc-change→coherence-refire→reopen path.
# Scope:   Over author, runner (the injected port), and the real-hat plan. Every
#          test uses fakes/injected transports — NO real API call is made here.

import json
from pathlib import Path

import pytest

from agent_loop.arbiter import ArbiterResult, CannedArbiter
from agent_loop.author import (
    AuthorAnchorStormError,
    AuthorEdit,
    AuthorParseError,
    AuthorRefusal,
    LlmAuthor,
    _authority_reference,
    _diagnose_author_defect,
)
from agent_loop.fetchers import RepoDocumentFetcher
from agent_loop.gates import route
from agent_loop.identity import derive_id
from agent_loop.ledger import (
    CitedAuthority,
    Finding,
    Ledger,
    LedgerHeader,
    LedgerStore,
)
from agent_loop.log import ActionLog
from agent_loop.real_hats import real_hat_plan
from agent_loop.reviewers import (
    IDENTITY_COHERENCE,
    IDENTITY_EA,
    IDENTITY_LAA,
    IDENTITY_SA,
    ScheduledReviewer,
    Substrate,
)
from agent_loop.runner import run_loop
from agent_loop.transport import LlmResponse, LlmTransportError, build_api_emitter

DESIGN_DIR = Path(__file__).resolve().parents[1] / "design"
AUTHOR_PROMPT = DESIGN_DIR / "author.prompt.md"

_DOC_TEXT = "# ADR-001\n\nAlpha section.\n\nBeta section.\n\nGamma section.\n"


# --- fakes -------------------------------------------------------------------


class ScriptedEmitter:
    """An LlmEmitter returning a scripted sequence; records (system, user) calls."""

    def __init__(self, script: list[str]) -> None:
        self.calls: list[tuple[str, str]] = []
        self._script = list(script)

    def __call__(self, system: str, user: str) -> str:
        self.calls.append((system, user))
        return self._script.pop(0)


class ScriptedTransport:
    """A transport returning/raising a scripted sequence per call."""

    def __init__(self, script: list) -> None:
        self.calls: list[dict] = []
        self._script = list(script)

    def __call__(self, system, user, model, max_tokens, cache_prefix=None):  # noqa: ANN001
        self.calls.append({"system": system, "user": user, "max_tokens": max_tokens})
        item = self._script.pop(0)
        if isinstance(item, Exception):
            raise item
        return LlmResponse(text=item, input_tokens=9, output_tokens=3)


def _substrate_fetcher(authorities=None, design_intent=None):
    def fetch(doc_ids: list[str]) -> Substrate:
        return Substrate(
            authorities=authorities if authorities is not None else {"adr-template": "AUTHORITY TEXT"},
            design_intent=design_intent if design_intent is not None else {"vision": "VISION TEXT"},
        )

    return fetch


def _documents_root(tmp_path: Path, docs: dict[str, str]) -> Path:
    root = tmp_path / "documents"
    root.mkdir(parents=True, exist_ok=True)
    for doc_id, text in docs.items():
        (root / f"{doc_id}-distilled.md").write_text(text, encoding="utf-8")
    return root


def _finding(
    *,
    claim: str = "the locus does not conform",
    severity: str = "MATERIAL",
    target: list[str] | None = None,
    locus: str = "§2",
    authority_locus: str | None = "adr-template §4",
    classification: str = "resolvable",
    cited_ref: str = "adr-template §4",
) -> Finding:
    finding = Finding(
        source="antagonist-SA",  # type: ignore[arg-type]
        altitude="SA",
        severity=severity,  # type: ignore[arg-type]
        target=["ADR-001"] if target is None else target,
        locus=locus,
        claim=claim,
        cited_authority=CitedAuthority(kind="canonical", ref=cited_ref),
        classification=classification,  # type: ignore[arg-type]
        authority_locus=authority_locus,
    )
    finding.id = derive_id(finding.target, finding.locus, finding.claim)
    return finding


def _ledger(findings: list[Finding], doc_ids: list[str] | None = None) -> Ledger:
    return Ledger(
        header=LedgerHeader(
            set=doc_ids if doc_ids is not None else ["ADR-001"],
            counted_severities=["BLOCKING", "MATERIAL"],
        ),
        findings=findings,
    )


def _author(tmp_path, emitter, *, docs=None, doc_ids=("ADR-001",), substrate=None) -> LlmAuthor:
    return LlmAuthor(
        prompt_path=AUTHOR_PROMPT,
        emitter=emitter,
        documents_root=_documents_root(tmp_path, docs if docs is not None else {"ADR-001": _DOC_TEXT}),
        substrate_fetcher=substrate if substrate is not None else _substrate_fetcher(),
        doc_ids=list(doc_ids),
    )


def _edit_json(old: str, new: str, *, target: str = "ADR-001", confidence: str = "high") -> str:
    return json.dumps(
        {
            "action": "edit",
            "finding_id": "echoed-value-ignored",
            "target": target,
            "old_string": old,
            "new_string": new,
            "authority_conformed": "adr-template §4",
            "rationale": "the template determines this heading",
            "confidence": confidence,
        }
    )


_REFUSE_JSON = json.dumps(
    {
        "action": "refuse",
        "finding_id": "echoed-value-ignored",
        "reason": "the template is silent on this locus",
        "confidence": "medium",
    }
)


# --- edit: parse + scoped apply ----------------------------------------------


def test_valid_edit_is_applied_to_the_document_copy_and_closes_the_finding(tmp_path) -> None:
    emitter = ScriptedEmitter([_edit_json("Beta section.", "Bravo section.")])
    author = _author(tmp_path, emitter)
    finding = _finding()
    ledger = _ledger([finding])
    log = ActionLog()

    author(ledger, 3, log)

    # The scoped find-replace landed on the run's document copy — and only there.
    text = (tmp_path / "documents" / "ADR-001-distilled.md").read_text()
    assert "Bravo section." in text
    assert "Beta section." not in text
    assert text == _DOC_TEXT.replace("Beta section.", "Bravo section.")
    # DocChange recorded so the coherence sweep re-fires next pass.
    assert [(c.doc, c.pass_number) for c in ledger.doc_changes] == [("ADR-001", 3)]
    assert ledger.doc_changed_in_pass("ADR-001", 3)
    # Finding closed, naming the authority it was conformed to.
    assert finding.status == "closed"
    assert finding.pass_closed == 3
    assert finding.resolution_note == "conformed to adr-template §4"
    event = log.of_kind("author_edit")[0]
    assert event.detail["finding_id"] == finding.id
    assert event.detail["doc"] == "ADR-001"
    assert event.detail["authority_conformed"] == "adr-template §4"


def test_the_user_block_carries_finding_authority_and_current_document(tmp_path) -> None:
    emitter = ScriptedEmitter([_edit_json("Beta section.", "Bravo section.")])
    author = _author(tmp_path, emitter)
    finding = _finding()
    author(_ledger([finding]), 1, ActionLog())

    system, user = emitter.calls[0]
    # System is the prompt file's ## System block, loaded as data.
    assert "You are the Author in a design-review loop." in system
    assert "RESOLVABLE FINDING:" in user
    assert finding.claim in user
    assert "adr-template §4" in user  # the arbiter's authority_locus, verbatim
    assert "DETERMINING AUTHORITY (fetched fresh):" in user
    assert "AUTHORITY TEXT" in user  # resolved fresh from the frozen substrate
    assert "CURRENT DOCUMENT (fetched fresh):" in user
    assert _DOC_TEXT in user


def test_a_second_finding_sees_the_first_findings_edit(tmp_path) -> None:
    # Documents are fetched fresh per finding: the anchor for finding 2 is checked
    # against the text as finding 1's edit left it.
    emitter = ScriptedEmitter(
        [
            _edit_json("Beta section.", "Bravo section."),
            _edit_json("Bravo section.\n\nGamma", "Bravo section.\n\nDelta"),
        ]
    )
    author = _author(tmp_path, emitter)
    first = _finding(claim="first defect", locus="§2")
    second = _finding(claim="second defect", locus="§3")
    ledger = _ledger([first, second])
    author(ledger, 1, ActionLog())

    assert "Bravo section." in emitter.calls[1][1]  # the re-read picked up edit 1
    assert first.status == "closed" and second.status == "closed"
    assert [c.doc for c in ledger.doc_changes] == ["ADR-001", "ADR-001"]


# --- anchor fidelity ---------------------------------------------------------


@pytest.mark.parametrize(
    ("doc_text", "old_string", "expected_count"),
    [
        (_DOC_TEXT, "Delta section.", 0),  # anchor matches nothing
        ("Beta.\n\nBeta.\n", "Beta.", 2),  # anchor is not unique
    ],
)
def test_anchor_that_does_not_match_exactly_once_fails_loud(
    tmp_path, doc_text, old_string, expected_count
) -> None:
    emitter = ScriptedEmitter([_edit_json(old_string, "Replaced.")])
    author = _author(tmp_path, emitter, docs={"ADR-001": doc_text})
    finding = _finding()
    ledger = _ledger([finding])
    log = ActionLog()

    author(ledger, 1, log)

    # No partial write, no doc-change, nothing closed.
    assert (tmp_path / "documents" / "ADR-001-distilled.md").read_text() == doc_text
    assert ledger.doc_changes == []
    assert finding.status == "open"
    assert finding.pass_closed is None
    assert log.of_kind("author_edit") == []
    fail = log.of_kind("author_anchor_fail")[0]
    assert fail.detail["match_count"] == expected_count
    assert fail.detail["finding_id"] == finding.id
    # The finding reaches the operator rather than being re-attempted forever.
    assert finding.classification == "decision-bearing"
    assert route(ledger).kind == "HALT_DECISION"


def test_an_edit_outside_the_findings_target_set_is_an_anchor_fail(tmp_path) -> None:
    emitter = ScriptedEmitter([_edit_json("Alpha", "Omega", target="ADR-002")])
    author = _author(
        tmp_path,
        emitter,
        docs={"ADR-001": _DOC_TEXT, "ADR-002": "Alpha elsewhere.\n"},
        doc_ids=("ADR-001", "ADR-002"),
    )
    finding = _finding(target=["ADR-001"])
    ledger = _ledger([finding], doc_ids=["ADR-001", "ADR-002"])
    log = ActionLog()

    author(ledger, 1, log)

    assert (tmp_path / "documents" / "ADR-002-distilled.md").read_text() == "Alpha elsewhere.\n"
    assert ledger.doc_changes == []
    assert "outside the finding's target set" in str(
        log.of_kind("author_anchor_fail")[0].detail["reason"]
    )
    assert finding.classification == "decision-bearing"


def test_all_edits_anchor_failing_in_one_pass_is_a_storm_and_aborts(tmp_path) -> None:
    # One anchor fail is a finding-level defect (escalated above); a pass where
    # every attempted edit failed and none applied is a prompt/assembly defect.
    emitter = ScriptedEmitter([_edit_json("Nope one", "x"), _edit_json("Nope two", "y")])
    author = _author(tmp_path, emitter)
    ledger = _ledger([_finding(claim="one", locus="§2"), _finding(claim="two", locus="§3")])

    with pytest.raises(AuthorAnchorStormError, match="anchor check"):
        author(ledger, 1, ActionLog())


def test_one_anchor_fail_alongside_one_applied_edit_is_not_a_storm(tmp_path) -> None:
    emitter = ScriptedEmitter(
        [_edit_json("Beta section.", "Bravo section."), _edit_json("Nope", "y")]
    )
    author = _author(tmp_path, emitter)
    good = _finding(claim="one", locus="§2")
    bad = _finding(claim="two", locus="§3")
    ledger = _ledger([good, bad])

    author(ledger, 1, ActionLog())  # does not raise

    assert good.status == "closed"
    assert bad.status == "open" and bad.classification == "decision-bearing"


# --- refuse → escalate -------------------------------------------------------


def test_refusal_escalates_to_the_operator_and_writes_nothing(tmp_path) -> None:
    emitter = ScriptedEmitter([_REFUSE_JSON])
    author = _author(tmp_path, emitter)
    finding = _finding()
    ledger = _ledger([finding])
    log = ActionLog()

    author(ledger, 1, log)

    assert (tmp_path / "documents" / "ADR-001-distilled.md").read_text() == _DOC_TEXT
    assert ledger.doc_changes == []
    assert log.of_kind("author_edit") == []
    refusal = log.of_kind("author_refused")[0]
    assert refusal.detail["reason"] == "the template is silent on this locus"
    assert refusal.detail["confidence"] == "medium"
    # D3: not closed, not left as a resolvable the author would re-attempt
    # forever — routed to the operator, unbundled.
    assert finding.status == "open"
    assert finding.classification == "decision-bearing"
    exit_ = route(ledger)
    assert exit_.kind == "HALT_DECISION"
    assert exit_.reason == "decision-bearing"
    assert [f.id for f in exit_.payload] == [finding.id]


def test_a_refused_cosmetic_still_halts_even_though_it_counts_zero(tmp_path) -> None:
    # Severity is orthogonal to the escalation: open_cbm stays 0, the router
    # halts anyway (mechanical-gates §Why decision-bearing gates convergence).
    emitter = ScriptedEmitter([_REFUSE_JSON])
    author = _author(tmp_path, emitter)
    finding = _finding(severity="COSMETIC")
    ledger = _ledger([finding])
    author(ledger, 1, ActionLog())
    assert route(ledger).kind == "HALT_DECISION"


# --- one per call, admission order, severity-blind ---------------------------


def test_findings_are_authored_one_per_call_in_admission_order_severity_blind(
    tmp_path,
) -> None:
    cosmetic = _finding(claim="cosmetic defect", locus="§2", severity="COSMETIC")
    material = _finding(claim="material defect", locus="§3", severity="MATERIAL")
    decision = _finding(claim="a fork", locus="§4", classification="decision-bearing")
    closed = _finding(claim="already fixed", locus="§5")
    closed.status = "closed"
    emitter = ScriptedEmitter(
        [
            _edit_json("Alpha section.", "Alpha section (conformed)."),
            _edit_json("Gamma section.", "Gamma section (conformed)."),
        ]
    )
    author = _author(tmp_path, emitter)
    # Ledger order is admission order; the author mirrors it.
    ledger = _ledger([cosmetic, material, decision, closed])

    author(ledger, 1, ActionLog())

    assert len(emitter.calls) == 2  # one call per open resolvable finding, no more
    assert "cosmetic defect" in emitter.calls[0][1]  # COSMETIC is not skipped
    assert "material defect" in emitter.calls[1][1]
    assert cosmetic.status == "closed" and material.status == "closed"
    # Untouched: the arbiter's decision-bearing finding and an already-closed one.
    assert decision.status == "open" and decision.classification == "decision-bearing"
    assert closed.pass_closed is None


# --- content retry: one, then abort; never fabricate -------------------------


def test_malformed_output_gets_one_corrective_retry_then_aborts(tmp_path) -> None:
    emitter = ScriptedEmitter(["not json at all", "still not json"])
    author = _author(tmp_path, emitter)
    finding = _finding()
    ledger = _ledger([finding])
    log = ActionLog()

    with pytest.raises(AuthorParseError, match="rather than fabricating an edit"):
        author(ledger, 1, log)

    assert len(emitter.calls) == 2  # exactly one retry
    retry = log.of_kind("llm_retry")[0]
    assert retry.detail["site"] == "author"
    assert retry.detail["retry_kind"] == "content"
    assert retry.detail["defect"] == "the previous output was not valid JSON"
    # Nothing fabricated: no edit, no close, no doc-change.
    assert (tmp_path / "documents" / "ADR-001-distilled.md").read_text() == _DOC_TEXT
    assert ledger.doc_changes == []
    assert finding.status == "open"


def test_the_retry_names_the_defect_and_the_second_attempt_can_succeed(tmp_path) -> None:
    # An action outside the two-object schema is malformed — never coerced.
    emitter = ScriptedEmitter(
        ['{"action": "rewrite"}', _edit_json("Beta section.", "Bravo section.")]
    )
    author = _author(tmp_path, emitter)
    finding = _finding()
    author(_ledger([finding]), 1, ActionLog())

    second_user = emitter.calls[1][1]
    assert "YOUR PREVIOUS RESPONSE COULD NOT BE PARSED" in second_user
    assert "'action' was not 'edit' or 'refuse'" in second_user
    assert "first character {" in second_user
    assert finding.status == "closed"


def test_a_low_confidence_edit_is_malformed_not_applied(tmp_path) -> None:
    # The bias rule's mirror of the arbiter's low-confidence `resolvable` ban:
    # low confidence means unsure, and unsure means refuse.
    low = _edit_json("Beta section.", "Bravo section.", confidence="low")
    emitter = ScriptedEmitter([low, low])
    author = _author(tmp_path, emitter)
    ledger = _ledger([_finding()])

    with pytest.raises(AuthorParseError):
        author(ledger, 1, ActionLog())

    assert (tmp_path / "documents" / "ADR-001-distilled.md").read_text() == _DOC_TEXT


@pytest.mark.parametrize(
    ("raw", "expected"),
    [
        ("<not json>", "the previous output was not valid JSON"),
        ("[]", "the previous output was not a JSON object"),
        ('{"action": "rewrite"}', "the previous output's 'action' was not 'edit' or 'refuse'"),
        (
            '{"action": "edit", "target": "ADR-001"}',
            "the previous output was missing required key(s): old_string, new_string, "
            "authority_conformed, rationale, confidence",
        ),
        (
            '{"action": "refuse", "confidence": "low"}',
            "the previous output was missing required key(s): reason",
        ),
        (
            '{"action": "refuse", "reason": "r", "confidence": "certain"}',
            "invalid vocabulary value",
        ),
    ],
)
def test_defect_diagnosis_names_the_actual_defect(raw, expected) -> None:
    assert expected in _diagnose_author_defect(raw)


@pytest.mark.parametrize(
    "action",
    [
        # An edit is rejected at construction on each prompt invariant it breaks.
        lambda: AuthorEdit("f", "ADR-001", "old", "new", "auth", "why", "low"),
        lambda: AuthorEdit("f", "  ", "old", "new", "auth", "why", "high"),
        lambda: AuthorEdit("f", "ADR-001", "", "new", "auth", "why", "high"),
        lambda: AuthorRefusal("f", "reason", "certain"),
        lambda: AuthorRefusal("f", "  ", "high"),
    ],
)
def test_author_action_invariants_are_enforced_at_construction(action) -> None:
    with pytest.raises(ValueError):
        action()


# --- assembly failures: escalate, never guess --------------------------------


@pytest.mark.parametrize("target", [["ADR-404"], []])
def test_a_target_outside_the_run_document_set_escalates_without_a_call(
    tmp_path, target
) -> None:
    emitter = ScriptedEmitter([])  # any call would IndexError — proves none happens
    author = _author(tmp_path, emitter)
    finding = _finding(target=target)
    ledger = _ledger([finding])
    log = ActionLog()

    author(ledger, 1, log)

    assert emitter.calls == []
    assert log.of_kind("author_unresolved")[0].detail["cause"] == "target"
    assert finding.classification == "decision-bearing"
    assert finding.status == "open"


def test_an_authority_the_run_never_froze_escalates_without_a_call(tmp_path) -> None:
    emitter = ScriptedEmitter([])
    author = _author(tmp_path, emitter)
    finding = _finding(authority_locus="some-unfrozen-standard §9", cited_ref="likewise §9")
    ledger = _ledger([finding])
    log = ActionLog()

    author(ledger, 1, log)

    assert emitter.calls == []
    unresolved = log.of_kind("author_unresolved")[0]
    assert unresolved.detail["cause"] == "authority"
    assert finding.classification == "decision-bearing"


def test_a_sibling_record_in_the_set_can_be_the_determining_authority(tmp_path) -> None:
    # A coherence finding's determining authority is frequently another document
    # under review, not a substrate file; it must resolve.
    emitter = ScriptedEmitter([_edit_json("Beta section.", "Bravo section.")])
    author = _author(
        tmp_path,
        emitter,
        docs={"ADR-001": _DOC_TEXT, "ADR-002": "ADR-002 governs the seam.\n"},
        doc_ids=("ADR-001", "ADR-002"),
    )
    finding = _finding(authority_locus="ADR-002 §2.5", cited_ref="ADR-002 §2.5 vs ADR-001 §2")
    author(_ledger([finding], doc_ids=["ADR-001", "ADR-002"]), 1, ActionLog())

    assert "ADR-002 governs the seam." in emitter.calls[0][1]
    assert finding.status == "closed"


def test_authority_reference_carries_the_locus_and_the_citation() -> None:
    finding = _finding(authority_locus="adr-template §4", cited_ref="ddr-template §2")
    reference = _authority_reference(finding)
    assert "adr-template §4" in reference
    assert "canonical: ddr-template §2" in reference
    # Defensive: a finding carrying neither is an empty reference, not a crash.
    bare = _finding(authority_locus=None)
    bare.cited_authority = None
    assert _authority_reference(bare) == ""


# --- the author call site's transport policy (mirrors the emitter's) ---------


def test_transport_failure_gets_one_retry_then_succeeds(tmp_path) -> None:
    transport = ScriptedTransport(
        [LlmTransportError("503"), _edit_json("Beta section.", "Bravo section.")]
    )
    log = ActionLog()
    emitter = build_api_emitter(
        site_label="author",
        model="claude-opus-4-8",
        max_tokens=8192,
        log=log,
        transport=transport,
        now=lambda: 0.0,
        sleeper=lambda seconds: None,
    )
    author = _author(tmp_path, emitter)
    finding = _finding()
    author(_ledger([finding]), 1, log)

    assert len(transport.calls) == 2
    assert log.of_kind("llm_retry")[0].detail["retry_kind"] == "transport"
    assert log.of_kind("llm_call")[0].detail["site"] == "author"
    assert finding.status == "closed"


def test_two_transport_failures_abort_the_author_with_nothing_written(tmp_path) -> None:
    transport = ScriptedTransport([LlmTransportError("503"), LlmTransportError("503")])
    log = ActionLog()
    emitter = build_api_emitter(
        site_label="author",
        model="claude-opus-4-8",
        max_tokens=8192,
        log=log,
        transport=transport,
        now=lambda: 0.0,
        sleeper=lambda seconds: None,
    )
    author = _author(tmp_path, emitter)
    ledger = _ledger([_finding()])

    with pytest.raises(LlmTransportError):
        author(ledger, 1, ActionLog())

    assert (tmp_path / "documents" / "ADR-001-distilled.md").read_text() == _DOC_TEXT
    assert ledger.doc_changes == []


# --- multi-pass integration through run_loop ---------------------------------


def _reviewer(identity, emissions_by_pass: dict[int, list[Finding]], ran: list[str]):
    def run(pass_number, snapshot, records, substrate, log):  # noqa: ANN001
        ran.append(f"{identity.label}:{pass_number}")
        return [f for f in emissions_by_pass.get(pass_number, [])]

    return ScheduledReviewer(identity, run)


def _multipass_rig(tmp_path, laa_emissions: dict[int, list[Finding]]):
    documents_root = _documents_root(tmp_path, {"ADR-001": _DOC_TEXT})
    ran: list[str] = []
    plan = real_hat_plan(
        _reviewer(IDENTITY_LAA, laa_emissions, ran),
        _reviewer(IDENTITY_SA, {}, ran),
        _reviewer(IDENTITY_EA, {}, ran),
        _reviewer(IDENTITY_COHERENCE, {}, ran),
    )
    return documents_root, ran, plan


def test_edit_makes_coherence_refire_next_pass_then_the_run_converges(tmp_path) -> None:
    finding = _finding()
    documents_root, ran, plan = _multipass_rig(tmp_path, {1: [finding]})
    emitter = ScriptedEmitter([_edit_json("Beta section.", "Bravo section.")])
    author = LlmAuthor(
        prompt_path=AUTHOR_PROMPT,
        emitter=emitter,
        documents_root=documents_root,
        substrate_fetcher=_substrate_fetcher(),
        doc_ids=["ADR-001"],
    )
    verdict = ArbiterResult(finding.id, "resolvable", "adr-template §4", "determined", "high")
    log = ActionLog()

    result = run_loop(
        header=LedgerHeader(set=["ADR-001"], counted_severities=["BLOCKING", "MATERIAL"]),
        plan=plan,
        arbiter=CannedArbiter({finding.id: verdict}),
        store=LedgerStore(tmp_path / "ledger.json"),
        author=author,
        fetch_documents=RepoDocumentFetcher(documents_root),
        fetch_substrate=_substrate_fetcher(),
        log=log,
        clock=lambda: "2026-07-16T00:00:00Z",
    )

    assert result.exit.kind == "CONVERGED"
    assert result.passes_run == 2
    # Pass 1: coherence fires (initial sweep). The author's edit records the
    # doc-change that makes it fire again on pass 2 — the point of the write.
    assert "coherence:1" in ran and "coherence:2" in ran
    assert log.of_kind("coherence_skip") == []
    assert log.of_kind("author_edit")[0].detail["doc"] == "ADR-001"
    # Pass 2 re-reviewed the conformed text and did not reopen: the edit holds.
    stored = LedgerStore(tmp_path / "ledger.json").load()
    edited = stored.find_by_id(finding.id)
    assert edited.status == "closed" and edited.recurrence_count == 0
    assert "Bravo section." in (documents_root / "ADR-001-distilled.md").read_text()


def test_edit_then_reopen_halts_to_the_operator(tmp_path) -> None:
    # The load-bearing trust signal (§9g): a finding the author edited that a
    # later pass reopens. The loop self-corrects — oscillation halts it.
    finding = _finding()
    documents_root, ran, plan = _multipass_rig(
        tmp_path, {1: [finding], 2: [_finding()]}  # pass 2 re-emits the same id
    )
    emitter = ScriptedEmitter([_edit_json("Beta section.", "Bravo section.")])
    author = LlmAuthor(
        prompt_path=AUTHOR_PROMPT,
        emitter=emitter,
        documents_root=documents_root,
        substrate_fetcher=_substrate_fetcher(),
        doc_ids=["ADR-001"],
    )
    verdict = ArbiterResult(finding.id, "resolvable", "adr-template §4", "determined", "high")
    log = ActionLog()

    result = run_loop(
        header=LedgerHeader(set=["ADR-001"], counted_severities=["BLOCKING", "MATERIAL"]),
        plan=plan,
        arbiter=CannedArbiter({finding.id: verdict}),
        store=LedgerStore(tmp_path / "ledger.json"),
        author=author,
        fetch_documents=RepoDocumentFetcher(documents_root),
        fetch_substrate=_substrate_fetcher(),
        log=log,
        clock=lambda: "2026-07-16T00:00:00Z",
    )

    assert result.exit.kind == "HALT_DECISION"
    assert result.exit.reason == "oscillation"
    assert [f.id for f in result.exit.payload] == [finding.id]
    assert len(emitter.calls) == 1  # the reopened finding was not re-authored
    reopened = result.ledger.find_by_id(finding.id)
    assert reopened.status == "open" and reopened.recurrence_count == 1
    # One proposed escalation, unbundled.
    assert len(log.of_kind("proposed_escalation")) == 1
