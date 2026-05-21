#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import random
import re
import shutil
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Callable

TEXT_SUFFIXES = {".md", ".markdown", ".txt"}
NO_QMD_POLICIES = {"fail", "warn_and_continue", "continue_silent"}
SEED_CARD_REQUIRED = {
    "card_type",
    "seed_document",
    "core_summary",
    "core_claim",
    "core_concepts",
    "tensions",
    "mechanisms",
    "failure_modes",
    "questions_to_dream_on",
    "avoid_searching_for",
    "evidence_spans",
}
CONSTELLATION_REQUIRED = {
    "graph_type",
    "article",
    "seed_document",
    "nodes",
    "edges",
    "ranked_connections",
    "search_coverage",
}
ABSTRACTION_LEVELS = {"surface", "mechanism", "meta"}
DREAM_STRATEGIES = {
    "random_collision",
    "tag_bridge",
    "temporal_bridge",
    "same_problem_different_domain",
}
CONNECTION_KINDS = {
    "close_echo",
    "mechanism_match",
    "failure_rhyme",
    "bridge",
    "distant_echo",
    "contrast",
}

Chooser = Callable[[list[Path]], Path]
Runner = Callable[[list[str], Path], str]
_AUTO_QMD = object()


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        result = dispatch(args)
    except Exception as exc:
        print(str(exc), file=sys.stderr)
        return 1
    if result is not None:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="daydream")
    sub = parser.add_subparsers(dest="command", required=True)

    check = sub.add_parser("check")
    check.add_argument("--corpus", required=True)
    check.add_argument("--output-dir")
    check.add_argument("--scheduled", action="store_true")
    check.add_argument("--no-qmd-policy", default="fail")
    check.add_argument("--allow-json", action="store_true")

    seed = sub.add_parser("pick-seed")
    seed.add_argument("--corpus", required=True)
    seed.add_argument("--allow-json", action="store_true")

    search = sub.add_parser("search")
    search.add_argument("query")
    search.add_argument("--corpus", required=True)
    search.add_argument("--collection")
    search.add_argument("--allow-cross-collection", action="store_true")
    search.add_argument("--limit", type=int, default=12)
    search.add_argument("--no-rerank", action="store_true")
    search.add_argument("--no-gpu", action="store_true")

    validate_seed = sub.add_parser("validate-seed-card")
    validate_seed.add_argument("input")

    validate_graph = sub.add_parser("validate-constellation")
    validate_graph.add_argument("input")

    save = sub.add_parser("save-dream")
    save.add_argument("--article", required=True)
    save.add_argument("--seed-card", required=True)
    save.add_argument("--constellation", required=True)
    save.add_argument("--keywords", required=True)
    save.add_argument("--output-dir")
    return parser


def dispatch(args: argparse.Namespace) -> Any:
    if args.command == "check":
        return check_corpus(
            Path(args.corpus),
            output_dir=Path(args.output_dir) if args.output_dir else None,
            scheduled=args.scheduled,
            no_qmd_policy=args.no_qmd_policy,
            allow_json=args.allow_json,
        )
    if args.command == "pick-seed":
        return pick_seed(Path(args.corpus), allow_json=args.allow_json)
    if args.command == "search":
        return semantic_search(
            Path(args.corpus),
            args.query,
            collection=args.collection,
            allow_cross_collection=args.allow_cross_collection,
            limit=args.limit,
            no_rerank=args.no_rerank,
            no_gpu=args.no_gpu,
        )
    if args.command == "validate-seed-card":
        validate_seed_card(read_json(Path(args.input)))
        return {"valid": "seed_card", "path": str(Path(args.input))}
    if args.command == "validate-constellation":
        validate_constellation(read_json(Path(args.input)))
        return {"valid": "constellation", "path": str(Path(args.input))}
    if args.command == "save-dream":
        return save_dream_outputs(
            output_dir=Path(args.output_dir) if args.output_dir else default_output_dir(),
            article_path=Path(args.article),
            seed_card_path=Path(args.seed_card),
            constellation_path=Path(args.constellation),
            keywords=args.keywords,
        )
    raise ValueError(f"Unknown command: {args.command}")


def default_output_dir() -> Path:
    return Path(__file__).resolve().parents[1] / "output"


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

    resolved_output = _validate_output_dir(output_dir) if output_dir else None
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


def semantic_search(
    corpus: Path,
    query: str,
    *,
    collection: str | None = None,
    allow_cross_collection: bool = False,
    limit: int = 12,
    runner: Runner | None = None,
    no_rerank: bool = False,
    no_gpu: bool = False,
) -> list[dict[str, Any]]:
    if not collection and not allow_cross_collection:
        raise ValueError(
            "Search scope is ambiguous. Pass --collection <qmd collection> to stay inside the target corpus, "
            "or pass --allow-cross-collection intentionally."
        )
    args = ["qmd", "query", query, "--json", "-n", str(limit)]
    if collection:
        args.extend(["-c", collection])
    if no_rerank:
        args.append("--no-rerank")
    if no_gpu:
        args.append("--no-gpu")
    data = json.loads((runner or default_runner)(args, corpus) or "[]")
    if not isinstance(data, list):
        raise ValueError("qmd query did not return a JSON list")
    return [item for item in data if isinstance(item, dict)]


def default_runner(args: list[str], cwd: Path) -> str:
    completed = subprocess.run(args, cwd=cwd, text=True, capture_output=True, check=False)
    if completed.returncode != 0:
        raise RuntimeError(completed.stderr.strip() or completed.stdout.strip())
    return completed.stdout


def validate_seed_card(payload: dict[str, Any]) -> dict[str, Any]:
    missing = _missing(payload, SEED_CARD_REQUIRED)
    if missing:
        raise ValueError(f"Seed card missing required fields: {', '.join(missing)}")
    if payload["card_type"] != "dream_seed_card":
        raise ValueError("card_type must be dream_seed_card")

    _require_object_fields(payload["seed_document"], "seed_document", {"title", "path", "source_layer"})
    _require_non_empty_text(payload, "core_summary")
    _require_non_empty_text(payload, "core_claim")
    _require_non_empty_dict_list(payload, "core_concepts")
    _require_non_empty_dict_list(payload, "tensions")
    _require_non_empty_dict_list(payload, "mechanisms")
    _require_non_empty_dict_list(payload, "failure_modes")
    _require_non_empty_dict_list(payload, "questions_to_dream_on")
    _require_string_list(payload, "avoid_searching_for")
    _require_non_empty_text_list(payload, "evidence_spans")

    for concept in payload["core_concepts"]:
        _require_object_fields(
            concept,
            "core_concepts item",
            {"name", "meaning", "search_text", "keywords", "abstraction_level"},
        )
        _require_non_empty_text_list(concept, "search_text")
        _require_string_list(concept, "keywords")
        if concept["abstraction_level"] not in ABSTRACTION_LEVELS:
            raise ValueError("core_concepts item abstraction_level must be surface, mechanism, or meta")

    for tension in payload["tensions"]:
        _require_object_fields(tension, "tensions item", {"description", "why_it_matters"})

    for mechanism in payload["mechanisms"]:
        _require_object_fields(mechanism, "mechanisms item", {"name", "description", "search_text"})
        _require_non_empty_text_list(mechanism, "search_text")

    for failure_mode in payload["failure_modes"]:
        _require_object_fields(failure_mode, "failure_modes item", {"description", "search_text"})
        _require_non_empty_text_list(failure_mode, "search_text")

    for question in payload["questions_to_dream_on"]:
        _require_object_fields(question, "questions_to_dream_on item", {"question", "preferred_strategy"})
        if question["preferred_strategy"] not in DREAM_STRATEGIES:
            raise ValueError("questions_to_dream_on item preferred_strategy is unsupported")
    return payload


def validate_constellation(payload: dict[str, Any]) -> dict[str, Any]:
    missing = _missing(payload, CONSTELLATION_REQUIRED)
    if missing:
        raise ValueError(f"Constellation missing required fields: {', '.join(missing)}")
    if payload["graph_type"] != "daydream_constellation":
        raise ValueError("graph_type must be daydream_constellation")

    _require_object_fields(payload["article"], "article", {"title", "path", "thesis"})
    _require_object_fields(payload["seed_document"], "seed_document", {"title", "path", "source_layer"})
    _require_non_empty_dict_list(payload, "nodes")
    _require_non_empty_dict_list(payload, "edges")
    _require_non_empty_dict_list(payload, "ranked_connections")
    _require_object_fields(
        payload["search_coverage"],
        "search_coverage",
        {"connection_count", "documents_considered", "documents_used", "notes"},
    )

    node_ids: set[str] = set()
    for node in payload["nodes"]:
        _require_object_fields(node, "nodes item", {"id", "type"})
        node_id = str(node["id"])
        if not node_id:
            raise ValueError("nodes item id must not be empty")
        node_ids.add(node_id)
        if node["type"] == "document":
            _require_object_fields(node, "document node", {"title", "path", "source_layer", "role"})
        elif node["type"] == "concept":
            _require_object_fields(node, "concept node", {"label", "meaning", "abstraction_level"})
            if node["abstraction_level"] not in ABSTRACTION_LEVELS:
                raise ValueError("concept node abstraction_level must be surface, mechanism, or meta")
        elif node["type"] == "tension":
            _require_object_fields(node, "tension node", {"description", "why_it_matters"})
        elif node["type"] == "question":
            _require_object_fields(node, "question node", {"question", "preferred_strategy"})
            if node["preferred_strategy"] not in DREAM_STRATEGIES:
                raise ValueError("question node preferred_strategy is unsupported")
        else:
            raise ValueError("nodes item type must be document, concept, tension, or question")

    for edge in payload["edges"]:
        _require_object_fields(edge, "edges item", {"from", "to", "type", "strength", "reason", "evidence"})
        if edge["from"] not in node_ids or edge["to"] not in node_ids:
            raise ValueError("edges item references unknown node")
        _require_unit_number(edge, "strength")
        _require_non_empty_text_list(edge, "evidence")

    for connection in payload["ranked_connections"]:
        _require_object_fields(
            connection,
            "ranked_connections item",
            {
                "rank",
                "from_node",
                "to_node",
                "strength",
                "connection_name",
                "connection_kind",
                "why_it_matters",
                "why_not_topic_overlap",
                "used_in_article_section",
                "documents_involved",
            },
        )
        if connection["from_node"] not in node_ids or connection["to_node"] not in node_ids:
            raise ValueError("ranked_connections item references unknown node")
        _require_unit_number(connection, "strength")
        if connection["connection_kind"] not in CONNECTION_KINDS:
            raise ValueError("ranked_connections item connection_kind is unsupported")
        _require_optional_non_empty_text(connection, "used_in_article_section")
        _require_non_empty_text_list(connection, "documents_involved")
    return payload


def save_dream_outputs(
    output_dir: Path,
    article_path: Path,
    seed_card_path: Path,
    constellation_path: Path,
    keywords: str,
    completed_at: datetime | None = None,
) -> dict[str, str]:
    article = article_path.read_text(encoding="utf-8")
    seed_card = validate_seed_card(read_json(seed_card_path))
    constellation = validate_constellation(read_json(constellation_path))

    stamp = (completed_at or datetime.now()).strftime("%Y%m%d-%H%M%S")
    prefix = f"{stamp}-{slugify(keywords)}"
    dream_dir = ensure_dir(ensure_dir(output_dir) / prefix)
    article_out = dream_dir / f"{prefix}.md"
    seed_out = dream_dir / f"{prefix}.seed-card.json"
    constellation_out = dream_dir / f"{prefix}.constellation.json"

    article_out.write_text(article, encoding="utf-8")
    write_json(seed_out, seed_card)
    write_json(constellation_out, constellation)
    return {
        "article": str(article_out),
        "seed_card": str(seed_out),
        "constellation": str(constellation_out),
        "prefix": prefix,
        "dream_dir": str(dream_dir),
    }


def ensure_dir(path: Path) -> Path:
    path.mkdir(parents=True, exist_ok=True)
    return path


def read_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, dict):
        raise ValueError(f"Expected a JSON object in {path}")
    return data


def write_json(path: Path, payload: Any) -> None:
    ensure_dir(path.parent)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def slugify(value: str, fallback: str = "untitled") -> str:
    slug = re.sub(r"[^A-Za-z0-9._-]+", "-", value.strip()).strip("-._")
    return slug.lower() or fallback


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


def _validate_output_dir(output_dir: Path) -> Path:
    resolved = output_dir.expanduser().resolve()
    if resolved.exists():
        if not resolved.is_dir():
            raise ValueError(f"Output path is not a directory: {output_dir}")
        if not os.access(resolved, os.W_OK):
            raise ValueError(f"Output directory is not writable: {output_dir}")
        return resolved

    parent = resolved.parent
    if not parent.exists() or not parent.is_dir() or not os.access(parent, os.W_OK):
        raise ValueError(f"Output directory parent is not writable: {parent}")
    return resolved


def _missing(payload: dict[str, Any], required: set[str]) -> list[str]:
    return sorted(key for key in required if key not in payload)


def _require_list(payload: dict[str, Any], key: str) -> None:
    if not isinstance(payload.get(key), list) or not payload[key]:
        raise ValueError(f"{key} must be a non-empty list")


def _require_non_empty_dict_list(payload: dict[str, Any], key: str) -> None:
    _require_list(payload, key)
    if not all(isinstance(item, dict) for item in payload[key]):
        raise ValueError(f"{key} items must be objects")


def _require_non_empty_text(payload: dict[str, Any], key: str) -> None:
    value = payload.get(key)
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{key} must be a non-empty string")


def _require_non_empty_text_list(payload: dict[str, Any], key: str) -> None:
    _require_list(payload, key)
    if not all(isinstance(item, str) and item.strip() for item in payload[key]):
        raise ValueError(f"{key} must contain non-empty strings")


def _require_string_list(payload: dict[str, Any], key: str) -> None:
    value = payload.get(key)
    if not isinstance(value, list) or not all(isinstance(item, str) for item in value):
        raise ValueError(f"{key} must be a list of strings")


def _require_optional_non_empty_text(payload: dict[str, Any], key: str) -> None:
    value = payload.get(key)
    if value is not None and (not isinstance(value, str) or not value.strip()):
        raise ValueError(f"{key} must be a non-empty string or null")


def _require_object_fields(payload: Any, label: str, fields: set[str]) -> None:
    if not isinstance(payload, dict):
        raise ValueError(f"{label} must be an object")
    missing = _missing(payload, fields)
    if missing:
        raise ValueError(f"{label} missing required fields: {', '.join(missing)}")


def _require_unit_number(payload: dict[str, Any], key: str) -> None:
    value = payload.get(key)
    if not isinstance(value, int | float):
        raise ValueError(f"{key} must be a number")
    if value < 0 or value > 1:
        raise ValueError(f"{key} must be between 0 and 1")


if __name__ == "__main__":
    raise SystemExit(main())
