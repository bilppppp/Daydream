from __future__ import annotations

from collections import Counter
from datetime import datetime
from pathlib import Path
from typing import Any

from .fs import ensure_dir, read_json, write_json

STRATEGIES = ("random-collision", "tag-bridge", "temporal-bridge")
SPECIAL_RUN_MODES = {"dream-field"}


def runs_dir(root: Path) -> Path:
    return root / "runs"


def latest_pointer(root: Path) -> Path:
    return runs_dir(root) / "latest"


def resolve_run_dir(root: Path, run: str) -> Path:
    if run == "latest":
        pointer = latest_pointer(root)
        if pointer.is_symlink():
            return pointer.resolve()
        if pointer.is_file():
            return runs_dir(root) / pointer.read_text(encoding="utf-8").strip()
        if pointer.is_dir():
            return pointer
        raise FileNotFoundError("No latest run exists")
    return runs_dir(root) / run


def start_run(root: Path, strategy: str = "auto") -> dict[str, Any]:
    ensure_dir(runs_dir(root))
    selected = choose_strategy(root) if strategy == "auto" else strategy
    if selected not in STRATEGIES and selected not in SPECIAL_RUN_MODES:
        raise ValueError(f"Unknown strategy: {selected}")

    created_at = datetime.now().astimezone().isoformat(timespec="seconds")
    run_id = datetime.now().strftime("%Y-%m-%d_%H%M%S_%f")
    run_path = runs_dir(root) / run_id
    ensure_dir(run_path)
    manifest = {
        "run_id": run_id,
        "strategy": selected,
        "created_at": created_at,
        "status": "started",
        "artifacts": {},
    }
    write_json(run_path / "manifest.json", manifest)
    update_latest(root, run_id)
    return {"run_id": run_id, "strategy": selected, "run_dir": str(run_path)}


def choose_strategy(root: Path) -> str:
    counts: Counter[str] = Counter()
    if runs_dir(root).exists():
        for manifest_path in runs_dir(root).glob("*/manifest.json"):
            try:
                strategy = read_json(manifest_path).get("strategy")
            except Exception:
                continue
            if strategy in STRATEGIES:
                counts[strategy] += 1
    return min(STRATEGIES, key=lambda item: (counts[item], STRATEGIES.index(item)))


def update_latest(root: Path, run_id: str) -> None:
    pointer = latest_pointer(root)
    ensure_dir(pointer.parent)
    if pointer.exists() or pointer.is_symlink():
        if pointer.is_dir() and not pointer.is_symlink():
            raise IsADirectoryError(f"latest pointer is a directory: {pointer}")
        pointer.unlink()
    target = runs_dir(root) / run_id
    try:
        pointer.symlink_to(target, target_is_directory=True)
    except OSError:
        pointer.write_text(run_id, encoding="utf-8")


def update_manifest(root: Path, run: str, **updates: Any) -> dict[str, Any]:
    run_path = resolve_run_dir(root, run)
    manifest_path = run_path / "manifest.json"
    manifest = read_json(manifest_path)
    artifacts = updates.pop("artifacts", None)
    manifest.update(updates)
    if artifacts:
        manifest.setdefault("artifacts", {}).update(artifacts)
    write_json(manifest_path, manifest)
    return manifest


def inspect_run(root: Path, run: str = "latest") -> dict[str, Any]:
    run_path = resolve_run_dir(root, run)
    manifest = read_json(run_path / "manifest.json")
    artifacts = {
        "qmd_results": (run_path / "qmd_results.json").exists(),
        "candidate_pool": (run_path / "candidate_pool.json").exists(),
        "cards": (run_path / "cards.jsonl").exists(),
        "pair_report": (run_path / "pair_report.json").exists(),
        "critic_report": (run_path / "critic_report.json").exists(),
        "constellation_report": (run_path / "constellation_report.json").exists(),
        "draft": (run_path / "draft.md").exists(),
        "rejection_report": (run_path / "rejection_report.md").exists(),
    }
    return {
        "run_id": manifest.get("run_id"),
        "strategy": manifest.get("strategy"),
        "status": manifest.get("status", "unknown"),
        "created_at": manifest.get("created_at"),
        "run_dir": str(run_path),
        "artifacts": artifacts,
    }
