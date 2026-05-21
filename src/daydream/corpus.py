from __future__ import annotations

import random
import shutil
from pathlib import Path
from typing import Any, Callable

TEXT_SUFFIXES = {".md", ".markdown", ".txt"}
NO_QMD_POLICIES = {"fail", "warn_and_continue", "continue_silent"}

Chooser = Callable[[list[Path]], Path]
_AUTO_QMD = object()


def check_corpus(
    corpus: Path,
    output_dir: Path | None = None,
    *,
    qmd_path: str | None | object = _AUTO_QMD,
    scheduled: bool = False,
    no_qmd_policy: str = "fail",
    allow_json: bool = False,
) -> dict[str, Any]:
    corpus = _require_corpus_dir(corpus)
    if scheduled and no_qmd_policy not in NO_QMD_POLICIES:
        raise ValueError("no_qmd_policy must be fail, warn_and_continue, or continue_silent")

    seeds = eligible_seed_paths(corpus, allow_json=allow_json)
    if not seeds:
        raise ValueError("Corpus does not contain an eligible seed document")

    resolved_output = output_dir.resolve() if output_dir else None
    detected_qmd = shutil.which("qmd") if qmd_path is _AUTO_QMD else qmd_path
    return {
        "corpus": str(corpus),
        "eligible_seed_count": len(seeds),
        "qmd": {"available": bool(detected_qmd), "path": detected_qmd},
        "scheduled": scheduled,
        "no_qmd_policy": no_qmd_policy if scheduled else None,
        "output_dir": str(resolved_output) if resolved_output else None,
    }


def pick_seed(
    corpus: Path,
    *,
    allow_json: bool = False,
    chooser: Chooser | None = None,
) -> dict[str, Any]:
    corpus = _require_corpus_dir(corpus)
    paths = eligible_seed_paths(corpus, allow_json=allow_json)
    if not paths:
        raise ValueError("Corpus does not contain an eligible seed document")
    selected = (chooser or random.choice)(paths)
    if selected not in paths:
        raise ValueError("Seed chooser returned a document outside the eligible corpus set")
    return {
        "path": str(selected.resolve()),
        "title": extract_title(selected),
        "source_layer": selected.parent.name if selected.parent != corpus else "corpus",
    }


def eligible_seed_paths(corpus: Path, allow_json: bool = False) -> list[Path]:
    corpus = _require_corpus_dir(corpus)
    paths: list[Path] = []
    for path in sorted(corpus.rglob("*")):
        if not path.is_file() or _under_output_dir(path, corpus):
            continue
        if _is_readme(path):
            continue
        if not _has_seed_suffix(path, allow_json):
            continue
        try:
            text = path.read_text(encoding="utf-8").strip()
        except UnicodeDecodeError:
            continue
        if len(text) < 24 or _looks_like_link_list(text):
            continue
        paths.append(path)
    return paths


def extract_title(path: Path) -> str:
    if path.suffix.lower() in {".md", ".markdown"}:
        try:
            for line in path.read_text(encoding="utf-8").splitlines():
                stripped = line.strip()
                if stripped.startswith("#"):
                    return stripped.lstrip("#").strip() or path.stem
        except UnicodeDecodeError:
            pass
    return path.stem


def _require_corpus_dir(corpus: Path) -> Path:
    resolved = corpus.expanduser().resolve()
    if not resolved.exists() or not resolved.is_dir():
        raise ValueError(f"Corpus path is not a readable directory: {corpus}")
    return resolved


def _under_output_dir(path: Path, corpus: Path) -> bool:
    return "output" in path.relative_to(corpus).parts


def _is_readme(path: Path) -> bool:
    return path.stem.lower().startswith("readme")


def _has_seed_suffix(path: Path, allow_json: bool) -> bool:
    suffix = path.suffix.lower()
    return suffix in TEXT_SUFFIXES or (allow_json and suffix == ".json")


def _looks_like_link_list(text: str) -> bool:
    lines = [line.strip() for line in text.splitlines() if line.strip() and not line.strip().startswith("#")]
    if not lines:
        return True
    link_lines = 0
    for line in lines:
        list_like = line.startswith(("-", "*", "+")) or line[:2].rstrip(".").isdigit()
        if list_like and ("http://" in line or "https://" in line):
            link_lines += 1
    return link_lines == len(lines)
