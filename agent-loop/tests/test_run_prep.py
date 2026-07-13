# Module: tests.test_run_prep
# Purpose: The run-prep.contract.md §10 test obligations (a–j) for the
#          supervised-run machinery: document/substrate fetchers, per-consumer
#          input isolation, emitter call policy, truncation→parse_drop, the
#          arbiter adapter, provenance/manifest, the live sink, the prep gates,
#          and regression. Every test uses fakes/injected transports — NO real
#          API call is made anywhere in this suite.
# Scope:   Over fetchers, transport, manifest, log sink, run_real, run_loop.

import itertools
import json
from pathlib import Path
from types import SimpleNamespace

import pytest

from agent_loop.arbiter import ArbiterResult, CannedArbiter
from agent_loop.fetchers import (
    DocumentResolutionError,
    RepoDocumentFetcher,
    RunSubstrateFetcher,
    SubstrateError,
    sha256_text,
    validate_substrate_manifest,
)
from agent_loop.ledger import (
    CitedAuthority,
    Finding,
    Ledger,
    LedgerHeader,
    LedgerStore,
)
from agent_loop.log import ActionLog, JsonlFileSink
from agent_loop.manifest import (
    finalize_manifest,
    per_site_token_totals,
    write_prep_manifest,
)
from agent_loop.prep import snapshot_documents
from agent_loop.reviewers import (
    IDENTITY_LAA,
    IDENTITY_SA,
    DocumentSet,
    ScheduledReviewer,
    Substrate,
)
from agent_loop.run_real import (
    ALL_PROMPT_FILES,
    PrepGateError,
    _default_git_docs_status,
    _default_git_head,
    run_prep_gates,
    run_real,
    validate_prep,
)
from agent_loop.runner import run_loop
from agent_loop.transport import (
    AnthropicTransport,
    ApiArbiter,
    ArbiterParseError,
    LlmResponse,
    LlmTransportError,
    build_api_emitter,
)

DESIGN_DIR = Path(__file__).resolve().parents[1] / "design"


# --- shared fakes ------------------------------------------------------------


def _counter_now(step: float = 0.01):
    """A monotonic-ish clock returning strictly increasing floats."""
    counter = itertools.count()
    return lambda: next(counter) * step


def _finding(claim: str, *, source: str = "antagonist-stub") -> Finding:
    return Finding(
        source=source,  # type: ignore[arg-type]
        altitude="LAA",
        severity="MATERIAL",
        target=["DOC-A"],
        locus="l",
        claim=claim,
        cited_authority=CitedAuthority(kind="canonical", ref="AUTH-1"),
    )


class ScriptedTransport:
    """A transport that returns/raises a scripted sequence per call."""

    def __init__(self, script: list) -> None:
        self.calls: list[dict] = []
        self._script = list(script)

    def __call__(self, system, user, model, max_tokens, cache_prefix=None):  # noqa: ANN001
        self.calls.append(
            {
                "system": system,
                "user": user,
                "model": model,
                "max_tokens": max_tokens,
                "cache_prefix": cache_prefix,
            }
        )
        item = self._script.pop(0)
        if isinstance(item, Exception):
            raise item
        if isinstance(item, str):
            return LlmResponse(text=item, input_tokens=11, output_tokens=7)
        return item


class RoutingTransport:
    """Returns reviewer text or arbiter text based on the system prompt."""

    def __init__(self, reviewer_text: str, arbiter_text: str) -> None:
        self.calls: list[dict] = []
        self._reviewer_text = reviewer_text
        self._arbiter_text = arbiter_text

    def __call__(self, system, user, model, max_tokens, cache_prefix=None):  # noqa: ANN001
        self.calls.append(
            {"system": system, "model": model, "max_tokens": max_tokens, "cache_prefix": cache_prefix}
        )
        rid = f"req-{len(self.calls)}"
        if system == "probe":
            return LlmResponse(text="ok", input_tokens=1, output_tokens=1, request_id=rid)
        if "Arbiter-Classifier" in system:
            return LlmResponse(
                text=self._arbiter_text, input_tokens=100, output_tokens=20, request_id=rid
            )
        return LlmResponse(
            text=self._reviewer_text, input_tokens=200, output_tokens=50, request_id=rid
        )


class DispatchTransport:
    """Routes by system prompt: probe / arbiter / reviewer to configured outcomes.

    Each outcome is an LlmResponse, a str (→ response text), or an Exception
    (raised). Probe defaults to a successful minimal response.
    """

    def __init__(self, *, probe=None, reviewer=None, arbiter=None):  # noqa: ANN001
        self.calls: list[dict] = []
        self._probe = probe if probe is not None else LlmResponse("ok", 1, 1)
        self._reviewer = reviewer
        self._arbiter = arbiter

    def __call__(self, system, user, model, max_tokens, cache_prefix=None):  # noqa: ANN001
        self.calls.append(
            {"system": system, "model": model, "max_tokens": max_tokens, "cache_prefix": cache_prefix}
        )
        if system == "probe":
            item = self._probe
        elif "Arbiter-Classifier" in system:
            item = self._arbiter
        else:
            item = self._reviewer
        if isinstance(item, Exception):
            raise item
        if isinstance(item, str):
            return LlmResponse(text=item, input_tokens=10, output_tokens=5)
        return item

    def non_probe_calls(self) -> list[dict]:
        return [c for c in self.calls if c["system"] != "probe"]


_VALID_FINDING_JSON = json.dumps(
    [
        {
            "severity": "MATERIAL",
            "target": ["ADR-001"],
            "locus": "s1",
            "claim": "a real-looking defect",
            "cited_authority": {"kind": "canonical", "ref": "AUTH-1 §2"},
        }
    ]
)
_VALID_CLASSIFICATION_JSON = json.dumps(
    {
        "finding_id": "echoed-value-ignored",
        "classification": "decision-bearing",
        "authority_locus": None,
        "rationale": "authority silent on the fork",
        "confidence": "high",
    }
)


# --- §10a: document fetcher resolution ---------------------------------------


def test_document_fetcher_resolves_one_file_verbatim(tmp_path) -> None:
    (tmp_path / "adr").mkdir()
    (tmp_path / "adr" / "ADR-001-reasoning.md").write_text("VERBATIM\ncontent", encoding="utf-8")
    result = RepoDocumentFetcher(tmp_path)(["ADR-001"])
    assert result.documents == {"ADR-001": "VERBATIM\ncontent"}


def test_document_fetcher_zero_matches_raises(tmp_path) -> None:
    with pytest.raises(DocumentResolutionError):
        RepoDocumentFetcher(tmp_path).resolve("ADR-999")


def test_document_fetcher_multiple_matches_raises_naming_both(tmp_path) -> None:
    (tmp_path / "ADR-001-a.md").write_text("a", encoding="utf-8")
    (tmp_path / "ADR-001-b.md").write_text("b", encoding="utf-8")
    with pytest.raises(DocumentResolutionError) as exc:
        RepoDocumentFetcher(tmp_path).resolve("ADR-001")
    assert "ADR-001-a.md" in str(exc.value) and "ADR-001-b.md" in str(exc.value)


# --- §10b: substrate read + manifest -----------------------------------------


def _write_substrate(substrate_root: Path, files: dict[str, dict[str, str]]) -> None:
    entries = []
    for category, items in files.items():
        directory = substrate_root / category
        directory.mkdir(parents=True, exist_ok=True)
        for stem, content in items.items():
            (directory / f"{stem}.md").write_text(content, encoding="utf-8")
            entries.append(
                {
                    "logical_id": stem,
                    "category": category,
                    "origin": "test-origin",
                    "retrieved": "2026-07-02",
                    "sha256": sha256_text(content),
                }
            )
    (substrate_root / "manifest.json").write_text(json.dumps({"files": entries}), encoding="utf-8")


def test_substrate_fetcher_reads_populated_folder(tmp_path) -> None:
    _write_substrate(
        tmp_path,
        {"authorities": {"adr-template": "A"}, "design-intent": {"vision": "V"}},
    )
    substrate = RunSubstrateFetcher(tmp_path)(["ADR-001"])  # doc_ids ignored
    assert substrate.authorities == {"adr-template": "A"}
    assert substrate.design_intent == {"vision": "V"}


def test_substrate_fetcher_missing_folder_raises(tmp_path) -> None:
    with pytest.raises(SubstrateError):
        RunSubstrateFetcher(tmp_path / "nope")(["ADR-001"])


def test_substrate_fetcher_empty_authorities_raises(tmp_path) -> None:
    # No authorities subdir at all — exercises the not-a-dir read path.
    (tmp_path / "design-intent").mkdir(parents=True)
    (tmp_path / "design-intent" / "v.md").write_text("V", encoding="utf-8")
    with pytest.raises(SubstrateError):
        RunSubstrateFetcher(tmp_path)([])


def test_substrate_fetcher_empty_design_intent_raises(tmp_path) -> None:
    (tmp_path / "authorities").mkdir(parents=True)
    (tmp_path / "authorities" / "a.md").write_text("A", encoding="utf-8")
    (tmp_path / "design-intent").mkdir(parents=True)
    with pytest.raises(SubstrateError):
        RunSubstrateFetcher(tmp_path)([])


def test_validate_substrate_manifest_ok(tmp_path) -> None:
    _write_substrate(tmp_path, {"authorities": {"a": "A"}, "design-intent": {"v": "V"}})
    validate_substrate_manifest(tmp_path)  # no raise


def test_validate_substrate_manifest_missing_raises(tmp_path) -> None:
    with pytest.raises(SubstrateError):
        validate_substrate_manifest(tmp_path)


def test_validate_substrate_manifest_hash_mismatch_raises(tmp_path) -> None:
    _write_substrate(tmp_path, {"authorities": {"a": "A"}, "design-intent": {"v": "V"}})
    (tmp_path / "authorities" / "a.md").write_text("MUTATED", encoding="utf-8")
    with pytest.raises(SubstrateError):
        validate_substrate_manifest(tmp_path)


def test_validate_substrate_manifest_unlisted_file_raises(tmp_path) -> None:
    _write_substrate(tmp_path, {"authorities": {"a": "A"}, "design-intent": {"v": "V"}})
    (tmp_path / "authorities" / "extra.md").write_text("X", encoding="utf-8")
    with pytest.raises(SubstrateError):
        validate_substrate_manifest(tmp_path)


def test_validate_substrate_manifest_bad_json_raises(tmp_path) -> None:
    (tmp_path / "manifest.json").write_text("{not json", encoding="utf-8")
    with pytest.raises(SubstrateError):
        validate_substrate_manifest(tmp_path)


def test_validate_substrate_manifest_missing_field_raises(tmp_path) -> None:
    (tmp_path / "authorities").mkdir(parents=True)
    (tmp_path / "authorities" / "a.md").write_text("A", encoding="utf-8")
    (tmp_path / "manifest.json").write_text(
        json.dumps({"files": [{"logical_id": "a", "category": "authorities"}]}), encoding="utf-8"
    )
    with pytest.raises(SubstrateError):
        validate_substrate_manifest(tmp_path)


def test_validate_substrate_manifest_bad_category_raises(tmp_path) -> None:
    (tmp_path / "manifest.json").write_text(
        json.dumps(
            {
                "files": [
                    {
                        "logical_id": "a",
                        "category": "bogus",
                        "origin": "o",
                        "retrieved": "t",
                        "sha256": "x",
                    }
                ]
            }
        ),
        encoding="utf-8",
    )
    with pytest.raises(SubstrateError):
        validate_substrate_manifest(tmp_path)


def test_validate_substrate_manifest_not_object_raises(tmp_path) -> None:
    (tmp_path / "manifest.json").write_text(json.dumps(["not", "an", "object"]), encoding="utf-8")
    with pytest.raises(SubstrateError):
        validate_substrate_manifest(tmp_path)


def test_validate_substrate_manifest_lists_missing_file_raises(tmp_path) -> None:
    # A well-formed entry whose file is absent on disk.
    (tmp_path / "manifest.json").write_text(
        json.dumps(
            {
                "files": [
                    {
                        "logical_id": "ghost",
                        "category": "authorities",
                        "origin": "o",
                        "retrieved": "t",
                        "sha256": "deadbeef",
                    }
                ]
            }
        ),
        encoding="utf-8",
    )
    with pytest.raises(SubstrateError):
        validate_substrate_manifest(tmp_path)


# --- §10c: per-consumer records/substrate isolation --------------------------


def test_reviewer_mutating_records_substrate_cannot_affect_others(tmp_path) -> None:
    seen: dict = {}

    def mutator_run(pn, snap, records, substrate, log):  # noqa: ANN001
        records.documents["INJECTED"] = "leak"
        substrate.authorities["INJECTED"] = "leak"
        seen.setdefault("mutator_records", []).append(records)
        return []

    def observer_run(pn, snap, records, substrate, log):  # noqa: ANN001
        seen.setdefault("observer_doc_keys", []).append(sorted(records.documents))
        seen.setdefault("observer_auth_keys", []).append(sorted(substrate.authorities))
        seen.setdefault("observer_records", []).append(records)
        return [_finding("observer finding")]

    def plan(pass_number, snapshot, log):  # noqa: ANN001
        return [
            ScheduledReviewer(IDENTITY_LAA, mutator_run),
            ScheduledReviewer(IDENTITY_SA, observer_run),
        ]

    fetch_docs = lambda ids: DocumentSet(documents={"ADR-001": "doc"})  # noqa: E731
    fetch_sub = lambda ids: Substrate(authorities={"a": "A"}, design_intent={"v": "V"})  # noqa: E731

    result = run_loop(
        header=LedgerHeader(set=["ADR-001"], counted_severities=["BLOCKING", "MATERIAL"]),
        plan=plan,
        arbiter=CannedArbiter(
            default=ArbiterResult("_", "resolvable", "AUTH-1 §2", "r", "high")
        ),
        store=LedgerStore(tmp_path / "c.json"),
        fetch_documents=fetch_docs,
        fetch_substrate=fetch_sub,
        max_passes=5,
    )

    # Later reviewer (same pass and the next pass) never sees the injection.
    assert all("INJECTED" not in keys for keys in seen["observer_doc_keys"])
    assert all("INJECTED" not in keys for keys in seen["observer_auth_keys"])
    # Ran more than one pass, so cross-pass isolation is exercised.
    assert len(seen["observer_doc_keys"]) >= 2
    # Distinct objects per consumer.
    assert seen["mutator_records"][0] is not seen["observer_records"][0]
    # The admitted ledger carries only the observer's finding — no leaked doc.
    assert [f.claim for f in result.ledger.findings] == ["observer finding"]


# --- §10d: emitter call policy -----------------------------------------------


def test_emitter_success_logs_llm_call_with_params_and_hash() -> None:
    log = ActionLog()
    transport = ScriptedTransport(["reviewer output"])
    emit = build_api_emitter(
        site_label="antagonist-LAA",
        model="claude-opus-4-8",
        max_tokens=8192,
        log=log,
        transport=transport,
        now=_counter_now(),
        sleeper=lambda s: None,
    )
    out = emit("SYSTEM", "USER")
    assert out == "reviewer output"
    # params + system reached the transport exactly as configured.
    assert transport.calls[0]["model"] == "claude-opus-4-8"
    assert transport.calls[0]["max_tokens"] == 8192
    assert transport.calls[0]["system"] == "SYSTEM"
    # provenance fields present.
    call = log.of_kind("llm_call")[0].detail
    assert call["site"] == "antagonist-LAA"
    assert call["system_sha256"] == sha256_text("SYSTEM")
    assert call["input_tokens"] == 11 and call["output_tokens"] == 7
    assert "latency_ms" in call


def test_emitter_one_transport_failure_then_success() -> None:
    log = ActionLog()
    slept: list[float] = []
    transport = ScriptedTransport([LlmTransportError("rate limit"), "ok"])
    emit = build_api_emitter(
        site_label="antagonist-SA",
        model="m",
        max_tokens=100,
        log=log,
        transport=transport,
        now=_counter_now(),
        sleeper=slept.append,
        backoff_seconds=30.0,
    )
    assert emit("s", "u") == "ok"
    assert slept == [30.0]  # bounded backoff applied
    assert len(log.of_kind("llm_retry")) == 1
    assert log.of_kind("llm_retry")[0].detail["retry_kind"] == "transport"
    assert len(log.of_kind("llm_call")) == 1


def test_emitter_two_transport_failures_raise_no_llm_call() -> None:
    log = ActionLog()
    transport = ScriptedTransport([LlmTransportError("boom"), LlmTransportError("boom2")])
    emit = build_api_emitter(
        site_label="antagonist-EA",
        model="m",
        max_tokens=100,
        log=log,
        transport=transport,
        now=_counter_now(),
        sleeper=lambda s: None,
    )
    with pytest.raises(LlmTransportError):
        emit("s", "u")
    assert log.of_kind("llm_call") == []
    assert len(log.of_kind("llm_retry")) == 1


def test_emitter_failure_aborts_run_with_no_partial_admission(tmp_path) -> None:
    # A hat whose emitter fails twice aborts the run; no finding is admitted.
    from agent_loop.real_hats import build_real_reviewer, real_hat_plan
    from agent_loop.reviewers import IDENTITY_COHERENCE, IDENTITY_EA

    log = ActionLog()
    dead = ScriptedTransport([LlmTransportError("x"), LlmTransportError("x")])
    ok = ScriptedTransport(["[]"] * 4)

    def emitter_for(transport):
        return build_api_emitter(
            site_label="s",
            model="m",
            max_tokens=10,
            log=log,
            transport=transport,
            now=_counter_now(),
            sleeper=lambda s: None,
        )

    plan = real_hat_plan(
        build_real_reviewer(IDENTITY_LAA, DESIGN_DIR / "antagonist-LAA.prompt.md", emitter_for(dead)),
        build_real_reviewer(IDENTITY_SA, DESIGN_DIR / "antagonist-SA.prompt.md", emitter_for(ok)),
        build_real_reviewer(IDENTITY_EA, DESIGN_DIR / "antagonist-EA.prompt.md", emitter_for(ok)),
        build_real_reviewer(IDENTITY_COHERENCE, DESIGN_DIR / "coherence-sweep.prompt.md", emitter_for(ok)),
    )
    store = LedgerStore(tmp_path / "abort.json")
    with pytest.raises(LlmTransportError):
        run_loop(
            header=LedgerHeader(set=["ADR-001"], counted_severities=["BLOCKING", "MATERIAL"]),
            plan=plan,
            arbiter=CannedArbiter(),
            store=store,
            log=log,
        )
    # Ledger was saved only with the header — no findings admitted this pass.
    assert store.load().findings == []


# --- §10e: truncation surfaces as parse_drop ---------------------------------


def test_truncated_json_surfaces_as_parse_drop(tmp_path) -> None:
    from agent_loop.real_hats import build_real_reviewer

    log = ActionLog()
    transport = ScriptedTransport(['[{"severity":"MATERIAL","target":["ADR-001"'])  # truncated
    emit = build_api_emitter(
        site_label="antagonist-LAA",
        model="m",
        max_tokens=10,
        log=log,
        transport=transport,
        now=_counter_now(),
        sleeper=lambda s: None,
    )
    # redraw=False isolates the parse seam: this asserts one truncated emission
    # surfaces as one parse_drop, without the below-floor re-draw (RBT-49 Item 2).
    reviewer = build_real_reviewer(
        IDENTITY_LAA, DESIGN_DIR / "antagonist-LAA.prompt.md", emit, redraw=False
    )
    snapshot = Ledger(header=LedgerHeader(set=[], counted_severities=["MATERIAL"]))
    findings = reviewer.run(
        1, snapshot, DocumentSet(documents={}), Substrate(authorities={}, design_intent={}), log
    )
    assert findings == []
    assert len(log.of_kind("parse_dropped")) == 1


# --- §10f: arbiter adapter ---------------------------------------------------


def _api_arbiter(log, transport):
    return ApiArbiter(
        prompt_path=DESIGN_DIR / "arbiter-classifier.prompt.md",
        transport=transport,
        log=log,
        model="claude-opus-4-8",
        max_tokens=8192,
        now=_counter_now(),
        sleeper=lambda s: None,
    )


def test_arbiter_valid_output_parses_and_stamps() -> None:
    log = ActionLog()
    arbiter = _api_arbiter(log, ScriptedTransport([_VALID_CLASSIFICATION_JSON]))
    result = arbiter.classify(_finding("some finding"), {"a": "A"}, {"v": "V"})
    assert result.classification == "decision-bearing"
    assert result.confidence == "high"
    # finding_id is stamped from the finding, not the model's echo.
    assert result.finding_id == _finding("some finding").id
    assert log.of_kind("llm_call")[0].detail["site"] == "arbiter"


def test_arbiter_malformed_then_valid_retries_once() -> None:
    log = ActionLog()
    arbiter = _api_arbiter(log, ScriptedTransport(["not json", _VALID_CLASSIFICATION_JSON]))
    result = arbiter.classify(_finding("f"), {"a": "A"}, {"v": "V"})
    assert result.classification == "decision-bearing"
    retries = log.of_kind("llm_retry")
    assert len(retries) == 1 and retries[0].detail["retry_kind"] == "content"


def test_arbiter_malformed_twice_aborts_never_fabricates() -> None:
    log = ActionLog()
    arbiter = _api_arbiter(log, ScriptedTransport(["bad", "still bad"]))
    with pytest.raises(ArbiterParseError):
        arbiter.classify(_finding("f"), {"a": "A"}, {"v": "V"})


def test_arbiter_low_confidence_resolvable_is_malformed() -> None:
    # A resolvable at low confidence violates the ArbiterResult invariant → a
    # content malformation, retried then aborted, never fabricated.
    log = ActionLog()
    bad = json.dumps(
        {
            "finding_id": "x",
            "classification": "resolvable",
            "authority_locus": "AUTH-1 §2",
            "rationale": "r",
            "confidence": "low",
        }
    )
    arbiter = _api_arbiter(log, ScriptedTransport([bad, bad]))
    with pytest.raises(ArbiterParseError):
        arbiter.classify(_finding("f"), {"a": "A"}, {"v": "V"})


def test_arbiter_transport_failure_retries_then_succeeds() -> None:
    log = ActionLog()
    arbiter = _api_arbiter(
        log, ScriptedTransport([LlmTransportError("5xx"), _VALID_CLASSIFICATION_JSON])
    )
    result = arbiter.classify(_finding("f"), {}, {})
    assert result.classification == "decision-bearing"
    assert log.of_kind("llm_retry")[0].detail["retry_kind"] == "transport"


def test_arbiter_formats_non_dict_substrate() -> None:
    # authorities/design_intent handed as plain strings still assemble (str()).
    log = ActionLog()
    transport = ScriptedTransport([_VALID_CLASSIFICATION_JSON])
    arbiter = _api_arbiter(log, transport)
    result = arbiter.classify(_finding("f"), "AUTHORITY TEXT", "INTENT TEXT")
    assert result.classification == "decision-bearing"
    assert "AUTHORITY TEXT" in transport.calls[0]["user"]


# --- §10f: corrective content retry (names the defect on attempt 2) ----------


def test_arbiter_fenced_valid_json_parses_without_corrective_retry() -> None:
    # Fenced-valid JSON parses on attempt 1 — no retry, one call, no corrective.
    log = ActionLog()
    fenced = "```json\n" + _VALID_CLASSIFICATION_JSON + "\n```"
    transport = ScriptedTransport([fenced])
    result = _api_arbiter(log, transport).classify(_finding("f"), {}, {})
    assert result.classification == "decision-bearing"
    assert log.of_kind("llm_retry") == []
    assert len(transport.calls) == 1


def test_arbiter_content_retry_is_corrective_names_missing_field() -> None:
    # attempt 1 omits a required key → attempt 2's user block names the field and
    # restates the Output-section instruction; the repaired output returns.
    log = ActionLog()
    missing_confidence = json.dumps(
        {
            "finding_id": "x",
            "classification": "decision-bearing",
            "authority_locus": None,
            "rationale": "r",
        }
    )
    transport = ScriptedTransport([missing_confidence, _VALID_CLASSIFICATION_JSON])
    result = _api_arbiter(log, transport).classify(_finding("f"), {"a": "A"}, {"v": "V"})
    assert result.classification == "decision-bearing"  # repair success returns the result
    first_user, second_user = transport.calls[0]["user"], transport.calls[1]["user"]
    assert "COULD NOT BE PARSED" not in first_user  # no corrective on the first attempt
    assert "missing required key(s): confidence" in second_user  # names the actual defect
    assert "all five fields, no fences, first character {" in second_user  # restated
    assert "FINDING:" in second_user  # appended to the base block, not a replacement
    # The corrective is recorded on the content-retry event.
    assert log.of_kind("llm_retry")[0].detail["retry_kind"] == "content"
    assert log.of_kind("llm_retry")[0].detail["defect"] == (
        "the previous output was missing required key(s): confidence"
    )


def test_arbiter_content_retry_names_json_parse_failure() -> None:
    log = ActionLog()
    transport = ScriptedTransport(["not json at all", _VALID_CLASSIFICATION_JSON])
    result = _api_arbiter(log, transport).classify(_finding("f"), {}, {})
    assert result.classification == "decision-bearing"
    assert "was not valid JSON" in transport.calls[1]["user"]


def test_arbiter_content_retry_names_non_object() -> None:
    log = ActionLog()
    transport = ScriptedTransport(["[1, 2, 3]", _VALID_CLASSIFICATION_JSON])
    result = _api_arbiter(log, transport).classify(_finding("f"), {}, {})
    assert result.classification == "decision-bearing"
    assert "was not a JSON object" in transport.calls[1]["user"]


def test_arbiter_content_retry_names_invalid_vocabulary() -> None:
    log = ActionLog()
    bad_vocab = json.dumps(
        {
            "finding_id": "x",
            "classification": "not-a-real-class",
            "authority_locus": None,
            "rationale": "r",
            "confidence": "high",
        }
    )
    transport = ScriptedTransport([bad_vocab, _VALID_CLASSIFICATION_JSON])
    result = _api_arbiter(log, transport).classify(_finding("f"), {}, {})
    assert result.classification == "decision-bearing"
    assert "invalid vocabulary value" in transport.calls[1]["user"]


def test_arbiter_corrective_retry_failure_still_raises() -> None:
    # A corrective second attempt still malformed aborts (never fabricates); the
    # corrective was in fact sent on the retry.
    log = ActionLog()
    transport = ScriptedTransport(["not json", "still not json"])
    with pytest.raises(ArbiterParseError):
        _api_arbiter(log, transport).classify(_finding("f"), {}, {})
    assert "COULD NOT BE PARSED" in transport.calls[1]["user"]


# --- Anthropic transport (fake client — no SDK/network) ----------------------


def test_anthropic_transport_extracts_text_and_usage() -> None:
    message = SimpleNamespace(
        content=[SimpleNamespace(text="hello "), SimpleNamespace(text="world")],
        usage=SimpleNamespace(input_tokens=12, output_tokens=3),
    )
    seen: dict = {}

    def create(**kw):
        seen.update(kw)
        return message

    client = SimpleNamespace(messages=SimpleNamespace(create=create))
    response = AnthropicTransport(client)("sys", "usr", "m", 100)
    assert response.text == "hello world"
    assert response.input_tokens == 12 and response.output_tokens == 3
    # No sampling parameters reach the API — only max_tokens (amendment).
    assert "temperature" not in seen and "top_p" not in seen and "top_k" not in seen
    assert seen["max_tokens"] == 100


def test_anthropic_transport_wraps_sdk_errors() -> None:
    def boom(**kwargs):
        raise RuntimeError("rate limited")

    client = SimpleNamespace(messages=SimpleNamespace(create=boom))
    with pytest.raises(LlmTransportError):
        AnthropicTransport(client)("s", "u", "m", 10)


# --- run-016 diagnosis rider: transport captures the API stop_reason ---------


def test_anthropic_transport_captures_stop_reason() -> None:
    message = SimpleNamespace(
        content=[SimpleNamespace(text="ok")],
        usage=SimpleNamespace(input_tokens=5, output_tokens=2),
        stop_reason="end_turn",
    )
    client = SimpleNamespace(messages=SimpleNamespace(create=lambda **kw: message))
    response = AnthropicTransport(client)("sys", "usr", "m", 10)
    assert response.stop_reason == "end_turn"


def test_anthropic_transport_stop_reason_absent_defaults_none() -> None:
    message = SimpleNamespace(  # a response object with no stop_reason attribute
        content=[SimpleNamespace(text="ok")],
        usage=SimpleNamespace(input_tokens=5, output_tokens=2),
    )
    client = SimpleNamespace(messages=SimpleNamespace(create=lambda **kw: message))
    response = AnthropicTransport(client)("sys", "usr", "m", 10)
    assert response.stop_reason is None


def test_llm_call_records_stop_reason() -> None:
    log = ActionLog()

    def transport(system, user, model, max_tokens, cache_prefix=None):  # noqa: ANN001
        return LlmResponse(text="[]", input_tokens=10, output_tokens=2, stop_reason="end_turn")

    emit = build_api_emitter(
        site_label="antagonist-SA", model="m", max_tokens=10, log=log,
        transport=transport, now=_counter_now(), sleeper=lambda s: None,
    )
    emit("sys", "user")
    call = log.of_kind("llm_call")[0]
    assert call.detail["stop_reason"] == "end_turn"


# --- §10g: provenance + manifest ---------------------------------------------


def test_per_site_token_totals_aggregates() -> None:
    log = ActionLog()
    log.emit("llm_call", site="antagonist-LAA", input_tokens=100, output_tokens=10)
    log.emit("llm_call", site="antagonist-LAA", input_tokens=50, output_tokens=5)
    log.emit("llm_call", site="arbiter", input_tokens=20, output_tokens=2)
    totals = per_site_token_totals(log)
    assert totals["antagonist-LAA"] == {
        "input_tokens": 150,
        "output_tokens": 15,
        "cache_creation_input_tokens": 0,
        "cache_read_input_tokens": 0,
        "calls": 2,
    }
    assert totals["arbiter"]["calls"] == 1


def test_manifest_prep_then_finalize(tmp_path) -> None:
    manifest_path = tmp_path / "manifest.json"
    write_prep_manifest(
        manifest_path,
        run_id="run-001",
        created="2026-07-02T00:00:00Z",
        document_set={"ADR-001": {"snapshot_path": "documents/ADR-001-x.md", "sha256": "abc"}},
        head_sha="48e031a",
        prompt_hashes={"a.prompt.md": "hash"},
        substrate_manifest_ref="substrate/manifest.json",
        model="claude-opus-4-8",
        parameters={"max_tokens": 8192},
    )
    prep = json.loads(manifest_path.read_text())
    assert prep["head_sha"] == "48e031a" and prep["finalized"] is False

    finalize_manifest(
        manifest_path,
        router_exit="HALT_DECISION:decision-bearing",
        passes_run=1,
        per_site_tokens={"antagonist-LAA": {"input_tokens": 1, "output_tokens": 1, "calls": 1}},
        wall_clock_seconds=12.5,
    )
    final = json.loads(manifest_path.read_text())
    assert final["finalized"] is True
    assert final["router_exit"] == "HALT_DECISION:decision-bearing"
    assert final["per_site_tokens"]["antagonist-LAA"]["calls"] == 1


# --- §10h: live sink ---------------------------------------------------------


def test_jsonl_sink_writes_per_event_flushed(tmp_path) -> None:
    sink = JsonlFileSink(tmp_path / "action-log.jsonl")
    log = ActionLog(sink=sink)
    log.emit("continue", pass_number=1)
    log.emit("halt", reason="decision-bearing")
    # Readable BEFORE close — proving per-event flush (incremental).
    lines = (tmp_path / "action-log.jsonl").read_text().splitlines()
    assert len(lines) == 2
    assert json.loads(lines[0])["kind"] == "continue"
    sink.close()


def test_run_loop_streams_all_events_to_sink(tmp_path) -> None:
    from agent_loop.scenarios import scenario_s1

    sink = JsonlFileSink(tmp_path / "s1.jsonl")
    log = ActionLog(sink=sink)
    scenario = scenario_s1()
    run_loop(
        header=scenario.header,
        plan=__import__("agent_loop.reviewers", fromlist=["stub_plan"]).stub_plan(
            scenario.antagonist, scenario.coherence
        ),
        arbiter=scenario.arbiter,
        store=LedgerStore(tmp_path / "s1.json"),
        fix_changes=scenario.fix_changes,
        log=log,
    )
    sink.close()
    lines = (tmp_path / "s1.jsonl").read_text().splitlines()
    # Every in-memory event streamed to the file (nothing buffered to exit).
    assert len(lines) == len(log.events)
    assert len(log.events) > 0


# --- §10i: prep gates fail-loud before any emitter call ----------------------


def _prep_env(tmp_path: Path, doc_ids: list[str]):
    sofia_root = tmp_path / "sofia"
    docs = sofia_root / "docs"
    docs.mkdir(parents=True)
    for doc_id in doc_ids:
        (docs / f"{doc_id}-distilled.md").write_text(f"content of {doc_id}", encoding="utf-8")
    runs_root = tmp_path / "runs"
    run_id = "run-001-test"
    substrate_root = runs_root / run_id / "substrate"
    _write_substrate(
        substrate_root,
        {"authorities": {"adr-template": "A"}, "design-intent": {"vision": "V"}},
    )
    # RBT-51 Item 3: the runner consumes a frozen document snapshot, so a prepared
    # folder carries one (produced here by the prep tool — the producer/consumer
    # pair exercised together). gate 3 resolves within it and gate 8 verifies it.
    snapshot_documents(
        doc_ids, docs_root=docs, sofia_root=sofia_root, run_dir=runs_root / run_id,
        run_id=run_id, sofia_head_sha="HEAD-SNAPSHOT", retrieved="2026-07-02",
    )
    return {
        "run_id": run_id,
        "doc_ids": doc_ids,
        "sofia_root": sofia_root,
        "runs_root": runs_root,
        "prompt_dir": DESIGN_DIR,
        "git_status": lambda root: "",  # clean
        "env": {"ANTHROPIC_API_KEY": "test-key"},
    }


def test_gates_only_with_key_passes_1_6_and_reports_probe_pending(tmp_path) -> None:
    # Gates-only (validate_prep) makes no API call: gate 7 reports pending even
    # with a key, because no probe is configured.
    env = _prep_env(tmp_path, ["ADR-001", "ADR-002", "DDR-001", "DDR-002"])
    report = validate_prep(
        env["run_id"],
        env["doc_ids"],
        sofia_root=env["sofia_root"],
        runs_root=env["runs_root"],
        prompt_dir=env["prompt_dir"],
        git_status=env["git_status"],
        env=env["env"],
    )
    assert [r.number for r in report.results] == [1, 2, 3, 4, 5, 6, 7, 8]
    assert all(r.passed for r in report.results if r.number <= 6)
    gate7 = next(r for r in report.results if r.number == 7)
    assert gate7.pending and not gate7.passed
    # Gate 8 (document snapshot) is a free local check that passes on a prepared
    # folder, independent of the probe.
    gate8 = next(r for r in report.results if r.number == 8)
    assert gate8.passed and not gate8.pending
    assert not report.ok  # a pending probe means the run cannot launch yet


def test_gates_only_without_key_reports_6_and_7_pending(tmp_path) -> None:
    # Phase-3 shape: no key → gates 1-5 pass, 6 and 7 pending.
    env = _prep_env(tmp_path, ["ADR-001", "ADR-002", "DDR-001", "DDR-002"])
    report = validate_prep(
        env["run_id"],
        env["doc_ids"],
        sofia_root=env["sofia_root"],
        runs_root=env["runs_root"],
        prompt_dir=env["prompt_dir"],
        git_status=env["git_status"],
        env={},  # no ANTHROPIC_API_KEY
    )
    assert all(r.passed for r in report.results if r.number <= 5)
    pending = {r.number for r in report.results if r.pending}
    assert pending == {6, 7}


def test_gate5_empty_system_prompt_is_reported(tmp_path) -> None:
    # A prompt file that loads but has an empty ## System block fails gate 5.
    prompt_dir = tmp_path / "prompts"
    prompt_dir.mkdir()
    for name in ALL_PROMPT_FILES:
        (prompt_dir / name).write_text(
            (DESIGN_DIR / name).read_text(encoding="utf-8"), encoding="utf-8"
        )
    (prompt_dir / ALL_PROMPT_FILES[0]).write_text(
        "# Title\n\n## System\n\n## User\nx\n", encoding="utf-8"
    )
    env = _prep_env(tmp_path, ["ADR-001"])
    report = run_prep_gates(
        env["run_id"], env["doc_ids"], sofia_root=env["sofia_root"],
        runs_root=env["runs_root"], prompt_dir=prompt_dir,
        git_status=env["git_status"], env=env["env"],
    )
    gate5 = next(r for r in report.results if r.number == 5)
    assert not gate5.passed and "empty ## System" in gate5.detail


def test_git_helpers_run_against_the_real_repo() -> None:
    # Cover the subprocess git helpers (no LLM); the repo root holds this file.
    repo_root = DESIGN_DIR.parents[1]
    status = _default_git_docs_status(repo_root)
    head = _default_git_head(repo_root)
    assert isinstance(status, str)
    assert len(head) == 40  # a git object SHA


def test_validate_prep_has_no_side_effects(tmp_path) -> None:
    env = _prep_env(tmp_path, ["ADR-001"])
    run_dir = env["runs_root"] / env["run_id"]
    validate_prep(
        env["run_id"], env["doc_ids"], sofia_root=env["sofia_root"],
        runs_root=env["runs_root"], prompt_dir=env["prompt_dir"],
        git_status=env["git_status"], env=env["env"],
    )
    assert not (run_dir / "ledger.json").exists()


@pytest.mark.parametrize("breaker", ["gate1", "gate2", "gate3", "gate4", "gate5", "gate6"])
def test_each_gate_failure_aborts_before_any_emitter_call(tmp_path, breaker) -> None:
    env = _prep_env(tmp_path, ["ADR-001", "ADR-002", "DDR-001", "DDR-002"])
    transport = ScriptedTransport([])  # any call would IndexError — proves none happen
    kwargs = dict(
        sofia_root=env["sofia_root"],
        runs_root=env["runs_root"],
        prompt_dir=env["prompt_dir"],
        transport=transport,
        git_status=env["git_status"],
        head_sha="HEAD",
        env=dict(env["env"]),
    )
    run_dir = env["runs_root"] / env["run_id"]
    if breaker == "gate1":
        (run_dir).mkdir(parents=True, exist_ok=True)
        (run_dir / "ledger.json").write_text("{}", encoding="utf-8")
    elif breaker == "gate2":
        kwargs["git_status"] = lambda root: " M docs/adr/ADR-001.md\n"
    elif breaker == "gate3":
        env["doc_ids"] = ["ADR-404"]
    elif breaker == "gate4":
        import shutil

        shutil.rmtree(run_dir / "substrate")
    elif breaker == "gate5":
        kwargs["prompt_dir"] = tmp_path / "empty-prompts"
        (tmp_path / "empty-prompts").mkdir()
    elif breaker == "gate6":
        kwargs["env"] = {}

    with pytest.raises(PrepGateError):
        run_real(env["run_id"], env["doc_ids"], **kwargs)
    assert transport.calls == []  # no LLM call before the abort


# --- §10g/§10j: full run_real integration (fakes only) -----------------------


def test_run_real_integration_writes_finalized_manifest_and_log(tmp_path) -> None:
    env = _prep_env(tmp_path, ["ADR-001", "ADR-002", "DDR-001", "DDR-002"])
    transport = RoutingTransport(_VALID_FINDING_JSON, _VALID_CLASSIFICATION_JSON)
    result = run_real(
        env["run_id"],
        env["doc_ids"],
        sofia_root=env["sofia_root"],
        runs_root=env["runs_root"],
        prompt_dir=env["prompt_dir"],
        transport=transport,
        git_status=env["git_status"],
        head_sha="48e031a-descendant",
        created="2026-07-02T00:00:00Z",
        now=_counter_now(),
        sleeper=lambda s: None,
        env=env["env"],
    )
    run_dir = env["runs_root"] / env["run_id"]

    # Router halted on the decision-bearing finding (dry-mode-legit exit).
    assert result.exit.kind == "HALT_DECISION"

    # Manifest finalized with provenance + per-hat cost.
    manifest = json.loads((run_dir / "manifest.json").read_text())
    assert manifest["finalized"] is True
    assert manifest["head_sha"] == "48e031a-descendant"
    assert len(manifest["prompt_sha256"]) == 5
    assert set(manifest["per_site_tokens"]) >= {
        "antagonist-LAA",
        "antagonist-SA",
        "antagonist-EA",
        "coherence",
        "arbiter",
    }
    assert manifest["passes_run"] == result.passes_run
    # Manifest parameters reflect the actual request payload: max_tokens only.
    assert manifest["parameters"] == {"max_tokens": 8192}
    # Calibration record: the manifest pins the live prompt set's generation.
    assert manifest["calibration"]["generation"] == 8
    # §7/T6: document_set records the frozen snapshot provenance (path + sha256),
    # not a working-tree path.
    doc_entry = manifest["document_set"]["ADR-001"]
    assert doc_entry["snapshot_path"] == "documents/ADR-001-distilled.md"
    assert doc_entry["sha256"] == sha256_text("content of ADR-001")
    # The gate-7 probe made prep-time contact (system == "probe").
    assert any(c["system"] == "probe" for c in transport.calls)

    # Live log streamed to disk and carries llm_call provenance.
    log_lines = (run_dir / "action-log.jsonl").read_text().splitlines()
    kinds = [json.loads(line)["kind"] for line in log_lines]
    assert "llm_call" in kinds
    assert len(log_lines) == len(result.log.events)


# --- launch-hardening amendments (2026-07-02) --------------------------------


def test_gate7_probe_pass_when_probe_succeeds(tmp_path) -> None:
    env = _prep_env(tmp_path, ["ADR-001", "ADR-002", "DDR-001", "DDR-002"])
    calls: list[int] = []
    report = run_prep_gates(
        env["run_id"], env["doc_ids"], sofia_root=env["sofia_root"],
        runs_root=env["runs_root"], prompt_dir=env["prompt_dir"],
        git_status=env["git_status"], env=env["env"],
        probe=lambda: calls.append(1),
    )
    assert report.ok
    gate7 = next(r for r in report.results if r.number == 7)
    assert gate7.passed and not gate7.pending
    assert calls == [1]  # probe was invoked exactly once


def test_gate7_probe_fail_is_a_prep_failure(tmp_path) -> None:
    env = _prep_env(tmp_path, ["ADR-001", "ADR-002", "DDR-001", "DDR-002"])

    def boom():
        raise LlmTransportError("401 invalid key")

    report = run_prep_gates(
        env["run_id"], env["doc_ids"], sofia_root=env["sofia_root"],
        runs_root=env["runs_root"], prompt_dir=env["prompt_dir"],
        git_status=env["git_status"], env=env["env"], probe=boom,
    )
    assert not report.ok
    gate7 = next(r for r in report.results if r.number == 7)
    assert not gate7.passed and not gate7.pending and "401" in gate7.detail


def test_gate7_not_probed_when_earlier_gate_fails(tmp_path) -> None:
    # Fast-fail: an earlier gate failing means the token is never spent.
    env = _prep_env(tmp_path, ["ADR-001", "ADR-002", "DDR-001", "DDR-002"])
    calls: list[int] = []
    report = run_prep_gates(
        env["run_id"], env["doc_ids"], sofia_root=env["sofia_root"],
        runs_root=env["runs_root"], prompt_dir=env["prompt_dir"],
        git_status=lambda root: " M docs/adr/ADR-001.md\n",  # gate 2 fails (dirty docs)
        env=env["env"], probe=lambda: calls.append(1),
    )
    assert calls == []  # probe not attempted
    gate7 = next(r for r in report.results if r.number == 7)
    assert gate7.pending


def test_run_real_probe_failure_aborts_before_any_reviewer_call(tmp_path) -> None:
    env = _prep_env(tmp_path, ["ADR-001", "ADR-002", "DDR-001", "DDR-002"])
    transport = DispatchTransport(probe=LlmTransportError("400 parameter shape"))
    with pytest.raises(PrepGateError):
        run_real(
            env["run_id"], env["doc_ids"], sofia_root=env["sofia_root"],
            runs_root=env["runs_root"], prompt_dir=env["prompt_dir"],
            transport=transport, git_status=env["git_status"], head_sha="H",
            now=_counter_now(), sleeper=lambda s: None, env=dict(env["env"]),
        )
    # The probe was attempted; no reviewer/arbiter call followed.
    assert transport.non_probe_calls() == []


def test_run_aborted_event_on_transport_exhaustion(tmp_path) -> None:
    env = _prep_env(tmp_path, ["ADR-001", "ADR-002", "DDR-001", "DDR-002"])
    transport = DispatchTransport(reviewer=LlmTransportError("5xx"))  # probe ok, reviewers die
    with pytest.raises(LlmTransportError):
        run_real(
            env["run_id"], env["doc_ids"], sofia_root=env["sofia_root"],
            runs_root=env["runs_root"], prompt_dir=env["prompt_dir"],
            transport=transport, git_status=env["git_status"], head_sha="H",
            now=_counter_now(), sleeper=lambda s: None, env=dict(env["env"]),
        )
    run_dir = env["runs_root"] / env["run_id"]
    lines = (run_dir / "action-log.jsonl").read_text().splitlines()
    last = json.loads(lines[-1])
    assert last["kind"] == "run_aborted" and "5xx" in last["reason"]
    # Manifest left unfinalized on abort.
    assert json.loads((run_dir / "manifest.json").read_text())["finalized"] is False


def test_run_aborted_event_on_arbiter_content_exhaustion(tmp_path) -> None:
    env = _prep_env(tmp_path, ["ADR-001", "ADR-002", "DDR-001", "DDR-002"])
    transport = DispatchTransport(reviewer=_VALID_FINDING_JSON, arbiter="not a classification")
    with pytest.raises(ArbiterParseError):
        run_real(
            env["run_id"], env["doc_ids"], sofia_root=env["sofia_root"],
            runs_root=env["runs_root"], prompt_dir=env["prompt_dir"],
            transport=transport, git_status=env["git_status"], head_sha="H",
            now=_counter_now(), sleeper=lambda s: None, env=dict(env["env"]),
        )
    run_dir = env["runs_root"] / env["run_id"]
    lines = (run_dir / "action-log.jsonl").read_text().splitlines()
    assert json.loads(lines[-1])["kind"] == "run_aborted"


# --- emission hardening (2026-07-02): capture, fence, instrument guard --------


def test_arbiter_parses_fenced_classification() -> None:
    log = ActionLog()
    fenced = "```json\n" + _VALID_CLASSIFICATION_JSON + "\n```"
    arbiter = _api_arbiter(log, ScriptedTransport([fenced]))
    result = arbiter.classify(_finding("f"), {}, {})
    assert result.classification == "decision-bearing"


def test_run_real_captures_raw_emissions_and_stamps_provenance(tmp_path) -> None:
    env = _prep_env(tmp_path, ["ADR-001", "ADR-002", "DDR-001", "DDR-002"])
    transport = RoutingTransport(_VALID_FINDING_JSON, _VALID_CLASSIFICATION_JSON)
    result = run_real(
        env["run_id"], env["doc_ids"], sofia_root=env["sofia_root"],
        runs_root=env["runs_root"], prompt_dir=env["prompt_dir"], transport=transport,
        git_status=env["git_status"], head_sha="H", created="2026-07-02T00:00:00Z",
        now=_counter_now(), sleeper=lambda s: None, env=env["env"],
    )
    run_dir = env["runs_root"] / env["run_id"]
    emissions = sorted(p.name for p in (run_dir / "emissions").glob("*.txt"))
    # One raw file per reviewer call plus the arbiter call, correctly named.
    assert "pass01-antagonist-LAA-1.txt" in emissions
    assert "pass01-coherence-1.txt" in emissions
    assert "pass01-arbiter-1.txt" in emissions
    # Raw body written verbatim (before parsing).
    assert (run_dir / "emissions" / "pass01-antagonist-LAA-1.txt").read_text() == _VALID_FINDING_JSON
    # llm_call events carry request_id + emission_path.
    for event in result.log.of_kind("llm_call"):
        assert event.detail["request_id"] is not None
        assert event.detail["emission_path"] is not None


def _dispatch_run(tmp_path, env, transport):
    return run_real(
        env["run_id"], env["doc_ids"], sofia_root=env["sofia_root"],
        runs_root=env["runs_root"], prompt_dir=env["prompt_dir"], transport=transport,
        git_status=env["git_status"], head_sha="H", now=_counter_now(),
        sleeper=lambda s: None, env=dict(env["env"]),
    )


def test_item_e_fully_dropped_reviewer_aborts_no_converged(tmp_path) -> None:
    from agent_loop.runner import InstrumentCompromisedError

    env = _prep_env(tmp_path, ["ADR-001", "ADR-002", "DDR-001", "DDR-002"])
    transport = DispatchTransport(reviewer="not json at all")  # every reviewer drops
    with pytest.raises(InstrumentCompromisedError):
        _dispatch_run(tmp_path, env, transport)
    run_dir = env["runs_root"] / env["run_id"]
    kinds = [json.loads(x)["kind"] for x in (run_dir / "action-log.jsonl").read_text().splitlines()]
    assert "run_aborted" in kinds
    assert "converged" not in kinds  # a false CONVERGED was NOT reachable


def test_item_e_partial_drop_proceeds(tmp_path) -> None:
    env = _prep_env(tmp_path, ["ADR-001", "ADR-002", "DDR-001", "DDR-002"])
    good = json.loads(_VALID_FINDING_JSON)[0]
    partial = json.dumps([good, {"severity": "MATERIAL"}])  # 1 valid + 1 malformed item
    transport = DispatchTransport(reviewer=partial, arbiter=_VALID_CLASSIFICATION_JSON)
    result = _dispatch_run(tmp_path, env, transport)
    # A parse-drop occurred but the reviewer also admitted a finding → not
    # compromised; the run proceeds to a legitimate router exit.
    assert result.exit.kind == "HALT_DECISION"
    assert len(result.log.of_kind("parse_dropped")) >= 1


def test_item_e_all_hats_null_aborts_no_false_converged(tmp_path) -> None:
    # SUPERSEDES the prior "empty emission proceeds to converged" ruling
    # (RBT-54 R-C; empirical basis: the run-016-ddr-002 fired draw). That run
    # showed an all-hats-null draw is a FALSE CONVERGED from a wholly null
    # instrument — every hat returned "[]", re-drew, "[]" again, hat_null, and
    # the router declared CONVERGED with zero findings. A legitimate empty result
    # is structurally impossible under the 2-POSITIVE floor, so the all-hats-null
    # guard now fails such a draw loud. Applied learning, not contradiction.
    from agent_loop.runner import InstrumentCompromisedError

    env = _prep_env(tmp_path, ["ADR-001", "ADR-002", "DDR-001", "DDR-002"])
    transport = DispatchTransport(reviewer="[]")  # every hat clean-null → hat_null
    with pytest.raises(InstrumentCompromisedError):
        _dispatch_run(tmp_path, env, transport)
    run_dir = env["runs_root"] / env["run_id"]
    kinds = [json.loads(x)["kind"] for x in (run_dir / "action-log.jsonl").read_text().splitlines()]
    assert "run_aborted" in kinds
    assert kinds.count("hat_null") == 4  # every hat went variance-to-zero
    assert "converged" not in kinds  # the false CONVERGED is no longer reachable


# --- RBT-49 Item 1: prompt caching — request structuring + accounting --------


def test_anthropic_transport_marks_system_and_cache_prefix_and_reads_cache_usage() -> None:
    # With a cache_prefix, the system block is marked cacheable and the user is
    # split into a cached head (the breakpoint) + an uncached tail; the API's
    # cache usage fields surface on the response (RBT-49 Item 1 §4).
    message = SimpleNamespace(
        content=[SimpleNamespace(text="ok")],
        usage=SimpleNamespace(
            input_tokens=50,
            output_tokens=2,
            cache_creation_input_tokens=0,
            cache_read_input_tokens=900,
        ),
    )
    seen: dict = {}

    def create(**kw):
        seen.update(kw)
        return message

    client = SimpleNamespace(messages=SimpleNamespace(create=create))
    response = AnthropicTransport(client)("SYS", "PREFIXtail", "m", 10, cache_prefix="PREFIX")

    # System is a cache-marked content block.
    assert seen["system"] == [
        {"type": "text", "text": "SYS", "cache_control": {"type": "ephemeral"}}
    ]
    # User splits at the prefix: cached head block + plain tail block.
    content = seen["messages"][0]["content"]
    assert content[0] == {"type": "text", "text": "PREFIX", "cache_control": {"type": "ephemeral"}}
    assert content[1] == {"type": "text", "text": "tail"}
    # The sent user content reconstructs the input byte-for-byte.
    assert content[0]["text"] + content[1]["text"] == "PREFIXtail"
    # Cache usage surfaced from the API.
    assert response.input_tokens == 50
    assert response.cache_creation_input_tokens == 0
    assert response.cache_read_input_tokens == 900


def test_anthropic_transport_without_cache_prefix_sends_one_user_block() -> None:
    # No cache_prefix (the reviewer path): a single uncached user block, but the
    # system is still cacheable; absent cache-usage fields default to 0.
    message = SimpleNamespace(
        content=[SimpleNamespace(text="ok")],
        usage=SimpleNamespace(input_tokens=7, output_tokens=1),  # no cache fields
    )
    seen: dict = {}

    def create(**kw):
        seen.update(kw)
        return message

    client = SimpleNamespace(messages=SimpleNamespace(create=create))
    response = AnthropicTransport(client)("SYS", "USER", "m", 10)  # cache_prefix defaults None

    assert seen["messages"][0]["content"] == [{"type": "text", "text": "USER"}]
    assert seen["system"][0]["cache_control"] == {"type": "ephemeral"}
    assert response.cache_creation_input_tokens == 0
    assert response.cache_read_input_tokens == 0


def test_anthropic_transport_cache_prefix_covering_whole_user_drops_empty_tail() -> None:
    # When the cache_prefix spans the entire user content there is no tail — a
    # single cached block is sent (no empty text block, which the API rejects).
    message = SimpleNamespace(
        content=[SimpleNamespace(text="ok")],
        usage=SimpleNamespace(input_tokens=1, output_tokens=1),
    )
    seen: dict = {}

    def create(**kw):
        seen.update(kw)
        return message

    client = SimpleNamespace(messages=SimpleNamespace(create=create))
    AnthropicTransport(client)("SYS", "WHOLE", "m", 10, cache_prefix="WHOLE")
    assert seen["messages"][0]["content"] == [
        {"type": "text", "text": "WHOLE", "cache_control": {"type": "ephemeral"}}
    ]


def test_llm_call_events_distinguish_cached_from_uncached_and_sum_per_site() -> None:
    # A mocked uncached (cache-write) call and a mocked cached (cache-read) call
    # are distinguishable per event and summable per site (RBT-49 Item 1 §4).
    log = ActionLog()
    write = LlmResponse(
        text="[]", input_tokens=900, output_tokens=4, cache_creation_input_tokens=900
    )
    read = LlmResponse(
        text="[]", input_tokens=40, output_tokens=4, cache_read_input_tokens=900
    )
    transport = ScriptedTransport([write, read])
    emit = build_api_emitter(
        site_label="arbiter",
        model="m",
        max_tokens=10,
        log=log,
        transport=transport,
        now=_counter_now(),
        sleeper=lambda s: None,
    )
    emit("s", "u")
    emit("s", "u")

    first, second = (e.detail for e in log.of_kind("llm_call"))
    # First call wrote the cache; second read it — distinguishable per call.
    assert first["cache_creation_input_tokens"] == 900 and first["cache_read_input_tokens"] == 0
    assert second["cache_read_input_tokens"] == 900 and second["cache_creation_input_tokens"] == 0
    assert first["input_tokens"] == 900 and second["input_tokens"] == 40  # uncached input

    totals = per_site_token_totals(log)["arbiter"]
    assert totals["cache_creation_input_tokens"] == 900
    assert totals["cache_read_input_tokens"] == 900
    assert totals["input_tokens"] == 940  # summed uncached input
    assert totals["calls"] == 2


def test_arbiter_reorders_substrate_ahead_of_finding_and_marks_it_cached() -> None:
    # Ra-2 reorder: the static substrate precedes the finding in the user block,
    # and that substrate is passed as the cache_prefix — a byte-exact prefix of
    # the user content, with the finding as the uncached tail.
    log = ActionLog()
    transport = ScriptedTransport([_VALID_CLASSIFICATION_JSON])
    _api_arbiter(log, transport).classify(
        _finding("f"), {"AUTH-1": "authority body"}, {"DI-1": "intent body"}
    )
    call = transport.calls[0]
    user, cache_prefix = call["user"], call["cache_prefix"]
    # Reordered: substrate blocks come before the finding.
    assert user.index("RATIFIED AUTHORITIES") < user.index("FINDING:")
    assert user.index("STATED DESIGN INTENT") < user.index("FINDING:")
    # The cache_prefix is the substrate and a byte-exact leading slice of user.
    assert cache_prefix is not None and user.startswith(cache_prefix)
    assert "RATIFIED AUTHORITIES" in cache_prefix and "STATED DESIGN INTENT" in cache_prefix
    assert "FINDING:" not in cache_prefix  # the finding is the uncached tail


def test_arbiter_content_retry_reuses_the_same_cache_prefix() -> None:
    # The substrate prefix is byte-identical across the corrective retry, so the
    # retry also reads the substrate from cache.
    log = ActionLog()
    transport = ScriptedTransport(["not json", _VALID_CLASSIFICATION_JSON])
    _api_arbiter(log, transport).classify(_finding("f"), {"a": "A"}, {"v": "V"})
    assert transport.calls[0]["cache_prefix"] is not None
    assert transport.calls[0]["cache_prefix"] == transport.calls[1]["cache_prefix"]


# --- RBT-49 Item 2: reviewer empty-emission re-draw --------------------------


def _single_reviewer_run(tmp_path, transport, *, arbiter, name):
    from agent_loop.real_hats import build_real_reviewer

    log = ActionLog()
    emit = build_api_emitter(
        site_label=IDENTITY_LAA.label,
        model="m",
        max_tokens=10,
        log=log,
        transport=transport,
        now=_counter_now(),
        sleeper=lambda s: None,
    )
    reviewer = build_real_reviewer(IDENTITY_LAA, DESIGN_DIR / "antagonist-LAA.prompt.md", emit)
    result = run_loop(
        header=LedgerHeader(set=["ADR-001"], counted_severities=["BLOCKING", "MATERIAL"]),
        plan=lambda pn, snap, lg: [reviewer],
        arbiter=arbiter,
        store=LedgerStore(tmp_path / f"{name}.json"),
        log=log,
    )
    return result, log


def _two_positives_json() -> str:
    return json.dumps([
        {
            "severity": "POSITIVE",
            "target": ["ADR-001"],
            "locus": f"s{i}",
            "claim": "a load-bearing surface held under attack",
            "cited_authority": {"kind": "canonical", "ref": "AUTH-1 §2"},
        }
        for i in (1, 2)
    ])


def test_reviewer_below_floor_empty_redraw_records_hat_null_and_run_continues(tmp_path) -> None:
    # RBT-49 Item 2 (ratified, content preserved): a single hat's below-floor
    # empty re-draw records hat_null and the run CONTINUES — degraded recall is
    # recoverable via union-over-runs. Moved to a MULTI-HAT harness (RBT-54 R-C):
    # the "continues" contract holds precisely because the other hats carry the
    # draw; an ALL-hats-null draw fails loud (its own test). Here LAA nulls while
    # SA/EA/coherence meet the 2-POSITIVE floor.
    from agent_loop.real_hats import build_real_reviewer, real_hat_plan
    from agent_loop.reviewers import IDENTITY_COHERENCE, IDENTITY_EA, IDENTITY_SA

    log = ActionLog()
    laa_calls: list[int] = []

    def laa_emit(system: str, user: str) -> str:  # empty both times → hat_null
        laa_calls.append(1)
        return "[]"

    def floor_emit(system: str, user: str) -> str:  # meets floor → no re-draw
        return _two_positives_json()

    plan = real_hat_plan(
        build_real_reviewer(IDENTITY_LAA, DESIGN_DIR / "antagonist-LAA.prompt.md", laa_emit),
        build_real_reviewer(IDENTITY_SA, DESIGN_DIR / "antagonist-SA.prompt.md", floor_emit),
        build_real_reviewer(IDENTITY_EA, DESIGN_DIR / "antagonist-EA.prompt.md", floor_emit),
        build_real_reviewer(IDENTITY_COHERENCE, DESIGN_DIR / "coherence-sweep.prompt.md", floor_emit),
    )
    result = run_loop(
        header=LedgerHeader(set=["ADR-001"], counted_severities=["BLOCKING", "MATERIAL"]),
        plan=plan, arbiter=CannedArbiter(), store=LedgerStore(tmp_path / "hn.json"), log=log,
    )

    # LAA emitted exactly twice (one re-draw); its hat_null is the only one.
    assert len(laa_calls) == 2
    redraws = [
        e for e in log.of_kind("llm_retry") if e.detail.get("retry_kind") == "reviewer_redraw"
    ]
    assert [e.detail.get("site") for e in redraws] == [IDENTITY_LAA.label]
    assert redraws[0].detail["positive_count"] == 0

    hat_nulls = log.of_kind("hat_null")
    assert len(hat_nulls) == 1 and hat_nulls[0].detail["reviewer"] == IDENTITY_LAA.label
    # The run CONTINUES to a real terminal exit — other hats carried the draw.
    assert result.exit.kind == "CONVERGED"
    assert log.of_kind("run_aborted") == []


def test_reviewer_below_floor_nonempty_redraw_is_admitted_no_hat_null(tmp_path) -> None:
    # Rb: first below floor → re-draw non-empty but still below floor (real
    # content, no POSITIVEs) → admit the emission, no hat_null (reserved for the
    # empty case), the below-floor episode visible via the re-draw event.
    transport = ScriptedTransport([_VALID_FINDING_JSON, _VALID_FINDING_JSON])
    arbiter = CannedArbiter(
        default=ArbiterResult("_", "decision-bearing", None, "authority silent", "high")
    )
    result, log = _single_reviewer_run(tmp_path, transport, arbiter=arbiter, name="rb")

    assert len(transport.calls) == 2  # exactly one re-draw
    assert log.of_kind("hat_null") == []  # Rb is not the empty case
    assert any(
        e.detail.get("retry_kind") == "reviewer_redraw" for e in log.of_kind("llm_retry")
    )
    # The re-draw's (below-floor) finding was admitted and drove a real exit.
    assert len(result.ledger.findings) == 1
    assert result.exit.kind == "HALT_DECISION"


def test_reviewer_meeting_floor_does_not_redraw(tmp_path) -> None:
    # A first emission at the 2-POSITIVE floor is compliant → no re-draw, one
    # emit, no reviewer_redraw event, no hat_null.
    two_positives = json.dumps(
        [
            {
                "severity": "POSITIVE",
                "target": ["ADR-001"],
                "locus": f"s{i}",
                "claim": "a load-bearing surface held under attack",
                "cited_authority": {"kind": "canonical", "ref": "AUTH-1 §2"},
            }
            for i in (1, 2)
        ]
    )
    transport = ScriptedTransport([two_positives])  # a second emit would IndexError
    result, log = _single_reviewer_run(tmp_path, transport, arbiter=CannedArbiter(), name="floor")

    assert len(transport.calls) == 1  # no re-draw
    assert [e for e in log.of_kind("llm_retry") if e.detail.get("retry_kind") == "reviewer_redraw"] == []
    assert log.of_kind("hat_null") == []
    # POSITIVEs bypass the arbiter and neither count nor block → CONVERGED.
    assert result.exit.kind == "CONVERGED"


# --- §10k: document-snapshot verification (RBT-51 Item 3) ---------------------


def test_gate8_matching_snapshot_proceeds(tmp_path) -> None:
    # A snapshot whose hashes match its provenance record lets the run proceed to
    # a legitimate router exit; the reviewed content is read from the snapshot.
    env = _prep_env(tmp_path, ["ADR-001", "ADR-002", "DDR-001", "DDR-002"])
    transport = RoutingTransport(_VALID_FINDING_JSON, _VALID_CLASSIFICATION_JSON)
    result = run_real(
        env["run_id"], env["doc_ids"], sofia_root=env["sofia_root"],
        runs_root=env["runs_root"], prompt_dir=env["prompt_dir"], transport=transport,
        git_status=env["git_status"], head_sha="H", now=_counter_now(),
        sleeper=lambda s: None, env=env["env"],
    )
    assert result.exit.kind == "HALT_DECISION"


def test_gate8_missing_snapshot_aborts_and_never_falls_back_to_working_tree(tmp_path) -> None:
    import shutil

    env = _prep_env(tmp_path, ["ADR-001", "ADR-002", "DDR-001", "DDR-002"])
    shutil.rmtree(env["runs_root"] / env["run_id"] / "documents")  # snapshot gone
    # The working-tree docs still exist — the runner must NOT fall back to them.
    assert (env["sofia_root"] / "docs" / "ADR-001-distilled.md").is_file()
    transport = DispatchTransport()
    with pytest.raises(PrepGateError):
        run_real(
            env["run_id"], env["doc_ids"], sofia_root=env["sofia_root"],
            runs_root=env["runs_root"], prompt_dir=env["prompt_dir"], transport=transport,
            git_status=env["git_status"], head_sha="H", now=_counter_now(),
            sleeper=lambda s: None, env=dict(env["env"]),
        )
    assert transport.non_probe_calls() == []  # aborted before any reviewer/arbiter call


def test_gate8_hash_mismatch_aborts_before_any_emitter_call(tmp_path) -> None:
    env = _prep_env(tmp_path, ["ADR-001", "ADR-002", "DDR-001", "DDR-002"])
    snap = env["runs_root"] / env["run_id"] / "documents" / "ADR-001-distilled.md"
    snap.write_text("MUTATED AFTER PREP", encoding="utf-8")  # breaks the recorded pin
    transport = DispatchTransport()
    with pytest.raises(PrepGateError):
        run_real(
            env["run_id"], env["doc_ids"], sofia_root=env["sofia_root"],
            runs_root=env["runs_root"], prompt_dir=env["prompt_dir"], transport=transport,
            git_status=env["git_status"], head_sha="H", now=_counter_now(),
            sleeper=lambda s: None, env=dict(env["env"]),
        )
    assert transport.non_probe_calls() == []
