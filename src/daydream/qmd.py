from __future__ import annotations

import json
import subprocess
from pathlib import Path
from typing import Any, Callable

Runner = Callable[[list[str], Path], str]


def default_runner(args: list[str], cwd: Path) -> str:
    completed = subprocess.run(args, cwd=cwd, text=True, capture_output=True, check=False)
    if completed.returncode != 0:
        raise RuntimeError(completed.stderr.strip() or completed.stdout.strip())
    return completed.stdout


def semantic_search(
    corpus: Path,
    query: str,
    *,
    collection: str | None = None,
    limit: int = 12,
    runner: Runner = default_runner,
    no_rerank: bool = False,
) -> list[dict[str, Any]]:
    args = ["qmd", "query", query, "--json", "-n", str(limit)]
    if collection:
        args.extend(["-c", collection])
    if no_rerank:
        args.append("--no-rerank")
    data = json.loads(runner(args, corpus) or "[]")
    if not isinstance(data, list):
        raise ValueError("qmd query did not return a JSON list")
    return [item for item in data if isinstance(item, dict)]
