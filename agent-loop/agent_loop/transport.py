# Module: agent_loop.transport
# Purpose: The real LLM transport, emitter, and arbiter adapter for supervised
#          runs (run-prep.contract.md §5, §6, §7). One fixed model per run,
#          temperature 0, no tools, one user turn; sequential calls in admission
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
from agent_loop.real_hats import load_system_prompt

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
        input_tokens: Prompt tokens, from the API usage block.
        output_tokens: Completion tokens, from the API usage block.
    """

    text: str
    input_tokens: int
    output_tokens: int


class Transport(Protocol):
    """The transport port: one stateless API call, or raise LlmTransportError."""

    def __call__(
        self, system: str, user: str, model: str, temperature: float, max_tokens: int
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
        self, system: str, user: str, model: str, temperature: float, max_tokens: int
    ) -> LlmResponse:
        """Call the API and normalize the response, wrapping failures."""
        try:
            message = self._client.messages.create(  # type: ignore[attr-defined]
                model=model,
                max_tokens=max_tokens,
                temperature=temperature,
                system=system,
                messages=[{"role": "user", "content": user}],
            )
        except Exception as exc:  # noqa: BLE001 — any SDK failure is transport-level
            raise LlmTransportError(f"anthropic transport failed: {exc}") from exc
        text = "".join(
            getattr(block, "text", "") for block in getattr(message, "content", [])
        )
        usage = message.usage
        return LlmResponse(
            text=text,
            input_tokens=usage.input_tokens,
            output_tokens=usage.output_tokens,
        )


# --- call policy: one transport retry, per-call provenance -------------------


def _timed_call(
    transport: Transport,
    system: str,
    user: str,
    site_label: str,
    model: str,
    temperature: float,
    max_tokens: int,
    log: ActionLog,
    now: Callable[[], float],
) -> LlmResponse:
    """Make one transport call, timing it and logging the `llm_call` on success."""
    start = now()
    response = transport(system, user, model, temperature, max_tokens)
    latency_ms = (now() - start) * 1000.0
    log.emit(
        "llm_call",
        site=site_label,
        model=model,
        temperature=temperature,
        max_tokens=max_tokens,
        system_sha256=sha256_text(system),
        input_tokens=response.input_tokens,
        output_tokens=response.output_tokens,
        latency_ms=latency_ms,
    )
    return response


def _call_with_transport_retry(
    transport: Transport,
    system: str,
    user: str,
    site_label: str,
    model: str,
    temperature: float,
    max_tokens: int,
    log: ActionLog,
    sleeper: Callable[[float], None],
    backoff_seconds: float,
    now: Callable[[], float],
) -> LlmResponse:
    """One transport call with a single bounded-backoff retry, then abort.

    A first transport failure logs `llm_retry`, sleeps `backoff_seconds`, and
    retries once; a second failure propagates (the run aborts loudly — a run
    minus one hat corrupts the independence evidence).
    """
    try:
        return _timed_call(
            transport, system, user, site_label, model, temperature, max_tokens, log, now
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
            transport, system, user, site_label, model, temperature, max_tokens, log, now
        )


def build_api_emitter(
    *,
    site_label: str,
    model: str,
    temperature: float,
    max_tokens: int,
    log: ActionLog,
    transport: Transport,
    now: Callable[[], float] = time.monotonic,
    sleeper: Callable[[float], None] = time.sleep,
    backoff_seconds: float = 30.0,
) -> LlmEmitter:
    """Build a per-call-site emitter binding a hat's label to the transport.

    Per-call-site construction is what lands token attribution per hat: every
    call this emitter makes logs an `llm_call` under `site_label`. The emitter's
    signature is the unchanged `LlmEmitter` port; content-level malformation is
    returned as-is for the parse seam, never retried here.
    """

    def emit(system: str, user: str) -> str:
        response = _call_with_transport_retry(
            transport,
            system,
            user,
            site_label,
            model,
            temperature,
            max_tokens,
            log,
            sleeper,
            backoff_seconds,
            now,
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


def _assemble_arbiter_user(
    finding: Finding, authorities: object, design_intent: object
) -> str:
    """Assemble the arbiter's user block (per arbiter-classifier.prompt.md)."""
    return (
        "FINDING:\n"
        f"{json.dumps(asdict(finding), indent=2)}\n\n"
        "RATIFIED AUTHORITIES (fetched fresh):\n"
        f"{_format_substrate(authorities)}\n\n"
        "STATED DESIGN INTENT (fetched fresh):\n"
        f"{_format_substrate(design_intent)}"
    )


def _parse_arbiter_output(raw_text: str, finding_id: str) -> ArbiterResult | None:
    """Parse arbiter output into an ArbiterResult, or None if malformed.

    Strict: classification must be in the schema vocabulary and confidence must
    be present and valid against the categorical vocabulary — both enforced by
    ArbiterResult construction. `finding_id` is stamped from the actual finding,
    not trusted from the model's echo. Any structural or vocabulary defect
    returns None (a content malformation), never a fabricated classification.
    """
    try:
        data = json.loads(raw_text)
        return ArbiterResult(
            finding_id=finding_id,
            classification=data["classification"],
            authority_locus=data.get("authority_locus"),
            rationale=data["rationale"],
            confidence=data["confidence"],
        )
    except (json.JSONDecodeError, KeyError, TypeError, ValueError):
        return None


class ApiArbiter:
    """Real arbiter over the API — the sole LLM on the exit path.

    Loads `arbiter-classifier.prompt.md`'s `## System` as data, assembles its
    user block from the finding plus the substrate handed to `run_loop`, and
    applies the §5 transport with the §6 call policy. Malformed output gets ONE
    content retry (logged) then aborts — the conservative decision-bearing bias
    lives in the prompt, never fabricated by fallback code.
    """

    def __init__(
        self,
        *,
        prompt_path: str | Path,
        transport: Transport,
        log: ActionLog,
        model: str,
        temperature: float,
        max_tokens: int,
        now: Callable[[], float] = time.monotonic,
        sleeper: Callable[[float], None] = time.sleep,
        backoff_seconds: float = 30.0,
    ) -> None:
        """Load the arbiter prompt and bind transport + call policy."""
        self._system = load_system_prompt(prompt_path)
        self._transport = transport
        self._log = log
        self._model = model
        self._temperature = temperature
        self._max_tokens = max_tokens
        self._now = now
        self._sleeper = sleeper
        self._backoff = backoff_seconds

    def classify(
        self, finding: Finding, authorities: object, design_intent: object
    ) -> ArbiterResult:
        """Classify one finding, with one content retry then a loud abort."""
        user = _assemble_arbiter_user(finding, authorities, design_intent)
        for attempt in (1, 2):
            response = _call_with_transport_retry(
                self._transport,
                self._system,
                user,
                "arbiter",
                self._model,
                self._temperature,
                self._max_tokens,
                self._log,
                self._sleeper,
                self._backoff,
                self._now,
            )
            parsed = _parse_arbiter_output(response.text, finding.id)
            if parsed is not None:
                return parsed
            if attempt == 1:
                self._log.emit(
                    "llm_retry",
                    site="arbiter",
                    retry_kind="content",
                    reason="malformed classification output",
                )
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
