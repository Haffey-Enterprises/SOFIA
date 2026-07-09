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


# --- substrate recipe (the SDD recipe is the ONLY recipe; there is no registry)


@dataclass(frozen=True)
class SubstrateSpec:
    """One substrate file to assemble.

    Exactly one source applies:
      - `repo_relpath` set: copy from `<sofia_root>/<repo_relpath>` (a
        repo-canonical source, tracked for lesson #3);
      - `carry_forward` True: copy from the prior draw's substrate under
        `--from-run` (for sources the runner cannot re-fetch — bedrock's
        archived templates/skills, Notion vision — carried forward with a pin
        assertion), reusing the prior manifest's origin block.
    """

    logical_id: str
    category: str  # "authorities" | "design-intent"
    origin: dict = field(default_factory=dict)
    repo_relpath: str | None = None
    carry_forward: bool = False


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
) -> None:
    """Assemble the frozen substrate into `run_dir/substrate/` (acts a-d).

    Each spec's file lands at `<category>/<logical_id>.md` (lesson #1), copied
    from its repo-canonical path or carried forward from `--from-run`, hashed
    validator-method (lesson #2), and (under `--from-run`, where a prior pin
    exists) asserted against that pin (act c). Emits the substrate manifest in
    the existing §3 schema (act d) and self-validates it. Finally asserts every
    repo-canonical source survived (lesson #3).
    """
    substrate_out = run_dir / "substrate"
    sofia_root = Path(sofia_root)
    prior_entries = _prior_substrate_entries(from_run_dir) if from_run_dir is not None else {}

    entries: list[dict] = []
    canonical_sources: list[Path] = []
    for spec in specs:
        category_dir = substrate_out / spec.category
        category_dir.mkdir(parents=True, exist_ok=True)
        dest = category_dir / f"{spec.logical_id}.md"  # lesson #1

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
    recipe=sdd_substrate_specs,
) -> Path:
    """Prepare one run folder (documents snapshot + substrate) and return it.

    Refuses to overwrite an existing folder — a prepared run-id is claimed, and a
    used one is immutable evidence (mirrors §8 gate 1). Assembles substrate and
    the document snapshot, then verifies the snapshot the way §8 gate 8 will, so
    a folder this tool returns is one the runner can consume.
    """
    runs_root = Path(runs_root)
    run_dir = runs_root / run_id
    if run_dir.exists():
        raise PrepError(f"run folder already exists (prepared run-ids are claimed): {run_dir}")
    run_dir.mkdir(parents=True)

    from_run_dir = runs_root / from_run if from_run is not None else None
    if from_run_dir is not None and not from_run_dir.is_dir():
        raise PrepError(f"--from-run draw not found: {from_run_dir}")

    sofia_root = Path(sofia_root)
    docs_root = sofia_root / "docs"

    assemble_substrate(
        recipe(from_run=from_run),
        run_dir=run_dir,
        sofia_root=sofia_root,
        retrieved=retrieved,
        from_run_dir=from_run_dir,
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
    recipe=sdd_substrate_specs,
) -> list[Path]:
    """Prepare N draws (act e) — one prepared folder per run-id.

    Every draw snapshots the same working-tree bytes at the same HEAD, so the
    draws differ only in run_id (the two-draw verification standard rests on
    exactly that). Returns the run folders in order.
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
        )
        for run_id in run_ids
    ]
