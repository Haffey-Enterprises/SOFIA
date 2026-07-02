# Module: agent_loop.scenarios
# Purpose: The dummy-case acceptance fixture — four scenarios (with variants
#          S2b, S3b) that each isolate one gate path and state its expected
#          router exit. Documents (DOC-A/DOC-B) and authorities (AUTH-1/AUTH-2/
#          DI-1) are abstract stand-ins: the skeleton proves plumbing, not SOFIA
#          review, so it deliberately does not touch the real ADR/DDR set.
# Scope:   Canned plants + planted arbiter verdicts. Each builder returns a
#          fully-wired Scenario the runner can drive deterministically.

from __future__ import annotations

from dataclasses import dataclass

from agent_loop.arbiter import Arbiter, ArbiterResult, CannedArbiter
from agent_loop.ledger import (
    CitedAuthority,
    Finding,
    Ledger,
    LedgerHeader,
)
from agent_loop.stubs import (
    Plant,
    Reviewer,
    fix_changes_for,
    no_reviewer,
    plant_emitter,
    verdicts_for,
)


@dataclass
class Scenario:
    """A fully-wired dummy scenario.

    Attributes:
        id: Scenario id (e.g. 'S1').
        header: Ledger header/parameters.
        antagonist: The antagonist reviewer stub.
        coherence: The coherence reviewer stub.
        arbiter: The (canned) arbiter port.
        fix_changes: Map finding id → doc changed when the author closes it.
        authorities: Fetched-fresh authorities (unused by the canned arbiter).
        design_intent: Fetched-fresh design intent (unused by the canned arbiter).
    """

    id: str
    header: LedgerHeader
    antagonist: Reviewer
    coherence: Reviewer
    arbiter: Arbiter
    fix_changes: dict[str, str]
    authorities: object = None
    design_intent: object = None


def _header() -> LedgerHeader:
    """The dummy-case header: counted {BLOCKING, MATERIAL}, plateau_N=3, dry."""
    return LedgerHeader(
        set=["DOC-A", "DOC-B"],
        counted_severities=["BLOCKING", "MATERIAL"],
        plateau_N=3,
        mode="dry",
    )


def _finding(
    *,
    source: str,
    altitude: str,
    severity: str,
    target: list[str],
    locus: str,
    claim: str,
    cited_authority: CitedAuthority | None,
) -> Finding:
    """Build a bare finding template (id derived at admission)."""
    return Finding(
        source=source,  # type: ignore[arg-type]
        altitude=altitude,  # type: ignore[arg-type]
        severity=severity,  # type: ignore[arg-type]
        target=target,
        locus=locus,
        claim=claim,
        cited_authority=cited_authority,
    )


# --- S1: happy path → CONVERGED ----------------------------------------------


def scenario_s1() -> Scenario:
    """S1 — counter, resolvable→close→count-decrease, coherence-rerun-on-change,
    and the CONVERGED conjunction. Converges in 3 passes."""
    p1 = Plant(
        label="P1",
        finding=_finding(
            source="antagonist-stub",
            altitude="LAA",
            severity="MATERIAL",
            target=["DOC-A"],
            locus="p1-cache-ttl",
            claim="DOC-A cache TTL contradicts AUTH-1.",
            cited_authority=CitedAuthority(kind="canonical", ref="AUTH-1 §2"),
        ),
        emit=lambda ctx: ctx.pass_number == 1,
        classification="resolvable",
        authority_locus="AUTH-1 §2",
        fix_changes_doc="DOC-A",  # fixing P1 changes DOC-A → unblocks P3
    )
    p3 = Plant(
        label="P3",
        finding=_finding(
            source="coherence-stub",
            altitude="cross-set",
            severity="MATERIAL",
            target=["DOC-A", "DOC-B"],
            locus="p3-desync",
            claim="Changed DOC-A now desyncs DOC-B per AUTH-2.",
            cited_authority=CitedAuthority(kind="coherence", ref="DOC-A×DOC-B"),
        ),
        # Withheld until the author records the DOC-A change from fixing P1.
        emit=lambda ctx: ctx.doc_changed_in_prev_pass("DOC-A"),
        classification="resolvable",
        authority_locus="AUTH-2 §1",
        fix_changes_doc=None,  # no downstream trigger; recording a change would false-trip
    )
    plants = [p1, p3]
    return Scenario(
        id="S1",
        header=_header(),
        antagonist=plant_emitter([p1]),
        coherence=plant_emitter([p3]),
        arbiter=CannedArbiter(verdicts=verdicts_for(plants)),
        fix_changes=fix_changes_for(plants),
    )


# --- S2 / S2b: decision-bearing → HALT_DECISION ------------------------------


def _scenario_s2(severity: str, scenario_id: str) -> Scenario:
    p2 = Plant(
        label="P2",
        finding=_finding(
            source="antagonist-stub",
            altitude="LAA",
            severity=severity,
            target=["DOC-A"],
            locus="p2-ordering-fork",
            claim="DOC-A exposes an ordering fork DI-1 is silent on.",
            cited_authority=CitedAuthority(kind="design-intent", ref="DI-1"),
        ),
        emit=lambda ctx: ctx.pass_number == 1,
        classification="decision-bearing",  # authority silent on the fork
        authority_locus=None,
    )
    return Scenario(
        id=scenario_id,
        header=_header(),
        antagonist=plant_emitter([p2]),
        coherence=no_reviewer,
        arbiter=CannedArbiter(verdicts=verdicts_for([p2])),
        fix_changes=fix_changes_for([p2]),
    )


def scenario_s2() -> Scenario:
    """S2 — arbiter classification, decision exit, unbundled surfacing (BLOCKING)."""
    return _scenario_s2(severity="BLOCKING", scenario_id="S2")


def scenario_s2b() -> Scenario:
    """S2b — severity-independence: same finding at `COSMETIC`; open_cbm==0 but the
    router must STILL halt on the open decision-bearing finding."""
    return _scenario_s2(severity="COSMETIC", scenario_id="S2b")


# --- S3: oscillation (recurrence) → HALT_DECISION ----------------------------


def scenario_s3() -> Scenario:
    """S3 — a trading pair rigged so each conforming fix re-emits the other, and
    the third pass reopens P5a with the same id (recurrence trips)."""
    p5a = Plant(
        label="P5a",
        finding=_finding(
            source="coherence-stub",
            altitude="cross-set",
            severity="MATERIAL",
            target=["DOC-A"],
            locus="p5a",
            claim="DOC-A violates AUTH-1.",
            cited_authority=CitedAuthority(kind="canonical", ref="AUTH-1 §3"),
        ),
        # Seed on pass 1; re-emitted (reopened) when fixing P5b changes DOC-B.
        emit=lambda ctx: ctx.pass_number == 1
        or ctx.doc_changed_in_prev_pass("DOC-B"),
        classification="resolvable",
        authority_locus="AUTH-1 §3",
        fix_changes_doc="DOC-A",  # fixing P5a changes DOC-A → emits P5b
    )
    p5b = Plant(
        label="P5b",
        finding=_finding(
            source="coherence-stub",
            altitude="cross-set",
            severity="MATERIAL",
            target=["DOC-B"],
            locus="p5b",
            claim="DOC-B violates AUTH-2.",
            cited_authority=CitedAuthority(kind="canonical", ref="AUTH-2 §3"),
        ),
        emit=lambda ctx: ctx.doc_changed_in_prev_pass("DOC-A"),
        classification="resolvable",
        authority_locus="AUTH-2 §3",
        fix_changes_doc="DOC-B",  # fixing P5b changes DOC-B → reopens P5a
    )
    plants = [p5a, p5b]
    return Scenario(
        id="S3",
        header=_header(),
        antagonist=no_reviewer,
        coherence=plant_emitter(plants),
        arbiter=CannedArbiter(verdicts=verdicts_for(plants)),
        fix_changes=fix_changes_for(plants),
    )


# --- S3b: plateau (no clean reopen) → HALT_DECISION --------------------------


def _s3b_churn(pass_number: int, ledger: Ledger) -> list[Finding]:
    """Coherence churn: two fresh, distinct-id resolvable findings each pass.

    The author closes them each pass, but a new pair replaces them — open_cbm
    holds flat at 2 with NO same-id reopen (recurrence stays 0). This is the
    faithful realization of 'fixes chasing their own tail' that isolates the
    plateau trigger from recurrence.
    """
    return [
        _finding(
            source="coherence-stub",
            altitude="cross-set",
            severity="MATERIAL",
            target=["DOC-A"],
            locus=f"churn-{pass_number}-a",
            claim=f"Transient cross-set conflict {pass_number}-A.",
            cited_authority=CitedAuthority(kind="coherence", ref="DOC-A×DOC-B"),
        ),
        _finding(
            source="coherence-stub",
            altitude="cross-set",
            severity="MATERIAL",
            target=["DOC-B"],
            locus=f"churn-{pass_number}-b",
            claim=f"Transient cross-set conflict {pass_number}-B.",
            cited_authority=CitedAuthority(kind="coherence", ref="DOC-A×DOC-B"),
        ),
    ]


def scenario_s3b() -> Scenario:
    """S3b — plateau without a clean reopen: open_cbm holds flat at 2, plateau
    trips at plateau_N + 1 passes → HALT_DECISION (oscillation)."""
    churn_default = ArbiterResult(
        finding_id="_",
        classification="resolvable",
        authority_locus="DOC-A×DOC-B coherence (churn)",
        rationale="each transient conflict conforms to coherence authority",
        confidence="high",
    )
    return Scenario(
        id="S3b",
        header=_header(),
        antagonist=no_reviewer,
        coherence=_s3b_churn,
        arbiter=CannedArbiter(default=churn_default),
        fix_changes={},
    )


# --- S4: scope drop at admission → CONVERGED ---------------------------------


def scenario_s4() -> Scenario:
    """S4 — the mechanical admission gate: a preference-only finding is dropped
    and never counted, so the empty ledger converges."""
    p4 = Plant(
        label="P4",
        finding=_finding(
            source="antagonist-stub",
            altitude="LAA",
            severity="MATERIAL",
            target=["DOC-B"],
            locus="p4-preference",
            claim="I'd have designed DOC-B differently.",
            cited_authority=None,  # no authority → dropped at admission
        ),
        emit=lambda ctx: ctx.pass_number == 1,
        classification="decision-bearing",  # never used — P4 is dropped pre-arbiter
        authority_locus=None,
    )
    return Scenario(
        id="S4",
        header=_header(),
        antagonist=plant_emitter([p4]),
        coherence=no_reviewer,
        arbiter=CannedArbiter(verdicts=verdicts_for([p4])),
        fix_changes=fix_changes_for([p4]),
    )


ALL_SCENARIOS = {
    "S1": scenario_s1,
    "S2": scenario_s2,
    "S2b": scenario_s2b,
    "S3": scenario_s3,
    "S3b": scenario_s3b,
    "S4": scenario_s4,
}
