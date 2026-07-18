# Module: agent_loop.arbiter
# Purpose: The single load-bearing LLM judgment in the whole system — build
#          step 3. It runs per finding and does exactly one thing: classify a
#          finding `resolvable` vs `decision-bearing`, biased conservative
#          (unsure → decision-bearing). It does NOT propose/apply fixes and does
#          NOT judge convergence.
# Scope:   A port (Arbiter protocol) so the skeleton can drive it deterministically.
#          CannedArbiter returns each planted finding's expected classification —
#          the only way to satisfy both "the only LLM judgment" and
#          "deterministic across repeated runs". The production arbiter is
#          transport.ApiArbiter, which loads arbiter-classifier.prompt.md at run
#          time; this module holds the port and the canned adapter only (no LLM
#          here, by design). The retired LlmArbiter/ARBITER_SYSTEM_PROMPT seam
#          (a never-wired duplicate ApiArbiter superseded) is gone as of RBT-67.

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

from agent_loop.ledger import Classification, Finding

_CONFIDENCE_VALUES = ("high", "medium", "low")


@dataclass
class ArbiterResult:
    """A per-finding classification result.

    Enforces two prompt invariants at construction so a malformed judgment can
    never reach the router:
      - a `resolvable` result must name the authority+locus that determines the
        fix (Hard rule 1: if you cannot name it, it is not resolvable);
      - a `low`-confidence `resolvable` is a contradiction with the bias rule
        (low confidence means unsure, and unsure means decision-bearing).

    Attributes:
        finding_id: The id of the finding classified.
        classification: 'resolvable' or 'decision-bearing'.
        authority_locus: For 'resolvable', the naming authority+locus; else None.
        rationale: One or two sentences.
        confidence: 'high' | 'medium' | 'low'.
    """

    finding_id: str
    classification: Classification
    authority_locus: str | None
    rationale: str
    confidence: str

    def __post_init__(self) -> None:
        if self.classification not in ("resolvable", "decision-bearing"):
            raise ValueError(
                "arbiter emits only 'resolvable' or 'decision-bearing', "
                f"got {self.classification!r}"
            )
        if self.confidence not in _CONFIDENCE_VALUES:
            raise ValueError(f"invalid confidence {self.confidence!r}")
        if self.classification == "resolvable":
            if not self.authority_locus:
                raise ValueError(
                    "resolvable requires a named authority_locus (Hard rule 1)"
                )
            if self.confidence == "low":
                raise ValueError(
                    "low-confidence 'resolvable' is forbidden — unsure means "
                    "decision-bearing (bias rule)"
                )


class Arbiter(Protocol):
    """The arbiter port. One method: classify one finding."""

    def classify(
        self, finding: Finding, authorities: object, design_intent: object
    ) -> ArbiterResult:
        """Classify a single finding, fetching authority fresh (in production)."""
        ...


class CannedArbiter:
    """Deterministic arbiter for the skeleton.

    Returns a pre-specified verdict per finding id (the dummy case already
    states each planted finding's expected classification). An optional
    `default` covers rig scenarios that generate fresh finding ids each pass
    (e.g. the S3b plateau churn); it is a fixture affordance, not a judgment
    rule, and still passes the ArbiterResult invariants.
    """

    def __init__(
        self,
        verdicts: dict[str, ArbiterResult] | None = None,
        default: ArbiterResult | None = None,
    ) -> None:
        """Bind the canned verdict table and optional default.

        Args:
            verdicts: Map of finding id → verdict.
            default: Verdict template used when a finding id is not in the table
                (its finding_id is rewritten to the actual finding). None means
                an unknown id is a programming error and raises.
        """
        self._verdicts = verdicts or {}
        self._default = default

    def classify(
        self, finding: Finding, authorities: object, design_intent: object
    ) -> ArbiterResult:
        """Return the canned verdict for this finding."""
        verdict = self._verdicts.get(finding.id)
        if verdict is not None:
            return verdict
        if self._default is not None:
            return ArbiterResult(
                finding_id=finding.id,
                classification=self._default.classification,
                authority_locus=self._default.authority_locus,
                rationale=self._default.rationale,
                confidence=self._default.confidence,
            )
        raise KeyError(
            f"no canned verdict for finding id {finding.id!r} and no default set"
        )
