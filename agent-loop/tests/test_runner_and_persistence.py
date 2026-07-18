# Module: tests.test_runner_and_persistence
# Purpose: Cover the runner's loud safety backstop, the ledger persistence
#          contract (the fresh-fetch spine), and the remaining arbiter/log
#          guards — behaviors claimed elsewhere but worth pinning directly.
# Scope:   Unit/e2e over runner.run_scenario, LedgerStore, ArbiterResult, ActionLog.

import pytest

from agent_loop.arbiter import ArbiterResult, CannedArbiter
from agent_loop.admission import admit
from agent_loop.ledger import (
    CitedAuthority,
    Finding,
    Ledger,
    LedgerHeader,
    LedgerStore,
)
from agent_loop.log import ActionLog
from agent_loop.runner import LoopBoundExceeded, run_scenario
from agent_loop.scenarios import Scenario, _header, no_reviewer, scenario_s1
from agent_loop.stubs import Plant, plant_emitter, verdicts_for


def _nonterminating_scenario() -> Scenario:
    # A coherence stub whose fresh, distinct resolvable emissions make open_cbm
    # alternate 2,1,2,1,... : never zero (never converges), a strict decrease in
    # every window (so plateau never trips), and distinct ids (so recurrence
    # never trips). The only possible outcome is CONTINUE forever — which the
    # loop bound must catch.
    def alternating(pass_number, ledger):
        emit_count = 2 if pass_number % 2 == 1 else 1
        return [
            Finding(
                source="coherence-stub",
                altitude="cross-set",
                severity="MATERIAL",
                target=["DOC-A"],
                locus=f"grow-{pass_number}-{k}",
                claim=f"conflict {pass_number}-{k}",
                cited_authority=CitedAuthority(kind="coherence", ref="DOC-A×DOC-B"),
            )
            for k in range(emit_count)
        ]

    default = ArbiterResult(
        finding_id="_",
        classification="resolvable",
        authority_locus="coherence",
        rationale="r",
        confidence="high",
    )
    return Scenario(
        id="NONTERM",
        header=_header(),
        antagonist=no_reviewer,
        coherence=alternating,
        arbiter=CannedArbiter(default=default),
        fix_changes={},
    )


def test_runner_raises_loudly_when_loop_does_not_terminate(tmp_path) -> None:
    # An open count that alternates 2,1,2,1,... never converges and never
    # plateaus (each window holds a strict decrease); the bound must fire rather
    # than spin — and it must raise, not return a fake exit.
    store = LedgerStore(tmp_path / "nonterm.json")
    with pytest.raises(LoopBoundExceeded):
        run_scenario(_nonterminating_scenario(), store, max_passes=6)


def _two_decisions_scenario() -> Scenario:
    """Two simultaneously-open decision-bearing findings raised on pass 1."""
    pa = Plant(
        label="D1",
        finding=Finding(
            source="antagonist-stub",
            altitude="LAA",
            severity="BLOCKING",
            target=["DOC-A"],
            locus="d1",
            claim="DOC-A exposes a fork on axis 1; DI-1 is silent.",
            cited_authority=CitedAuthority(kind="design-intent", ref="DI-1"),
        ),
        emit=lambda ctx: ctx.pass_number == 1,
        classification="decision-bearing",
        authority_locus=None,
    )
    pb = Plant(
        label="D2",
        finding=Finding(
            source="antagonist-stub",
            altitude="SA",
            severity="MATERIAL",
            target=["DOC-B"],
            locus="d2",
            claim="DOC-B exposes a fork on axis 2; DI-2 is silent.",
            cited_authority=CitedAuthority(kind="design-intent", ref="DI-2"),
        ),
        emit=lambda ctx: ctx.pass_number == 1,
        classification="decision-bearing",
        authority_locus=None,
    )
    plants = [pa, pb]
    return Scenario(
        id="TWO-DEC",
        header=_header(),
        antagonist=plant_emitter(plants),
        coherence=no_reviewer,
        arbiter=CannedArbiter(verdicts=verdicts_for(plants)),
        fix_changes={},
    )


def test_two_open_decisions_surface_as_two_distinct_unbundled_escalations(
    tmp_path,
) -> None:
    # Characterization (design review): the one-escalation-per-finding guarantee
    # must hold at N>=2, not just N=1. Bundling multiple decisions into one
    # ticket is the exact opposite of ratify-one-at-a-time.
    result = run_scenario(
        _two_decisions_scenario(), LedgerStore(tmp_path / "twodec.json")
    )

    assert result.exit.kind == "HALT_DECISION"
    assert result.exit.reason == "decision-bearing"
    escalations = result.log.of_kind("proposed_escalation")
    assert len(escalations) == 2  # one per finding — unbundled
    escalated_ids = {event.detail["finding_id"] for event in escalations}
    assert len(escalated_ids) == 2  # two distinct findings, not one bundled ticket
    assert {f.id for f in result.exit.payload} == escalated_ids


def test_ledger_store_round_trips_state(tmp_path) -> None:
    # Arrange
    store = LedgerStore(tmp_path / "ledger.json")
    assert store.exists() is False
    ledger = Ledger(
        header=LedgerHeader(
            set=["DOC-A"], counted_severities=["BLOCKING", "MATERIAL"], plateau_N=2, mode="dry"
        )
    )
    log = ActionLog()
    admit(
        ledger,
        Finding(
            source="antagonist-stub",
            altitude="LAA",
            severity="MATERIAL",
            target=["DOC-A"],
            locus="l",
            claim="c",
            cited_authority=CitedAuthority(kind="canonical", ref="AUTH-1"),
        ),
        pass_number=1,
        log=log,
    )

    # Act: persist and fetch fresh.
    store.save(ledger)
    reloaded = store.load()

    # Assert: the finding and its nested authority survive the round trip.
    assert store.exists() is True
    assert len(reloaded.findings) == 1
    assert reloaded.findings[0].cited_authority.kind == "canonical"
    assert reloaded.header.plateau_N == 2


def test_run_persists_a_readable_final_ledger(tmp_path) -> None:
    # The spine is on disk, not in memory: the final ledger is fetchable.
    store = LedgerStore(tmp_path / "s1.json")
    run_scenario(scenario_s1(), store)
    on_disk = store.load()
    assert len(on_disk.passes) == 3


def test_arbiter_result_rejects_unknown_classification() -> None:
    with pytest.raises(ValueError):
        ArbiterResult(
            finding_id="a",
            classification="maybe",  # type: ignore[arg-type]
            authority_locus=None,
            rationale="r",
            confidence="high",
        )


def test_arbiter_result_rejects_unknown_confidence() -> None:
    with pytest.raises(ValueError):
        ArbiterResult(
            finding_id="a",
            classification="decision-bearing",
            authority_locus=None,
            rationale="r",
            confidence="certain",  # type: ignore[arg-type]
        )


def test_admission_drops_finding_with_invalid_authority_kind() -> None:
    ledger = Ledger(header=_header())
    log = ActionLog()
    result = admit(
        ledger,
        Finding(
            source="antagonist-stub",
            altitude="LAA",
            severity="MATERIAL",
            target=["DOC-A"],
            locus="l",
            claim="c",
            cited_authority=CitedAuthority(kind="vibes", ref="AUTH-1"),  # type: ignore[arg-type]
        ),
        pass_number=1,
        log=log,
    )
    assert result.dropped is True


def test_action_log_render_emits_json_lines() -> None:
    log = ActionLog()
    log.emit("dropped", finding_id="x", reason="no authority")
    rendered = log.render()
    assert '"kind": "dropped"' in rendered
    assert '"finding_id": "x"' in rendered


def test_plant_id_matches_admission_derived_id() -> None:
    # The verdict table keys must line up with the ids admission assigns, or the
    # canned arbiter would miss every finding.
    plant = Plant(
        label="P",
        finding=Finding(
            source="antagonist-stub",
            altitude="LAA",
            severity="MATERIAL",
            target=["DOC-A"],
            locus="l",
            claim="c",
            cited_authority=CitedAuthority(kind="canonical", ref="AUTH-1"),
        ),
        emit=lambda ctx: True,
        classification="resolvable",
        authority_locus="AUTH-1 §2",
    )
    ledger = Ledger(header=_header())
    log = ActionLog()
    emitted = plant_emitter([plant])(1, ledger)[0]
    admit(ledger, emitted, pass_number=1, log=log)
    assert ledger.findings[0].id == plant.plant_id()
    assert plant.plant_id() in verdicts_for([plant])
