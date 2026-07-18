# Module: tests.test_prep
# Purpose: RBT-52 prep tool (the snapshot PRODUCER). Covers the five acts of
#          record, the document snapshot-at-prep + provenance sub-schema, the
#          three carried lessons enforced as fail-loud assertions, the --from-run
#          carry-forward chain, N-draw emission, and the acceptance obligation:
#          a prepared folder passes run_real's gates 1-7 unmodified and provides
#          everything §8 gate 8 verifies. No LLM, no network, no git — the engine
#          is driven with injected HEAD SHA + retrieval date against a tmp tree.
#          RBT-57 adds the recipe registry (doctype selector, DDR recipe, SDD
#          byte-regression, fail-loud on a missing deliberation record).
# Scope:   Over agent_loop.prep and the agent_loop.fetchers document-snapshot
#          verifier (verify_document_snapshot / DocumentSnapshotError).

import json
from pathlib import Path

import pytest
from agent_loop.fetchers import (
    DocumentSnapshotError,
    sha256_text,
    verify_document_snapshot,
)
from agent_loop.prep import (
    RECIPES,
    PrepError,
    SubstrateSpec,
    _resolve_docs_root,
    adr_substrate_specs,
    assemble_substrate,
    ddr_substrate_specs,
    infer_doctype,
    prep_draws,
    prep_run,
    resolve_deliberation_record,
    resolve_document,
    sdd_substrate_specs,
    select_recipe,
    snapshot_documents,
)
from agent_loop.run_real import validate_prep

# Repo root (agent-loop/tests/ -> agent-loop/ -> repo). Used by the SDD
# byte-regression, which re-preps against the real develop tree + run-011.
REPO_ROOT = Path(__file__).resolve().parents[2]

DESIGN_DIR = Path(__file__).resolve().parents[1] / "design"


# --- fixtures / helpers ------------------------------------------------------


def _mini_recipe(*, from_run):  # noqa: ANN001 — matches recipe() signature
    """A minimal two-file recipe (one authority, one design-intent), both
    repo-canonical — no carry-forward, so it needs no prior draw."""
    return [
        SubstrateSpec(
            "adr-template", "authorities",
            {"source": "sofia-repo", "path": "docs/adr-template.md"},
            repo_relpath="docs/adr-template.md",
        ),
        SubstrateSpec(
            "vision", "design-intent",
            {"source": "sofia-repo", "path": "docs/vision.md"},
            repo_relpath="docs/vision.md",
        ),
    ]


def _cf_recipe(*, from_run):  # noqa: ANN001
    """One repo authority + one carry-forward design-intent (needs --from-run)."""
    return [
        SubstrateSpec(
            "adr-template", "authorities",
            {"source": "sofia-repo", "path": "docs/adr-template.md"},
            repo_relpath="docs/adr-template.md",
        ),
        SubstrateSpec("vision", "design-intent", carry_forward=True),
    ]


def _sofia_tree(tmp_path: Path, doc_ids: list[str]) -> Path:
    """A synthetic $SOFIA_ROOT: docs/ with the reviewed docs + mini-recipe
    substrate sources."""
    sofia_root = tmp_path / "sofia"
    docs = sofia_root / "docs"
    docs.mkdir(parents=True)
    for doc_id in doc_ids:
        (docs / f"{doc_id}-distilled.md").write_text(f"content of {doc_id}", encoding="utf-8")
    (docs / "adr-template.md").write_text("AUTHORITY BODY", encoding="utf-8")
    (docs / "vision.md").write_text("DESIGN INTENT BODY", encoding="utf-8")
    return sofia_root


def _build_prior_draw(
    runs_root: Path,
    run_id: str,
    *,
    substrate: dict[str, dict[str, str]],
    documents: dict[str, tuple[str, str]] | None = None,
) -> Path:
    """Hand-build a prior draw's substrate manifest (the very first substrate
    was assembled by hand; later draws carry it forward). The default — no
    `documents` — mirrors the real layout of every pre-tool run folder:
    substrate/ + substrate/manifest.json present, NO documents/ folder. Pass
    `documents` to also lay down a document snapshot + manifest."""
    run_dir = runs_root / run_id
    sub = run_dir / "substrate"
    entries = []
    for category, items in substrate.items():
        (sub / category).mkdir(parents=True, exist_ok=True)
        for logical_id, content in items.items():
            (sub / category / f"{logical_id}.md").write_text(content, encoding="utf-8")
            entries.append(
                {
                    "logical_id": logical_id,
                    "category": category,
                    "origin": {"source": "hand", "note": logical_id},
                    "retrieved": "2026-07-05",
                    "sha256": sha256_text(content),
                }
            )
    (sub / "manifest.json").write_text(json.dumps({"files": entries}), encoding="utf-8")

    if documents is not None:
        docs_out = run_dir / "documents"
        docs_out.mkdir(parents=True, exist_ok=True)
        doc_files = []
        for doc_id, (name, content) in documents.items():
            (docs_out / name).write_text(content, encoding="utf-8")
            doc_files.append(
                {
                    "doc_id": doc_id,
                    "snapshot_path": f"documents/{name}",
                    "origin": {"source": "sofia-repo", "canonical_path": f"docs/{name}"},
                    "retrieved": "2026-07-05",
                    "sha256": sha256_text(content),
                }
            )
        (docs_out / "manifest.json").write_text(
            json.dumps({"run_id": run_id, "sofia_head_sha": "PRIOR", "files": doc_files}),
            encoding="utf-8",
        )
    return run_dir


# --- act (a): resolution (homed in prep now) ---------------------------------


def test_resolve_document_one_match(tmp_path) -> None:
    (tmp_path / "sdd").mkdir()
    target = tmp_path / "sdd" / "SDD-001-ks.md"
    target.write_text("x", encoding="utf-8")
    assert resolve_document(tmp_path, "SDD-001") == target


def test_resolve_document_zero_matches_raises(tmp_path) -> None:
    with pytest.raises(PrepError):
        resolve_document(tmp_path, "SDD-999")


def test_resolve_document_multiple_matches_raises_naming_both(tmp_path) -> None:
    (tmp_path / "SDD-001-a.md").write_text("a", encoding="utf-8")
    (tmp_path / "SDD-001-b.md").write_text("b", encoding="utf-8")
    with pytest.raises(PrepError) as exc:
        resolve_document(tmp_path, "SDD-001")
    assert "SDD-001-a.md" in str(exc.value) and "SDD-001-b.md" in str(exc.value)


# --- the SDD recipe (only recipe; no registry) -------------------------------


def test_sdd_recipe_requires_from_run_for_carry_forward() -> None:
    with pytest.raises(PrepError):
        sdd_substrate_specs(from_run=None)


def test_sdd_recipe_returns_run_one_set_with_from_run() -> None:
    specs = sdd_substrate_specs(from_run="run-011-sdd-001")
    ids = {s.logical_id for s in specs}
    assert {"ADR-001", "ADR-002", "DDR-001", "DDR-002", "sdd-template", "sofia-vision"} <= ids
    # Both substrate categories are populated (gate 4 requires each non-empty).
    assert {s.category for s in specs} == {"authorities", "design-intent"}
    # bedrock/Notion items are carry-forward; repo items are not.
    carried = {s.logical_id for s in specs if s.carry_forward}
    assert carried == {
        "sdd-template", "author-decision-record-SKILL", "sofia-vision", "sdd-001-charter-notes"
    }


# --- act (b/c): document snapshot + provenance -------------------------------


def test_snapshot_documents_copies_hashes_and_records(tmp_path) -> None:
    sofia_root = _sofia_tree(tmp_path, ["SDD-001"])
    run_dir = tmp_path / "runs" / "run-100-sdd"
    snapshot_documents(
        ["SDD-001"], docs_root=sofia_root / "docs", sofia_root=sofia_root,
        run_dir=run_dir, run_id="run-100-sdd", sofia_head_sha="HEAD123", retrieved="2026-07-06",
    )
    snap = run_dir / "documents" / "SDD-001-distilled.md"
    assert snap.read_text() == "content of SDD-001"  # copied verbatim
    assert (sofia_root / "docs" / "SDD-001-distilled.md").is_file()  # source survived (copy)
    manifest = json.loads((run_dir / "documents" / "manifest.json").read_text())
    entry = manifest["files"][0]
    assert entry["doc_id"] == "SDD-001"
    assert entry["snapshot_path"] == "documents/SDD-001-distilled.md"
    assert entry["sha256"] == sha256_text("content of SDD-001")  # validator-method
    assert entry["origin"]["canonical_path"] == "docs/SDD-001-distilled.md"
    # Standalone provenance only — no prior-draw reference anywhere.
    assert set(entry) == {"doc_id", "snapshot_path", "origin", "retrieved", "sha256"}
    assert manifest["sofia_head_sha"] == "HEAD123"
    assert set(manifest) == {"run_id", "sofia_head_sha", "files"}


def test_prep_from_run_prior_draw_without_document_manifest_succeeds(tmp_path) -> None:
    # The real shape of every pre-tool run folder: substrate/ + its manifest,
    # no documents/ folder at all. It serves as substrate donor; the document
    # snapshot is taken fresh from the working tree regardless.
    sofia_root = _sofia_tree(tmp_path, ["SDD-001"])
    runs_root = tmp_path / "runs"
    prior = _build_prior_draw(
        runs_root, "run-099-sdd",
        substrate={"authorities": {"adr-template": "AUTHORITY BODY"},
                   "design-intent": {"vision": "V-BODY"}},
    )
    assert not (prior / "documents").exists()
    run_dir = prep_run(
        "run-100-sdd", ["SDD-001"], sofia_root=sofia_root, runs_root=runs_root,
        sofia_head_sha="HEAD2", retrieved="2026-07-06", from_run="run-099-sdd", recipe=_cf_recipe,
    )
    verify_document_snapshot(run_dir)  # fresh snapshot, standalone provenance


def test_prep_from_run_prior_document_bytes_differ_is_irrelevant(tmp_path) -> None:
    # An amendment draw: the reviewed document's working-tree bytes match
    # nothing in the prior draw. Irrelevant to prep — the snapshot is fresh
    # and records the working-tree hash, not any prior pin.
    sofia_root = _sofia_tree(tmp_path, ["SDD-001"])
    runs_root = tmp_path / "runs"
    _build_prior_draw(
        runs_root, "run-099-sdd",
        substrate={"authorities": {"adr-template": "AUTHORITY BODY"},
                   "design-intent": {"vision": "V-BODY"}},
        documents={"SDD-001": ("SDD-001-distilled.md", "DIFFERENT bytes")},
    )
    run_dir = prep_run(
        "run-100-sdd", ["SDD-001"], sofia_root=sofia_root, runs_root=runs_root,
        sofia_head_sha="HEAD2", retrieved="2026-07-06", from_run="run-099-sdd", recipe=_cf_recipe,
    )
    entry = json.loads((run_dir / "documents" / "manifest.json").read_text())["files"][0]
    assert entry["sha256"] == sha256_text("content of SDD-001")  # fresh working-tree hash


# --- substrate assembly (acts a-d) + lessons ---------------------------------


def test_assemble_substrate_repo_specs_lands_by_stem_and_validates(tmp_path) -> None:
    sofia_root = _sofia_tree(tmp_path, [])
    run_dir = tmp_path / "runs" / "run-100"
    assemble_substrate(
        _mini_recipe(from_run=None), run_dir=run_dir, sofia_root=sofia_root, retrieved="2026-07-06"
    )
    # Lesson #1: files land as <category>/<logical_id>.md, resolved by stem.
    assert (run_dir / "substrate" / "authorities" / "adr-template.md").read_text() == "AUTHORITY BODY"
    assert (run_dir / "substrate" / "design-intent" / "vision.md").read_text() == "DESIGN INTENT BODY"
    manifest = json.loads((run_dir / "substrate" / "manifest.json").read_text())
    ids = {e["logical_id"]: e for e in manifest["files"]}
    # Lesson #2: validator-method hashes.
    assert ids["adr-template"]["sha256"] == sha256_text("AUTHORITY BODY")


def test_assemble_substrate_repo_source_missing_raises(tmp_path) -> None:
    sofia_root = tmp_path / "sofia"
    (sofia_root / "docs").mkdir(parents=True)  # no adr-template.md / vision.md
    with pytest.raises(PrepError):
        assemble_substrate(
            _mini_recipe(from_run=None), run_dir=tmp_path / "r", sofia_root=sofia_root, retrieved="t"
        )


def test_assemble_substrate_carry_forward_without_from_run_raises(tmp_path) -> None:
    sofia_root = _sofia_tree(tmp_path, [])
    with pytest.raises(PrepError):
        assemble_substrate(
            _cf_recipe(from_run=None), run_dir=tmp_path / "r", sofia_root=sofia_root, retrieved="t"
        )


def test_assemble_substrate_carry_forward_copies_and_reuses_origin(tmp_path) -> None:
    sofia_root = _sofia_tree(tmp_path, [])
    runs_root = tmp_path / "runs"
    prior = _build_prior_draw(
        runs_root, "run-099",
        substrate={"authorities": {"adr-template": "AUTHORITY BODY"}, "design-intent": {"vision": "V-BODY"}},
    )
    run_dir = runs_root / "run-100"
    assemble_substrate(
        _cf_recipe(from_run="run-099"), run_dir=run_dir, sofia_root=sofia_root,
        retrieved="2026-07-06", from_run_dir=prior,
    )
    assert (run_dir / "substrate" / "design-intent" / "vision.md").read_text() == "V-BODY"
    manifest = {e["logical_id"]: e for e in json.loads((run_dir / "substrate" / "manifest.json").read_text())["files"]}
    # Carry-forward reuses the prior origin block.
    assert manifest["vision"]["origin"] == {"source": "hand", "note": "vision"}


def test_assemble_substrate_carry_forward_source_missing_raises(tmp_path) -> None:
    sofia_root = _sofia_tree(tmp_path, [])
    runs_root = tmp_path / "runs"
    # Prior manifest lists vision but the file is absent on disk.
    prior = runs_root / "run-099"
    (prior / "substrate" / "authorities").mkdir(parents=True)
    (prior / "substrate" / "design-intent").mkdir(parents=True)
    (prior / "substrate" / "manifest.json").write_text(
        json.dumps({"files": [
            {"logical_id": "vision", "category": "design-intent", "origin": {"s": 1},
             "retrieved": "t", "sha256": "x"},
        ]}), encoding="utf-8",
    )
    with pytest.raises(PrepError):
        assemble_substrate(
            _cf_recipe(from_run="run-099"), run_dir=runs_root / "run-100",
            sofia_root=sofia_root, retrieved="t", from_run_dir=prior,
        )


def test_assemble_substrate_pin_mismatch_raises(tmp_path) -> None:
    # A repo source whose bytes differ from the prior pin trips act (c).
    sofia_root = _sofia_tree(tmp_path, [])
    runs_root = tmp_path / "runs"
    prior = _build_prior_draw(
        runs_root, "run-099",
        substrate={"authorities": {"adr-template": "OLD BYTES"}, "design-intent": {"vision": "V"}},
    )
    with pytest.raises(PrepError):
        assemble_substrate(
            _mini_recipe(from_run="run-099"), run_dir=runs_root / "run-100",
            sofia_root=sofia_root, retrieved="t", from_run_dir=prior,
        )


def test_assemble_substrate_without_prior_manifest_raises(tmp_path) -> None:
    sofia_root = _sofia_tree(tmp_path, [])
    runs_root = tmp_path / "runs"
    (runs_root / "run-099").mkdir(parents=True)  # from_run dir, no substrate manifest
    with pytest.raises(PrepError):
        assemble_substrate(
            _mini_recipe(from_run="run-099"), run_dir=runs_root / "run-100",
            sofia_root=sofia_root, retrieved="t", from_run_dir=runs_root / "run-099",
        )


# --- lesson #3 (assertion in isolation) --------------------------------------


def test_lesson3_source_survival_assertion_trips_on_vanished_source(tmp_path) -> None:
    from agent_loop.prep import _assert_sources_survive

    present = tmp_path / "here.md"
    present.write_text("x", encoding="utf-8")
    _assert_sources_survive([present])  # no raise
    with pytest.raises(PrepError):
        _assert_sources_survive([tmp_path / "gone.md"])


# --- orchestration: prep_run + prep_draws ------------------------------------


def test_prep_run_produces_consumable_folder(tmp_path) -> None:
    sofia_root = _sofia_tree(tmp_path, ["SDD-001"])
    runs_root = tmp_path / "runs"
    run_dir = prep_run(
        "run-100-sdd", ["SDD-001"], sofia_root=sofia_root, runs_root=runs_root,
        sofia_head_sha="HEAD1", retrieved="2026-07-06", recipe=_mini_recipe,
    )
    # Snapshot verifier (what §8 gate 8 runs) passes on the produced folder.
    verify_document_snapshot(run_dir)
    assert (run_dir / "substrate" / "manifest.json").is_file()
    assert not (run_dir / "ledger.json").exists()  # not a used run (gate 1 passes)


def test_prep_run_refuses_existing_folder(tmp_path) -> None:
    sofia_root = _sofia_tree(tmp_path, ["SDD-001"])
    runs_root = tmp_path / "runs"
    (runs_root / "run-100-sdd").mkdir(parents=True)
    with pytest.raises(PrepError):
        prep_run(
            "run-100-sdd", ["SDD-001"], sofia_root=sofia_root, runs_root=runs_root,
            sofia_head_sha="H", retrieved="t", recipe=_mini_recipe,
        )


def test_prep_run_from_run_not_found_raises(tmp_path) -> None:
    sofia_root = _sofia_tree(tmp_path, ["SDD-001"])
    with pytest.raises(PrepError):
        prep_run(
            "run-100-sdd", ["SDD-001"], sofia_root=sofia_root, runs_root=tmp_path / "runs",
            sofia_head_sha="H", retrieved="t", from_run="run-404", recipe=_mini_recipe,
        )


def test_prep_run_from_run_carries_forward_end_to_end(tmp_path) -> None:
    sofia_root = _sofia_tree(tmp_path, ["SDD-001"])
    runs_root = tmp_path / "runs"
    prior = _build_prior_draw(
        runs_root, "run-099-sdd",
        substrate={"authorities": {"adr-template": "AUTHORITY BODY"}, "design-intent": {"vision": "V-BODY"}},
    )
    assert prior.is_dir()
    run_dir = prep_run(
        "run-100-sdd", ["SDD-001"], sofia_root=sofia_root, runs_root=runs_root,
        sofia_head_sha="HEAD2", retrieved="2026-07-06", from_run="run-099-sdd", recipe=_cf_recipe,
    )
    # Substrate carriage: the carry-forward file arrived with its prior bytes.
    assert (run_dir / "substrate" / "design-intent" / "vision.md").read_text() == "V-BODY"
    # Document independence: standalone provenance, no prior-draw reference.
    manifest = json.loads((run_dir / "documents" / "manifest.json").read_text())
    assert set(manifest) == {"run_id", "sofia_head_sha", "files"}
    doc_entry = manifest["files"][0]
    assert doc_entry["sha256"] == sha256_text("content of SDD-001")
    assert "carry_forward" not in doc_entry


def test_prep_draws_differ_only_in_run_id(tmp_path) -> None:
    sofia_root = _sofia_tree(tmp_path, ["SDD-001"])
    runs_root = tmp_path / "runs"
    folders = prep_draws(
        ["run-100-a", "run-100-b"], ["SDD-001"], sofia_root=sofia_root, runs_root=runs_root,
        sofia_head_sha="HEAD", retrieved="2026-07-06", recipe=_mini_recipe,
    )
    assert [f.name for f in folders] == ["run-100-a", "run-100-b"]
    ma = json.loads((folders[0] / "documents" / "manifest.json").read_text())
    mb = json.loads((folders[1] / "documents" / "manifest.json").read_text())
    # Differ only in run_id: same file hashes, same HEAD.
    assert ma["run_id"] != mb["run_id"]
    assert [f["sha256"] for f in ma["files"]] == [f["sha256"] for f in mb["files"]]
    assert ma["sofia_head_sha"] == mb["sofia_head_sha"]


# --- acceptance: a prepared folder passes gates 1-7 unmodified ---------------


def test_prepared_folder_passes_run_prep_gates(tmp_path) -> None:
    doc_ids = ["SDD-001"]
    sofia_root = _sofia_tree(tmp_path, doc_ids)
    runs_root = tmp_path / "runs"
    prep_run(
        "run-100-sdd", doc_ids, sofia_root=sofia_root, runs_root=runs_root,
        sofia_head_sha="HEAD1", retrieved="2026-07-06", recipe=_mini_recipe,
    )
    report = validate_prep(
        "run-100-sdd", doc_ids, sofia_root=sofia_root, runs_root=runs_root,
        prompt_dir=DESIGN_DIR, git_status=lambda root: "", env={"ANTHROPIC_API_KEY": "k"},
    )
    # Gates 1-6 pass on the prep-produced folder; 7 pending (gates-only, no probe).
    assert all(r.passed for r in report.results if r.number <= 6)
    gate7 = next(r for r in report.results if r.number == 7)
    assert gate7.pending


# --- fetchers.verify_document_snapshot: every failure mode -------------------


def _good_snapshot(tmp_path: Path) -> Path:
    run_dir = tmp_path / "runs" / "run-100"
    docs = run_dir / "documents"
    docs.mkdir(parents=True)
    (docs / "SDD-001-x.md").write_text("body", encoding="utf-8")
    (docs / "manifest.json").write_text(
        json.dumps({"run_id": "run-100", "sofia_head_sha": "H", "files": [
            {"doc_id": "SDD-001", "snapshot_path": "documents/SDD-001-x.md",
             "origin": {"source": "sofia-repo", "canonical_path": "docs/SDD-001-x.md"},
             "retrieved": "t", "sha256": sha256_text("body")},
        ]}), encoding="utf-8",
    )
    return run_dir


def test_verify_snapshot_ok(tmp_path) -> None:
    verify_document_snapshot(_good_snapshot(tmp_path))  # no raise


def test_verify_snapshot_missing_folder_raises(tmp_path) -> None:
    with pytest.raises(DocumentSnapshotError):
        verify_document_snapshot(tmp_path / "runs" / "nope")


def test_verify_snapshot_missing_manifest_raises(tmp_path) -> None:
    run_dir = tmp_path / "runs" / "run-100"
    (run_dir / "documents").mkdir(parents=True)
    with pytest.raises(DocumentSnapshotError):
        verify_document_snapshot(run_dir)


def test_verify_snapshot_bad_json_raises(tmp_path) -> None:
    run_dir = tmp_path / "runs" / "run-100"
    (run_dir / "documents").mkdir(parents=True)
    (run_dir / "documents" / "manifest.json").write_text("{not json", encoding="utf-8")
    with pytest.raises(DocumentSnapshotError):
        verify_document_snapshot(run_dir)


def test_verify_snapshot_not_object_raises(tmp_path) -> None:
    run_dir = tmp_path / "runs" / "run-100"
    (run_dir / "documents").mkdir(parents=True)
    (run_dir / "documents" / "manifest.json").write_text(json.dumps(["x"]), encoding="utf-8")
    with pytest.raises(DocumentSnapshotError):
        verify_document_snapshot(run_dir)


def test_verify_snapshot_empty_files_raises(tmp_path) -> None:
    run_dir = tmp_path / "runs" / "run-100"
    (run_dir / "documents").mkdir(parents=True)
    (run_dir / "documents" / "manifest.json").write_text(json.dumps({"files": []}), encoding="utf-8")
    with pytest.raises(DocumentSnapshotError):
        verify_document_snapshot(run_dir)


def test_verify_snapshot_missing_field_raises(tmp_path) -> None:
    run_dir = tmp_path / "runs" / "run-100"
    (run_dir / "documents").mkdir(parents=True)
    (run_dir / "documents" / "manifest.json").write_text(
        json.dumps({"files": [{"doc_id": "SDD-001"}]}), encoding="utf-8"
    )
    with pytest.raises(DocumentSnapshotError):
        verify_document_snapshot(run_dir)


def test_verify_snapshot_listed_missing_file_raises(tmp_path) -> None:
    run_dir = tmp_path / "runs" / "run-100"
    (run_dir / "documents").mkdir(parents=True)
    (run_dir / "documents" / "manifest.json").write_text(
        json.dumps({"files": [
            {"doc_id": "SDD-001", "snapshot_path": "documents/ghost.md", "origin": {},
             "retrieved": "t", "sha256": "x"},
        ]}), encoding="utf-8",
    )
    with pytest.raises(DocumentSnapshotError):
        verify_document_snapshot(run_dir)


def test_verify_snapshot_hash_mismatch_raises(tmp_path) -> None:
    run_dir = _good_snapshot(tmp_path)
    (run_dir / "documents" / "SDD-001-x.md").write_text("MUTATED", encoding="utf-8")
    with pytest.raises(DocumentSnapshotError):
        verify_document_snapshot(run_dir)


def test_verify_snapshot_unlisted_on_disk_file_raises(tmp_path) -> None:
    run_dir = _good_snapshot(tmp_path)
    (run_dir / "documents" / "SDD-002-extra.md").write_text("x", encoding="utf-8")
    with pytest.raises(DocumentSnapshotError):
        verify_document_snapshot(run_dir)


# =============================================================================
# RBT-57 — recipe registry generalization (doctype selector + DDR recipe)
# =============================================================================

# The SDD-specific substrate the DDR recipe must NOT leak (RBT-57 ruling).
_SDD_ONLY_SUBSTRATE = {
    "sdd-template",
    "sdd-001-charter-notes",
    "deliberation-record-sdd-001",
}


def _ddr_sofia_tree(tmp_path: Path, *, ddr_id: str, ddr_slug: str) -> Path:
    """A synthetic $SOFIA_ROOT wired for a DDR review: the canonical authority
    paths the DDR recipe hardcodes (ADR/DDR canon + SDD-001 consuming context),
    the reviewed DDR document, and the DDR's deliberation record by convention.
    Carry-forward substrate (ddr-template, the SKILL, sofia-vision) is NOT here —
    it arrives from a prior draw, exactly as in production."""
    sofia_root = tmp_path / "sofia"
    docs = sofia_root / "docs"
    for sub in ("adr", "ddr", "sdd"):
        (docs / sub).mkdir(parents=True)
    canon = {
        "adr/ADR-001-reasoning-architecture.md": "ADR-001 BODY",
        "adr/ADR-002-graph-system-of-record.md": "ADR-002 BODY",
        "ddr/DDR-001-data-architecture.md": "DDR-001 BODY",
        "ddr/DDR-002-graph-schema.md": "DDR-002 BODY",
        "sdd/SDD-001-knowledge-service.md": "SDD-001 BODY",
        # The reviewed document: the DDR itself.
        f"ddr/{ddr_id}-{ddr_slug}.md": f"{ddr_id} REVIEWED BODY",
    }
    for rel, body in canon.items():
        (docs / rel).write_text(body, encoding="utf-8")
    # Design-intent lineage: the DDR's deliberation record, by convention.
    record_dir = sofia_root / "agent-loop" / "deliberation" / f"{ddr_id.lower()}-{ddr_slug}"
    record_dir.mkdir(parents=True)
    (record_dir / "record.md").write_text(f"{ddr_id} DELIBERATION RECORD", encoding="utf-8")
    return sofia_root


def _ddr_prior_draw(runs_root: Path, run_id: str) -> Path:
    """A prior draw carrying the DDR recipe's sole carry-forward substrate — the
    Notion sofia-vision block, which prep cannot re-fetch. Since RBT-54 (F4) the
    bedrock ddr-template + author-decision-record SKILL no longer ride
    --from-run: they are sourced from the installed plugin cache and verified
    pin-vs-installed (see the RBT-54 section), so they are absent here."""
    return _build_prior_draw(
        runs_root, run_id,
        substrate={
            "design-intent": {"sofia-vision": "VISION BODY"},
        },
    )


# --- doctype selector (inference from the review-target doc-id) --------------


def test_infer_doctype_from_sdd_docid() -> None:
    assert infer_doctype(["SDD-001"]) == "sdd"


def test_infer_doctype_from_ddr_docid() -> None:
    assert infer_doctype(["DDR-004"]) == "ddr"


def test_infer_doctype_empty_raises() -> None:
    with pytest.raises(PrepError):
        infer_doctype([])


def test_infer_doctype_mixed_doctypes_raises() -> None:
    with pytest.raises(PrepError):
        infer_doctype(["SDD-001", "DDR-004"])


def test_registry_holds_sdd_and_ddr() -> None:
    # Structured as a registry so adr slots in later without another rewrite.
    assert {"sdd", "ddr"} <= set(RECIPES)


def test_select_recipe_sdd_returns_sdd_specs(tmp_path) -> None:
    recipe = select_recipe(["SDD-001"], sofia_root=tmp_path)
    ids = {s.logical_id for s in recipe(from_run="run-011-sdd-001")}
    assert "sdd-template" in ids and "deliberation-record-sdd-001" in ids


def test_select_recipe_unknown_doctype_raises(tmp_path) -> None:
    with pytest.raises(PrepError):
        select_recipe(["XYZ-001"], sofia_root=tmp_path)


def test_select_recipe_ddr_resolves_record_and_builds(tmp_path) -> None:
    sofia_root = _ddr_sofia_tree(tmp_path, ddr_id="DDR-004", ddr_slug="inherited-confidence")
    recipe = select_recipe(["DDR-004"], sofia_root=sofia_root)
    ids = {s.logical_id for s in recipe(from_run="run-013-ddr")}
    assert "ddr-template" in ids
    assert "deliberation-record-ddr-004" in ids
    assert not (_SDD_ONLY_SUBSTRATE & ids)


def test_select_recipe_ddr_requires_single_target(tmp_path) -> None:
    sofia_root = _ddr_sofia_tree(tmp_path, ddr_id="DDR-004", ddr_slug="ic")
    with pytest.raises(PrepError):
        select_recipe(["DDR-004", "DDR-005"], sofia_root=sofia_root)


# --- deliberation-record resolution (design-intent lineage, by convention) ---


def test_resolve_deliberation_record_one_match(tmp_path) -> None:
    sofia_root = _ddr_sofia_tree(tmp_path, ddr_id="DDR-004", ddr_slug="inherited-confidence")
    record = resolve_deliberation_record(sofia_root, "DDR-004")
    assert record.read_text() == "DDR-004 DELIBERATION RECORD"
    assert record.parent.name == "ddr-004-inherited-confidence"


def test_resolve_deliberation_record_zero_matches_raises(tmp_path) -> None:
    sofia_root = _ddr_sofia_tree(tmp_path, ddr_id="DDR-004", ddr_slug="ic")
    with pytest.raises(PrepError):
        resolve_deliberation_record(sofia_root, "DDR-999")


def test_resolve_deliberation_record_multiple_matches_raises(tmp_path) -> None:
    sofia_root = _ddr_sofia_tree(tmp_path, ddr_id="DDR-004", ddr_slug="ic")
    delib = sofia_root / "agent-loop" / "deliberation"
    (delib / "ddr-004-duplicate").mkdir()
    (delib / "ddr-004-duplicate" / "record.md").write_text("dup", encoding="utf-8")
    with pytest.raises(PrepError) as exc:
        resolve_deliberation_record(sofia_root, "DDR-004")
    assert "ddr-004" in str(exc.value)


# --- the DDR recipe: the ruled substrate set (present + excluded) ------------


def test_ddr_recipe_present_and_excluded_substrate() -> None:
    specs = ddr_substrate_specs(
        "DDR-004",
        "agent-loop/deliberation/ddr-004-inherited-confidence/record.md",
        from_run="run-013-ddr",
    )
    ids = {s.logical_id for s in specs}
    # Present: shared canon + SDD-001 consuming context + doctype authoring
    # authority + the design-intent lineage + doctype-agnostic vision.
    assert ids == {
        "ADR-001", "ADR-002", "DDR-001", "DDR-002",
        "SDD-001",
        "ddr-template", "author-decision-record-SKILL",
        "deliberation-record-ddr-004",
        "sofia-vision",
    }
    # Explicitly excluded: no SDD-specific artifact leaks in.
    assert not (_SDD_ONLY_SUBSTRATE & ids)
    # Both categories populated (gate 4 requires each non-empty).
    assert {s.category for s in specs} == {"authorities", "design-intent"}
    # Notion vision carries forward; bedrock authorities are cache-sourced
    # (RBT-54 F4), not --from-run; repo-canonical items are neither.
    carried = {s.logical_id for s in specs if s.carry_forward}
    assert carried == {"sofia-vision"}
    cache_sourced = {s.logical_id for s in specs if s.bedrock_cache}
    assert cache_sourced == {"ddr-template", "author-decision-record-SKILL"}


def test_ddr_recipe_deliberation_logical_id_is_generic() -> None:
    # Proves the design-intent lineage is derived from the target, not hardcoded
    # to ddr-004 — a different DDR yields its own record logical_id.
    specs = ddr_substrate_specs(
        "DDR-007", "agent-loop/deliberation/ddr-007-x/record.md", from_run="prior"
    )
    ids = {s.logical_id for s in specs}
    assert "deliberation-record-ddr-007" in ids
    assert "deliberation-record-ddr-004" not in ids


def test_ddr_recipe_requires_from_run_for_carry_forward() -> None:
    with pytest.raises(PrepError):
        ddr_substrate_specs(
            "DDR-004", "agent-loop/deliberation/ddr-004-x/record.md", from_run=None
        )


# --- end-to-end DDR prep: emits the DDR substrate, no SDD leakage (byte) -----


def test_prep_run_ddr_emits_substrate_without_sdd_leakage(tmp_path) -> None:
    sofia_root = _ddr_sofia_tree(tmp_path, ddr_id="DDR-004", ddr_slug="inherited-confidence")
    runs_root = tmp_path / "runs"
    _ddr_prior_draw(runs_root, "run-013-ddr")
    cache = _real_bedrock_1_4_0_cache(tmp_path)  # skips if the plugin is absent
    run_dir = prep_run(
        "run-014-ddr", ["DDR-004"], sofia_root=sofia_root, runs_root=runs_root,
        sofia_head_sha="HEADDDR", retrieved="2026-07-11", from_run="run-013-ddr",
        bedrock_cache_root=cache, verified_at="2026-07-11",
    )
    substrate = run_dir / "substrate"
    auth = substrate / "authorities"
    intent = substrate / "design-intent"
    # Present, landed by stem (lesson #1).
    for stem in ("ADR-001", "ADR-002", "DDR-001", "DDR-002", "SDD-001",
                 "ddr-template", "author-decision-record-SKILL"):
        assert (auth / f"{stem}.md").is_file()
    assert (intent / "deliberation-record-ddr-004.md").is_file()
    assert (intent / "sofia-vision.md").is_file()
    # No SDD-specific artifact leaked (byte-level: no such file anywhere in substrate).
    leaked = [p.name for p in substrate.rglob("*.md") if p.stem in _SDD_ONLY_SUBSTRATE]
    assert leaked == []
    # Content is the real bytes: consuming context + design-intent lineage.
    assert (auth / "SDD-001.md").read_text() == "SDD-001 BODY"
    assert (intent / "deliberation-record-ddr-004.md").read_text() == "DDR-004 DELIBERATION RECORD"
    # Bedrock authority is the installed-cache 1.4.0 bytes, with a structured
    # verified_against record (pin-vs-installed matched) and no prose note.
    manifest = json.loads((substrate / "manifest.json").read_text(encoding="utf-8"))
    skill = next(e for e in manifest["files"] if e["logical_id"] == "author-decision-record-SKILL")
    assert skill["sha256"] == "d3fb4499b8d3ff899ae3f822e8873300c1f5330cc9ee55f193fc4f9eaf9da966"
    assert skill["verified_against"] == {
        "path": "plugins/bedrock/skills/author-decision-record/SKILL.md",
        "sha256": "d3fb4499b8d3ff899ae3f822e8873300c1f5330cc9ee55f193fc4f9eaf9da966",
        "source": "installed-cache",
        "verified_at": "2026-07-11",
    }
    assert "currency_override" not in skill
    assert "note" not in skill["origin"]
    # The reviewed document snapshot is the DDR itself.
    assert (run_dir / "documents" / "DDR-004-inherited-confidence.md").is_file()
    verify_document_snapshot(run_dir)


def test_prep_run_ddr_selects_recipe_by_default(tmp_path) -> None:
    # No recipe injected: the doctype selector picks the DDR recipe from the
    # review target (the recipe=None production path).
    sofia_root = _ddr_sofia_tree(tmp_path, ddr_id="DDR-004", ddr_slug="ic")
    runs_root = tmp_path / "runs"
    _ddr_prior_draw(runs_root, "run-013-ddr")
    cache = _real_bedrock_1_4_0_cache(tmp_path)  # skips if the plugin is absent
    run_dir = prep_run(
        "run-014-ddr", ["DDR-004"], sofia_root=sofia_root, runs_root=runs_root,
        sofia_head_sha="H", retrieved="2026-07-11", from_run="run-013-ddr",
        bedrock_cache_root=cache, verified_at="2026-07-11",
    )
    assert (run_dir / "substrate" / "authorities" / "ddr-template.md").is_file()


# --- fail-loud: a DDR target whose deliberation record is absent -------------


def test_prep_run_ddr_missing_deliberation_record_fails_loud_and_emits_no_folder(tmp_path) -> None:
    sofia_root = _ddr_sofia_tree(tmp_path, ddr_id="DDR-004", ddr_slug="ic")
    # Remove the deliberation record — the design-intent lineage is now absent.
    import shutil
    shutil.rmtree(sofia_root / "agent-loop" / "deliberation" / "ddr-004-ic")
    runs_root = tmp_path / "runs"
    _ddr_prior_draw(runs_root, "run-013-ddr")
    with pytest.raises(PrepError):
        prep_run(
            "run-014-ddr", ["DDR-004"], sofia_root=sofia_root, runs_root=runs_root,
            sofia_head_sha="H", retrieved="2026-07-11", from_run="run-013-ddr",
        )
    # Fail at prep, not a silently-incomplete folder: nothing was emitted.
    assert not (runs_root / "run-014-ddr").exists()


# --- SDD recipe regression: unchanged, byte-for-byte -------------------------


def test_sdd_recipe_spec_pin() -> None:
    # Pins the SDD recipe definition exactly — any change to logical_id,
    # category, carry_forward, repo_relpath, or origin trips this.
    specs = sdd_substrate_specs(from_run="run-011-sdd-001")
    pinned = [
        (s.logical_id, s.category, s.carry_forward, s.repo_relpath, s.origin)
        for s in specs
    ]
    assert pinned == [
        ("ADR-001", "authorities", False, "docs/adr/ADR-001-reasoning-architecture.md",
         {"source": "sofia-repo", "path": "docs/adr/ADR-001-reasoning-architecture.md"}),
        ("ADR-002", "authorities", False, "docs/adr/ADR-002-graph-system-of-record.md",
         {"source": "sofia-repo", "path": "docs/adr/ADR-002-graph-system-of-record.md"}),
        ("DDR-001", "authorities", False, "docs/ddr/DDR-001-data-architecture.md",
         {"source": "sofia-repo", "path": "docs/ddr/DDR-001-data-architecture.md"}),
        ("DDR-002", "authorities", False, "docs/ddr/DDR-002-graph-schema.md",
         {"source": "sofia-repo", "path": "docs/ddr/DDR-002-graph-schema.md"}),
        ("sdd-template", "authorities", True, None, {}),
        ("author-decision-record-SKILL", "authorities", True, None, {}),
        ("deliberation-record-sdd-001", "design-intent", False,
         "agent-loop/deliberation/sdd-001-knowledge-service/record.md",
         {"source": "sofia-repo",
          "path": "agent-loop/deliberation/sdd-001-knowledge-service/record.md"}),
        ("sofia-vision", "design-intent", True, None, {}),
        ("sdd-001-charter-notes", "design-intent", True, None, {}),
    ]


def test_sdd_recipe_byte_regression_reproduces_run_011(tmp_path) -> None:
    # Property under test: the SDD prep PIPELINE reproduces a prior run's
    # substrate byte-for-byte from that run's OWN inputs — pipeline determinism,
    # NOT world-state equality with today's working tree, whose canon legitimately
    # evolves (e.g. DDR-002 v1.3.0; RBT-54 adjudicated rider). So the re-prep is
    # sourced hermetically from run-011's stored substrate, never live REPO_ROOT.
    real_run_011 = REPO_ROOT / "agent-loop" / "runs" / "run-011-sdd-001"
    assert real_run_011.is_dir(), "run-011 must exist as the known SDD baseline"

    import shutil
    runs_root = tmp_path / "runs"
    prior = runs_root / "run-011-sdd-001"
    prior.mkdir(parents=True)
    shutil.copytree(real_run_011 / "substrate", prior / "substrate")

    # Reconstruct a run-011-era $SOFIA_ROOT from run-011's own stored bytes: each
    # repo-canonical spec lands at its recipe repo_relpath (carry-forward items
    # arrive via --from-run). The reviewed SDD-001 doc is a placeholder — its
    # bytes never enter the substrate this test pins.
    sofia_root = tmp_path / "sofia-run011"
    for spec in sdd_substrate_specs(from_run="run-011-sdd-001"):
        if spec.repo_relpath is None:
            continue
        src = real_run_011 / "substrate" / spec.category / f"{spec.logical_id}.md"
        dest = sofia_root / spec.repo_relpath
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dest)
    reviewed = sofia_root / "docs" / "sdd" / "SDD-001-knowledge-service.md"
    reviewed.parent.mkdir(parents=True, exist_ok=True)
    reviewed.write_text("SDD-001 reviewed doc (bytes irrelevant to substrate)", encoding="utf-8")

    run_dir = prep_run(
        "run-regress-sdd", ["SDD-001"], sofia_root=sofia_root, runs_root=runs_root,
        sofia_head_sha="HEADX", retrieved="2026-07-11", from_run="run-011-sdd-001",
    )

    # Every produced substrate file matches run-011's committed bytes exactly.
    produced = sorted(
        p for p in (run_dir / "substrate").rglob("*.md")
    )
    assert produced, "expected substrate files"
    for path in produced:
        rel = path.relative_to(run_dir / "substrate")
        baseline = real_run_011 / "substrate" / rel
        assert baseline.is_file(), f"unexpected substrate file {rel}"
        assert path.read_bytes() == baseline.read_bytes(), f"byte drift in {rel}"
    # And the set of files matches (no missing / extra substrate).
    baseline_set = {
        p.relative_to(real_run_011 / "substrate")
        for p in (real_run_011 / "substrate").rglob("*.md")
    }
    produced_set = {p.relative_to(run_dir / "substrate") for p in produced}
    assert produced_set == baseline_set


# =============================================================================
# RBT-54 / F4 — forward currency check for bedrock-origin substrate (G1 + G2)
# =============================================================================
#
# Bedrock authorities are sourced from the INSTALLED plugin cache (injected as
# bedrock_cache_root — hermetic in tests, discovered by the CLI in production)
# and verified PIN-vs-INSTALLED: the spec carries the ratified expected_sha256;
# the check hashes the cache file and compares. Staleness-by-carry is
# unexpressible by construction — bedrock never rides --from-run. A match writes
# an entry-level verified_against {path, sha256, source: installed-cache,
# verified_at}; a mismatch fails loud unless a sanctioned
# --accept-stale-authority <id> --reason override is supplied, which writes an
# entry-level currency_override {status, expected_sha256, installed_sha256,
# reason, timestamp}. origin.note retires for bedrock-origin entries.

# The DDR recipe's ratified bedrock 1.4.0 pins (move only by explicit operator ratification).
_DDR_TEMPLATE_PIN = "59068b3a2741f497e92bff240da238d4f8b6b57471c8ff7a76ab8c09ba9668f9"
_ADR_SKILL_PIN = "d3fb4499b8d3ff899ae3f822e8873300c1f5330cc9ee55f193fc4f9eaf9da966"
_SKILL_CACHE_RELPATH = "skills/author-decision-record/SKILL.md"
_SKILL_ORIGIN_PATH = f"plugins/bedrock/{_SKILL_CACHE_RELPATH}"


def _bedrock_cache_tree(tmp_path: Path, files: dict[str, str]) -> Path:
    """A synthetic installed-bedrock plugin cache root: each key is a
    cache-relative path (e.g. 'skills/author-decision-record/SKILL.md'), written
    with the given bytes. Hermetic — the currency check reads this, never
    ~/.claude."""
    cache_root = tmp_path / "bedrock-cache"
    for relpath, content in files.items():
        dest = cache_root / relpath
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(content, encoding="utf-8")
    return cache_root


_DDR_TEMPLATE_CACHE_RELPATH = "skills/author-decision-record/templates/ddr-template.md"
_ADR_TEMPLATE_CACHE_RELPATH = "skills/author-decision-record/templates/adr-template.md"


def _real_bedrock_1_4_0_cache(
    tmp_path: Path,
    relpaths: tuple[str, ...] = (_DDR_TEMPLATE_CACHE_RELPATH, _SKILL_CACHE_RELPATH),
) -> Path:
    """Copy a recipe's bedrock files from the real installed 1.4.0 cache into a
    tmp cache root (keeps the run folder hermetic while sourcing bytes that hash
    to the ratified pins). Defaults to the DDR recipe's pair; the ADR recipe
    passes its own. Skips if the plugin isn't installed — these end-to-end tests
    exercise the real recipe, which carries real pins."""
    import shutil

    config = Path.home() / ".claude" / "plugins" / "installed_plugins.json"
    if not config.is_file():
        pytest.skip("bedrock plugin not installed (no installed_plugins.json)")
    data = json.loads(config.read_text(encoding="utf-8"))
    install_path = None
    for entry in data.get("plugins", {}).get("bedrock@bedrock", []):
        candidate = Path(entry.get("installPath", ""))
        if candidate.is_dir():
            install_path = candidate
            break
    if install_path is None:
        pytest.skip("bedrock plugin cache not resolvable")
    cache_root = tmp_path / "real-bedrock-cache"
    for relpath in relpaths:
        src = install_path / relpath
        if not src.is_file():
            pytest.skip(f"installed bedrock cache missing {relpath}")
        dest = cache_root / relpath
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dest)
    return cache_root


def _skill_spec(expected_sha256: str) -> SubstrateSpec:
    """A bedrock-cache SubstrateSpec for the author-decision-record SKILL."""
    return SubstrateSpec(
        "author-decision-record-SKILL", "authorities",
        {"source": "bedrock", "path": _SKILL_ORIGIN_PATH},
        bedrock_cache=True,
        expected_sha256=expected_sha256,
    )


def _repo_intent_spec() -> SubstrateSpec:
    """A repo-canonical design-intent spec, so substrate has both categories."""
    return SubstrateSpec(
        "vision", "design-intent",
        {"source": "sofia-repo", "path": "docs/vision.md"},
        repo_relpath="docs/vision.md",
    )


def _sofia_with_vision(tmp_path: Path) -> Path:
    sofia_root = tmp_path / "sofia"
    (sofia_root / "docs").mkdir(parents=True)
    (sofia_root / "docs" / "vision.md").write_text("VISION", encoding="utf-8")
    return sofia_root


def _skill_entry(run_dir: Path) -> dict:
    manifest = json.loads((run_dir / "substrate" / "manifest.json").read_text(encoding="utf-8"))
    return next(e for e in manifest["files"] if e["logical_id"] == "author-decision-record-SKILL")


# --- currency match: verified_against recorded, no override, note retired ----


def test_bedrock_cache_currency_match_records_verified_against(tmp_path) -> None:
    content = "SKILL 1.3.0 BODY"
    sha = sha256_text(content)
    cache = _bedrock_cache_tree(tmp_path, {_SKILL_CACHE_RELPATH: content})
    sofia_root = _sofia_with_vision(tmp_path)
    run_dir = tmp_path / "runs" / "r1"
    assemble_substrate(
        [_skill_spec(sha), _repo_intent_spec()],
        run_dir=run_dir, sofia_root=sofia_root, retrieved="2026-07-13",
        bedrock_cache_root=cache, verified_at="2026-07-13",
    )
    entry = _skill_entry(run_dir)
    assert entry["sha256"] == sha
    assert entry["verified_against"] == {
        "path": _SKILL_ORIGIN_PATH,
        "sha256": sha,
        "source": "installed-cache",
        "verified_at": "2026-07-13",
    }
    assert "currency_override" not in entry
    assert "note" not in entry["origin"]  # prose currency note retired for bedrock
    # The snapshotted bytes are the cache bytes.
    landed = run_dir / "substrate" / "authorities" / "author-decision-record-SKILL.md"
    assert landed.read_text(encoding="utf-8") == content


def test_bedrock_cache_verified_at_defaults_to_retrieved(tmp_path) -> None:
    content = "SKILL BODY"
    cache = _bedrock_cache_tree(tmp_path, {_SKILL_CACHE_RELPATH: content})
    sofia_root = _sofia_with_vision(tmp_path)
    run_dir = tmp_path / "runs" / "r1"
    assemble_substrate(
        [_skill_spec(sha256_text(content)), _repo_intent_spec()],
        run_dir=run_dir, sofia_root=sofia_root, retrieved="2026-07-13",
        bedrock_cache_root=cache,  # verified_at omitted
    )
    assert _skill_entry(run_dir)["verified_against"]["verified_at"] == "2026-07-13"


# --- pin mismatch: fail loud, naming file + both hashes ----------------------


def test_bedrock_cache_pin_mismatch_fails_loud(tmp_path) -> None:
    installed = "DRIFTED BODY"
    cache = _bedrock_cache_tree(tmp_path, {_SKILL_CACHE_RELPATH: installed})
    sofia_root = _sofia_with_vision(tmp_path)
    pinned_sha = sha256_text("PINNED BODY")
    with pytest.raises(PrepError) as exc:
        assemble_substrate(
            [_skill_spec(pinned_sha), _repo_intent_spec()],
            run_dir=tmp_path / "runs" / "r1", sofia_root=sofia_root,
            retrieved="2026-07-13", bedrock_cache_root=cache, verified_at="2026-07-13",
        )
    msg = str(exc.value)
    assert "author-decision-record-SKILL" in msg
    assert pinned_sha in msg            # expected
    assert sha256_text(installed) in msg  # installed


# --- sanctioned override: accepts a mismatch, records currency_override -------


def test_bedrock_cache_override_accepts_mismatch_and_records_currency_override(tmp_path) -> None:
    installed = "DRIFTED 1.3.1 BODY"
    installed_sha = sha256_text(installed)
    pinned_sha = sha256_text("PINNED 1.3.0 BODY")
    cache = _bedrock_cache_tree(tmp_path, {_SKILL_CACHE_RELPATH: installed})
    sofia_root = _sofia_with_vision(tmp_path)
    run_dir = tmp_path / "runs" / "r1"
    reason = "operator-ratified 1.3.1 drift, RBT-99"
    assemble_substrate(
        [_skill_spec(pinned_sha), _repo_intent_spec()],
        run_dir=run_dir, sofia_root=sofia_root, retrieved="2026-07-13",
        bedrock_cache_root=cache,
        accept_stale={"author-decision-record-SKILL": reason},
        verified_at="2026-07-13",
    )
    entry = _skill_entry(run_dir)
    assert entry["sha256"] == installed_sha  # snapshotted the actual installed bytes
    assert entry["currency_override"] == {
        "status": "accepted-stale",
        "expected_sha256": pinned_sha,
        "installed_sha256": installed_sha,
        "reason": reason,
        "timestamp": "2026-07-13",
    }
    assert entry["verified_against"]["sha256"] == installed_sha


def test_bedrock_cache_override_without_reason_rejected(tmp_path) -> None:
    cache = _bedrock_cache_tree(tmp_path, {_SKILL_CACHE_RELPATH: "DRIFTED BODY"})
    sofia_root = _sofia_with_vision(tmp_path)
    with pytest.raises(PrepError):
        assemble_substrate(
            [_skill_spec(sha256_text("PINNED BODY")), _repo_intent_spec()],
            run_dir=tmp_path / "runs" / "r1", sofia_root=sofia_root,
            retrieved="2026-07-13", bedrock_cache_root=cache,
            accept_stale={"author-decision-record-SKILL": "   "},  # blank reason
            verified_at="2026-07-13",
        )


# --- fail-loud on misconfiguration: no cache root, absent cache file ----------


def test_bedrock_cache_missing_cache_root_raises(tmp_path) -> None:
    sofia_root = _sofia_with_vision(tmp_path)
    with pytest.raises(PrepError):
        assemble_substrate(
            [_skill_spec(_ADR_SKILL_PIN), _repo_intent_spec()],
            run_dir=tmp_path / "runs" / "r1", sofia_root=sofia_root,
            retrieved="2026-07-13", bedrock_cache_root=None, verified_at="2026-07-13",
        )


def test_bedrock_cache_missing_file_raises(tmp_path) -> None:
    cache = _bedrock_cache_tree(tmp_path, {})  # empty cache — SKILL.md absent
    sofia_root = _sofia_with_vision(tmp_path)
    with pytest.raises(PrepError) as exc:
        assemble_substrate(
            [_skill_spec(_ADR_SKILL_PIN), _repo_intent_spec()],
            run_dir=tmp_path / "runs" / "r1", sofia_root=sofia_root,
            retrieved="2026-07-13", bedrock_cache_root=cache, verified_at="2026-07-13",
        )
    assert "SKILL.md" in str(exc.value)


# --- cache-relpath derivation (origin.path -> cache-relative) ----------------


def test_bedrock_cache_relpath_strips_plugin_prefix() -> None:
    from agent_loop.prep import _bedrock_cache_relpath

    assert (
        _bedrock_cache_relpath(_SKILL_ORIGIN_PATH)
        == _SKILL_CACHE_RELPATH
    )


def test_bedrock_cache_relpath_bad_prefix_raises() -> None:
    from agent_loop.prep import _bedrock_cache_relpath

    with pytest.raises(PrepError):
        _bedrock_cache_relpath("skills/author-decision-record/SKILL.md")


# --- the DDR recipe pins bedrock authorities at their 1.4.0 hashes ------------


def test_ddr_recipe_pins_bedrock_authorities_from_cache_at_1_4_0() -> None:
    specs = ddr_substrate_specs(
        "DDR-004", "agent-loop/deliberation/ddr-004-x/record.md", from_run="prior"
    )
    by_id = {s.logical_id: s for s in specs}

    ddr_tmpl = by_id["ddr-template"]
    assert ddr_tmpl.bedrock_cache is True and ddr_tmpl.carry_forward is False
    assert ddr_tmpl.expected_sha256 == _DDR_TEMPLATE_PIN
    assert ddr_tmpl.origin == {
        "source": "bedrock",
        "path": "plugins/bedrock/skills/author-decision-record/templates/ddr-template.md",
    }

    skill = by_id["author-decision-record-SKILL"]
    assert skill.bedrock_cache is True and skill.carry_forward is False
    assert skill.expected_sha256 == _ADR_SKILL_PIN
    assert skill.origin == {"source": "bedrock", "path": _SKILL_ORIGIN_PATH}

    # sofia-vision stays carry-forward (Notion, not bedrock).
    assert by_id["sofia-vision"].carry_forward is True
    assert by_id["sofia-vision"].bedrock_cache is False


def test_bedrock_cache_spec_without_pin_raises(tmp_path) -> None:
    # A bedrock-cache spec must carry its ratified pin — the pin is its authority.
    cache = _bedrock_cache_tree(tmp_path, {_SKILL_CACHE_RELPATH: "BODY"})
    sofia_root = _sofia_with_vision(tmp_path)
    unpinned = SubstrateSpec(
        "author-decision-record-SKILL", "authorities",
        {"source": "bedrock", "path": _SKILL_ORIGIN_PATH},
        bedrock_cache=True,  # expected_sha256 left None
    )
    with pytest.raises(PrepError):
        assemble_substrate(
            [unpinned, _repo_intent_spec()],
            run_dir=tmp_path / "runs" / "r1", sofia_root=sofia_root,
            retrieved="2026-07-13", bedrock_cache_root=cache, verified_at="2026-07-13",
        )


# =============================================================================
# RBT-54 / S-2 — per-run --extra-canon substrate extension (E2' completeness)
# =============================================================================
#
# Landing-state substrate completeness (E2' warrant): a review must read against
# the landing-state corpus, which may include coupled records the general recipe
# does not carry (run-016 reviews amended DDR-002 and must see DDR-004 v1.1.0).
# `extra_specs` folds such authorities into a single run WITHOUT widening the
# doctype recipe; a logical_id already in the recipe is rejected (no silent dup).


def test_prep_run_extra_canon_folds_in_authority(tmp_path) -> None:
    sofia_root = _sofia_tree(tmp_path, ["SDD-001"])
    (sofia_root / "docs" / "coupled.md").write_text("COUPLED CANON", encoding="utf-8")
    extra = SubstrateSpec(
        "DDR-COUPLED", "authorities",
        {"source": "sofia-repo", "path": "docs/coupled.md"},
        repo_relpath="docs/coupled.md",
    )
    run_dir = prep_run(
        "run-x", ["SDD-001"], sofia_root=sofia_root, runs_root=tmp_path / "runs",
        sofia_head_sha="H", retrieved="2026-07-13", recipe=_mini_recipe,
        extra_specs=[extra],
    )
    landed = run_dir / "substrate" / "authorities" / "DDR-COUPLED.md"
    assert landed.read_text(encoding="utf-8") == "COUPLED CANON"
    manifest = json.loads((run_dir / "substrate" / "manifest.json").read_text(encoding="utf-8"))
    assert any(e["logical_id"] == "DDR-COUPLED" for e in manifest["files"])


def test_prep_run_extra_canon_duplicate_logical_id_raises_and_emits_no_folder(tmp_path) -> None:
    sofia_root = _sofia_tree(tmp_path, ["SDD-001"])
    dup = SubstrateSpec(
        "adr-template", "authorities",  # already carried by _mini_recipe
        {"source": "sofia-repo", "path": "docs/adr-template.md"},
        repo_relpath="docs/adr-template.md",
    )
    runs_root = tmp_path / "runs"
    with pytest.raises(PrepError):
        prep_run(
            "run-x", ["SDD-001"], sofia_root=sofia_root, runs_root=runs_root,
            sofia_head_sha="H", retrieved="2026-07-13", recipe=_mini_recipe,
            extra_specs=[dup],
        )
    # Fail before the folder is created (no silently-partial run).
    assert not (runs_root / "run-x").exists()


# =============================================================================
# RBT-67 — the ADR recipe + sandbox-fixture ingest (docs_root override)
# =============================================================================

# Substrate belonging to other doctypes' recipes, which an ADR prep must not leak.
_NON_ADR_SUBSTRATE = _SDD_ONLY_SUBSTRATE | {"ddr-template", "SDD-001"}


def _adr_sofia_tree(tmp_path: Path) -> Path:
    """A synthetic $SOFIA_ROOT wired for an ADR review: the canonical authority
    paths the ADR recipe hardcodes, the fixed triage-001 charter carrier, and a
    SANDBOX fixture holding the reviewed ADR-003 — deliberately outside docs/,
    which is what keeps the canonical tree clean for gate 2. Carry-forward
    substrate (sofia-vision) is not here; it arrives from a prior draw."""
    sofia_root = tmp_path / "sofia"
    docs = sofia_root / "docs"
    for sub in ("adr", "ddr"):
        (docs / sub).mkdir(parents=True)
    for rel, body in {
        "adr/ADR-001-reasoning-architecture.md": "ADR-001 BODY",
        "adr/ADR-002-graph-system-of-record.md": "ADR-002 BODY",
        "ddr/DDR-001-data-architecture.md": "DDR-001 BODY",
        "ddr/DDR-002-graph-schema.md": "DDR-002 BODY",
    }.items():
        (docs / rel).write_text(body, encoding="utf-8")
    charter = sofia_root / "agent-loop" / "triage" / "triage-001-distilled-set"
    charter.mkdir(parents=True)
    (charter / "record.md").write_text("TRIAGE-001 CHARTER", encoding="utf-8")
    # The sandbox fixture: the reviewed draft, never canonical.
    fixture = sofia_root / "agent-loop" / "sandbox" / "adr-003-fixture" / "docs" / "adr"
    fixture.mkdir(parents=True)
    (fixture / "ADR-003-kg-entry-governance.md").write_text(
        "ADR-003 SANDBOX FIXTURE BODY", encoding="utf-8"
    )
    return sofia_root


def _adr_prior_draw(runs_root: Path, run_id: str) -> Path:
    """A prior draw carrying the ADR recipe's sole carry-forward substrate — the
    Notion sofia-vision block, which prep cannot re-fetch. The bedrock
    adr-template + SKILL do not ride --from-run (RBT-54 F4), so they are absent."""
    return _build_prior_draw(
        runs_root, run_id, substrate={"design-intent": {"sofia-vision": "VISION BODY"}},
    )


def test_infer_doctype_from_adr_docid() -> None:
    assert infer_doctype(["ADR-003"]) == "adr"


def test_select_recipe_adr_returns_adr_specs(tmp_path) -> None:
    recipe = select_recipe(["ADR-003"], sofia_root=tmp_path)
    assert recipe is adr_substrate_specs
    assert "adr" in RECIPES


def test_adr_recipe_present_and_excluded_substrate() -> None:
    specs = adr_substrate_specs(from_run="seed-ddr-carry-forward")
    ids = {s.logical_id for s in specs}
    # Present: shared canon + doctype authoring authority + the fixed charter
    # carrier + doctype-agnostic vision.
    assert ids == {
        "ADR-001", "ADR-002", "DDR-001", "DDR-002",
        "adr-template", "author-decision-record-SKILL",
        "triage-001-charter",
        "sofia-vision",
    }
    # The ratified floor: without these the seeded defects are not catchable.
    assert {"ADR-001", "ADR-002", "DDR-002", "adr-template", "triage-001-charter"} <= ids
    # Excluded: no other doctype's artifact leaks in.
    assert not (_NON_ADR_SUBSTRATE & ids)
    # Both categories populated (gate 4 requires each non-empty).
    assert {s.category for s in specs} == {"authorities", "design-intent"}
    # Notion vision carries forward; bedrock authorities are cache-sourced
    # (RBT-54 F4), not --from-run; repo-canonical items are neither.
    assert {s.logical_id for s in specs if s.carry_forward} == {"sofia-vision"}
    assert {s.logical_id for s in specs if s.bedrock_cache} == {
        "adr-template", "author-decision-record-SKILL"
    }


def test_adr_recipe_has_no_per_target_resolver() -> None:
    # Unlike the DDR recipe, an ADR's charter is the fixed triage-001 record —
    # the recipe takes no target and yields the same charter for any ADR.
    for target in (["ADR-003"], ["ADR-009"]):
        recipe = select_recipe(target, sofia_root=Path("/nonexistent"))
        ids = {s.logical_id for s in recipe(from_run="prior")}
        assert "triage-001-charter" in ids
        assert not any(i.startswith("deliberation-record-") for i in ids)


def test_adr_recipe_requires_from_run_for_carry_forward() -> None:
    with pytest.raises(PrepError):
        adr_substrate_specs(from_run=None)


def test_prep_run_adr_sandbox_ingest_emits_fixture_snapshot_and_canon_substrate(
    tmp_path,
) -> None:
    sofia_root = _adr_sofia_tree(tmp_path)
    runs_root = tmp_path / "runs"
    _adr_prior_draw(runs_root, "seed-adr")
    cache = _real_bedrock_1_4_0_cache(
        tmp_path, (_ADR_TEMPLATE_CACHE_RELPATH, _SKILL_CACHE_RELPATH)
    )
    sandbox_docs = sofia_root / "agent-loop" / "sandbox" / "adr-003-fixture" / "docs"

    run_dir = prep_run(
        "run-019-adr-003-sandbox", ["ADR-003"], sofia_root=sofia_root, runs_root=runs_root,
        sofia_head_sha="HEADADR", retrieved="2026-07-17", from_run="seed-adr",
        bedrock_cache_root=cache, verified_at="2026-07-17", docs_root=sandbox_docs,
    )

    # The reviewed document came from the SANDBOX, not the canonical corpus.
    snap = run_dir / "documents" / "ADR-003-kg-entry-governance.md"
    assert snap.read_text() == "ADR-003 SANDBOX FIXTURE BODY"
    doc_manifest = json.loads((run_dir / "documents" / "manifest.json").read_text())
    entry = doc_manifest["files"][0]
    assert entry["doc_id"] == "ADR-003"
    # Provenance rides the content hash; the canonical_path records the fixture.
    assert entry["sha256"] == sha256_text("ADR-003 SANDBOX FIXTURE BODY")
    assert "sandbox/adr-003-fixture" in entry["origin"]["canonical_path"]
    assert not entry["origin"]["canonical_path"].startswith("docs/")

    # The authorities still came from the REAL docs/ — a fixture read against canon.
    auth = run_dir / "substrate" / "authorities"
    for stem in ("ADR-001", "ADR-002", "DDR-001", "DDR-002",
                 "adr-template", "author-decision-record-SKILL"):
        assert (auth / f"{stem}.md").is_file()
    assert (auth / "ADR-001.md").read_text() == "ADR-001 BODY"
    intent = run_dir / "substrate" / "design-intent"
    assert (intent / "triage-001-charter.md").read_text() == "TRIAGE-001 CHARTER"
    assert (intent / "sofia-vision.md").read_text() == "VISION BODY"
    # The real adr-template bytes landed (pin-verified against the installed cache).
    assert "adr" in (auth / "adr-template.md").read_text().lower()
    # No other doctype's substrate leaked in.
    leaked = [p.name for p in (run_dir / "substrate").rglob("*.md")
              if p.stem in _NON_ADR_SUBSTRATE]
    assert leaked == []
    # The sandbox source survived its copy (lesson #3 holds for the fixture too).
    assert (sandbox_docs / "adr" / "ADR-003-kg-entry-governance.md").is_file()


def test_docs_root_override_wins_over_the_canonical_corpus(tmp_path) -> None:
    # The discriminating case: the same doc-id resolvable in BOTH trees. The
    # override decides — otherwise a sandbox run could silently review canon.
    sofia_root = _adr_sofia_tree(tmp_path)
    (sofia_root / "docs" / "adr" / "ADR-003-kg-entry-governance.md").write_text(
        "ADR-003 CANONICAL BODY", encoding="utf-8"
    )
    runs_root = tmp_path / "runs"
    _adr_prior_draw(runs_root, "seed-adr")
    cache = _real_bedrock_1_4_0_cache(
        tmp_path, (_ADR_TEMPLATE_CACHE_RELPATH, _SKILL_CACHE_RELPATH)
    )
    sandbox_docs = sofia_root / "agent-loop" / "sandbox" / "adr-003-fixture" / "docs"

    run_dir = prep_run(
        "run-020-adr", ["ADR-003"], sofia_root=sofia_root, runs_root=runs_root,
        sofia_head_sha="H", retrieved="2026-07-17", from_run="seed-adr",
        bedrock_cache_root=cache, verified_at="2026-07-17", docs_root=sandbox_docs,
    )
    text = (run_dir / "documents" / "ADR-003-kg-entry-governance.md").read_text()
    assert text == "ADR-003 SANDBOX FIXTURE BODY"
    assert "CANONICAL" not in text


def test_docs_root_defaults_to_the_canonical_corpus(tmp_path) -> None:
    # Omitting the override is the production path: docs/ is the source.
    sofia_root = _adr_sofia_tree(tmp_path)
    (sofia_root / "docs" / "adr" / "ADR-003-kg-entry-governance.md").write_text(
        "ADR-003 CANONICAL BODY", encoding="utf-8"
    )
    runs_root = tmp_path / "runs"
    _adr_prior_draw(runs_root, "seed-adr")
    cache = _real_bedrock_1_4_0_cache(
        tmp_path, (_ADR_TEMPLATE_CACHE_RELPATH, _SKILL_CACHE_RELPATH)
    )
    run_dir = prep_run(
        "run-021-adr", ["ADR-003"], sofia_root=sofia_root, runs_root=runs_root,
        sofia_head_sha="H", retrieved="2026-07-17", from_run="seed-adr",
        bedrock_cache_root=cache, verified_at="2026-07-17",
    )
    assert (run_dir / "documents" / "ADR-003-kg-entry-governance.md").read_text() == (
        "ADR-003 CANONICAL BODY"
    )


def test_sandbox_prepped_folder_validates_and_gate2_reads_the_real_docs_tree(
    tmp_path,
) -> None:
    # Gate 2's subject is unchanged by the sandbox ingest: it checks the
    # canonical docs/ tree of $SOFIA_ROOT, which the fixture never touches.
    sofia_root = _adr_sofia_tree(tmp_path)
    runs_root = tmp_path / "runs"
    _adr_prior_draw(runs_root, "seed-adr")
    cache = _real_bedrock_1_4_0_cache(
        tmp_path, (_ADR_TEMPLATE_CACHE_RELPATH, _SKILL_CACHE_RELPATH)
    )
    sandbox_docs = sofia_root / "agent-loop" / "sandbox" / "adr-003-fixture" / "docs"
    prep_run(
        "run-019-adr-003-sandbox", ["ADR-003"], sofia_root=sofia_root, runs_root=runs_root,
        sofia_head_sha="H", retrieved="2026-07-17", from_run="seed-adr",
        bedrock_cache_root=cache, verified_at="2026-07-17", docs_root=sandbox_docs,
    )
    seen: list[Path] = []

    def git_status(root: Path) -> str:
        seen.append(root)
        return ""  # clean docs tree

    report = validate_prep(
        "run-019-adr-003-sandbox", ["ADR-003"], sofia_root=sofia_root,
        runs_root=runs_root, prompt_dir=DESIGN_DIR, git_status=git_status, env={},
    )
    # Gate 2 was asked about the real $SOFIA_ROOT, not the sandbox root.
    assert seen == [sofia_root]
    # Gates 1-5 and 8 pass on a sandbox-prepped folder; 6/7 pend without a key.
    passed = {r.number for r in report.results if r.passed}
    assert {1, 2, 3, 4, 5, 8} <= passed
    assert {r.number for r in report.results if r.pending} == {6, 7}


def test_docs_root_relative_override_is_repo_relative(tmp_path) -> None:
    # The CLI shape: an operator types --docs-root agent-loop/sandbox/.../docs.
    # A relative root resolves against $SOFIA_ROOT, and the snapshot's
    # repo-relative canonical_path provenance still computes.
    sofia_root = _adr_sofia_tree(tmp_path)
    runs_root = tmp_path / "runs"
    _adr_prior_draw(runs_root, "seed-adr")
    cache = _real_bedrock_1_4_0_cache(
        tmp_path, (_ADR_TEMPLATE_CACHE_RELPATH, _SKILL_CACHE_RELPATH)
    )
    run_dir = prep_run(
        "run-022-adr", ["ADR-003"], sofia_root=sofia_root, runs_root=runs_root,
        sofia_head_sha="H", retrieved="2026-07-17", from_run="seed-adr",
        bedrock_cache_root=cache, verified_at="2026-07-17",
        docs_root="agent-loop/sandbox/adr-003-fixture/docs",  # relative
    )
    assert (run_dir / "documents" / "ADR-003-kg-entry-governance.md").read_text() == (
        "ADR-003 SANDBOX FIXTURE BODY"
    )
    entry = json.loads((run_dir / "documents" / "manifest.json").read_text())["files"][0]
    assert entry["origin"]["canonical_path"] == (
        "agent-loop/sandbox/adr-003-fixture/docs/adr/ADR-003-kg-entry-governance.md"
    )


def test_docs_root_outside_the_repo_fails_loud(tmp_path) -> None:
    # Provenance is repo-relative, so an out-of-repo root has none to record.
    sofia_root = _adr_sofia_tree(tmp_path)
    outside = tmp_path / "elsewhere" / "docs"
    (outside / "adr").mkdir(parents=True)
    (outside / "adr" / "ADR-003-x.md").write_text("OUTSIDE", encoding="utf-8")
    runs_root = tmp_path / "runs"
    with pytest.raises(PrepError, match="outside .SOFIA_ROOT"):
        prep_run(
            "run-023-adr", ["ADR-003"], sofia_root=sofia_root, runs_root=runs_root,
            sofia_head_sha="H", retrieved="2026-07-17",
            recipe=_mini_recipe, docs_root=outside,
        )
    # Fail before the folder is created (no silently-partial run).
    assert not (runs_root / "run-023-adr").exists()


def test_resolve_docs_root_relative_override_is_repo_relative(tmp_path) -> None:
    # The relative-override happy path of _resolve_docs_root: an operator-typed
    # repo-relative docs_root resolves under $SOFIA_ROOT and is returned. Covered
    # directly (no bedrock plugin needed) so the 100% line+branch bar holds in CI,
    # where the plugin-gated real-recipe tests that also exercise this path skip.
    sofia_root = tmp_path
    fixture = sofia_root / "agent-loop" / "sandbox" / "adr-003-fixture" / "docs"
    fixture.mkdir(parents=True)

    resolved = _resolve_docs_root("agent-loop/sandbox/adr-003-fixture/docs", sofia_root)

    assert resolved == fixture.resolve()


def test_resolve_docs_root_none_is_the_canonical_corpus(tmp_path) -> None:
    # None → <sofia_root>/docs (the canonical corpus), the other lawful branch.
    assert _resolve_docs_root(None, tmp_path) == tmp_path / "docs"
