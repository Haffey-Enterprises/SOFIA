# Module: agent_loop.prep
# Purpose: Run-prep tool — the snapshot PRODUCER (RBT-52) that assembles a run
#          folder the runner (RBT-51 Item 3) later consumes. It scripts the five
#          acts of record for a supervised run:
#            (a) resolve logical ids -> canonical working-tree paths
#                (docs/**/<doc-id>-*.md; resolution lives HERE now, per amended
#                 run-prep.contract.md §2 / T3 — the runner no longer touches the
#                 working tree);
#            (b) COPY the resolved files into the run folder — never move; a
#                canonical path is a source, not staging;
#            (c) compute content hashes (validator-method — text via
#                read_text().encode()) and, under --from-run, ASSERT them against
#                the prior draw's pins;
#            (d) emit the substrate manifest (the existing §3 schema);
#            (e) emit N draws whose provenance records differ only in run_id.
#          Plus the document snapshot-at-prep: the reviewed document set is
#          copied into runs/<run-id>/documents/, every file hashed, and recorded
#          in a validated provenance sub-schema (documents/manifest.json)
#          alongside the SOFIA HEAD SHA — this is exactly what §8 gate 8 verifies.
# Scope:   Filesystem copy + hashing + manifest emission. NO LLM, NO network,
#          NO git (the HEAD SHA and retrieval timestamp are passed in, so the
#          engine is deterministic and every test drives it against a tmp tree).
#          The thin CLI entry that stamps HEAD/timestamp lives at
#          scripts/prep_run.py.
#
# RBT-54 (F4) adds a third substrate source beside repo-canonical and
# --from-run carry-forward: bedrock authorities are sourced from the INSTALLED
# plugin cache (an injected cache root — the CLI discovers it; tests inject a
# tmp cache, so determinism holds) and verified PIN-vs-INSTALLED against a
# ratified expected_sha256. A drifted cache fails loud unless a sanctioned
# --accept-stale-authority override is supplied; verified_against (and any
# currency_override) are recorded entry-level on the substrate manifest.
#
# Three lessons carried from the run-009..011 substrate work, enforced here as
# assertions with fail-loud coverage (RBT-52):
#   #1 substrate files land as <category>/<logical_id>.md — resolution by stem,
#      never hand-named;
#   #2 ALL hashes are validator-method (sha256_text over read_text()) — never
#      raw bytes, never hand-transcribed;
#   #3 post-assembly, every canonical source still exists at its canonical path
#      (copy-not-move, proven after the fact).

from __future__ import annotations

import json
from collections.abc import Callable
from dataclasses import dataclass, field
from pathlib import Path

from agent_loop.fetchers import (
    sha256_text,
    validate_substrate_manifest,
    verify_document_snapshot,
)


class PrepError(RuntimeError):
    """Prep failed loudly: a doc-id did not resolve, a source was missing, a
    carry-forward pin mismatched, or a lesson assertion tripped. Prep never
    proceeds past a violation — a silently-wrong run folder is the failure this
    tool exists to prevent."""


# --- substrate recipes: a registry keyed by reviewed doctype (RBT-57) ---------
#
# The recipe is selected by the doctype of the document under review, inferred
# from its doc-id (SDD-001 -> sdd, DDR-004 -> ddr). Inference from the target —
# not an operator-supplied flag — is deliberate: the failure this tool exists to
# prevent is a recipe/target mismatch (the SDD recipe run against a DDR emits
# SDD-specific substrate and omits the DDR's authority). A flag reintroduces that
# mismatch as human error; a doctype read off the target structurally forbids it.
# The registry (RECIPES) is keyed by doctype so `adr` slots in later by adding
# one entry — no rewrite. The SDD recipe below is unchanged from RBT-52 and is
# regression-pinned byte-for-byte; the DDR recipe duplicates the shared canon
# rather than share a helper, to keep the SDD recipe's source demonstrably
# untouched.


@dataclass(frozen=True)
class SubstrateSpec:
    """One substrate file to assemble.

    Exactly one source applies:
      - `repo_relpath` set: copy from `<sofia_root>/<repo_relpath>` (a
        repo-canonical source, tracked for lesson #3);
      - `carry_forward` True: copy from the prior draw's substrate under
        `--from-run` (for sources the runner cannot re-fetch that are NOT
        forward-verifiable — the Notion vision — carried forward with a pin
        assertion), reusing the prior manifest's origin block;
      - `bedrock_cache` True: source from the INSTALLED bedrock plugin cache
        (RBT-54 F4). The bytes come from the injected cache root at the
        cache-relative path derived from `origin.path`, and are verified
        PIN-vs-INSTALLED against `expected_sha256` — the ratified content pin.
        Bedrock authorities never ride `--from-run`, so staleness-by-carry is
        unexpressible by construction; a drifted cache fails loud at prep unless
        a sanctioned `--accept-stale-authority` override is supplied.
    """

    logical_id: str
    category: str  # "authorities" | "design-intent"
    origin: dict = field(default_factory=dict)
    repo_relpath: str | None = None
    carry_forward: bool = False
    bedrock_cache: bool = False
    expected_sha256: str | None = None  # ratified pin; required when bedrock_cache


def sdd_substrate_specs(*, from_run: str | None) -> list[SubstrateSpec]:
    """The SDD review recipe: the run-one substrate set (matches run-011).

    Authorities: the ratified corpus (ADR-001/002, DDR-001/002) plus the
    sdd-template and the author-decision-record SKILL. Design-intent: the SDD-001
    deliberation record, the SOFIA vision block, and the SDD-001 charter notes.

    Repo-canonical items resolve from the working tree; bedrock and Notion items
    are carried forward from a prior draw (they cannot be re-fetched at prep),
    so the recipe requires `--from-run` whenever it emits a carry-forward spec.
    """
    specs = [
        SubstrateSpec(
            "ADR-001", "authorities",
            {"source": "sofia-repo", "path": "docs/adr/ADR-001-reasoning-architecture.md"},
            repo_relpath="docs/adr/ADR-001-reasoning-architecture.md",
        ),
        SubstrateSpec(
            "ADR-002", "authorities",
            {"source": "sofia-repo", "path": "docs/adr/ADR-002-graph-system-of-record.md"},
            repo_relpath="docs/adr/ADR-002-graph-system-of-record.md",
        ),
        SubstrateSpec(
            "DDR-001", "authorities",
            {"source": "sofia-repo", "path": "docs/ddr/DDR-001-data-architecture.md"},
            repo_relpath="docs/ddr/DDR-001-data-architecture.md",
        ),
        SubstrateSpec(
            "DDR-002", "authorities",
            {"source": "sofia-repo", "path": "docs/ddr/DDR-002-graph-schema.md"},
            repo_relpath="docs/ddr/DDR-002-graph-schema.md",
        ),
        SubstrateSpec("sdd-template", "authorities", carry_forward=True),
        SubstrateSpec("author-decision-record-SKILL", "authorities", carry_forward=True),
        SubstrateSpec(
            "deliberation-record-sdd-001", "design-intent",
            {"source": "sofia-repo",
             "path": "agent-loop/deliberation/sdd-001-knowledge-service/record.md"},
            repo_relpath="agent-loop/deliberation/sdd-001-knowledge-service/record.md",
        ),
        SubstrateSpec("sofia-vision", "design-intent", carry_forward=True),
        SubstrateSpec("sdd-001-charter-notes", "design-intent", carry_forward=True),
    ]
    if from_run is None and any(spec.carry_forward for spec in specs):
        raise PrepError(
            "the SDD recipe carries bedrock/Notion substrate forward and requires "
            "--from-run; no prior draw was given"
        )
    return specs


def ddr_substrate_specs(
    target: str, record_relpath: str, *, from_run: str | None
) -> list[SubstrateSpec]:
    """The DDR review recipe (RBT-57 substrate ruling, ratified 2026-07-10).

    What a DDR review reads against:
      - Shared canon (same as the SDD recipe): ADR-001/002, DDR-001/002.
      - Consuming context: SDD-001 — a DDR's Reconciliation/Cross-References make
        verifiable claims about the SDDs that implement it, so reviewers need it.
        Hardcoded while a single SDD exists; when a second SDD lands, "which SDDs
        implement this DDR" becomes a resolver (flagged in RBT-57 — n=1 today).
      - Doctype authoring authority: the ddr-template and the
        author-decision-record SKILL — sourced from the installed bedrock plugin
        cache and verified pin-vs-installed (RBT-54 F4). Unlike the SDD recipe's
        carried sdd-template, these do not ride --from-run; the ratified pin is
        their authority and a drifted cache fails loud at prep.
      - Design-intent lineage: the target DDR's deliberation record, resolved by
        convention (`agent-loop/deliberation/<ddr-slug>/record.md`) and passed in
        as `record_relpath`; its logical_id is derived from `target`, never
        hardcoded to a specific DDR.
      - General context: sofia-vision (doctype-agnostic, carried forward as the
        SDD recipe carries it).

    Explicitly EXCLUDED (SDD-specific): sdd-template, sdd-001-charter-notes,
    deliberation-record-sdd-001 — none appear below, so a DDR prep cannot leak
    them.

    Args:
        target: The reviewed DDR's doc-id (e.g. "DDR-004"); names the
            deliberation-record logical_id.
        record_relpath: Repo-relative path to the DDR's deliberation record,
            pre-resolved by convention (see `resolve_deliberation_record`).
        from_run: Prior draw to carry bedrock/Notion substrate forward from;
            required whenever the recipe emits a carry-forward spec.

    Returns:
        The DDR substrate spec list.

    Raises:
        PrepError: If carry-forward substrate is emitted without a `from_run`.
    """
    specs = [
        # Shared canon — duplicated (not shared) to keep sdd_substrate_specs
        # pristine and byte-for-byte regression-clean (RBT-57).
        SubstrateSpec(
            "ADR-001", "authorities",
            {"source": "sofia-repo", "path": "docs/adr/ADR-001-reasoning-architecture.md"},
            repo_relpath="docs/adr/ADR-001-reasoning-architecture.md",
        ),
        SubstrateSpec(
            "ADR-002", "authorities",
            {"source": "sofia-repo", "path": "docs/adr/ADR-002-graph-system-of-record.md"},
            repo_relpath="docs/adr/ADR-002-graph-system-of-record.md",
        ),
        SubstrateSpec(
            "DDR-001", "authorities",
            {"source": "sofia-repo", "path": "docs/ddr/DDR-001-data-architecture.md"},
            repo_relpath="docs/ddr/DDR-001-data-architecture.md",
        ),
        SubstrateSpec(
            "DDR-002", "authorities",
            {"source": "sofia-repo", "path": "docs/ddr/DDR-002-graph-schema.md"},
            repo_relpath="docs/ddr/DDR-002-graph-schema.md",
        ),
        # Consuming context (n=1 SDD hardcode; see docstring).
        SubstrateSpec(
            "SDD-001", "authorities",
            {"source": "sofia-repo", "path": "docs/sdd/SDD-001-knowledge-service.md"},
            repo_relpath="docs/sdd/SDD-001-knowledge-service.md",
        ),
        # Doctype authoring authority — sourced from the installed bedrock
        # plugin cache and verified pin-vs-installed (RBT-54 F4 / G1). The pins
        # are the ratified 1.3.0 content hashes; they move only by explicit
        # operator ratification (a bump here IS the ratification act).
        SubstrateSpec(
            "ddr-template", "authorities",
            {"source": "bedrock",
             "path": "plugins/bedrock/skills/author-decision-record/templates/ddr-template.md"},
            bedrock_cache=True,
            expected_sha256="59068b3a2741f497e92bff240da238d4f8b6b57471c8ff7a76ab8c09ba9668f9",
        ),
        SubstrateSpec(
            "author-decision-record-SKILL", "authorities",
            {"source": "bedrock",
             "path": "plugins/bedrock/skills/author-decision-record/SKILL.md"},
            bedrock_cache=True,
            expected_sha256="d3fb4499b8d3ff899ae3f822e8873300c1f5330cc9ee55f193fc4f9eaf9da966",
        ),
        # Design-intent lineage: the target DDR's deliberation record, by convention.
        SubstrateSpec(
            f"deliberation-record-{target.lower()}", "design-intent",
            {"source": "sofia-repo", "path": record_relpath},
            repo_relpath=record_relpath,
        ),
        # General context (doctype-agnostic; carried forward as the SDD recipe does).
        SubstrateSpec("sofia-vision", "design-intent", carry_forward=True),
    ]
    if from_run is None and any(spec.carry_forward for spec in specs):
        raise PrepError(
            "the DDR recipe carries bedrock/Notion substrate forward and requires "
            "--from-run; no prior draw was given"
        )
    return specs


def resolve_deliberation_record(sofia_root: str | Path, target: str) -> Path:
    """Resolve a DDR's deliberation record by convention, or raise on 0/>1.

    Prefix glob `<sofia_root>/agent-loop/deliberation/<target-lower>-*/record.md`
    (e.g. DDR-004 -> `agent-loop/deliberation/ddr-004-*/record.md`). This is the
    design-intent lineage the DDR recipe reads against; it resolves at PREP time,
    so a target whose record is absent fails loud here — before any run folder is
    created — rather than emitting a silently-incomplete run. Zero or multiple
    matches raise with the target and the match list; no fallback, no fuzzy match.

    Args:
        sofia_root: The $SOFIA_ROOT working tree.
        target: The reviewed DDR's doc-id (e.g. "DDR-004").

    Returns:
        The single `record.md` path.

    Raises:
        PrepError: If the record resolves to zero or more than one file.
    """
    delib_root = Path(sofia_root) / "agent-loop" / "deliberation"
    matches = sorted(delib_root.glob(f"{target.lower()}-*/record.md"))
    if len(matches) != 1:
        raise PrepError(
            f"deliberation record for {target!r} resolved to {len(matches)} files "
            f"under {delib_root} (expected exactly 1): {[str(m) for m in matches]}"
        )
    return matches[0]


# --- recipe selection: doctype off the review target -> registry --------------


def infer_doctype(doc_ids: list[str]) -> str:
    """Infer the reviewed doctype from the document set's doc-id prefixes.

    "SDD-001" -> "sdd", "DDR-004" -> "ddr". A review targets one doctype; a set
    spanning doctypes (or an empty set) has no single recipe and raises.

    Args:
        doc_ids: The reviewed document ids.

    Returns:
        The lowercase doctype prefix.

    Raises:
        PrepError: On an empty set or one spanning multiple doctypes.
    """
    if not doc_ids:
        raise PrepError("no doc-ids given; cannot infer a review doctype")
    doctypes = {doc_id.split("-", 1)[0].lower() for doc_id in doc_ids}
    if len(doctypes) != 1:
        raise PrepError(
            f"doc-ids span multiple doctypes {sorted(doctypes)}; a review targets "
            f"one doctype: {doc_ids}"
        )
    return doctypes.pop()


def _sdd_recipe_for(
    doc_ids: list[str], sofia_root: str | Path
) -> Callable[..., list[SubstrateSpec]]:
    """Registry builder for the SDD recipe — target context is not needed."""
    return sdd_substrate_specs


def _ddr_recipe_for(
    doc_ids: list[str], sofia_root: str | Path
) -> Callable[..., list[SubstrateSpec]]:
    """Registry builder for the DDR recipe.

    A DDR review targets exactly one DDR; its deliberation record is resolved by
    convention here (fail-loud on absence) and bound into a `(*, from_run)`
    recipe, so selection matches the calling convention every recipe shares.
    """
    if len(doc_ids) != 1:
        raise PrepError(f"a DDR review targets exactly one DDR; got {doc_ids}")
    target = doc_ids[0]
    record = resolve_deliberation_record(sofia_root, target)
    record_relpath = str(record.relative_to(Path(sofia_root)))

    def recipe(*, from_run: str | None) -> list[SubstrateSpec]:
        return ddr_substrate_specs(target, record_relpath, from_run=from_run)

    return recipe


# Keyed by reviewed doctype. Add `adr` here to extend — no other change needed.
RECIPES = {
    "sdd": _sdd_recipe_for,
    "ddr": _ddr_recipe_for,
}


def select_recipe(
    doc_ids: list[str], *, sofia_root: str | Path
) -> Callable[..., list[SubstrateSpec]]:
    """Select the substrate recipe for the reviewed doctype.

    Infers the doctype from the review target (`infer_doctype`) and returns the
    registry recipe as a `(*, from_run) -> list[SubstrateSpec]` callable — the
    same shape an explicitly-injected recipe has. An unknown doctype fails loud.

    Args:
        doc_ids: The reviewed document ids.
        sofia_root: The $SOFIA_ROOT working tree (needed to resolve doctype
            context such as a DDR's deliberation record).

    Returns:
        A `(*, from_run)` recipe callable.

    Raises:
        PrepError: On an unresolvable doctype or an unknown doctype.
    """
    doctype = infer_doctype(doc_ids)
    try:
        builder = RECIPES[doctype]
    except KeyError:
        raise PrepError(
            f"no substrate recipe for doctype {doctype!r} (doc-ids {doc_ids}); "
            f"known doctypes: {sorted(RECIPES)}"
        ) from None
    return builder(doc_ids, sofia_root)


# --- act (a): resolution — homed here now (amended contract §2 / T3) ----------


def resolve_document(docs_root: str | Path, doc_id: str) -> Path:
    """Resolve a doc-id to its single working-tree file, or raise on 0/>1.

    Prefix glob `<docs_root>/**/<doc-id>-*.md`. This is the working-tree
    resolution the runner used to do; the amendment moves it to prep, where the
    snapshot is taken. Zero or multiple matches raise with the doc-id and the
    match list — no fallback, no fuzzy matching.
    """
    matches = sorted(Path(docs_root).glob(f"**/{doc_id}-*.md"))
    if len(matches) != 1:
        raise PrepError(
            f"doc-id {doc_id!r} resolved to {len(matches)} files under {docs_root} "
            f"(expected exactly 1): {[str(m) for m in matches]}"
        )
    return matches[0]


# --- lesson #3: canonical sources survive their copy --------------------------


def _assert_sources_survive(sources: list[Path]) -> None:
    """Lesson #3: every repo-canonical source still exists at its canonical path.

    Copy-not-move means this must always hold; the assertion makes a regression
    (an accidental move, a source consumed as staging) fail loud at prep rather
    than silently corrupt the working tree.
    """
    vanished = [str(path) for path in sources if not path.is_file()]
    if vanished:
        raise PrepError(f"canonical source(s) did not survive assembly: {vanished}")


# --- document snapshot (acts a, b, c) + provenance sub-schema -----------------


def snapshot_documents(
    doc_ids: list[str],
    *,
    docs_root: str | Path,
    sofia_root: str | Path,
    run_dir: Path,
    run_id: str,
    sofia_head_sha: str,
    retrieved: str,
) -> None:
    """Snapshot the reviewed document set into `run_dir/documents/` (acts a-c).

    Resolves each doc-id (act a), copies it verbatim — never moves (act b) —
    hashes it validator-method (act c, lesson #2), and records the provenance
    sub-schema in `documents/manifest.json` alongside the SOFIA HEAD SHA. The
    snapshot is always taken fresh from the working tree with self-contained
    provenance — `--from-run` is substrate-only and never constrains it;
    cross-version comparison is the audit's act (manifests side by side).
    """
    documents_out = run_dir / "documents"
    documents_out.mkdir(parents=True, exist_ok=True)
    sofia_root = Path(sofia_root)

    files: list[dict] = []
    for doc_id in doc_ids:
        source = resolve_document(docs_root, doc_id)  # act (a)
        content = source.read_text(encoding="utf-8")
        digest = sha256_text(content)  # act (c), lesson #2
        dest = documents_out / source.name
        dest.write_text(content, encoding="utf-8")  # act (b): copy, never move

        files.append(
            {
                "doc_id": doc_id,
                "snapshot_path": f"documents/{source.name}",
                "origin": {
                    "source": "sofia-repo",
                    "canonical_path": str(source.relative_to(sofia_root)),
                },
                "retrieved": retrieved,
                "sha256": digest,
            }
        )

    manifest = {
        "run_id": run_id,
        "sofia_head_sha": sofia_head_sha,
        "files": files,
    }
    (documents_out / "manifest.json").write_text(
        json.dumps(manifest, indent=2), encoding="utf-8"
    )


# --- substrate assembly (acts a-d) --------------------------------------------


# --- RBT-54 F4: bedrock forward currency check (pin-vs-installed) ------------

_BEDROCK_ORIGIN_PREFIX = "plugins/bedrock/"


def _bedrock_cache_relpath(origin_path: str) -> str:
    """Map a bedrock `origin.path` to its path within the installed plugin cache.

    origin.path is recorded plugin-rooted (`plugins/bedrock/skills/...`); the
    installed cache lays the plugin out under its version dir WITHOUT that prefix
    (`<cache_root>/skills/...`). Stripping the known prefix is the whole mapping;
    an origin.path that does not carry it is a malformed bedrock spec and fails
    loud rather than resolving to a wrong (or absent) cache file.
    """
    if not origin_path.startswith(_BEDROCK_ORIGIN_PREFIX):
        raise PrepError(
            f"bedrock origin path {origin_path!r} does not start with "
            f"{_BEDROCK_ORIGIN_PREFIX!r}; cannot resolve it in the plugin cache"
        )
    return origin_path[len(_BEDROCK_ORIGIN_PREFIX):]


def _verify_bedrock_currency(
    spec: SubstrateSpec,
    *,
    bedrock_cache_root: str | Path | None,
    accept_stale: dict[str, str] | None,
    verified_at: str,
) -> tuple[str, str, dict, dict | None]:
    """Source a bedrock authority from the installed cache and verify its pin.

    Returns `(content, installed_sha256, verified_against, currency_override)`.
    The check is PIN-vs-INSTALLED: the spec's `expected_sha256` (ratified) is
    compared against the hash of the installed-cache file. On a match,
    `currency_override` is None. On a mismatch, prep FAILS LOUD — naming the
    logical_id, the expected pin, and the installed hash — unless `accept_stale`
    carries a non-blank reason for this logical_id, which is a sanctioned
    override: the run records a `currency_override` block and proceeds on the
    installed bytes. A blank/whitespace reason is rejected (reason is mandatory).

    Raises:
        PrepError: on a missing cache root, a spec without a pin, an absent
            cache file, an unsanctioned mismatch, or a reason-less override.
    """
    if bedrock_cache_root is None:
        raise PrepError(
            f"substrate {spec.logical_id!r} is bedrock-cache but no bedrock cache "
            "root was given (F4 currency check cannot run)"
        )
    if spec.expected_sha256 is None:
        raise PrepError(
            f"bedrock-cache substrate {spec.logical_id!r} carries no expected_sha256 "
            "pin; the pin is its authority (F4)"
        )
    relpath = _bedrock_cache_relpath(spec.origin["path"])
    source = Path(bedrock_cache_root) / relpath
    if not source.is_file():
        raise PrepError(
            f"bedrock cache source missing for {spec.logical_id!r}: {source}"
        )
    content = source.read_text(encoding="utf-8")
    installed = sha256_text(content)
    verified_against = {
        "path": spec.origin["path"],
        "sha256": installed,
        "source": "installed-cache",
        "verified_at": verified_at,
    }
    if installed == spec.expected_sha256:
        return content, installed, verified_against, None

    reason = (accept_stale or {}).get(spec.logical_id)
    if reason is None:
        raise PrepError(
            f"bedrock currency mismatch for {spec.logical_id!r} "
            f"({spec.origin['path']}): expected pin {spec.expected_sha256}, "
            f"installed {installed}. Re-pin (operator ratification) or override "
            f"with --accept-stale-authority {spec.logical_id} --reason '...'."
        )
    if not reason.strip():
        raise PrepError(
            f"--accept-stale-authority {spec.logical_id!r} requires a non-blank "
            "--reason; a reason-less override is rejected"
        )
    currency_override = {
        "status": "accepted-stale",
        "expected_sha256": spec.expected_sha256,
        "installed_sha256": installed,
        "reason": reason,
        "timestamp": verified_at,
    }
    return content, installed, verified_against, currency_override


def _prior_substrate_entries(from_run_dir: Path) -> dict[str, dict]:
    """Map logical_id -> prior manifest entry from a prior draw's substrate."""
    manifest_path = from_run_dir / "substrate" / "manifest.json"
    if not manifest_path.is_file():
        raise PrepError(f"--from-run draw has no substrate manifest: {manifest_path}")
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    return {entry["logical_id"]: entry for entry in manifest["files"]}


def assemble_substrate(
    specs: list[SubstrateSpec],
    *,
    run_dir: Path,
    sofia_root: str | Path,
    retrieved: str,
    from_run_dir: Path | None = None,
    bedrock_cache_root: str | Path | None = None,
    accept_stale: dict[str, str] | None = None,
    verified_at: str | None = None,
) -> None:
    """Assemble the frozen substrate into `run_dir/substrate/` (acts a-d).

    Each spec's file lands at `<category>/<logical_id>.md` (lesson #1), sourced
    from its repo-canonical path, carried forward from `--from-run`, or (RBT-54
    F4) from the installed bedrock plugin cache; hashed validator-method (lesson
    #2); and, where a prior pin exists (`--from-run`), asserted against it (act
    c). Bedrock-cache specs are verified pin-vs-installed against the injected
    `bedrock_cache_root` and record entry-level `verified_against` (and, on a
    sanctioned `accept_stale` override, `currency_override`) beside `origin`.
    Emits the substrate manifest in the existing §3 schema (act d) and
    self-validates it. Finally asserts every repo-canonical source survived
    (lesson #3).

    Args:
        bedrock_cache_root: Installed bedrock plugin cache root; required when
            any spec is `bedrock_cache` (fail-loud otherwise).
        accept_stale: Map logical_id -> reason sanctioning a bedrock pin
            mismatch; a reason-less entry is rejected.
        verified_at: Timestamp recorded in `verified_against` / override;
            defaults to `retrieved` when omitted.
    """
    substrate_out = run_dir / "substrate"
    sofia_root = Path(sofia_root)
    prior_entries = _prior_substrate_entries(from_run_dir) if from_run_dir is not None else {}
    verified_at = verified_at if verified_at is not None else retrieved

    entries: list[dict] = []
    canonical_sources: list[Path] = []
    for spec in specs:
        category_dir = substrate_out / spec.category
        category_dir.mkdir(parents=True, exist_ok=True)
        dest = category_dir / f"{spec.logical_id}.md"  # lesson #1

        if spec.bedrock_cache:
            # RBT-54 F4: source from the installed cache, verify pin-vs-installed.
            content, digest, verified_against, currency_override = _verify_bedrock_currency(
                spec,
                bedrock_cache_root=bedrock_cache_root,
                accept_stale=accept_stale,
                verified_at=verified_at,
            )
            dest.write_text(content, encoding="utf-8")  # copy, never move
            entry = {
                "logical_id": spec.logical_id,
                "category": spec.category,
                "origin": dict(spec.origin),  # source + path; prose note retires
                "retrieved": retrieved,
                "sha256": digest,
                "verified_against": verified_against,
            }
            if currency_override is not None:
                entry["currency_override"] = currency_override
            entries.append(entry)
            continue

        if spec.carry_forward:
            if from_run_dir is None:
                raise PrepError(
                    f"substrate {spec.logical_id!r} is carry-forward but no "
                    "--from-run draw was given"
                )
            source = from_run_dir / "substrate" / spec.category / f"{spec.logical_id}.md"
            if not source.is_file():
                raise PrepError(
                    f"carry-forward source missing for {spec.logical_id!r}: {source}"
                )
            origin = prior_entries[spec.logical_id]["origin"]
        else:
            source = sofia_root / spec.repo_relpath
            if not source.is_file():
                raise PrepError(
                    f"repo-canonical source missing for {spec.logical_id!r}: {source}"
                )
            canonical_sources.append(source)
            origin = spec.origin

        content = source.read_text(encoding="utf-8")
        dest.write_text(content, encoding="utf-8")  # copy, never move
        digest = sha256_text(content)  # lesson #2

        prior = prior_entries.get(spec.logical_id)
        if prior is not None and prior["sha256"] != digest:
            raise PrepError(
                f"substrate {spec.logical_id!r} sha256 differs from prior pin: "
                f"prior {prior['sha256']}, now {digest}"
            )

        entries.append(
            {
                "logical_id": spec.logical_id,
                "category": spec.category,
                "origin": origin,
                "retrieved": retrieved,
                "sha256": digest,
            }
        )

    (substrate_out / "manifest.json").write_text(
        json.dumps({"files": entries}, indent=2), encoding="utf-8"
    )
    validate_substrate_manifest(substrate_out)  # act (d): self-validate
    _assert_sources_survive(canonical_sources)  # lesson #3


# --- orchestration: one draw, then N draws (act e) ----------------------------


def prep_run(
    run_id: str,
    doc_ids: list[str],
    *,
    sofia_root: str | Path,
    runs_root: str | Path,
    sofia_head_sha: str,
    retrieved: str,
    from_run: str | None = None,
    recipe: Callable[..., list[SubstrateSpec]] | None = None,
    bedrock_cache_root: str | Path | None = None,
    accept_stale: dict[str, str] | None = None,
    verified_at: str | None = None,
    extra_specs: list[SubstrateSpec] | None = None,
) -> Path:
    """Prepare one run folder (documents snapshot + substrate) and return it.

    Refuses to overwrite an existing folder — a prepared run-id is claimed, and a
    used one is immutable evidence (mirrors §8 gate 1). Assembles substrate and
    the document snapshot, then verifies the snapshot the way §8 gate 8 will, so
    a folder this tool returns is one the runner can consume.

    When `recipe` is None (the production path) the substrate recipe is selected
    by the reviewed doctype (`select_recipe`); an explicit `recipe` overrides
    selection (tests inject minimal recipes). Recipe selection runs BEFORE any
    folder is created, so a fail-loud selection failure — e.g. a DDR whose
    deliberation record is absent — emits no run folder.

    `bedrock_cache_root` / `accept_stale` / `verified_at` thread the RBT-54 F4
    currency check into substrate assembly (see `assemble_substrate`); they are
    inert for recipes with no bedrock-cache specs.

    `extra_specs` (RBT-54 S-2 / E2' landing-state completeness) folds additional
    authorities into THIS run's substrate without widening the doctype recipe —
    for a review that must read against coupled landing-state records the general
    recipe does not carry (run-016 reviews amended DDR-002 and must see DDR-004).
    An extra spec whose logical_id already appears in the recipe is rejected (no
    silent duplicate), and the check runs before any folder is created.
    """
    sofia_root = Path(sofia_root)
    if recipe is None:
        recipe = select_recipe(doc_ids, sofia_root=sofia_root)
    specs = list(recipe(from_run=from_run))
    if extra_specs:
        recipe_ids = {spec.logical_id for spec in specs}
        clashes = sorted(s.logical_id for s in extra_specs if s.logical_id in recipe_ids)
        if clashes:
            raise PrepError(
                f"extra_specs logical_id(s) already carried by the recipe: {clashes}"
            )
        specs = specs + list(extra_specs)
    runs_root = Path(runs_root)
    run_dir = runs_root / run_id
    if run_dir.exists():
        raise PrepError(f"run folder already exists (prepared run-ids are claimed): {run_dir}")
    run_dir.mkdir(parents=True)

    from_run_dir = runs_root / from_run if from_run is not None else None
    if from_run_dir is not None and not from_run_dir.is_dir():
        raise PrepError(f"--from-run draw not found: {from_run_dir}")

    docs_root = sofia_root / "docs"

    assemble_substrate(
        specs,
        run_dir=run_dir,
        sofia_root=sofia_root,
        retrieved=retrieved,
        from_run_dir=from_run_dir,
        bedrock_cache_root=bedrock_cache_root,
        accept_stale=accept_stale,
        verified_at=verified_at,
    )
    snapshot_documents(
        doc_ids,
        docs_root=docs_root,
        sofia_root=sofia_root,
        run_dir=run_dir,
        run_id=run_id,
        sofia_head_sha=sofia_head_sha,
        retrieved=retrieved,
    )
    verify_document_snapshot(run_dir)  # what §8 gate 8 verifies, proven at prep
    return run_dir


def prep_draws(
    run_ids: list[str],
    doc_ids: list[str],
    *,
    sofia_root: str | Path,
    runs_root: str | Path,
    sofia_head_sha: str,
    retrieved: str,
    from_run: str | None = None,
    recipe: Callable[..., list[SubstrateSpec]] | None = None,
    bedrock_cache_root: str | Path | None = None,
    accept_stale: dict[str, str] | None = None,
    verified_at: str | None = None,
    extra_specs: list[SubstrateSpec] | None = None,
) -> list[Path]:
    """Prepare N draws (act e) — one prepared folder per run-id.

    Every draw snapshots the same working-tree bytes at the same HEAD, so the
    draws differ only in run_id (the two-draw verification standard rests on
    exactly that). Returns the run folders in order. `recipe` follows `prep_run`:
    None selects by doctype; an explicit recipe overrides (every draw shares the
    same doc set, so every draw resolves the same recipe). The RBT-54 F4 currency
    args and `extra_specs` (S-2) thread through identically to every draw.
    """
    return [
        prep_run(
            run_id,
            doc_ids,
            sofia_root=sofia_root,
            runs_root=runs_root,
            sofia_head_sha=sofia_head_sha,
            retrieved=retrieved,
            from_run=from_run,
            recipe=recipe,
            bedrock_cache_root=bedrock_cache_root,
            accept_stale=accept_stale,
            verified_at=verified_at,
            extra_specs=extra_specs,
        )
        for run_id in run_ids
    ]
