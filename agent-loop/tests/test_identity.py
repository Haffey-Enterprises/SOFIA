# Module: tests.test_identity
# Purpose: Lock the finding-identity/normalization rule — the load-bearing
#          subtlety the ledger schema (§Identity) demands its own test for.
#          A stable id across passes is what makes oscillation detection
#          possible; minting a fresh id per pass silently disables it.
# Scope:   Pure unit tests over identity.normalize_claim / derive_id.

from agent_loop.identity import derive_id, normalize_claim


def test_normalize_claim_strips_wording_and_formatting_noise() -> None:
    # Arrange: same claim, cosmetically different (case, markdown, whitespace,
    # punctuation).
    a = "The **cache TTL** contradicts AUTH-1."
    b = "the   cache ttl contradicts auth-1"

    # Act
    na = normalize_claim(a)
    nb = normalize_claim(b)

    # Assert: normalization collapses the noise to the same canonical form.
    assert na == nb


def test_derive_id_is_stable_across_cosmetic_claim_variants() -> None:
    # Arrange: identical target+locus, claim differs only cosmetically.
    target = ["DOC-A"]
    locus = "section-3"
    claim_v1 = "The cache TTL contradicts AUTH-1."
    claim_v2 = "the  CACHE ttl   contradicts auth-1"

    # Act
    id_v1 = derive_id(target, locus, claim_v1)
    id_v2 = derive_id(target, locus, claim_v2)

    # Assert: a genuinely-recurring finding hashes to the SAME id.
    assert id_v1 == id_v2


def test_derive_id_is_order_independent_over_target_documents() -> None:
    # Arrange: a cross-set finding names two docs; emission order must not
    # change identity.
    claim = "DOC-A and DOC-B disagree on ownership."
    locus = "ownership"

    # Act / Assert
    assert derive_id(["DOC-A", "DOC-B"], locus, claim) == derive_id(
        ["DOC-B", "DOC-A"], locus, claim
    )


def test_derive_id_differs_when_claim_substance_differs() -> None:
    # Arrange: same target+locus, materially different claim.
    target = ["DOC-A"]
    locus = "section-3"

    # Act
    id_a = derive_id(target, locus, "The cache TTL contradicts AUTH-1.")
    id_b = derive_id(target, locus, "The retry budget contradicts AUTH-2.")

    # Assert: substance change must yield a different id (else real recurrence
    # collides with unrelated findings).
    assert id_a != id_b


def test_derive_id_differs_when_target_or_locus_differs() -> None:
    claim = "Contradicts AUTH-1."

    assert derive_id(["DOC-A"], "s3", claim) != derive_id(["DOC-B"], "s3", claim)
    assert derive_id(["DOC-A"], "s3", claim) != derive_id(["DOC-A"], "s4", claim)
