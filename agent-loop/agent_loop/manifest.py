# Module: agent_loop.manifest
# Purpose: The run manifest (run-prep.contract.md §7): written at prep and
#          finalized at run end. Prep records provenance (run-id, HEAD SHA,
#          document set + resolved paths, all five prompt-file hashes, substrate
#          reference, model + params); finalize records outcome (router exit,
#          passes, per-call-site token totals, wall-clock). Per-hat cost is a
#          first-class output — the roster question is independence per cost.
# Scope:   Pure manifest read/write + token aggregation over the action log. No
#          LLM, no git (the HEAD SHA is passed in).

from __future__ import annotations

import json
from pathlib import Path

from agent_loop.log import ActionLog


def per_site_token_totals(log: ActionLog) -> dict[str, dict[str, int]]:
    """Aggregate `llm_call` events into per-site token totals.

    The cache-creation / cache-read sums (RBT-49 Item 1 §4) make the run-level
    caching effect summable per site; `input_tokens` is the uncached input. The
    cache fields default to 0 for events emitted without them (older events, or
    a transport that reported no cache usage), so this stays additive.

    Returns:
        Map of call-site label → {input_tokens, output_tokens,
        cache_creation_input_tokens, cache_read_input_tokens, calls}.
    """
    totals: dict[str, dict[str, int]] = {}
    for event in log.of_kind("llm_call"):
        site = str(event.detail["site"])
        bucket = totals.setdefault(
            site,
            {
                "input_tokens": 0,
                "output_tokens": 0,
                "cache_creation_input_tokens": 0,
                "cache_read_input_tokens": 0,
                "calls": 0,
            },
        )
        bucket["input_tokens"] += int(event.detail["input_tokens"])  # type: ignore[arg-type]
        bucket["output_tokens"] += int(event.detail["output_tokens"])  # type: ignore[arg-type]
        bucket["cache_creation_input_tokens"] += int(
            event.detail.get("cache_creation_input_tokens", 0)  # type: ignore[arg-type]
        )
        bucket["cache_read_input_tokens"] += int(
            event.detail.get("cache_read_input_tokens", 0)  # type: ignore[arg-type]
        )
        bucket["calls"] += 1
    return totals


def write_prep_manifest(
    manifest_path: str | Path,
    *,
    run_id: str,
    created: str,
    document_set: dict[str, dict[str, str]],
    head_sha: str,
    prompt_hashes: dict[str, str],
    substrate_manifest_ref: str,
    model: str,
    parameters: dict[str, object],
    calibration: dict[str, object] | None = None,
) -> None:
    """Write the prep half of the run manifest.

    Args:
        manifest_path: Where to write `manifest.json`.
        run_id: The run id.
        created: ISO-8601 creation timestamp.
        document_set: Map of doc-id → the frozen snapshot provenance
            ({run-folder-relative `snapshot_path`, content `sha256`}), recording
            what was actually reviewed (amended 2026-07-06 / RBT-51 Item 3 / T6).
        head_sha: `git rev-parse HEAD` of the SOFIA repo.
        prompt_hashes: Map of prompt-file name → SHA-256 (all five prompts).
        substrate_manifest_ref: Path/reference to the substrate manifest.
        model: The fixed run model.
        parameters: The request-payload parameters recorded (max_tokens).
        calibration: The prompt-set calibration generation for this run and its
            rationale (e.g. `{"generation": 3, "rationale": ...}`), recorded
            alongside the re-pinned `prompt_sha256` when a ratified calibration
            event changed a pinned prompt (RBT-49/Ra-2). None omits the key.
    """
    manifest = {
        "run_id": run_id,
        "created": created,
        "document_set": document_set,
        "head_sha": head_sha,
        "prompt_sha256": prompt_hashes,
        "substrate_manifest": substrate_manifest_ref,
        "model": model,
        "parameters": parameters,
        "finalized": False,
    }
    if calibration is not None:
        manifest["calibration"] = calibration
    Path(manifest_path).write_text(
        json.dumps(manifest, indent=2, sort_keys=False), encoding="utf-8"
    )


def finalize_manifest(
    manifest_path: str | Path,
    *,
    router_exit: str,
    passes_run: int,
    per_site_tokens: dict[str, dict[str, int]],
    wall_clock_seconds: float,
) -> None:
    """Add the run-end half to an existing prep manifest.

    Args:
        manifest_path: The prep `manifest.json` to finalize (must exist).
        router_exit: The router exit kind (and reason, if any).
        passes_run: How many passes executed.
        per_site_tokens: Per-call-site token totals (see per_site_token_totals).
        wall_clock_seconds: Total run wall-clock.
    """
    path = Path(manifest_path)
    manifest = json.loads(path.read_text(encoding="utf-8"))
    manifest["router_exit"] = router_exit
    manifest["passes_run"] = passes_run
    manifest["per_site_tokens"] = per_site_tokens
    manifest["wall_clock_seconds"] = wall_clock_seconds
    manifest["finalized"] = True
    path.write_text(json.dumps(manifest, indent=2, sort_keys=False), encoding="utf-8")
