# Module: tests.test_prep
# Purpose: RBT-52 prep tool (the snapshot PRODUCER). Covers the five acts of
#          record, the document snapshot-at-prep + provenance sub-schema, the
#          three carried lessons enforced as fail-loud assertions, the --from-run
#          carry-forward chain, N-draw emission, and the acceptance obligation:
#          a prepared folder passes run_real's gates 1-7 unmodified and provides
#          everything §8 gate 8 verifies. No LLM, no network, no git — the engine
#          is driven with injected HEAD SHA + retrieval date against a tmp tree.
# Scope:   Over agent_loop.prep and the agent_loop.fetchers document-snapshot
#          verifier (verify_document_snapshot / DocumentSnapshotError).

import json
from pathlib import Path

import pytest

from agent_loop.fetchers import (
    DocumentSnapshotError,
    SubstrateError,
    sha256_text,
    verify_document_snapshot,
)
from agent_loop.prep import (
    PrepError,
    SubstrateSpec,
    assemble_substrate,
    prep_draws,
    prep_run,
    resolve_document,
    sdd_substrate_specs,
    snapshot_documents,
)
from agent_loop.run_real import validate_prep

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
    documents: dict[str, tuple[str, str]],
) -> Path:
    """Hand-build a prior draw's substrate + document manifests (the very first
    substrate was assembled by hand; later draws carry it forward)."""
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
                "carry_forward": None,
            }
        )
    (docs_out / "manifest.json").write_text(
        json.dumps({"run_id": run_id, "sofia_head_sha": "PRIOR", "from_run": None, "files": doc_files}),
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
    assert entry["carry_forward"] is None
    assert manifest["sofia_head_sha"] == "HEAD123" and manifest["from_run"] is None


def test_snapshot_documents_from_run_records_carry_forward_when_pin_matches(tmp_path) -> None:
    sofia_root = _sofia_tree(tmp_path, ["SDD-001"])
    runs_root = tmp_path / "runs"
    prior = _build_prior_draw(
        runs_root, "run-099-sdd",
        substrate={"authorities": {"a": "A"}, "design-intent": {"d": "D"}},
        documents={"SDD-001": ("SDD-001-distilled.md", "content of SDD-001")},
    )
    run_dir = runs_root / "run-100-sdd"
    snapshot_documents(
        ["SDD-001"], docs_root=sofia_root / "docs", sofia_root=sofia_root,
        run_dir=run_dir, run_id="run-100-sdd", sofia_head_sha="H", retrieved="2026-07-06",
        from_run_dir=prior,
    )
    entry = json.loads((run_dir / "documents" / "manifest.json").read_text())["files"][0]
    assert entry["carry_forward"] == {
        "from_run": "run-099-sdd", "prior_sha256": sha256_text("content of SDD-001")
    }


def test_snapshot_documents_from_run_missing_prior_doc_raises(tmp_path) -> None:
    sofia_root = _sofia_tree(tmp_path, ["SDD-001"])
    runs_root = tmp_path / "runs"
    prior = _build_prior_draw(
        runs_root, "run-099-sdd",
        substrate={"authorities": {"a": "A"}, "design-intent": {"d": "D"}},
        documents={"SDD-002": ("SDD-002-x.md", "other")},  # no SDD-001
    )
    with pytest.raises(PrepError):
        snapshot_documents(
            ["SDD-001"], docs_root=sofia_root / "docs", sofia_root=sofia_root,
            run_dir=runs_root / "run-100-sdd", run_id="run-100-sdd",
            sofia_head_sha="H", retrieved="t", from_run_dir=prior,
        )


def test_snapshot_documents_from_run_pin_mismatch_raises(tmp_path) -> None:
    sofia_root = _sofia_tree(tmp_path, ["SDD-001"])
    runs_root = tmp_path / "runs"
    prior = _build_prior_draw(
        runs_root, "run-099-sdd",
        substrate={"authorities": {"a": "A"}, "design-intent": {"d": "D"}},
        documents={"SDD-001": ("SDD-001-distilled.md", "DIFFERENT bytes")},  # pin differs
    )
    with pytest.raises(PrepError):
        snapshot_documents(
            ["SDD-001"], docs_root=sofia_root / "docs", sofia_root=sofia_root,
            run_dir=runs_root / "run-100-sdd", run_id="run-100-sdd",
            sofia_head_sha="H", retrieved="t", from_run_dir=prior,
        )


def test_snapshot_documents_from_run_without_document_manifest_raises(tmp_path) -> None:
    sofia_root = _sofia_tree(tmp_path, ["SDD-001"])
    runs_root = tmp_path / "runs"
    (runs_root / "run-099-sdd").mkdir(parents=True)  # a from_run dir with no documents/manifest
    with pytest.raises(PrepError):
        snapshot_documents(
            ["SDD-001"], docs_root=sofia_root / "docs", sofia_root=sofia_root,
            run_dir=runs_root / "run-100-sdd", run_id="run-100-sdd",
            sofia_head_sha="H", retrieved="t", from_run_dir=runs_root / "run-099-sdd",
        )


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
        documents={"SDD-001": ("SDD-001-x.md", "d")},
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
        documents={"SDD-001": ("SDD-001-x.md", "d")},
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
        documents={"SDD-001": ("SDD-001-distilled.md", "content of SDD-001")},
    )
    assert prior.is_dir()
    run_dir = prep_run(
        "run-100-sdd", ["SDD-001"], sofia_root=sofia_root, runs_root=runs_root,
        sofia_head_sha="HEAD2", retrieved="2026-07-06", from_run="run-099-sdd", recipe=_cf_recipe,
    )
    doc_entry = json.loads((run_dir / "documents" / "manifest.json").read_text())["files"][0]
    assert doc_entry["carry_forward"]["from_run"] == "run-099-sdd"


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
        json.dumps({"run_id": "run-100", "sofia_head_sha": "H", "from_run": None, "files": [
            {"doc_id": "SDD-001", "snapshot_path": "documents/SDD-001-x.md",
             "origin": {"source": "sofia-repo", "canonical_path": "docs/SDD-001-x.md"},
             "retrieved": "t", "sha256": sha256_text("body"), "carry_forward": None},
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
