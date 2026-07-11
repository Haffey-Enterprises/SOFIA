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
    """A prior draw carrying the DDR recipe's carry-forward substrate (the
    bedrock ddr-template + author-decision-record SKILL, and the Notion
    sofia-vision block) — the sources prep cannot re-fetch."""
    return _build_prior_draw(
        runs_root, run_id,
        substrate={
            "authorities": {
                "ddr-template": "DDR-TEMPLATE BODY",
                "author-decision-record-SKILL": "SKILL BODY",
            },
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
    # bedrock/Notion items carry forward; repo-canonical items do not.
    carried = {s.logical_id for s in specs if s.carry_forward}
    assert carried == {"ddr-template", "author-decision-record-SKILL", "sofia-vision"}


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
    run_dir = prep_run(
        "run-014-ddr", ["DDR-004"], sofia_root=sofia_root, runs_root=runs_root,
        sofia_head_sha="HEADDDR", retrieved="2026-07-11", from_run="run-013-ddr",
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
    assert (auth / "ddr-template.md").read_text() == "DDR-TEMPLATE BODY"  # carried forward
    # The reviewed document snapshot is the DDR itself.
    assert (run_dir / "documents" / "DDR-004-inherited-confidence.md").is_file()
    verify_document_snapshot(run_dir)


def test_prep_run_ddr_selects_recipe_by_default(tmp_path) -> None:
    # No recipe injected: the doctype selector picks the DDR recipe from the
    # review target (the recipe=None production path).
    sofia_root = _ddr_sofia_tree(tmp_path, ddr_id="DDR-004", ddr_slug="ic")
    runs_root = tmp_path / "runs"
    _ddr_prior_draw(runs_root, "run-013-ddr")
    run_dir = prep_run(
        "run-014-ddr", ["DDR-004"], sofia_root=sofia_root, runs_root=runs_root,
        sofia_head_sha="H", retrieved="2026-07-11", from_run="run-013-ddr",
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
    # Re-prep an SDD run against the real develop tree + run-011 as the
    # carry-forward donor; the produced substrate reproduces run-011's
    # substrate byte-for-byte (RBT-57 acceptance: SDD recipe regression-clean).
    real_run_011 = REPO_ROOT / "agent-loop" / "runs" / "run-011-sdd-001"
    assert real_run_011.is_dir(), "run-011 must exist as the known SDD baseline"

    import shutil
    runs_root = tmp_path / "runs"
    prior = runs_root / "run-011-sdd-001"
    prior.mkdir(parents=True)
    shutil.copytree(real_run_011 / "substrate", prior / "substrate")

    run_dir = prep_run(
        "run-regress-sdd", ["SDD-001"], sofia_root=REPO_ROOT, runs_root=runs_root,
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
