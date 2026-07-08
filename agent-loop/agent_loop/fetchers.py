# Module: agent_loop.fetchers
# Purpose: Real DocumentFetcher and SubstrateFetcher for supervised runs
#          (run-prep.contract.md §2, §3). Documents are read per-pass from the
#          run's FROZEN document snapshot (`runs/<run-id>/documents/`, amended
#          2026-07-06 / RBT-51 Item 3 — never the working tree); substrate is
#          per-run frozen, read fresh each pass from the run folder. Both
#          fetchers only READ — they never assemble, edit, truncate, or annotate.
#          Snapshot and substrate (and their manifests) are produced at prep by
#          the prep tool (RBT-52) and verified/validated here.
# Scope:   Filesystem reads + a substrate-manifest validator. No LLM, no network,
#          no git. Fetchers fill the existing DocumentFetcher/SubstrateFetcher
#          ports (signatures unchanged, run-prep §9).

from __future__ import annotations

import hashlib
import json
from pathlib import Path

from agent_loop.reviewers import DocumentSet, Substrate


class DocumentResolutionError(RuntimeError):
    """A doc-id did not resolve to exactly one file under the docs root."""


class SubstrateError(RuntimeError):
    """The run substrate is missing, empty, or its manifest fails validation."""


class DocumentSnapshotError(RuntimeError):
    """The per-run document snapshot is missing, empty, or fails hash verification.

    Raised by the snapshot verifier (run-prep.contract.md §8 gate 8, amended
    2026-07-06 / RBT-51 Item 3): the runner consumes `runs/<run-id>/documents/`
    and must fail loud on absence or any mismatch against the prep-written
    provenance record, never falling back to the working tree.
    """


# --- §2: document fetcher ----------------------------------------------------


class RepoDocumentFetcher:
    """Resolve doc-ids to files in the run's frozen document snapshot, verbatim.

    Resolution is a prefix glob `<snapshot_root>/**/<doc-id>-*.md`; zero or more
    than one match raises immediately, naming the doc-id and the matches (no
    fallback, no fuzzy matching). Content is returned verbatim. Invoked per pass
    by the runner, reading `runs/<run-id>/documents/` each time (amended
    2026-07-06 / RBT-51 Item 3): entry provenance is immutable and, in dry mode,
    the snapshot never changes mid-run; the per-pass read is kept because in live
    mode the author's changes land in the run's own document home. Working-tree
    resolution now lives in the prep tool (RBT-52), never here.
    """

    def __init__(self, snapshot_root: str | Path) -> None:
        """Bind the fetcher to the run's document snapshot root (no hardcoded paths)."""
        self._docs_root = Path(snapshot_root)

    def resolve(self, doc_id: str) -> Path:
        """Return the single file matching `doc_id`, or raise on 0/>1 matches."""
        matches = sorted(self._docs_root.glob(f"**/{doc_id}-*.md"))
        if len(matches) != 1:
            raise DocumentResolutionError(
                f"doc-id {doc_id!r} resolved to {len(matches)} files under "
                f"{self._docs_root} (expected exactly 1): "
                f"{[str(m) for m in matches]}"
            )
        return matches[0]

    def __call__(self, doc_ids: list[str]) -> DocumentSet:
        """Fetch each doc-id's file content verbatim, keyed by doc-id."""
        documents: dict[str, str] = {}
        for doc_id in doc_ids:
            path = self.resolve(doc_id)
            documents[doc_id] = path.read_text(encoding="utf-8")
        return DocumentSet(documents=documents)


# --- §3: substrate fetcher + manifest validation -----------------------------

_SUBSTRATE_CATEGORIES = ("authorities", "design-intent")


def _read_category(category_dir: Path) -> dict[str, str]:
    """Read every `*.md` in a substrate category dir, keyed by filename stem."""
    if not category_dir.is_dir():
        return {}
    return {
        path.stem: path.read_text(encoding="utf-8")
        for path in sorted(category_dir.glob("*.md"))
    }


class RunSubstrateFetcher:
    """Read a run's frozen substrate folder fresh each pass.

    Returns `Substrate(authorities={stem: content}, design_intent={stem:
    content})`. The `doc_ids` argument is accepted (port signature unchanged) and
    ignored — substrate scope is per-run, not per-doc. An empty or missing
    substrate folder raises at first fetch: a real run with empty substrate is a
    prep failure, not a degraded mode (empty authorities collapses SA = Solution
    Architect into internal-correctness review and corrupts the SA/coherence
    overlap evidence; empty design-intent starves the arbiter's exit-path
    judgment).
    """

    def __init__(self, substrate_root: str | Path) -> None:
        """Bind the fetcher to a run's `substrate/` folder."""
        self._root = Path(substrate_root)

    def __call__(self, doc_ids: list[str]) -> Substrate:
        """Read substrate fresh; raise if missing or empty."""
        if not self._root.is_dir():
            raise SubstrateError(f"substrate folder missing: {self._root}")
        authorities = _read_category(self._root / "authorities")
        design_intent = _read_category(self._root / "design-intent")
        if not authorities:
            raise SubstrateError(
                f"substrate authorities are empty under {self._root} — a real "
                "run with empty substrate is a prep failure"
            )
        if not design_intent:
            raise SubstrateError(
                f"substrate design-intent is empty under {self._root} — a real "
                "run with empty substrate is a prep failure"
            )
        return Substrate(authorities=authorities, design_intent=design_intent)


def sha256_text(text: str) -> str:
    """Return the hex SHA-256 of `text` (UTF-8)."""
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def validate_substrate_manifest(substrate_root: str | Path) -> None:
    """Validate a run's `substrate/manifest.json` against the files on disk.

    Checks (run-prep §3 / prep gate 4), raising SubstrateError on any failure:
      - the manifest exists and is a JSON object with a `files` list;
      - each entry has logical_id, category (in the two categories), origin,
        retrieved, and sha256, and its file exists with a matching content hash;
      - every `*.md` under authorities/ and design-intent/ is listed exactly
        once (no unlisted files, no manifest entries without a file).

    Args:
        substrate_root: The run's `substrate/` folder.

    Raises:
        SubstrateError: On any missing/mismatched/unlisted condition.
    """
    root = Path(substrate_root)
    manifest_path = root / "manifest.json"
    if not manifest_path.is_file():
        raise SubstrateError(f"substrate manifest missing: {manifest_path}")
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise SubstrateError(f"substrate manifest is not valid JSON: {exc}") from exc
    if not isinstance(manifest, dict) or not isinstance(manifest.get("files"), list):
        raise SubstrateError("substrate manifest must be an object with a 'files' list")

    listed_paths: set[Path] = set()
    for entry in manifest["files"]:
        for field_name in ("logical_id", "category", "origin", "retrieved", "sha256"):
            if field_name not in entry:
                raise SubstrateError(
                    f"substrate manifest entry missing '{field_name}': {entry}"
                )
        category = entry["category"]
        if category not in _SUBSTRATE_CATEGORIES:
            raise SubstrateError(
                f"substrate manifest entry has invalid category {category!r}: {entry}"
            )
        file_path = root / category / f"{entry['logical_id']}.md"
        if not file_path.is_file():
            raise SubstrateError(f"substrate manifest lists a missing file: {file_path}")
        actual = sha256_text(file_path.read_text(encoding="utf-8"))
        if actual != entry["sha256"]:
            raise SubstrateError(
                f"substrate manifest sha256 mismatch for {file_path}: "
                f"recorded {entry['sha256']}, actual {actual}"
            )
        listed_paths.add(file_path.resolve())

    on_disk = {
        path.resolve()
        for category in _SUBSTRATE_CATEGORIES
        for path in (root / category).glob("*.md")
    }
    unlisted = on_disk - listed_paths
    if unlisted:
        raise SubstrateError(
            f"substrate files not covered by manifest: {sorted(str(p) for p in unlisted)}"
        )


# --- §8 gate 8 / T7: document-snapshot verification --------------------------

_DOCUMENT_ENTRY_FIELDS = ("doc_id", "snapshot_path", "origin", "retrieved", "sha256")


def verify_document_snapshot(run_dir: str | Path) -> None:
    """Verify a run's frozen document snapshot against its provenance record.

    The runner's launch-time check (run-prep.contract.md §8 gate 8, amended
    2026-07-06 / RBT-51 Item 3): `runs/<run-id>/documents/` is present and
    non-empty, its `documents/manifest.json` provenance record lists every
    snapshot file, and every listed file's SHA-256 (validator-method — text via
    `read_text().encode()`) matches the recorded pin. Any absence or mismatch
    raises — the runner never falls back to the working tree.

    Args:
        run_dir: The run folder (`runs/<run-id>/`).

    Raises:
        DocumentSnapshotError: On a missing/empty snapshot, a missing or
            malformed provenance record, a listed-but-absent file, a hash
            mismatch, or an on-disk file not covered by the record.
    """
    documents_root = Path(run_dir) / "documents"
    if not documents_root.is_dir():
        raise DocumentSnapshotError(f"document snapshot folder missing: {documents_root}")

    manifest_path = documents_root / "manifest.json"
    if not manifest_path.is_file():
        raise DocumentSnapshotError(f"document snapshot manifest missing: {manifest_path}")
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise DocumentSnapshotError(
            f"document snapshot manifest is not valid JSON: {exc}"
        ) from exc
    if not isinstance(manifest, dict) or not isinstance(manifest.get("files"), list):
        raise DocumentSnapshotError(
            "document snapshot manifest must be an object with a 'files' list"
        )
    if not manifest["files"]:
        raise DocumentSnapshotError(
            f"document snapshot is empty (no files recorded): {manifest_path}"
        )

    listed_paths: set[Path] = set()
    for entry in manifest["files"]:
        for field_name in _DOCUMENT_ENTRY_FIELDS:
            if field_name not in entry:
                raise DocumentSnapshotError(
                    f"document snapshot entry missing '{field_name}': {entry}"
                )
        file_path = Path(run_dir) / entry["snapshot_path"]
        if not file_path.is_file():
            raise DocumentSnapshotError(
                f"document snapshot manifest lists a missing file: {file_path}"
            )
        actual = sha256_text(file_path.read_text(encoding="utf-8"))
        if actual != entry["sha256"]:
            raise DocumentSnapshotError(
                f"document snapshot sha256 mismatch for {file_path}: "
                f"recorded {entry['sha256']}, actual {actual}"
            )
        listed_paths.add(file_path.resolve())

    on_disk = {path.resolve() for path in documents_root.glob("*.md")}
    unlisted = on_disk - listed_paths
    if unlisted:
        raise DocumentSnapshotError(
            f"document snapshot files not covered by manifest: "
            f"{sorted(str(p) for p in unlisted)}"
        )
