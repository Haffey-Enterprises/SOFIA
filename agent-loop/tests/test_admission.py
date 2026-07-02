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
