# Module: tests.test_identity
# Purpose: Lock the finding-identity/normalization rule — the load-bearing
#          subtlety the ledger schema (§Identity) demands its own test for.
#          A stable id across passes is what makes oscillation detection
#          possible; minting a fresh id per pass silently disables it. RBT-69
#          moved altitude INTO the key and claim OUT of it, and added
#          normalize_locus alongside normalize_claim.
# Scope:   Pure unit tests over identity.normalize_claim / normalize_locus /
#          derive_id.

from agent_loop.identity import derive_id, normalize_claim, normalize_locus


def test_normalize_claim_strips_wording_and_formatting_noise() -> None:
    # Arrange: same claim, cosmetically different (case, markdown, whitespace,
    # punctuation). Retained for the divergence guard, no longer identity-bearing.
    a = "The **cache TTL** contradicts AUTH-1."
    b = "the   cache ttl contradicts auth-1"

    # Act / Assert
    assert normalize_claim(a) == normalize_claim(b)


def test_normalize_locus_strips_formatting_noise() -> None:
    # Formatting-only locus drift collapses to one canonical form (T5, first half).
    assert normalize_locus("§2.3") == normalize_locus("**§2.3**")
    assert normalize_locus("  Section 2.3  ") == normalize_locus("section 2.3")


def test_normalize_locus_keeps_distinct_loci_distinct() -> None:
    # Conservative: a genuinely different section anchor must NOT collapse (T5,
    # second half) — over-normalizing a locus would merge distinct loci.
    assert normalize_locus("§2.3") != normalize_locus("§2.4")
    assert normalize_locus("ownership") != normalize_locus("retention")


def test_derive_id_is_stable_across_cosmetic_claim_variants() -> None:
    # Arrange: identical target+locus+altitude; the claim is no longer in the key,
    # so ANY claim (reworded or wholly different) yields the SAME id.
    target = ["DOC-A"]
    locus = "section-3"

    # Act
    id_v1 = derive_id(target, locus, "LAA")
    id_v2 = derive_id(target, locus, "LAA")

    # Assert: a hat's re-emission of its own stance-at-locus hashes to the SAME id.
    assert id_v1 == id_v2


def test_derive_id_is_stable_across_locus_formatting_drift() -> None:
    # Formatting-only locus drift with the same target+altitude → same id.
    assert derive_id(["DOC-A"], "§2.3", "EA") == derive_id(["DOC-A"], "**§2.3**", "EA")


def test_derive_id_is_order_independent_over_target_documents() -> None:
    # A cross-set finding names two docs; emission order must not change identity.
    locus = "ownership"
    assert derive_id(["DOC-A", "DOC-B"], locus, "cross-set") == derive_id(
        ["DOC-B", "DOC-A"], locus, "cross-set"
    )


def test_derive_id_differs_by_altitude() -> None:
    # T3 at the pure-function level: identical target+locus, different altitude →
    # different id (cross-hat overlap preserved, not deduped).
    target = ["DOC-A"]
    locus = "section-3"
    assert derive_id(target, locus, "LAA") != derive_id(target, locus, "EA")


def test_derive_id_differs_when_target_or_locus_differs() -> None:
    assert derive_id(["DOC-A"], "s3", "LAA") != derive_id(["DOC-B"], "s3", "LAA")
    assert derive_id(["DOC-A"], "s3", "LAA") != derive_id(["DOC-A"], "s4", "LAA")
