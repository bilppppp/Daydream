from __future__ import annotations

from pathlib import Path
from typing import Any

from .fs import slugify, write_json
from .runs import resolve_run_dir, start_run, update_manifest


def dream_run(root: Path, collection: str = "corpus", limit: int = 25) -> dict[str, Any]:
    if limit <= 0:
        raise ValueError("limit must be greater than 0")
    docs = _select_documents(root, collection, limit)
    if not docs:
        raise ValueError(f"No markdown documents found for collection: {collection}")

    run = start_run(root, "dream-field")
    run_path = Path(run["run_dir"])
    payload = {
        "run_id": run["run_id"],
        "mode": "dream-field",
        "collection": collection,
        "limit": limit,
        "documents": docs,
    }
    out = run_path / "corpus_field.json"
    write_json(out, payload)
    update_manifest(
        root,
        run["run_id"],
        mode="dream-field",
        status="field_selected",
        artifacts={"corpus_field": "corpus_field.json"},
    )
    return {
        "run_id": run["run_id"],
        "mode": "dream-field",
        "document_count": len(docs),
        "corpus_field": str(out),
        "run_dir": str(run_path),
    }


def inspect_dream(root: Path, run: str = "latest") -> dict[str, Any]:
    run_path = resolve_run_dir(root, run)
    corpus_field = run_path / "corpus_field.json"
    document_count = 0
    collection = None
    if corpus_field.exists():
        import json

        payload = json.loads(corpus_field.read_text(encoding="utf-8"))
        document_count = len(payload.get("documents", []))
        collection = payload.get("collection")
    artifacts = {
        "corpus_field": corpus_field.exists(),
        "structure_cards": (run_path / "structure_cards.jsonl").exists(),
        "matrix_report": (run_path / "matrix_report.json").exists(),
        "edge_pruning_report": (run_path / "edge_pruning_report.json").exists(),
        "opponent_reports": (run_path / "opponent_reports.jsonl").exists(),
        "adjudication_reports": (run_path / "adjudication_reports.jsonl").exists(),
        "resonance_graph": (run_path / "resonance_graph.json").exists(),
        "cluster_reports": (run_path / "cluster_reports.json").exists(),
        "mesh_report": (run_path / "mesh_report.json").exists(),
        "mesh_draft": (run_path / "mesh_draft.md").exists(),
    }
    return {
        "run_id": run_path.name,
        "mode": "dream-field",
        "collection": collection,
        "document_count": document_count,
        "run_dir": str(run_path),
        "artifacts": artifacts,
    }


def _select_documents(root: Path, collection: str, limit: int) -> list[dict[str, Any]]:
    collection_dir = root / collection
    if not collection_dir.exists() or not collection_dir.is_dir():
        raise ValueError(f"Collection directory does not exist: {collection}")
    docs: list[dict[str, Any]] = []
    for path in sorted(collection_dir.glob("**/*.md"))[:limit]:
        relpath = path.relative_to(root)
        docs.append(
            {
                "doc_id": slugify(path.stem),
                "title": _extract_title(path),
                "path": str(relpath),
                "collection": collection,
                "source_type": "markdown",
            }
        )
    return docs


def _extract_title(path: Path) -> str:
    for line in path.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if stripped.startswith("#"):
            return stripped.lstrip("#").strip() or path.stem
    return path.stem
