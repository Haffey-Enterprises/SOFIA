# Module: agent_loop.transport
# Purpose: The real LLM transport, emitter, and arbiter adapter for supervised
#          runs (run-prep.contract.md §5, §6, §7). One fixed model per run,
#          no sampling parameters, no tools, one user turn; sequential calls in admission
#          order. Transport-level failure gets ONE retry after a bounded backoff
#          then aborts loudly; the arbiter additionally gets ONE content retry on
#          malformed output then aborts — never a fabricated classification.
#          Every call logs an `llm_call` provenance event (site, model, params,
#          system-prompt hash, tokens, latency).
# Scope:   Transport + call policy + provenance. Content-level reviewer
#          malformation stays with the real_hats parse seam (§7 of the runner
#          contract), never retried here. The real Anthropic client is
#          constructed only on the launch path (pragma: no cover); all logic is
#          driven by an injected Transport so no test makes a real API call.

from __future__ import annotations

import json
import time
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Callable, Protocol

from agent_loop.arbiter import ArbiterResult
from agent_loop.fetchers import sha256_text
from agent_loop.ledger import Finding
from agent_loop.log import ActionLog
from agent_loop.real_hats import load_system_prompt, strip_code_fences

# An LLM emitter (matches real_hats.LlmEmitter): (system, user) -> raw text.
LlmEmitter = Callable[[str, str], str]


class LlmTransportError(RuntimeError):
    """A transport-level failure (rate limit, 5xx, timeout, connection).

    Raised by a Transport when the API call itself fails. Content-level
    malformation is NOT this — it is a well-formed transport response whose body
    parses badly, handled by the parse seam (reviewers) or the arbiter's content
    retry.
    """


class ArbiterParseError(RuntimeError):
    """The arbiter output could not be parsed after its one content retry."""


@dataclass(frozen=True)
class LlmResponse:
    """A successful transport response.

    Attributes:
        text: The model's raw text output.
        input_tokens: Uncached prompt tokens, from the API usage block. When
            prompt caching is active this is the *uncached* input only — the
            cached portion is reported separately below (RBT-49 Item 1 §4).
        output_tokens: Completion tokens, from the API usage block.
        request_id: The API request id (from the SDK response), or None.
        cache_creation_input_tokens: Tokens written to the prompt cache on this
            call (full price; the first call over a fresh prefix). 0 when no
            cache write occurred or the response carries no cache usage.
        cache_read_input_tokens: Tokens read from the prompt cache on this call
            (a small fraction of base input; repeated prefixes). 0 otherwise.
        cache_creation_ephemeral_1h_input_tokens: The share of
            `cache_creation_input_tokens` written to the **1-hour** TTL bucket
            (RBT-69 Piece 2 marks the run-frozen breakpoints `ttl:"1h"`). Captured
            so a supervised run can prove the writes landed in the 1h bucket, not
            the default 5m one — the TTL application becomes a logged fact, not an
            assumption. 0 when the response carries no `cache_creation` sub-object.
        cache_creation_ephemeral_5m_input_tokens: The share written to the
            **5-minute** TTL bucket (the two sum to `cache_creation_input_tokens`).
        stop_reason: Why the model stopped (`end_turn`, `max_tokens`, …), from
            the API response, or None when the response carries none (run-016
            diagnosis rider — distinguishes a self-terminated empty emission from
            a truncated one).
    """

    text: str
    input_tokens: int
    output_tokens: int
    request_id: str | None = None
    cache_creation_input_tokens: int = 0
    cache_read_input_tokens: int = 0
    cache_creation_ephemeral_1h_input_tokens: int = 0
    cache_creation_ephemeral_5m_input_tokens: int = 0
    stop_reason: str | None = None


class Transport(Protocol):
    """The transport port: one stateless API call, or raise LlmTransportError.

    No sampling parameters are part of the signature: `temperature`, `top_p`,
    and `top_k` are deprecated on Claude Opus 4.7+ and 400 on non-default values
    (run-prep §6, amended 2026-07-02). Only `max_tokens` is sent.

    `cache_prefix` (RBT-49 Item 1) is request metadata, not prompt content: when
    supplied it is the leading, byte-identical-across-calls portion of `user`
    (its length locates the cache breakpoint; the sent user content is always
    exactly `user`). None means no user-level caching for this call — the system
    block is still marked cacheable.
    """

    def __call__(
        self,
        system: str,
        user: str,
        model: str,
        max_tokens: int,
        cache_prefix: str | None = None,
    ) -> LlmResponse:
        """Make one Messages API call and return the response, or raise."""
        ...


# --- Anthropic transport (real client injected; logic tested with a fake) -----


class AnthropicTransport:
    """Transport over the Anthropic Messages API via the official SDK client.

    The client is injected so the extraction/error-wrapping logic is testable
    with a fake; the real `anthropic.Anthropic()` is built only on the launch
    path. Exactly the contract's context: system verbatim, one user turn, no
    tools, no extra turns.
    """

    def __init__(self, client: object) -> None:
        """Bind an Anthropic-SDK-shaped client (`.messages.create`)."""
        self._client = client

    def __call__(
        self,
        system: str,
        user: str,
        model: str,
        max_tokens: int,
        cache_prefix: str | None = None,
    ) -> LlmResponse:
        """Call the API and normalize the response, wrapping failures.

        Sends `max_tokens` only — no `temperature`/`top_p`/`top_k` (deprecated
        on Opus 4.7+; omitted entirely, not sent as null).

        Prompt caching (RBT-49 Item 1): the system block is always marked
        `cache_control` ephemeral, so a repeated system prefix (the arbiter's
        identical system across N findings; a hat's system across passes) reads
        from cache. When `cache_prefix` is supplied, `user` is additionally split
        at `len(cache_prefix)` into a cached head block and an uncached tail
        block — the head is sliced from `user` itself, so the content the model
        receives is byte-identical to the uncached path regardless of what
        `cache_prefix` is. A sub-minimum prefix is simply not cached by the API
        (no error), so marking is always safe.

        Cache TTL (RBT-69 Piece 2): both cache breakpoints — the run-frozen system
        block and the run-frozen leading substrate/document head — carry the
        1-hour TTL, so the cache survives the multi-minute gaps between passes
        (the default 5-minute ephemeral TTL expired *between* passes, giving the
        once-per-pass hats ≈0 cache_read; run-028). The 1-hour TTL is GA on the
        first-party Messages API via `cache_control.ttl` — no beta header. The
        morphing surface (document set, growing ledger snapshot) is never marked,
        so it stays the uncached tail. Cost trade (stated honestly): a 1-hour
        write is priced above a 5-minute write; reads are equally cheap —
        net-positive whenever a prefix is re-read across ≥2 passes, mildly
        wasteful on a single-pass run (which is cheap regardless).
        """
        ephemeral = {"type": "ephemeral", "ttl": "1h"}
        system_blocks = [{"type": "text", "text": system, "cache_control": ephemeral}]
        content = _user_content_blocks(user, cache_prefix, ephemeral)
        try:
            message = self._client.messages.create(  # type: ignore[attr-defined]
                model=model,
                max_tokens=max_tokens,
                system=system_blocks,
                messages=[{"role": "user", "content": content}],
            )
        except Exception as exc:  # noqa: BLE001 — any SDK failure is transport-level
            raise LlmTransportError(f"anthropic transport failed: {exc}") from exc
        text = "".join(
            getattr(block, "text", "") for block in getattr(message, "content", [])
        )
        usage = message.usage
        # The 1h/5m split lives in a `cache_creation` sub-object that is absent or
        # partial on a no-cache response — extract it with the same defensive
        # `getattr(..., 0) or 0` pattern as the totals above, so a response with no
        # cache usage yields 0/0 rather than raising.
        cache_creation = getattr(usage, "cache_creation", None)
        return LlmResponse(
            text=text,
            input_tokens=usage.input_tokens,
            output_tokens=usage.output_tokens,
            request_id=getattr(message, "_request_id", None),
            cache_creation_input_tokens=getattr(usage, "cache_creation_input_tokens", 0) or 0,
            cache_read_input_tokens=getattr(usage, "cache_read_input_tokens", 0) or 0,
            cache_creation_ephemeral_1h_input_tokens=getattr(
                cache_creation, "ephemeral_1h_input_tokens", 0
            )
            or 0,
            cache_creation_ephemeral_5m_input_tokens=getattr(
                cache_creation, "ephemeral_5m_input_tokens", 0
            )
            or 0,
            stop_reason=getattr(message, "stop_reason", None),
        )


def _user_content_blocks(
    user: str, cache_prefix: str | None, ephemeral: dict[str, str]
) -> list[dict[str, object]]:
    """Build the user message content blocks, placing the cache breakpoint.

    Without a `cache_prefix`, one uncached text block. With one, the leading
    `len(cache_prefix)` characters of `user` become a `cache_control` block (the
    cache breakpoint — it also caches everything before it in the request, i.e.
    the system block) and the remainder an uncached tail. An empty tail is
    dropped so no empty text block is sent.
    """
    if not cache_prefix:
        return [{"type": "text", "text": user}]
    split = len(cache_prefix)
    head = user[:split]
    tail = user[split:]
    blocks: list[dict[str, object]] = [
        {"type": "text", "text": head, "cache_control": ephemeral}
    ]
    if tail:
        blocks.append({"type": "text", "text": tail})
    return blocks


# --- call policy: one transport retry, per-call provenance -------------------


def _timed_call(
    transport: Transport,
    system: str,
    user: str,
    site_label: str,
    model: str,
    max_tokens: int,
    log: ActionLog,
    now: Callable[[], float],
    capture: object | None,
    cache_prefix: str | None,
) -> LlmResponse:
    """Make one transport call; capture the raw body, then log the `llm_call`.

    The raw response body is written to the emissions folder BEFORE any parsing
    (run-prep §7); the `llm_call` carries the API request_id and the emission
    file path. When `capture` is None (unit tests without a run folder), no file
    is written and `emission_path` is None. The event carries the split of input
    tokens into cache-creation / cache-read / uncached (RBT-49 Item 1 §4) so the
    cached vs uncached cost is distinguishable per call and summable per run.
    """
    start = now()
    response = transport(system, user, model, max_tokens, cache_prefix)
    latency_ms = (now() - start) * 1000.0
    emission_path = capture.write(site_label, response.text) if capture is not None else None  # type: ignore[attr-defined]
    log.emit(
        "llm_call",
        site=site_label,
        model=model,
        max_tokens=max_tokens,
        system_sha256=sha256_text(system),
        input_tokens=response.input_tokens,
        output_tokens=response.output_tokens,
        cache_creation_input_tokens=response.cache_creation_input_tokens,
        cache_read_input_tokens=response.cache_read_input_tokens,
        cache_creation_ephemeral_1h_input_tokens=response.cache_creation_ephemeral_1h_input_tokens,
        cache_creation_ephemeral_5m_input_tokens=response.cache_creation_ephemeral_5m_input_tokens,
        latency_ms=latency_ms,
        request_id=response.request_id,
        stop_reason=response.stop_reason,
        emission_path=emission_path,
    )
    return response


def _call_with_transport_retry(
    transport: Transport,
    system: str,
    user: str,
    site_label: str,
    model: str,
    max_tokens: int,
    log: ActionLog,
    sleeper: Callable[[float], None],
    backoff_seconds: float,
    now: Callable[[], float],
    capture: object | None,
    cache_prefix: str | None = None,
) -> LlmResponse:
    """One transport call with a single bounded-backoff retry, then abort.

    A first transport failure logs `llm_retry`, sleeps `backoff_seconds`, and
    retries once; a second failure propagates (the run aborts loudly — a run
    minus one hat corrupts the independence evidence).
    """
    try:
        return _timed_call(
            transport, system, user, site_label, model, max_tokens, log, now, capture, cache_prefix
        )
    except LlmTransportError as first_error:
        log.emit(
            "llm_retry",
            site=site_label,
            retry_kind="transport",
            backoff_s=backoff_seconds,
            error=str(first_error),
        )
        sleeper(backoff_seconds)
        return _timed_call(
            transport, system, user, site_label, model, max_tokens, log, now, capture, cache_prefix
        )


def build_api_emitter(
    *,
    site_label: str,
    model: str,
    max_tokens: int,
    log: ActionLog,
    transport: Transport,
    now: Callable[[], float] = time.monotonic,
    sleeper: Callable[[float], None] = time.sleep,
    backoff_seconds: float = 30.0,
    capture: object | None = None,
    cache_prefix_of: Callable[[str], str | None] | None = None,
) -> LlmEmitter:
    """Build a per-call-site emitter binding a hat's label to the transport.

    Per-call-site construction is what lands token attribution per hat: every
    call this emitter makes logs an `llm_call` under `site_label`. The emitter's
    signature is the unchanged `LlmEmitter` port `(system, user) -> str`;
    content-level malformation is returned as-is for the parse seam, never
    retried here. Only `max_tokens` is sent — no sampling parameters (run-prep
    §6). When `capture` is supplied, the raw body is written before parsing and
    its path lands on the `llm_call`.

    Caching (RBT-49 Item 1 / RBT-69 Piece 2): `cache_prefix_of` is an optional
    splitter that, given the call's own assembled `user`, returns the leading
    run-frozen prefix to cache (the hat substrate; the author's run document) —
    or `None` for no user-level caching. It is applied to `user` *inside* this
    closure, so the `LlmEmitter` port stays `(system, user) -> str` and the
    prefix is a genuine slice of the sent bytes (the content-neutrality guarantee
    of `_user_content_blocks` — never a hand-built substrate string that could
    diverge from what is sent). When omitted, no user-level `cache_prefix` is
    passed; the transport still marks the system block cacheable, so a hat's
    repeated system across passes reads from cache.
    """

    def emit(system: str, user: str) -> str:
        cache_prefix = cache_prefix_of(user) if cache_prefix_of is not None else None
        response = _call_with_transport_retry(
            transport,
            system,
            user,
            site_label,
            model,
            max_tokens,
            log,
            sleeper,
            backoff_seconds,
            now,
            capture,
            cache_prefix,
        )
        return response.text

    return emit


# --- arbiter adapter: strict parse, one content retry, never fabricate -------


def _format_substrate(obj: object) -> str:
    """Render an authorities/design-intent substrate object for the user block."""
    if isinstance(obj, dict):
        if not obj:
            return "(none)"
        return "\n\n".join(f"### {key}\n{value}" for key, value in sorted(obj.items()))
    return str(obj)


def _assemble_arbiter_substrate(authorities: object, design_intent: object) -> str:
    """Assemble the arbiter's static substrate block (the cacheable prefix).

    Authorities + design intent are identical across every finding in a run, so
    this block fronts a byte-identical cache prefix (RBT-49 Item 1). Per the Ra-2
    reorder it precedes the finding; the trailing blank line separates it from
    the finding tail so the concatenation renders as the reordered `## User`
    template (authorities → design intent → finding).
    """
    return (
        "RATIFIED AUTHORITIES (fetched fresh):\n"
        f"{_format_substrate(authorities)}\n\n"
        "STATED DESIGN INTENT (fetched fresh):\n"
        f"{_format_substrate(design_intent)}\n\n"
    )


def _assemble_arbiter_finding(finding: Finding) -> str:
    """Assemble the arbiter's per-finding tail (the variable, uncached part).

    Concatenated after the substrate this renders the reordered `## User`
    template (authorities → design intent → finding); `ApiArbiter.classify` keeps
    the two apart so the substrate can be marked as the cache prefix.
    """
    return "FINDING:\n" f"{json.dumps(asdict(finding), indent=2)}"


def _parse_arbiter_output(raw_text: str, finding_id: str) -> ArbiterResult | None:
    """Parse arbiter output into an ArbiterResult, or None if malformed.

    Strict: classification must be in the schema vocabulary and confidence must
    be present and valid against the categorical vocabulary — both enforced by
    ArbiterResult construction. `finding_id` is stamped from the actual finding,
    not trusted from the model's echo. Any structural or vocabulary defect
    returns None (a content malformation), never a fabricated classification.
    The raw text is fence-unwrapped first (transport unwrapping only).
    """
    try:
        data = json.loads(strip_code_fences(raw_text))
        return ArbiterResult(
            finding_id=finding_id,
            classification=data["classification"],
            authority_locus=data.get("authority_locus"),
            rationale=data["rationale"],
            confidence=data["confidence"],
        )
    except (json.JSONDecodeError, KeyError, TypeError, ValueError):
        return None


# The three required keys the parser subscripts (authority_locus is optional via
# .get); a corrective retry names any of these that are absent.
_ARBITER_REQUIRED_KEYS = ("classification", "rationale", "confidence")


def _diagnose_arbiter_defect(raw_text: str) -> str:
    """Name why arbiter output failed to parse, for a corrective retry message.

    Read-only diagnosis that mirrors `_parse_arbiter_output`'s checks WITHOUT
    changing the parser's strictness — it does not construct an ArbiterResult or
    alter what parses. It reports the actual defect minimally: a JSON parse
    failure (bad JSON or a non-object), missing required key(s) by name after
    fence-stripping, or (keys present but rejected) an invalid vocabulary value.
    """
    try:
        data = json.loads(strip_code_fences(raw_text))
    except json.JSONDecodeError:
        return "the previous output was not valid JSON"
    if not isinstance(data, dict):
        return "the previous output was not a JSON object"
    missing = [key for key in _ARBITER_REQUIRED_KEYS if key not in data]
    if missing:
        return "the previous output was missing required key(s): " + ", ".join(missing)
    return (
        "the previous output used an invalid vocabulary value (classification "
        "must be 'resolvable' or 'decision-bearing'; confidence must be 'high', "
        "'medium', or 'low'; a 'resolvable' needs an authority_locus and cannot "
        "be low confidence)"
    )


def _arbiter_repair_suffix(defect: str) -> str:
    """The corrective instruction appended to the user block on the content retry.

    Names the diagnosed defect, then restates the Output-section contract so the
    second attempt is corrected rather than blindly re-prompted with the same
    input. Appended to the base user block; the block itself is unchanged.
    """
    return (
        f"\n\nYOUR PREVIOUS RESPONSE COULD NOT BE PARSED: {defect}. "
        "Emit the complete raw JSON object per the Output section — all five "
        "fields, no fences, first character {."
    )


class ApiArbiter:
    """Real arbiter over the API — the sole LLM on the exit path.

    Loads `arbiter-classifier.prompt.md`'s `## System` as data, assembles its
    user block from the finding plus the substrate handed to `run_loop`, and
    applies the §5 transport with the §6 call policy. Malformed output gets ONE
    corrective content retry — the second attempt's user block names the actual
    defect (logged) — then aborts. The conservative decision-bearing bias lives
    in the prompt, never fabricated by fallback code.
    """

    def __init__(
        self,
        *,
        prompt_path: str | Path,
        transport: Transport,
        log: ActionLog,
        model: str,
        max_tokens: int,
        now: Callable[[], float] = time.monotonic,
        sleeper: Callable[[float], None] = time.sleep,
        backoff_seconds: float = 30.0,
        capture: object | None = None,
    ) -> None:
        """Load the arbiter prompt and bind transport + call policy."""
        self._system = load_system_prompt(prompt_path)
        self._transport = transport
        self._log = log
        self._model = model
        self._max_tokens = max_tokens
        self._now = now
        self._sleeper = sleeper
        self._backoff = backoff_seconds
        self._capture = capture

    def classify(
        self, finding: Finding, authorities: object, design_intent: object
    ) -> ArbiterResult:
        """Classify one finding, with one corrective content retry then abort.

        On a first malformed output, the second attempt appends a repair
        instruction that names the actual defect (the transport retry count,
        abort behavior, and parser strictness are unchanged — only the retry's
        user block is made corrective).
        """
        # The substrate is byte-identical across every finding this run and
        # fronts base_user (and the corrective retry), so it is the cache prefix
        # (RBT-49 Item 1): one full-price write on the first finding, cheap reads
        # thereafter; the finding tail is uncached.
        substrate = _assemble_arbiter_substrate(authorities, design_intent)
        base_user = substrate + _assemble_arbiter_finding(finding)
        user = base_user
        for attempt in (1, 2):
            response = _call_with_transport_retry(
                self._transport,
                self._system,
                user,
                "arbiter",
                self._model,
                self._max_tokens,
                self._log,
                self._sleeper,
                self._backoff,
                self._now,
                self._capture,
                substrate,
            )
            parsed = _parse_arbiter_output(response.text, finding.id)
            if parsed is not None:
                return parsed
            if attempt == 1:
                defect = _diagnose_arbiter_defect(response.text)
                self._log.emit(
                    "llm_retry",
                    site="arbiter",
                    retry_kind="content",
                    reason="malformed classification output",
                    defect=defect,
                )
                user = base_user + _arbiter_repair_suffix(defect)
        raise ArbiterParseError(
            f"arbiter output for finding {finding.id!r} malformed after one "
            "content retry — aborting rather than fabricating a classification"
        )


def build_real_transport() -> AnthropicTransport:  # pragma: no cover
    """Construct the real Anthropic transport (launch path only).

    Imports the SDK lazily and reads `ANTHROPIC_API_KEY` from the environment
    (the SDK's default). Excluded from coverage: it is the one real-infrastructure
    line that needs the installed SDK plus a live key to construct; all transport
    logic above is driven by an injected Transport and fully tested with fakes.
    """
    import anthropic

    return AnthropicTransport(anthropic.Anthropic())
