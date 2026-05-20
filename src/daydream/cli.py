from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

from .artifacts import (
    save_card,
    save_constellation_report,
    save_critic_report,
    save_draft,
    save_pair_report,
    save_rejection,
    validate_run,
)
from .candidates import build_candidate_pool
from .evaluation import load_resonance_samples, summarize_sample_labels
from .qmd import index_workspace, qmd_query
from .runs import inspect_run, start_run
from .workspace import doctor, init_workspace


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    root = Path(getattr(args, "root", ".")).resolve()
    try:
        result = dispatch(args, root)
    except Exception as exc:
        print(str(exc), file=sys.stderr)
        return 1
    if result is not None:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="daydream")
    parser.add_argument("--root", default=".", help="Project root")
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("init")
    sub.add_parser("doctor")
    sub.add_parser("index")
    sub.add_parser("eval-samples")

    query = sub.add_parser("qmd-query")
    query.add_argument("query")
    query.add_argument("--collection", default="corpus")
    query.add_argument("--limit", type=int, default=12)
    query.add_argument("--no-rerank", action="store_true", help="Skip qmd reranking for fast offline checks")

    pool = sub.add_parser("candidate-pool")
    pool.add_argument("queries", nargs="+")
    pool.add_argument("--collection", default="corpus")
    pool.add_argument("--per-query-limit", type=int, default=25)
    pool.add_argument("--target-size", type=int, default=50)
    pool.add_argument("--no-rerank", action="store_true")

    start = sub.add_parser("start-run")
    start.add_argument("--strategy", default="auto")

    card = sub.add_parser("save-card")
    card.add_argument("--run", required=True)
    card.add_argument("--doc", required=True)
    card.add_argument("--input", required=True)

    pair = sub.add_parser("save-pair-report")
    pair.add_argument("--run", required=True)
    pair.add_argument("--input", required=True)

    critic = sub.add_parser("save-critic-report")
    critic.add_argument("--run", required=True)
    critic.add_argument("--input", required=True)

    constellation = sub.add_parser("save-constellation-report")
    constellation.add_argument("--run", required=True)
    constellation.add_argument("--input", required=True)

    draft = sub.add_parser("save-draft")
    draft.add_argument("--run", required=True)
    draft.add_argument("--title", required=True)
    draft.add_argument("--input", required=True)

    rejection = sub.add_parser("save-rejection")
    rejection.add_argument("--run", required=True)
    rejection.add_argument("--input", required=True)

    inspect = sub.add_parser("inspect")
    inspect.add_argument("--run", default="latest")

    validate = sub.add_parser("validate")
    validate.add_argument("--run", default="latest")
    return parser


def dispatch(args: argparse.Namespace, root: Path) -> Any:
    if args.command == "init":
        return init_workspace(root)
    if args.command == "doctor":
        return doctor(root)
    if args.command == "index":
        return index_workspace(root)
    if args.command == "eval-samples":
        samples = load_resonance_samples(root / "docs/resonance_samples")
        return {"total": len(samples), "labels": summarize_sample_labels(samples)}
    if args.command == "qmd-query":
        return qmd_query(root, args.query, collection=args.collection, limit=args.limit, no_rerank=args.no_rerank)
    if args.command == "candidate-pool":
        return build_candidate_pool(
            root,
            queries=args.queries,
            collection=args.collection,
            per_query_limit=args.per_query_limit,
            target_size=args.target_size,
            no_rerank=args.no_rerank,
        )
    if args.command == "start-run":
        return start_run(root, args.strategy)
    if args.command == "save-card":
        return save_card(root, args.run, args.doc, Path(args.input))
    if args.command == "save-pair-report":
        return save_pair_report(root, args.run, Path(args.input))
    if args.command == "save-critic-report":
        return save_critic_report(root, args.run, Path(args.input))
    if args.command == "save-constellation-report":
        return save_constellation_report(root, args.run, Path(args.input))
    if args.command == "save-draft":
        return save_draft(root, args.run, args.title, Path(args.input))
    if args.command == "save-rejection":
        return save_rejection(root, args.run, Path(args.input))
    if args.command == "inspect":
        return inspect_run(root, args.run)
    if args.command == "validate":
        return validate_run(root, args.run)
    raise ValueError(f"Unknown command: {args.command}")


if __name__ == "__main__":
    raise SystemExit(main())
