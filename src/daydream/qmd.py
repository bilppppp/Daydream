from __future__ import annotations

import json
import subprocess
from pathlib import Path
from typing import Any, Callable

from .fs import write_json
from .runs import resolve_run_dir, update_manifest

Runner = Callable[[list[str], Path], str]


def default_runner(args: list[str], cwd: Path) -> str:
    completed = subprocess.run(args, cwd=cwd, text=True, capture_output=True, check=False)
    if completed.returncode != 0:
        raise RuntimeError(completed.stderr.strip() or completed.stdout.strip())
    return completed.stdout


def qmd_query(
    root: Path,
    query: str,
    collection: str = "corpus",
    limit: int = 12,
    runner: Runner = default_runner,
    no_rerank: bool = False,
) -> list[dict[str, Any]]:
    args = ["qmd", "query", query, "--json", "-n", str(limit)]
    if collection:
        args.extend(["-c", collection])
    if no_rerank:
        args.append("--no-rerank")
    output = runner(args, root)
    data = json.loads(output or "[]")
    if not isinstance(data, list):
        raise ValueError("qmd query did not return a JSON list")
    run_path = resolve_run_dir(root, "latest")
    out = run_path / "qmd_results.json"
    write_json(out, data)
    update_manifest(root, "latest", artifacts={"qmd_results": "qmd_results.json"})
    return data


def index_workspace(root: Path, runner: Runner = default_runner) -> dict[str, Any]:
    messages: list[str] = []
    if not (root / ".qmd").exists():
        messages.append(runner(["qmd", "init"], root).strip())
    for name in ["corpus", "cards"]:
        path = root / name
        if path.exists():
            try:
                messages.append(runner(["qmd", "collection", "add", str(path), "--name", name], root).strip())
            except RuntimeError as exc:
                if "already" not in str(exc).lower():
                    raise
    messages.append(runner(["qmd", "update"], root).strip())
    return {"indexed": True, "messages": [msg for msg in messages if msg]}
