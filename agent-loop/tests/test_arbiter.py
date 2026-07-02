# Module: tests.test_arbiter
# Purpose: Specify the arbiter port's fail-safe invariants and the canned
#          adapter. The arbiter is the ONLY LLM judgment; its result object
#          enforces the prompt's hard rules structurally so a malformed judgment
#          cannot reach the router. The LlmArbiter seam must stay unwired in the
#          skeleton (no network, no nondeterminism).
# Scope:   Unit tests over ArbiterResult, CannedArbiter, LlmArbiter.

import pytest

from agent_loop.arbiter import ArbiterResult, CannedArbiter, LlmArbiter
from agent_loop.ledger import CitedAuthority, Finding


def _finding(fid: str) -> Finding:
    return Finding(
        source="antagonist-stub",
        altitude="LAA",
        severity="MATERIAL",
        target=["DOC-A"],
        locus="l",
        claim="c",
        cited_authority=CitedAuthority(kind="canonical", ref="AUTH-1"),
        id=fid,
    )


def test_resolvable_requires_named_authority_locus() -> None:
    # Hard rule 1: resolvable with no authority_locus is invalid.
    with pytest.raises(ValueError):
        ArbiterResult(
            finding_id="a",
            classification="resolvable",
            authority_locus=None,
            rationale="r",
            confidence="high",
        )


def test_low_confidence_resolvable_is_forbidden() -> None:
    # Bias rule: low-confidence resolvable is a contradiction.
    with pytest.raises(ValueError):
        ArbiterResult(
            finding_id="a",
            classification="resolvable",
            authority_locus="AUTH-1 §2",
            rationale="r",
            confidence="low",
        )


def test_decision_bearing_may_be_low_confidence_and_have_no_locus() -> None:
    # Conservative bias: decision-bearing is the safe label; no locus required.
    result = ArbiterResult(
        finding_id="a",
        classification="decision-bearing",
        authority_locus=None,
        rationale="authority silent on the fork",
        confidence="low",
    )
    assert result.classification == "decision-bearing"


def test_canned_arbiter_returns_verdict_by_finding_id() -> None:
    verdict = ArbiterResult(
        finding_id="a",
        classification="resolvable",
        authority_locus="AUTH-1 §2",
        rationale="conforms to AUTH-1",
        confidence="high",
    )
    arbiter = CannedArbiter(verdicts={"a": verdict})
    assert arbiter.classify(_finding("a"), None, None) is verdict


def test_canned_arbiter_uses_default_for_unknown_id() -> None:
    default = ArbiterResult(
        finding_id="_",
        classification="resolvable",
        authority_locus="AUTH-1 §2",
        rationale="churn",
        confidence="high",
    )
    arbiter = CannedArbiter(default=default)
    result = arbiter.classify(_finding("churn-7"), None, None)
    assert result.classification == "resolvable"
    assert result.finding_id == "churn-7"  # rewritten to the actual finding


def test_canned_arbiter_without_verdict_or_default_raises() -> None:
    with pytest.raises(KeyError):
        CannedArbiter().classify(_finding("missing"), None, None)


def test_llm_arbiter_is_unwired_in_the_skeleton() -> None:
    # The only LLM path must not run in dry mode: no client → NotImplementedError.
    with pytest.raises(NotImplementedError):
        LlmArbiter().classify(_finding("a"), None, None)
