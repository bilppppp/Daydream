#!/usr/bin/env python3
from __future__ import annotations

import argparse
import contextlib
import csv
import fcntl
import hashlib
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
QMD_RECOVERY_POLICIES = {"auto", "off"}
RUN_LEDGER_FIELDS = [
    "run_id",
    "started_at",
    "ended_at",
    "status",
    "trigger",
    "dream_dir",
    "article_path",
    "seed_card_path",
    "constellation_path",
]
RUN_STATUSES = {"running", "success", "failed", "cancelled"}
RUN_FINISH_STATUSES = {"success", "failed", "cancelled"}
RUN_TRIGGERS = {"manual", "cron", "host", "unknown"}
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
Runner = Callable[[list[str], Path, dict[str, str] | None], str]
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
    check.add_argument("--collection")
    check.add_argument("--qmd-probe-query")
    check.add_argument("--env-file")
    check.add_argument("--no-rerank", action="store_true")
    check.add_argument("--no-gpu", action="store_true")
    check.add_argument("--recovery", choices=sorted(QMD_RECOVERY_POLICIES), default="auto")

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
    search.add_argument("--env-file")
    search.add_argument("--recovery", choices=sorted(QMD_RECOVERY_POLICIES), default="auto")

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
    save.add_argument("--run-id")

    runs = sub.add_parser("runs")
    runs_sub = runs.add_subparsers(dest="runs_command", required=True)

    runs_start = runs_sub.add_parser("start")
    runs_start.add_argument("--trigger", choices=sorted(RUN_TRIGGERS), default="manual")
    runs_start.add_argument("--output-dir")

    runs_finish = runs_sub.add_parser("finish")
    runs_finish.add_argument("--run-id", required=True)
    runs_finish.add_argument("--status", choices=sorted(RUN_FINISH_STATUSES), required=True)

    runs_list = runs_sub.add_parser("list")
    runs_list.add_argument("--status", choices=sorted(RUN_STATUSES))
    runs_list.add_argument("--limit", type=int)
    runs_list.add_argument("--json", action="store_true")
    return parser


def dispatch(args: argparse.Namespace) -> Any:
    if args.command == "check":
        return check_corpus(
            Path(args.corpus),
            output_dir=Path(args.output_dir) if args.output_dir else None,
            scheduled=args.scheduled,
            no_qmd_policy=args.no_qmd_policy,
            allow_json=args.allow_json,
            qmd_collection=args.collection,
            qmd_probe_query=args.qmd_probe_query,
            qmd_env=qmd_env_from_file(Path(args.env_file)) if args.env_file else None,
            no_rerank=args.no_rerank,
            no_gpu=args.no_gpu,
            recovery=args.recovery,
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
            qmd_env=qmd_env_from_file(Path(args.env_file)) if args.env_file else None,
            recovery=args.recovery,
        )
    if args.command == "validate-seed-card":
        validate_seed_card(read_json(Path(args.input)))
        return {"valid": "seed_card", "path": str(Path(args.input))}
    if args.command == "validate-constellation":
        validate_constellation(read_json(Path(args.input)))
        return {"valid": "constellation", "path": str(Path(args.input))}
    if args.command == "save-dream":
        return save_dream_outputs(
            output_dir=Path(args.output_dir) if args.output_dir else None,
            article_path=Path(args.article),
            seed_card_path=Path(args.seed_card),
            constellation_path=Path(args.constellation),
            keywords=args.keywords,
            run_id=args.run_id,
        )
    if args.command == "runs":
        if args.runs_command == "start":
            return start_run(
                trigger=args.trigger,
                output_dir=Path(args.output_dir) if args.output_dir else None,
            )
        if args.runs_command == "finish":
            return finish_run(args.run_id, args.status)
        if args.runs_command == "list":
            return list_runs(status=args.status, limit=args.limit)
    raise ValueError(f"Unknown command: {args.command}")


def skill_dir() -> Path:
    return Path(__file__).resolve().parents[1]


def default_output_dir() -> Path:
    return skill_dir() / "output"


def default_ledger_path() -> Path:
    return default_output_dir() / "daydream-runs.csv"


def start_run(
    *,
    trigger: str = "manual",
    output_dir: Path | None = None,
    ledger_path: Path | None = None,
    started_at: datetime | None = None,
    run_id: str | None = None,
) -> dict[str, str]:
    if trigger not in RUN_TRIGGERS:
        raise ValueError("trigger must be manual, cron, host, or unknown")

    started_at_text = _iso_time(started_at)
    run_id = run_id or _generate_run_id(started_at_text)
    output_root = ensure_dir(output_dir or default_output_dir())
    paths = _paths_for_run(output_root, f"{_stamp_from_iso(started_at_text)}-{run_id}")
    row = {
        "run_id": run_id,
        "started_at": started_at_text,
        "ended_at": "",
        "status": "running",
        "trigger": trigger,
        **paths,
    }
    _append_ledger_row(ledger_path or default_ledger_path(), row)
    return {"run_id": run_id, **paths}


def finish_run(
    run_id: str,
    status: str,
    *,
    ledger_path: Path | None = None,
    ended_at: datetime | None = None,
    path_updates: dict[str, str] | None = None,
) -> dict[str, Any]:
    if status not in RUN_FINISH_STATUSES:
        raise ValueError("status must be success, failed, or cancelled")

    ledger = ledger_path or default_ledger_path()
    with _ledger_lock(ledger):
        rows = _read_ledger_rows(ledger)
        found = False
        updated_row: dict[str, str] | None = None
        for row in rows:
            if row["run_id"] != run_id:
                continue
            found = True
            row["status"] = status
            row["ended_at"] = _iso_time(ended_at)
            if path_updates:
                for field in ("dream_dir", "article_path", "seed_card_path", "constellation_path"):
                    if field in path_updates:
                        row[field] = str(path_updates[field])
            updated_row = row
            break
        if not found or updated_row is None:
            raise ValueError(f"Run id not found in ledger: {run_id}")

        _write_ledger_rows(ledger, rows)
    return {"run": updated_row}


def list_runs(
    *,
    status: str | None = None,
    limit: int | None = None,
    ledger_path: Path | None = None,
) -> dict[str, list[dict[str, str]]]:
    if status is not None and status not in RUN_STATUSES:
        raise ValueError("status must be running, success, failed, or cancelled")
    if limit is not None and limit < 0:
        raise ValueError("limit must not be negative")

    rows = _read_ledger_rows(ledger_path or default_ledger_path())
    if status is not None:
        rows = [row for row in rows if row["status"] == status]
    rows.sort(key=lambda row: _started_sort_value(row["started_at"]), reverse=True)
    if limit is not None:
        rows = rows[:limit]
    return {"runs": rows}


def check_corpus(
    corpus: Path,
    output_dir: Path | None = None,
    *,
    qmd_path: str | None | object = _AUTO_QMD,
    scheduled: bool = False,
    no_qmd_policy: str = "fail",
    allow_json: bool = False,
    qmd_collection: str | None = None,
    qmd_probe_query: str | None = None,
    qmd_env: dict[str, str] | None = None,
    qmd_runner: Runner | None = None,
    no_rerank: bool = False,
    no_gpu: bool = False,
    recovery: str = "auto",
) -> dict[str, Any]:
    corpus = _require_corpus_dir(corpus)
    if scheduled and no_qmd_policy not in NO_QMD_POLICIES:
        raise ValueError("no_qmd_policy must be fail, warn_and_continue, or continue_silent")

    seeds = eligible_seed_paths(corpus, allow_json=allow_json)
    if not seeds:
        raise ValueError("Corpus does not contain an eligible seed document")

    resolved_output = _validate_output_dir(output_dir) if output_dir else None
    qmd_path_env = (qmd_env or os.environ).get("PATH")
    detected_qmd = shutil.which("qmd", path=qmd_path_env) if qmd_path is _AUTO_QMD else qmd_path
    qmd_probe = _check_qmd_probe(
        corpus,
        qmd_path=detected_qmd,
        collection=qmd_collection,
        query=qmd_probe_query,
        qmd_env=qmd_env,
        runner=qmd_runner,
        no_rerank=no_rerank,
        no_gpu=no_gpu,
        recovery=recovery,
    )
    return {
        "corpus": str(corpus),
        "eligible_seed_count": len(seeds),
        "qmd": {"available": bool(detected_qmd), "path": detected_qmd, "probe": qmd_probe},
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
    qmd_env: dict[str, str] | None = None,
    recovery: str = "auto",
) -> list[dict[str, Any]]:
    if not collection and not allow_cross_collection:
        raise ValueError(
            "Search scope is ambiguous. Pass --collection <qmd collection> to stay inside the target corpus, "
            "or pass --allow-cross-collection intentionally."
        )
    if recovery not in QMD_RECOVERY_POLICIES:
        raise ValueError("recovery must be auto or off")

    attempts = [_qmd_search_args("query", query, collection, limit, no_rerank=no_rerank, no_gpu=no_gpu)]
    if recovery == "auto":
        if not no_gpu:
            attempts.append(_qmd_search_args("query", query, collection, limit, no_rerank=no_rerank, no_gpu=True))
        attempts.append(_qmd_search_args("vsearch", query, collection, limit, no_rerank=False, no_gpu=True))

    failures: list[str] = []
    for args in attempts:
        try:
            data = json.loads((runner or default_runner)(args, corpus, qmd_env) or "[]")
        except RuntimeError as exc:
            failures.append(f"{args[1]}: {exc}")
            continue
        if not isinstance(data, list):
            raise ValueError(f"qmd {args[1]} did not return a JSON list")
        return [item for item in data if isinstance(item, dict)]

    raise RuntimeError("qmd semantic search failed after recovery attempts: " + " | ".join(failures))


def default_runner(args: list[str], cwd: Path, env: dict[str, str] | None = None) -> str:
    completed = subprocess.run(args, cwd=cwd, env=env, text=True, capture_output=True, check=False)
    if completed.returncode != 0:
        raise RuntimeError(completed.stderr.strip() or completed.stdout.strip())
    return completed.stdout


def qmd_env_from_file(path: Path, base_env: dict[str, str] | None = None) -> dict[str, str]:
    env = dict(os.environ if base_env is None else base_env)
    for line_number, raw_line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        if line.startswith("export "):
            line = line.removeprefix("export ").strip()
        if "=" not in line:
            raise ValueError(f"Invalid env line {line_number} in {path}: expected KEY=VALUE")
        key, value = line.split("=", 1)
        key = key.strip()
        if not key or not re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", key):
            raise ValueError(f"Invalid env key on line {line_number} in {path}: {key}")
        env[key] = value.strip().strip("\"'")
    return env


def _check_qmd_probe(
    corpus: Path,
    *,
    qmd_path: str | None,
    collection: str | None,
    query: str | None,
    qmd_env: dict[str, str] | None,
    runner: Runner | None,
    no_rerank: bool,
    no_gpu: bool,
    recovery: str,
) -> dict[str, Any]:
    if not query:
        return {
            "status": "not_run",
            "reason": "Pass --collection and --qmd-probe-query to run a real collection-scoped qmd search.",
        }
    if not collection:
        raise ValueError("--qmd-probe-query requires --collection")
    if not qmd_path:
        return {"status": "failed", "error": "qmd binary was not found"}

    try:
        results = semantic_search(
            corpus,
            query,
            collection=collection,
            limit=1,
            runner=runner,
            no_rerank=no_rerank,
            no_gpu=no_gpu,
            qmd_env=qmd_env,
            recovery=recovery,
        )
    except Exception as exc:
        return {"status": "failed", "error": str(exc)}
    return {"status": "passed", "collection": collection, "result_count": len(results)}


def _qmd_search_args(
    mode: str,
    query: str,
    collection: str | None,
    limit: int,
    *,
    no_rerank: bool,
    no_gpu: bool,
) -> list[str]:
    args = ["qmd", mode, query, "--json", "-n", str(limit)]
    if collection:
        args.extend(["-c", collection])
    if no_rerank and mode == "query":
        args.append("--no-rerank")
    if no_gpu:
        args.append("--no-gpu")
    return args


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
    output_dir: Path | None,
    article_path: Path,
    seed_card_path: Path,
    constellation_path: Path,
    keywords: str,
    completed_at: datetime | None = None,
    run_id: str | None = None,
    ledger_path: Path | None = None,
) -> dict[str, str]:
    article = article_path.read_text(encoding="utf-8")
    seed_card = validate_seed_card(read_json(seed_card_path))
    constellation = validate_constellation(read_json(constellation_path))

    ledger = ledger_path or default_ledger_path()
    if run_id:
        run_row = _find_ledger_row(ledger, run_id)
        output_root = output_dir if output_dir else Path(run_row["dream_dir"]).parent
        prefix = f"{_stamp_from_iso(run_row['started_at'])}-{slugify(keywords)}-{run_id}"
    else:
        completed_time = completed_at or datetime.now().astimezone()
        ended_at_text = _iso_time(completed_time)
        output_root = output_dir or default_output_dir()
        prefix = f"{_stamp_from_iso(ended_at_text)}-{slugify(keywords)}"

    dream_dir = ensure_dir(ensure_dir(output_root) / prefix)
    article_out = dream_dir / f"{prefix}.md"
    seed_out = dream_dir / f"{prefix}.seed-card.json"
    constellation_out = dream_dir / f"{prefix}.constellation.json"

    article_out.write_text(article, encoding="utf-8")
    write_json(seed_out, seed_card)
    write_json(constellation_out, constellation)
    result = {
        "article": str(article_out),
        "seed_card": str(seed_out),
        "constellation": str(constellation_out),
        "prefix": prefix,
        "dream_dir": str(dream_dir),
    }
    ledger_paths = {
        "dream_dir": str(dream_dir),
        "article_path": str(article_out),
        "seed_card_path": str(seed_out),
        "constellation_path": str(constellation_out),
    }
    if run_id:
        finish_run(run_id, "success", ledger_path=ledger, path_updates=ledger_paths)
    else:
        _append_success_ledger_row(
            ledger,
            started_at=ended_at_text,
            ended_at=ended_at_text,
            paths=ledger_paths,
        )
    return result


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


def _paths_for_run(output_root: Path, prefix: str) -> dict[str, str]:
    dream_dir = output_root / prefix
    return {
        "dream_dir": str(dream_dir),
        "article_path": str(dream_dir / f"{prefix}.md"),
        "seed_card_path": str(dream_dir / f"{prefix}.seed-card.json"),
        "constellation_path": str(dream_dir / f"{prefix}.constellation.json"),
    }


def _append_success_ledger_row(
    ledger_path: Path,
    *,
    started_at: str,
    ended_at: str,
    paths: dict[str, str],
) -> None:
    _append_ledger_row(
        ledger_path,
        {
            "run_id": _generate_run_id(started_at),
            "started_at": started_at,
            "ended_at": ended_at,
            "status": "success",
            "trigger": "manual",
            **paths,
        },
    )


def _append_ledger_row(ledger_path: Path, row: dict[str, str]) -> None:
    with _ledger_lock(ledger_path):
        rows = _read_ledger_rows(ledger_path)
        if any(existing["run_id"] == row["run_id"] for existing in rows):
            raise ValueError(f"Run id already exists in ledger: {row['run_id']}")
        rows.append(_normalize_ledger_row(row))
        _write_ledger_rows(ledger_path, rows)


@contextlib.contextmanager
def _ledger_lock(ledger_path: Path) -> Any:
    ensure_dir(ledger_path.parent)
    lock_path = ledger_path.with_name(f".{ledger_path.name}.lock")
    with lock_path.open("w", encoding="utf-8") as handle:
        fcntl.flock(handle, fcntl.LOCK_EX)
        try:
            yield
        finally:
            fcntl.flock(handle, fcntl.LOCK_UN)


def _find_ledger_row(ledger_path: Path, run_id: str) -> dict[str, str]:
    for row in _read_ledger_rows(ledger_path):
        if row["run_id"] == run_id:
            return row
    raise ValueError(f"Run id not found in ledger: {run_id}")


def _read_ledger_rows(ledger_path: Path) -> list[dict[str, str]]:
    if not ledger_path.exists():
        return []
    with ledger_path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames != RUN_LEDGER_FIELDS:
            raise ValueError(f"Run ledger has unexpected fields: {ledger_path}")
        return [_normalize_ledger_row(row) for row in reader]


def _write_ledger_rows(ledger_path: Path, rows: list[dict[str, str]]) -> None:
    ensure_dir(ledger_path.parent)
    temp_path = ledger_path.with_name(f".{ledger_path.name}.tmp")
    with temp_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=RUN_LEDGER_FIELDS)
        writer.writeheader()
        for row in rows:
            writer.writerow(_normalize_ledger_row(row))
    os.replace(temp_path, ledger_path)


def _normalize_ledger_row(row: dict[str, Any]) -> dict[str, str]:
    return {field: str(row.get(field, "")) for field in RUN_LEDGER_FIELDS}


def _generate_run_id(seed: str) -> str:
    raw = f"{seed}|{os.getpid()}|{random.getrandbits(128)}"
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()[:16]


def _iso_time(value: datetime | None = None) -> str:
    timestamp = value or datetime.now().astimezone()
    if timestamp.tzinfo is None:
        timestamp = timestamp.astimezone()
    return timestamp.isoformat(timespec="seconds")


def _stamp_from_iso(value: str) -> str:
    try:
        return datetime.fromisoformat(value).strftime("%Y%m%d-%H%M%S")
    except ValueError:
        return datetime.now().astimezone().strftime("%Y%m%d-%H%M%S")


def _started_sort_value(value: str) -> float:
    try:
        return datetime.fromisoformat(value).timestamp()
    except ValueError:
        return 0.0


def slugify(value: str, fallback: str = "untitled") -> str:
    slug = re.sub(r"[^\w._-]+", "-", value.strip(), flags=re.UNICODE).strip("-._")
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
