# Module: tests.test_real_hats
# Purpose: The runner-real-hats.contract.md §9 test set (a–f). Exercises the
#          real-reviewer machinery — frozen snapshot / no cross-anchoring,
#          gather-then-admit ordering, snapshot immutability, coherence
#          scheduling, identity stamping, malformed-emission drop — with
#          probe/fake reviewers only. NO real LLM reviewer is invoked (first dry
#          runs are a separate, supervised session). §9g (S1–S4 regression) is
#          covered by test_scenarios.py, unchanged.
# Scope:   Over run_loop + real_hats + reviewers with injected fakes.

import copy
import json

from pathlib import Path

import pytest

from agent_loop.arbiter import ArbiterResult, CannedArbiter
from agent_loop.ledger import (
    CitedAuthority,
    DocChange,
    Finding,
    Ledger,
    LedgerHeader,
    LedgerStore,
    PassRecord,
)
from agent_loop.log import ActionLog
from agent_loop.real_hats import (
    assemble_user_prompt,
    build_real_hat_plan,
    build_real_reviewer,
    load_system_prompt,
    parse_emissions,
    real_hat_plan,
)
from agent_loop.reviewers import (
    IDENTITY_COHERENCE,
    IDENTITY_EA,
    IDENTITY_LAA,
    IDENTITY_SA,
    DocumentSet,
    Substrate,
    ReviewerIdentity,
    ScheduledReviewer,
    default_document_fetcher,
    default_substrate_fetcher,
)
from agent_loop.runner import run_loop

DESIGN_DIR = Path(__file__).resolve().parent.parent / "design"


# --- helpers -----------------------------------------------------------------


def _header() -> LedgerHeader:
    return LedgerHeader(
        set=["DOC-A", "DOC-B"],
        counted_severities=["BLOCKING", "MATERIAL"],
        plateau_N=3,
        mode="dry",
    )


def _finding(claim: str, *, source: str = "antagonist-stub", altitude: str = "LAA") -> Finding:
    return Finding(
        source=source,  # type: ignore[arg-type]
        altitude=altitude,  # type: ignore[arg-type]
        severity="MATERIAL",
        target=["DOC-A"],
        locus="l",
        claim=claim,
        cited_authority=CitedAuthority(kind="canonical", ref="AUTH-1 §2"),
    )


def _emitting_reviewer(identity: ReviewerIdentity, findings: list[Finding]) -> ScheduledReviewer:
    def run(pn, snap, recs, sub, log):  # noqa: ANN001
        return [copy.deepcopy(f) for f in findings]

    return ScheduledReviewer(identity, run)


class _AllDecisionBearing:
    """Fake arbiter: classifies every finding decision-bearing → HALT on pass 1.

    Keeps the machinery tests to a single deterministic pass.
    """

    def classify(self, finding, authorities, design_intent):  # noqa: ANN001
        return ArbiterResult(
            finding_id=finding.id,
            classification="decision-bearing",
            authority_locus=None,
            rationale="test double",
            confidence="high",
        )


def _json_finding(claim: str, *, severity: str = "MATERIAL", bad_source: bool = True) -> dict:
    item = {
        "severity": severity,
        "target": ["DOC-A"],
        "locus": "l",
        "claim": claim,
        "cited_authority": {"kind": "canonical", "ref": "AUTH-1 §2"},
    }
    if bad_source:
        # Values the runner must ignore and override (§7 / §9e).
        item["source"] = "antagonist-EA"
        item["altitude"] = "EA"
    return item


def _emitter_returning(payload: str):
    return lambda system, user: payload


# --- §9a: structural no-cross-anchoring --------------------------------------


def test_probe_reviewer_observes_no_current_pass_findings(tmp_path) -> None:
    # A probe scheduled AFTER an emitting reviewer must still observe zero
    # current-pass findings — the emitter's output is not admitted until every
    # reviewer has returned, and the snapshot is frozen.
    sink: list[dict] = []

    def probe_run(pn, snap, recs, sub, log):  # noqa: ANN001
        sink.append(
            {
                "snapshot_finding_ids": [f.id for f in snap.findings],
                "admitted_seen": len(log.of_kind("admitted")),
            }
        )
        return []

    emitter_id = ReviewerIdentity("emitter", "antagonist-LAA", "LAA", 0)
    probe_id = ReviewerIdentity("probe", "antagonist-SA", "SA", 1)

    def plan(pass_number, snapshot, log):  # noqa: ANN001
        return [
            _emitting_reviewer(emitter_id, [_finding("emitter finding")]),
            ScheduledReviewer(probe_id, probe_run),
        ]

    result = run_loop(
        header=_header(),
        plan=plan,
        arbiter=_AllDecisionBearing(),
        store=LedgerStore(tmp_path / "a.json"),
    )

    # The emitter's finding WAS admitted this pass...
    assert any(f.claim == "emitter finding" for f in result.ledger.findings)
    # ...yet the probe saw no current-pass findings and no prior admission.
    assert sink[0]["snapshot_finding_ids"] == []
    assert sink[0]["admitted_seen"] == 0


# --- §9b: gather-then-admit (no admission until all returned; fixed order) ----


def test_no_admission_occurs_until_all_reviewers_returned(tmp_path) -> None:
    # Each reviewer records how many admissions it observed at run time; with
    # gather-then-admit that must be zero for all, even though every reviewer
    # emits a finding that is ultimately admitted.
    seen: list[int] = []

    def make(identity: ReviewerIdentity, claim: str) -> ScheduledReviewer:
        def run(pn, snap, recs, sub, log):  # noqa: ANN001
            seen.append(len(log.of_kind("admitted")))
            return [_finding(claim)]

        return ScheduledReviewer(identity, run)

    def plan(pass_number, snapshot, log):  # noqa: ANN001
        return [
            make(IDENTITY_LAA, "laa"),
            make(IDENTITY_SA, "sa"),
            make(IDENTITY_EA, "ea"),
        ]

    result = run_loop(
        header=_header(),
        plan=plan,
        arbiter=_AllDecisionBearing(),
        store=LedgerStore(tmp_path / "b1.json"),
    )

    assert seen == [0, 0, 0]  # no admission during any reviewer run
    assert len(result.ledger.findings) == 3  # all admitted afterwards


def test_admission_order_is_laa_sa_ea_coherence(tmp_path) -> None:
    # Build real reviewers whose emitters return one finding each; assert the
    # admitted findings appear in the fixed order regardless of schedule order.
    def hat_emitter(claim: str):
        return _emitter_returning(json.dumps([_json_finding(claim)]))

    plan = real_hat_plan(
        build_real_reviewer(IDENTITY_LAA, DESIGN_DIR / "antagonist-LAA.prompt.md", hat_emitter("laa")),
        build_real_reviewer(IDENTITY_SA, DESIGN_DIR / "antagonist-SA.prompt.md", hat_emitter("sa")),
        build_real_reviewer(IDENTITY_EA, DESIGN_DIR / "antagonist-EA.prompt.md", hat_emitter("ea")),
        build_real_reviewer(
            IDENTITY_COHERENCE, DESIGN_DIR / "coherence-sweep.prompt.md", hat_emitter("coh")
        ),
    )

    result = run_loop(
        header=_header(),
        plan=plan,
        arbiter=_AllDecisionBearing(),
        store=LedgerStore(tmp_path / "b2.json"),
    )

    assert [f.source for f in result.ledger.findings] == [
        "antagonist-LAA",
        "antagonist-SA",
        "antagonist-EA",
        "coherence",
    ]


# --- §9c: snapshot immutability ----------------------------------------------


def test_admission_mutations_not_visible_through_snapshot(tmp_path) -> None:
    captured: dict = {}

    def probe_run(pn, snap, recs, sub, log):  # noqa: ANN001
        captured["snapshot"] = snap  # hold the reference admission must not touch
        return []

    def plan(pass_number, snapshot, log):  # noqa: ANN001
        return [
            _emitting_reviewer(IDENTITY_LAA, [_finding("laa finding")]),
            ScheduledReviewer(IDENTITY_SA, probe_run),
        ]

    result = run_loop(
        header=_header(),
        plan=plan,
        arbiter=_AllDecisionBearing(),
        store=LedgerStore(tmp_path / "c.json"),
    )

    # Findings were admitted to the live ledger this pass...
    assert len(result.ledger.findings) == 1
    # ...but the snapshot the reviewer held is a distinct, unmutated object.
    assert captured["snapshot"] is not result.ledger
    assert captured["snapshot"].findings == []


# --- §9h: per-reviewer snapshot isolation (ratified 2026-07-02) --------------


def test_reviewer_mutating_its_snapshot_copy_cannot_affect_others(tmp_path) -> None:
    # A reviewer that scribbles on its own snapshot copy must not leak to any
    # later reviewer's view, the scheduling plan's view, or the admitted ledger.
    seen: dict = {}

    def mutator_run(pn, snap, recs, sub, log):  # noqa: ANN001
        # Structural attack: corrupt the input in place.
        snap.findings.append(_finding("MUTANT"))
        snap.header.set.append("DOC-INJECTED")
        seen["mutator_snap"] = snap  # retained so lifetimes overlap for `is not`
        return []  # emits nothing legitimate

    def observer_run(pn, snap, recs, sub, log):  # noqa: ANN001
        seen["observer_saw_claims"] = [f.claim for f in snap.findings]
        seen["observer_saw_set"] = list(snap.header.set)
        seen["observer_snap"] = snap
        return [_finding("observer")]

    def plan(pass_number, snapshot, log):  # noqa: ANN001
        seen["plan_saw_claims"] = [f.claim for f in snapshot.findings]
        seen["plan_snap"] = snapshot
        return [
            ScheduledReviewer(IDENTITY_LAA, mutator_run),
            ScheduledReviewer(IDENTITY_SA, observer_run),
        ]

    result = run_loop(
        header=_header(),
        plan=plan,
        arbiter=_AllDecisionBearing(),
        store=LedgerStore(tmp_path / "h.json"),
    )

    # The later reviewer's view is untouched by the mutator.
    assert "MUTANT" not in seen["observer_saw_claims"]
    assert "DOC-INJECTED" not in seen["observer_saw_set"]
    # The plan's scheduling view is untouched.
    assert "MUTANT" not in seen["plan_saw_claims"]
    # The admitted ledger carries only what reviewers returned — no MUTANT.
    assert [f.claim for f in result.ledger.findings] == ["observer"]
    assert "DOC-INJECTED" not in result.ledger.header.set
    # Structural: every consumer held a distinct snapshot object (no sharing).
    assert seen["mutator_snap"] is not seen["observer_snap"]
    assert seen["mutator_snap"] is not seen["plan_snap"]
    assert seen["observer_snap"] is not seen["plan_snap"]


# --- §9d: coherence scheduling -----------------------------------------------


def _noop_reviewer(identity: ReviewerIdentity) -> ScheduledReviewer:
    return ScheduledReviewer(identity, lambda pn, snap, recs, sub, log: [])


def _real_hat_plan_of_noops():
    return real_hat_plan(
        _noop_reviewer(IDENTITY_LAA),
        _noop_reviewer(IDENTITY_SA),
        _noop_reviewer(IDENTITY_EA),
        _noop_reviewer(IDENTITY_COHERENCE),
    )


def test_coherence_invoked_on_pass_one() -> None:
    log = ActionLog()
    scheduled = _real_hat_plan_of_noops()(1, Ledger(header=_header()), log)
    labels = [s.identity.label for s in scheduled]
    assert "coherence" in labels
    assert log.of_kind("coherence_skip") == []


def test_coherence_skipped_and_logged_on_no_change_pass() -> None:
    log = ActionLog()
    snapshot = Ledger(
        header=_header(),
        passes=[PassRecord(pass_number=1, open_cbm_count=0, agents_run=[], timestamp="t")],
    )
    scheduled = _real_hat_plan_of_noops()(2, snapshot, log)
    labels = [s.identity.label for s in scheduled]
    assert labels == ["antagonist-LAA", "antagonist-SA", "antagonist-EA"]
    assert len(log.of_kind("coherence_skip")) == 1


def test_coherence_invoked_on_pass_after_recorded_doc_change() -> None:
    log = ActionLog()
    snapshot = Ledger(
        header=_header(),
        doc_changes=[DocChange(doc="DOC-A", pass_number=1)],
    )
    scheduled = _real_hat_plan_of_noops()(2, snapshot, log)
    assert any(s.identity.label == "coherence" for s in scheduled)
    assert log.of_kind("coherence_skip") == []


# --- §9e: identity stamping --------------------------------------------------


def test_emitted_source_and_altitude_are_overridden_by_identity() -> None:
    # The emission carries source/altitude "antagonist-EA"/"EA"; parsed under
    # the LAA identity, both must be stamped LAA.
    raw = json.dumps([_json_finding("some claim", bad_source=True)])
    findings = parse_emissions(IDENTITY_LAA, raw, ActionLog())
    assert len(findings) == 1
    assert findings[0].source == "antagonist-LAA"
    assert findings[0].altitude == "LAA"


# --- fence unwrapping (emission hardening 2026-07-02) ------------------------


def test_strip_code_fences_unwraps_and_leaves_bare_or_unmatched() -> None:
    from agent_loop.real_hats import strip_code_fences

    assert strip_code_fences("```json\n[1]\n```") == "[1]"
    assert strip_code_fences("```\n{\"a\": 1}\n```") == '{"a": 1}'
    assert strip_code_fences("[1]") == "[1]"  # bare — unchanged
    # unmatched (open, no close) is left intact so it still fails parsing:
    assert strip_code_fences("```json\n[1]") == "```json\n[1]"


def test_fenced_json_array_parses() -> None:
    raw = "```json\n" + json.dumps([_json_finding("c", bad_source=False)]) + "\n```"
    findings = parse_emissions(IDENTITY_LAA, raw, ActionLog())
    assert len(findings) == 1


def test_bare_json_array_still_parses() -> None:
    raw = json.dumps([_json_finding("c", bad_source=False)])
    findings = parse_emissions(IDENTITY_LAA, raw, ActionLog())
    assert len(findings) == 1


def test_prose_preamble_still_drops() -> None:
    log = ActionLog()
    raw = "Here are the findings:\n" + json.dumps([_json_finding("c", bad_source=False)])
    findings = parse_emissions(IDENTITY_LAA, raw, log, emission_path="e.txt")
    assert findings == []
    drop = log.of_kind("parse_dropped")[0]
    assert drop.detail["emission_path"] == "e.txt"  # drop references the raw file


# --- §9f: malformed-emission drop --------------------------------------------


def test_positive_severity_parses_as_a_valid_ladder_tier() -> None:
    # §8: POSITIVE becomes actually-used — the ladder accepts it at the seam
    # (gates still never count it; that is covered in test_gates).
    raw = json.dumps([{**_json_finding("load-bearing surface held under attack"), "severity": "POSITIVE"}])
    findings = parse_emissions(IDENTITY_LAA, raw, ActionLog())
    assert len(findings) == 1
    assert findings[0].severity == "POSITIVE"


def test_invalid_json_is_dropped_at_parse_and_logged() -> None:
    log = ActionLog()
    findings = parse_emissions(IDENTITY_LAA, "not json {", log)
    assert findings == []
    assert len(log.of_kind("parse_dropped")) == 1


def test_non_array_emission_is_dropped_at_parse() -> None:
    log = ActionLog()
    findings = parse_emissions(IDENTITY_LAA, json.dumps({"not": "an array"}), log)
    assert findings == []
    assert log.of_kind("parse_dropped")


def test_malformed_item_dropped_valid_item_kept() -> None:
    log = ActionLog()
    payload = json.dumps(
        [
            {"severity": "MATERIAL", "target": ["DOC-A"], "locus": "l"},  # missing fields
            _json_finding("good", bad_source=False),
            {**_json_finding("bad severity"), "severity": "SHOWSTOPPER"},  # invalid enum
            {**_json_finding("bad kind"), "cited_authority": {"kind": "vibes", "ref": "x"}},
        ]
    )
    findings = parse_emissions(IDENTITY_SA, payload, log)
    assert [f.claim for f in findings] == ["good"]
    assert len(log.of_kind("parse_dropped")) == 3


def test_every_emission_defect_shape_is_dropped_at_parse() -> None:
    # One item per malformed shape the parse seam must reject.
    payload = json.dumps(
        [
            "not an object",  # non-object item
            {**_json_finding("bad target type"), "target": "DOC-A"},  # target not a list
            {**_json_finding("bad target elem"), "target": [1, 2]},  # target elem not str
            {**_json_finding("bad locus"), "locus": 5},  # locus not str
            {**_json_finding("bad claim"), "claim": 5},  # claim not str
            {**_json_finding("bad authority type"), "cited_authority": "AUTH-1"},  # not dict/null
        ]
    )
    log = ActionLog()
    findings = parse_emissions(IDENTITY_LAA, payload, log)
    assert findings == []
    assert len(log.of_kind("parse_dropped")) == 6


def test_null_authority_passes_parse_and_is_left_for_admission() -> None:
    # A null cited_authority is a valid *shape*; it is an admission-scope drop,
    # not a parse drop — keeping the two drop points distinct.
    payload = json.dumps([{**_json_finding("no authority"), "cited_authority": None}])
    log = ActionLog()
    findings = parse_emissions(IDENTITY_LAA, payload, log)
    assert len(findings) == 1
    assert findings[0].cited_authority is None
    assert log.of_kind("parse_dropped") == []


def test_fully_dropped_reviewer_is_instrument_compromised(tmp_path) -> None:
    # A hat emitting garbage does not crash the pass at the parse level, but the
    # instrument-compromised guard (Item E) now fails loud rather than allowing a
    # false CONVERGED: LAA parse-drops and admits nothing, so the pass aborts.
    from agent_loop.runner import InstrumentCompromisedError

    plan = real_hat_plan(
        build_real_reviewer(
            IDENTITY_LAA,
            DESIGN_DIR / "antagonist-LAA.prompt.md",
            _emitter_returning("}{ not json"),
        ),
        build_real_reviewer(
            IDENTITY_SA, DESIGN_DIR / "antagonist-SA.prompt.md", _emitter_returning("[]")
        ),
        build_real_reviewer(
            IDENTITY_EA, DESIGN_DIR / "antagonist-EA.prompt.md", _emitter_returning("[]")
        ),
        build_real_reviewer(
            IDENTITY_COHERENCE,
            DESIGN_DIR / "coherence-sweep.prompt.md",
            _emitter_returning("[]"),
        ),
    )

    with pytest.raises(InstrumentCompromisedError):
        run_loop(
            header=_header(),
            plan=plan,
            arbiter=CannedArbiter(),  # never reached
            store=LedgerStore(tmp_path / "f.json"),
        )


# --- prompt loading + input assembly (§4/§5) ---------------------------------


def test_load_system_prompt_extracts_system_block() -> None:
    system = load_system_prompt(DESIGN_DIR / "antagonist-LAA.prompt.md")
    assert system.startswith("You are the LAA antagonist")
    # Must stop before the next top-level section.
    assert "## User" not in system


def test_load_system_prompt_raises_without_system_section(tmp_path) -> None:
    bad = tmp_path / "no-system.prompt.md"
    bad.write_text("# Title\n\nno system section here\n", encoding="utf-8")
    with pytest.raises(ValueError):
        load_system_prompt(bad)


def test_assemble_user_prompt_includes_docs_substrate_and_snapshot() -> None:
    records = DocumentSet(documents={"DOC-A": "alpha", "DOC-B": "beta"})
    substrate = Substrate(authorities={"AUTH-1": "auth text"}, design_intent={"DI-1": "intent"})
    snapshot = Ledger(header=_header())
    user = assemble_user_prompt(records, substrate, snapshot)
    assert "DOCUMENT SET" in user and "DOC-A" in user and "DOC-B" in user
    assert "AUTH-1" in user and "DI-1" in user
    assert "LEDGER SNAPSHOT" in user


def test_default_fetchers_produce_placeholder_inputs() -> None:
    records = default_document_fetcher(["DOC-A", "DOC-B"])
    substrate = default_substrate_fetcher(["DOC-A"])
    assert set(records.documents) == {"DOC-A", "DOC-B"}
    assert substrate.authorities == {} and substrate.design_intent == {}


def test_build_real_hat_plan_wires_four_reviewers_from_prompt_dir() -> None:
    plan = build_real_hat_plan(DESIGN_DIR, _emitter_returning("[]"))
    scheduled = plan(1, Ledger(header=_header()), ActionLog())
    assert [s.identity.label for s in scheduled] == [
        "antagonist-LAA",
        "antagonist-SA",
        "antagonist-EA",
        "coherence",
    ]
