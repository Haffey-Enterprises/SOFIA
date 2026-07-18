# Module: tests.test_cache_provenance
# Purpose: The RBT-69 Piece 2 blocking cache-provenance suite (C1–C2). Prove the
#          correctness invariant of reviewer-substrate caching: what each actor
#          sees is byte-identical to the uncached assembly (C1), and a
#          genuinely-different substrate produces different leading-prefix bytes
#          so no cross-run bleed is possible (C2). C3 (a multi-pass run shows hat
#          cache_read > 0 on passes 2+) is a supervised-run acceptance check read
#          from the manifest, not a unit test.
# Scope:   Pure over the assemblers + splitters + the transport's user-block
#          construction. No real API — the byte-identity guarantee is structural.

from types import SimpleNamespace

from agent_loop.author import _assemble_author_user, author_cache_prefix
from agent_loop.ledger import (
    CitedAuthority,
    Finding,
    Ledger,
    LedgerHeader,
)
from agent_loop.log import ActionLog
from agent_loop.manifest import per_site_token_totals
from agent_loop.real_hats import assemble_user_prompt, substrate_cache_prefix
from agent_loop.reviewers import DocumentSet, Substrate
from agent_loop.transport import (
    AnthropicTransport,
    LlmResponse,
    _assemble_arbiter_finding,
    _assemble_arbiter_substrate,
    _user_content_blocks,
    build_api_emitter,
)

_EPHEMERAL = {"type": "ephemeral", "ttl": "1h"}


def _reconstruct(user: str, cache_prefix: str | None) -> str:
    """The exact bytes the model receives = concatenation of the sent blocks."""
    blocks = _user_content_blocks(user, cache_prefix, _EPHEMERAL)
    return "".join(block["text"] for block in blocks)  # type: ignore[misc]


def _header() -> LedgerHeader:
    return LedgerHeader(set=["DOC-A"], counted_severities=["BLOCKING", "MATERIAL"])


def _hat_user(substrate: Substrate) -> str:
    return assemble_user_prompt(
        DocumentSet(documents={"DOC-A": "doc-a body"}),
        substrate,
        Ledger(header=_header()),
    )


def _author_user(doc_text: str = "the current text under review") -> str:
    finding = Finding(
        source="antagonist-SA",
        altitude="SA",
        severity="MATERIAL",
        target=["ADR-001"],
        locus="§2",
        claim="the locus does not conform",
        cited_authority=CitedAuthority(kind="canonical", ref="adr-template §4"),
        classification="resolvable",
        authority_locus="adr-template §4",
    )
    return _assemble_author_user(
        finding,
        reference="adr-template §4",
        authority_texts={"adr-template": "AUTHORITY TEXT"},
        documents={"ADR-001": doc_text},
    )


def _arbiter_base_user() -> tuple[str, str]:
    substrate = _assemble_arbiter_substrate(
        {"adr-template": "A"}, {"vision": "V"}
    )
    finding = Finding(
        source="antagonist-LAA",
        altitude="LAA",
        severity="MATERIAL",
        target=["ADR-001"],
        locus="§2",
        claim="c",
        cited_authority=CitedAuthority(kind="canonical", ref="r"),
        id="abc123",
    )
    return substrate + _assemble_arbiter_finding(finding), substrate


# --- C1 — byte-identity at every call site -----------------------------------


def test_c1_user_content_blocks_reconstructs_byte_identically_for_arbitrary_prefix() -> None:
    # The structural guarantee: head + tail == user, for ANY prefix — empty,
    # partial, whole, and over-length (a prefix longer than user still slices
    # safely to the whole string).
    user = "SUBSTRATE...\nDOCUMENT SET (fetched fresh):\ntail-that-morphs"
    for prefix in (None, "", "SUBSTRATE", user, user + "EXTRA-BEYOND-END"):
        assert _reconstruct(user, prefix) == user


def test_c1_hat_substrate_prefix_is_a_true_prefix_and_reconstructs() -> None:
    user = _hat_user(Substrate(authorities={"a": "A"}, design_intent={"d": "D"}))
    prefix = substrate_cache_prefix(user)
    assert prefix is not None
    assert user.startswith(prefix)  # a genuine leading slice
    assert prefix.endswith("\n\n")  # ends before the DOCUMENT SET heading
    assert "DOCUMENT SET" not in prefix  # never the morphing tail
    assert _reconstruct(user, prefix) == user  # byte-identical


def test_c1_author_document_prefix_is_a_true_prefix_and_reconstructs() -> None:
    user = _author_user()
    prefix = author_cache_prefix(user)
    assert prefix is not None
    assert user.startswith(prefix)
    assert "RESOLVABLE FINDING" not in prefix  # finding stays in the uncached tail
    assert "the current text under review" in prefix  # the stable doc IS cached
    assert _reconstruct(user, prefix) == user


def test_c1_arbiter_substrate_is_a_true_prefix_and_reconstructs() -> None:
    base_user, substrate = _arbiter_base_user()
    assert base_user.startswith(substrate)  # substrate fronts the finding by construction
    assert "FINDING:" not in substrate  # the per-finding tail is not in the prefix
    assert _reconstruct(base_user, substrate) == base_user


def test_c1_empty_tail_yields_no_empty_block() -> None:
    # A prefix covering the whole user drops the empty tail block (the API rejects
    # an empty text block) — still byte-identical.
    user = "WHOLE"
    blocks = _user_content_blocks(user, user, _EPHEMERAL)
    assert len(blocks) == 1
    assert _reconstruct(user, user) == user


# --- C2 — cross-run isolation -------------------------------------------------


def test_c2_different_substrate_yields_different_hat_prefix_bytes() -> None:
    user_run1 = _hat_user(Substrate(authorities={"a": "RUN-1 AUTHORITY"}, design_intent={}))
    user_run2 = _hat_user(Substrate(authorities={"a": "RUN-2 AUTHORITY"}, design_intent={}))
    p1 = substrate_cache_prefix(user_run1)
    p2 = substrate_cache_prefix(user_run2)
    # Content-addressed keying makes cross-run reuse of a genuinely-different
    # substrate impossible: different substrate → different prefix bytes.
    assert p1 != p2


def test_c2_identical_substrate_yields_identical_prefix_bytes() -> None:
    # A hit on identical bytes is correct by construction, not bleed: the same
    # frozen substrate (re-assembled, as each pass does) produces the same prefix,
    # which is exactly what lets passes 2+ read the cache (C3).
    substrate = Substrate(authorities={"a": "STABLE"}, design_intent={"d": "STABLE"})
    p1 = substrate_cache_prefix(_hat_user(substrate))
    p2 = substrate_cache_prefix(_hat_user(substrate))
    assert p1 == p2 is not None


def test_c2_different_run_document_yields_different_author_prefix_bytes() -> None:
    p1 = author_cache_prefix(_author_user("RUN-1 document body"))
    p2 = author_cache_prefix(_author_user("RUN-2 document body"))
    assert p1 != p2


# --- splitter guards (a valid prefix or nothing, never the tail) --------------


def test_substrate_prefix_returns_none_when_heading_absent() -> None:
    assert substrate_cache_prefix("no heading here at all") is None


def test_author_prefix_returns_none_when_heading_at_position_zero() -> None:
    # Degenerate assembly starting with the variable heading → no caching, never a
    # zero-length or wrong prefix.
    assert author_cache_prefix("RESOLVABLE FINDING:\nx") is None
    assert substrate_cache_prefix("DOCUMENT SET (fetched fresh):\nx") is None


# --- 1-hour-TTL observability + structural proof (RBT-69 review follow-up) ----


def _recording_client() -> tuple[object, dict]:
    """A fake Anthropic SDK client that records the `messages.create` kwargs."""
    seen: dict = {}
    message = SimpleNamespace(
        content=[SimpleNamespace(text="ok")],
        usage=SimpleNamespace(input_tokens=1, output_tokens=1),
    )

    def create(**kw):
        seen.update(kw)
        return message

    return SimpleNamespace(messages=SimpleNamespace(create=create)), seen


def test_outgoing_ttl_is_1h_on_both_run_frozen_breakpoints() -> None:
    # Verification method 1 (structural): the 1-hour TTL is SENT on both run-frozen
    # breakpoints — the system block and the leading user cache-prefix (head) block
    # — for a call made with a cache_prefix. Pins the outgoing marker so a silent
    # drop back to the 5-minute default would fail here.
    client, seen = _recording_client()
    AnthropicTransport(client)("SYS", "PREFIXtail", "m", 10, cache_prefix="PREFIX")

    expected_cc = {"type": "ephemeral", "ttl": "1h"}
    # (a) system block.
    assert seen["system"][0]["cache_control"] == expected_cc
    # (b) leading user head block; the tail stays uncached.
    head, tail = seen["messages"][0]["content"]
    assert head["cache_control"] == expected_cc
    assert head["text"] == "PREFIX"
    assert "cache_control" not in tail  # the morphing tail is never TTL-marked


def test_anthropic_transport_captures_1h_5m_cache_creation_split() -> None:
    # Verification method 2 (parse): the response's usage.cache_creation 1h/5m split
    # is captured onto LlmResponse so the TTL application is a measured fact.
    message = SimpleNamespace(
        content=[SimpleNamespace(text="ok")],
        usage=SimpleNamespace(
            input_tokens=50,
            output_tokens=2,
            cache_creation_input_tokens=248,
            cache_read_input_tokens=1800,
            cache_creation=SimpleNamespace(
                ephemeral_1h_input_tokens=100,
                ephemeral_5m_input_tokens=148,
            ),
        ),
    )
    client = SimpleNamespace(messages=SimpleNamespace(create=lambda **kw: message))
    response = AnthropicTransport(client)("SYS", "USER", "m", 10)

    assert response.cache_creation_input_tokens == 248
    assert response.cache_creation_ephemeral_1h_input_tokens == 100
    assert response.cache_creation_ephemeral_5m_input_tokens == 148
    # The split sums to the total (the two buckets partition cache-creation).
    assert (
        response.cache_creation_ephemeral_1h_input_tokens
        + response.cache_creation_ephemeral_5m_input_tokens
        == response.cache_creation_input_tokens
    )


def test_anthropic_transport_missing_cache_creation_defaults_split_to_zero() -> None:
    # Defensive path: a no-cache response carries no `cache_creation` sub-object —
    # the extraction must default both buckets to 0, never raise.
    message = SimpleNamespace(
        content=[SimpleNamespace(text="ok")],
        usage=SimpleNamespace(input_tokens=7, output_tokens=1),  # no cache_creation
    )
    client = SimpleNamespace(messages=SimpleNamespace(create=lambda **kw: message))
    response = AnthropicTransport(client)("SYS", "USER", "m", 10)

    assert response.cache_creation_ephemeral_1h_input_tokens == 0
    assert response.cache_creation_ephemeral_5m_input_tokens == 0


class _SplitTransport:
    """A fake transport returning a response carrying the 1h/5m TTL-bucket split."""

    def __call__(self, system, user, model, max_tokens, cache_prefix=None):  # noqa: ANN001
        return LlmResponse(
            text="out",
            input_tokens=5,
            output_tokens=3,
            cache_creation_input_tokens=248,
            cache_read_input_tokens=1800,
            cache_creation_ephemeral_1h_input_tokens=100,
            cache_creation_ephemeral_5m_input_tokens=148,
        )


def test_llm_call_event_and_manifest_carry_the_ttl_bucket_split() -> None:
    # The split propagates from LlmResponse → the `llm_call` provenance event →
    # the per-site manifest totals: the C3 proof surface, per actor.
    log = ActionLog()
    emit = build_api_emitter(
        site_label="antagonist-LAA",
        model="m",
        max_tokens=10,
        log=log,
        transport=_SplitTransport(),
        now=iter([0.0, 0.001]).__next__,
        sleeper=lambda s: None,
    )
    emit("SYS", "USER")

    call = log.of_kind("llm_call")[0].detail
    assert call["cache_creation_ephemeral_1h_input_tokens"] == 100
    assert call["cache_creation_ephemeral_5m_input_tokens"] == 148

    totals = per_site_token_totals(log)["antagonist-LAA"]
    assert totals["cache_creation_ephemeral_1h_input_tokens"] == 100
    assert totals["cache_creation_ephemeral_5m_input_tokens"] == 148
    assert totals["cache_creation_input_tokens"] == 248


def test_cache_prefix_never_carries_snapshot_or_document_set() -> None:
    # Belt-and-suspenders on the correctness invariant: the morphing surface — the
    # document set and the growing ledger snapshot — is in the uncached tail,
    # never the cached head.
    user = _hat_user(Substrate(authorities={"a": "A"}, design_intent={}))
    prefix = substrate_cache_prefix(user)
    assert prefix is not None
    assert "LEDGER SNAPSHOT" not in prefix
    assert "DOCUMENT SET" not in prefix
    assert "doc-a body" not in prefix
