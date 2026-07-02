# Module: agent_loop.identity
# Purpose: Deterministic finding identity. `id` is derived once at first
#          emission from hash(target + locus + normalized(claim)) and preserved
#          thereafter, so a recurring finding keeps the SAME id and oscillation
#          detection can see a reopen. Minting a fresh id per pass silently
#          disables recurrence detection — this module and its test exist to
#          prevent that root-cause trap (ledger-schema.md §Identity).
# Scope:   Pure functions, no I/O, no LLM.

from __future__ import annotations

import hashlib
import re

# Characters that carry no semantic weight in a claim: markdown emphasis,
# punctuation, and quoting. Stripped so cosmetic re-wording hashes stably.
_NOISE = re.compile(r"[*_`#>~\-\"'.,;:!?()\[\]{}]")
_WHITESPACE = re.compile(r"\s+")


def normalize_claim(claim: str) -> str:
    """Reduce a claim to a canonical form that ignores wording/formatting noise.

    Lowercases, strips markdown and punctuation, and collapses runs of
    whitespace. The goal is that two cosmetically-different phrasings of the
    *same* finding normalize to the same string, so their derived ids collide
    (which is the desired behaviour — it is how a reopen is recognised).

    Args:
        claim: The raw finding claim as emitted by a reviewer.

    Returns:
        The normalized claim string.
    """
    lowered = claim.lower()
    without_noise = _NOISE.sub(" ", lowered)
    return _WHITESPACE.sub(" ", without_noise).strip()


def derive_id(target: list[str], locus: str, claim: str) -> str:
    """Derive the stable finding id from its identity-bearing fields.

    Identity is hash(target + locus + normalized(claim)). The target list is
    sorted so emission order over a multi-document (cross-set) finding does not
    change identity.

    Args:
        target: The document id(s) the finding is raised against.
        locus: The section/decision within the target.
        claim: The finding statement (normalized internally).

    Returns:
        A hex digest string used as the finding id, stable across passes.
    """
    canonical_target = "|".join(sorted(target))
    payload = "\x1f".join((canonical_target, locus, normalize_claim(claim)))
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()[:16]
