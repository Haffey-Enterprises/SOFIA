# Module: tests.test_admission
# Purpose: Specify the mechanical admission gate and the identity/dedup rule.
#          The gate enforces reviewer scope structurally (a finding must carry a
#          well-formed cited_authority); the dedup rule preserves finding
#          identity across passes so a reopen is a reopen, not a new record.
# Scope:   Unit tests over admission.admit against an in-memory ledger.

from agent_loop.admission import admit
from agent_loop.ledger import CitedAuthority, Finding, Ledger, LedgerHeader
from agent_loop.log import ActionLog


def _header() -> LedgerHeader:
    return LedgerHeader(
        set=["DOC-A", "DOC-B"],
        counted_severities=["BLOCKING", "MATERIAL"],
    )


def _finding(**overrides: object) -> Finding:
    base: dict[str, object] = dict(
        source="antagonist-stub",
        altitude="LAA",
        severity="MATERIAL",
        target=["DOC-A"],
        locus="section-3",
        claim="Contradicts AUTH-1.",
        cited_authority=CitedAuthority(kind="canonical", ref="AUTH-1 §2"),
    )
    base.update(overrides)
    return Finding(**base)  # type: ignore[arg-type]


def test_admit_wellformed_finding_enters_ledger_open() -> None:
    # Arrange
    ledger = Ledger(header=_header())
    log = ActionLog()

    # Act
    result = admit(ledger, _finding(), pass_number=1, log=log)

    # Assert
    assert result.admitted is True
    assert len(ledger.findings) == 1
    admitted = ledger.findings[0]
    assert admitted.status == "open"
    assert admitted.pass_raised == 1
    assert admitted.id != ""
    assert log.of_kind("admitted")


def test_admit_drops_finding_with_null_authority_and_logs_it() -> None:
    # Arrange: the S4 planted preference-only finding.
    ledger = Ledger(header=_header())
    log = ActionLog()

    # Act
    result = admit(ledger, _finding(cited_authority=None), pass_number=1, log=log)

    # Assert: dropped, never counted, and the drop is observable.
    assert result.admitted is False
    assert ledger.findings == []
    assert log.of_kind("dropped")


def test_admit_drops_bare_preference_ref() -> None:
    # Arrange: a citation of the required *shape* but a bare preference in ref.
    ledger = Ledger(header=_header())
    log = ActionLog()
    preference = CitedAuthority(
        kind="design-intent", ref="I'd have designed it differently"
    )

    # Act
    result = admit(ledger, _finding(cited_authority=preference), pass_number=1, log=log)

    # Assert
    assert result.admitted is False
    assert ledger.findings == []


def test_admit_drops_empty_ref() -> None:
    ledger = Ledger(header=_header())
    log = ActionLog()
    result = admit(
        ledger,
        _finding(cited_authority=CitedAuthority(kind="canonical", ref="   ")),
        pass_number=1,
        log=log,
    )
    assert result.admitted is False


def test_reemitting_open_finding_does_not_create_a_second_record() -> None:
    # Arrange: same finding emitted twice while open.
    ledger = Ledger(header=_header())
    log = ActionLog()
    admit(ledger, _finding(), pass_number=1, log=log)

    # Act: emit the identical finding again (same target+locus+claim).
    result = admit(ledger, _finding(), pass_number=1, log=log)

    # Assert: still one record; dedup observed.
    assert len(ledger.findings) == 1
    assert result.admitted is False
    assert log.of_kind("dedup_open")


def test_reemitting_closed_finding_reopens_same_id_and_increments_recurrence() -> None:
    # Arrange: admit, then close the finding (simulating the author).
    ledger = Ledger(header=_header())
    log = ActionLog()
    admit(ledger, _finding(), pass_number=1, log=log)
    ledger.findings[0].status = "closed"
    ledger.findings[0].pass_closed = 1
    original_id = ledger.findings[0].id

    # Act: the SAME finding is emitted again on a later pass, phrased
    # cosmetically differently — normalization must still collide the id.
    reopen = _finding(claim="  Contradicts **AUTH-1**.  ")
    result = admit(ledger, reopen, pass_number=3, log=log)

    # Assert: no new record; the standing record reopens with the SAME id and
    # recurrence_count increments — the oscillation signal.
    assert len(ledger.findings) == 1
    reopened = ledger.findings[0]
    assert reopened.id == original_id
    assert reopened.status == "open"
    assert reopened.recurrence_count == 1
    assert reopened.classification == "unclassified"  # re-judged fresh
    assert result.reopened is True
    assert log.of_kind("reopened")


def test_reopen_preserves_pass_raised_but_clears_closure_fields() -> None:
    ledger = Ledger(header=_header())
    log = ActionLog()
    admit(ledger, _finding(), pass_number=1, log=log)
    ledger.findings[0].status = "closed"
    ledger.findings[0].pass_closed = 1
    ledger.findings[0].resolution_note = "proposed fix"

    admit(ledger, _finding(), pass_number=4, log=log)

    reopened = ledger.findings[0]
    assert reopened.pass_raised == 1  # first admission pass preserved
    assert reopened.pass_closed is None
    assert reopened.resolution_note is None


# --- RBT-69 Piece 1 blocking suite (T1–T5) -----------------------------------
#
# Identity is now (sorted(target), normalize_locus(locus), altitude); the claim
# is out of the key and retained on the record. The claim-divergence guard is the
# safety net for the one residual risk of the coarser key.


def test_t1_surface_mutation_of_claim_dedups_without_inflation() -> None:
    # T1 — the run-028 EA/§2.3 case: same (target, locus, altitude), claim
    # reworded across passes → same id → dedup_open, no new record, no open_cbm
    # inflation. The wording drift that minted a fresh id under the old claim-key
    # now collapses.
    ledger = Ledger(header=_header())
    log = ActionLog()
    admit(ledger, _finding(claim="§2.3 reversibility is under-specified."),
          pass_number=1, log=log)

    result = admit(
        ledger,
        _finding(claim="Section 2.3 does not pin the reversibility guarantee."),
        pass_number=2,
        log=log,
    )

    assert result.admitted is False
    assert len(ledger.findings) == 1  # no inflation
    assert log.of_kind("dedup_open")


def test_t2_distinct_findings_at_one_locus_both_retained_finding_stays_open() -> None:
    # T2 (adversarial) — two genuinely distinct findings at one identical
    # (target, locus, altitude), materially different claims. The divergence guard
    # fires: claim_divergence logged, BOTH claims retained and recoverable, the
    # finding stays open. Nothing is hidden and nothing is discarded.
    ledger = Ledger(header=_header())
    log = ActionLog()
    admit(ledger, _finding(claim="§2.3 omits the rollback path."),
          pass_number=1, log=log)

    result = admit(
        ledger,
        _finding(claim="§2.3 contradicts ADR-002 on ownership."),
        pass_number=1,
        log=log,
    )

    # No second record; the standing finding stays open.
    assert result.admitted is False
    assert len(ledger.findings) == 1
    standing = ledger.findings[0]
    assert standing.status == "open"
    # Both claims are recoverable from the ledger — one on `claim`, one on
    # `claim_variants` — so the cold audit can split a true two-as-one.
    both = [standing.claim, *standing.claim_variants]
    assert "§2.3 omits the rollback path." in both
    assert "§2.3 contradicts ADR-002 on ownership." in both
    # The divergence is observable.
    div = log.of_kind("claim_divergence")
    assert len(div) == 1
    assert div[0].detail["existing_claim"] == "§2.3 omits the rollback path."
    assert div[0].detail["incoming_claim"] == "§2.3 contradicts ADR-002 on ownership."


def test_t2_repeated_identical_divergent_claim_is_not_appended_twice() -> None:
    # Guard hygiene: a hat re-emitting the SAME divergent wording each pass appends
    # exactly one variant, not one per pass — distinct variants are captured,
    # duplicates are not (still nothing discarded, T2's property intact).
    ledger = Ledger(header=_header())
    log = ActionLog()
    admit(ledger, _finding(claim="claim A"), pass_number=1, log=log)
    admit(ledger, _finding(claim="claim B, materially different"), pass_number=1, log=log)
    # Cosmetic-only re-wording (case + whitespace) of variant B → normalizes equal,
    # so it is not appended a second time.
    admit(ledger, _finding(claim="Claim B,   Materially  Different"), pass_number=2, log=log)

    standing = ledger.findings[0]
    assert standing.claim_variants == ["claim B, materially different"]
    assert len(log.of_kind("claim_divergence")) == 1


def test_t3_same_claim_and_locus_different_altitude_do_not_dedup() -> None:
    # T3 — identical claim, identical locus, different altitude → two distinct ids
    # (two records). Cross-hat overlap is preserved, not deduped: a defect found by
    # two altitudes counts twice (distinct instrument's finding), by design.
    ledger = Ledger(header=_header())
    log = ActionLog()
    admit(ledger, _finding(altitude="LAA", claim="§2.3 is under-specified."),
          pass_number=1, log=log)
    result = admit(ledger, _finding(altitude="EA", claim="§2.3 is under-specified."),
                   pass_number=1, log=log)

    assert result.admitted is True
    assert len(ledger.findings) == 2
    assert ledger.findings[0].id != ledger.findings[1].id
    assert {f.altitude for f in ledger.findings} == {"LAA", "EA"}


def test_t4_reworded_reemission_of_a_closed_finding_reopens_and_counts() -> None:
    # T4 — oscillation survives the key change (a strengthening): close a finding,
    # then re-emit the same (target, locus, altitude) with the claim REWORDED. The
    # old claim-key would have missed this reopen; the new key catches it → reopen
    # + recurrence_count += 1. The bad-fix catch stays intact.
    ledger = Ledger(header=_header())
    log = ActionLog()
    admit(ledger, _finding(claim="§2.3 reversibility gap."), pass_number=1, log=log)
    ledger.findings[0].status = "closed"
    ledger.findings[0].pass_closed = 1
    original_id = ledger.findings[0].id

    result = admit(
        ledger,
        _finding(claim="The §2.3 rollback guarantee is still not pinned."),
        pass_number=3,
        log=log,
    )

    assert result.reopened is True
    reopened = ledger.findings[0]
    assert reopened.id == original_id
    assert reopened.status == "open"
    assert reopened.recurrence_count == 1
    assert log.of_kind("reopened")


def test_t5_locus_formatting_drift_dedups_but_distinct_locus_does_not() -> None:
    # T5 at the admission level — formatting-only locus drift collapses to one id
    # (dedup), a genuinely different locus does not (a new record). Mirrors the
    # normalize_locus pure-function test.
    ledger = Ledger(header=_header())
    log = ActionLog()
    admit(ledger, _finding(locus="§2.3", claim="c1"), pass_number=1, log=log)

    drift = admit(ledger, _finding(locus="**§2.3**", claim="c2"), pass_number=1, log=log)
    assert drift.admitted is False  # same id under locus normalization
    assert len(ledger.findings) == 1

    distinct = admit(ledger, _finding(locus="§2.4", claim="c3"), pass_number=1, log=log)
    assert distinct.admitted is True  # a different locus is a different finding
    assert len(ledger.findings) == 2
