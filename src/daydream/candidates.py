from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .fs import write_json
from .qmd import Runner, default_runner
from .runs import resolve_run_dir, update_manifest


def build_candidate_pool(
    root: Path,
    queries: list[str],
    collection: str = "corpus",
    per_query_limit: int = 25,
    target_size: int = 50,
    runner: Runner = default_runner,
    no_rerank: bool = False,
) -> dict[str, Any]:
    candidates_by_file: dict[str, dict[str, Any]] = {}
    for query in queries:
        args = ["qmd", "query", query, "--json", "-n", str(per_query_limit), "-c", collection]
        if no_rerank:
            args.append("--no-rerank")
        data = json.loads(runner(args, root) or "[]")
        if not isinstance(data, list):
            raise ValueError("qmd query did not return a JSON list")
        for item in data:
            if not isinstance(item, dict):
                continue
            file_id = str(item.get("file", ""))
            if not file_id:
                continue
            current = candidates_by_file.get(file_id)
            if current is None or float(item.get("score", 0)) > float(current.get("score", 0)):
                enriched = dict(item)
                enriched["query"] = query
                candidates_by_file[file_id] = enriched

    candidates = sorted(candidates_by_file.values(), key=lambda item: float(item.get("score", 0)), reverse=True)
    candidates = candidates[:target_size]
    payload = {"queries": queries, "collection": collection, "candidates": candidates}
    run_path = resolve_run_dir(root, "latest")
    out = run_path / "candidate_pool.json"
    write_json(out, payload)
    update_manifest(root, "latest", artifacts={"candidate_pool": "candidate_pool.json"})
    return {"candidate_count": len(candidates), "saved": str(out)}
