# Module: agent_loop.identity
# Purpose: Deterministic finding identity. `id` is derived once at first
#          emission from hash(sorted(target) + normalize_locus(locus) + altitude)
#          and preserved thereafter, so a recurring finding keeps the SAME id and
#          oscillation detection can see a reopen. Minting a fresh id per pass
#          silently disables recurrence detection — this module and its test exist
#          to prevent that root-cause trap (ledger-schema.md §Identity).
# Scope:   Pure functions, no I/O, no LLM. Identity is a deterministic function —
#          no similarity/embedding/LLM step (execute-vs-reason bright line).
# Note (RBT-69): `altitude` entered the key and `claim` left it. Keying on the
#          claim sentence was too fine — a reworded re-emission minted a fresh id
#          and inflated open_cbm (run-028); keying on stance-at-locus is stable
#          under wording drift while keeping two distinct-stance findings at one
#          locus separate. `normalize_claim` is retained for the divergence guard
#          (admission.py), no longer identity-bearing.

from __future__ import annotations

import hashlib
import re

# Characters that carry no semantic weight in a claim/locus: markdown emphasis,
# punctuation, and quoting. Stripped so cosmetic re-wording hashes stably.
_NOISE = re.compile(r"[*_`#>~\-\"'.,;:!?()\[\]{}]")
_WHITESPACE = re.compile(r"\s+")


def normalize_claim(claim: str) -> str:
    """Reduce a claim to a canonical form that ignores wording/formatting noise.

    Lowercases, strips markdown and punctuation, and collapses runs of
    whitespace. Retained (RBT-69) as the discriminator for the claim-divergence
    guard: two cosmetically-different phrasings normalize to the same string, so
    the guard only fires on a *materially* different claim. No longer
    identity-bearing.

    Args:
        claim: The raw finding claim as emitted by a reviewer.

    Returns:
        The normalized claim string.
    """
    lowered = claim.lower()
    without_noise = _NOISE.sub(" ", lowered)
    return _WHITESPACE.sub(" ", without_noise).strip()


def normalize_locus(locus: str) -> str:
    """Reduce a locus to a canonical form that absorbs formatting drift only.

    Lowercases, strips the same markdown/punctuation/quoting noise as
    `normalize_claim`, and collapses whitespace, so a locus reworded cosmetically
    across passes ("§2.3", "**§2.3**", "  section 2.3  ") hashes to one id. Kept
    deliberately conservative — it does NOT semantically alter the locus (a
    genuinely different section anchor stays distinct), because over-normalizing a
    locus risks merging distinct loci, the coverage regression the identity rule
    forbids (ledger-schema.md §Identity).

    Args:
        locus: The raw section/decision anchor as emitted by a reviewer.

    Returns:
        The normalized locus string.
    """
    lowered = locus.lower()
    without_noise = _NOISE.sub(" ", lowered)
    return _WHITESPACE.sub(" ", without_noise).strip()


def derive_id(target: list[str], locus: str, altitude: str) -> str:
    """Derive the stable finding id from its identity-bearing fields.

    Identity is hash(sorted(target) + normalize_locus(locus) + altitude) — the
    stance-at-locus, not the claim sentence (RBT-69). The target list is sorted so
    emission order over a multi-document (cross-set) finding does not change
    identity; the locus is normalized so cosmetic locus drift does not mint a
    fresh id; `altitude` enters raw (a fixed enum value, no normalization needed).

    Args:
        target: The document id(s) the finding is raised against.
        locus: The section/decision within the target (normalized internally).
        altitude: The invoking reviewer's altitude (LAA/SA/EA/cross-set), stamped
            at the parse seam before admission.

    Returns:
        A hex digest string used as the finding id, stable across passes.
    """
    canonical_target = "|".join(sorted(target))
    payload = "\x1f".join((canonical_target, normalize_locus(locus), altitude))
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()[:16]
