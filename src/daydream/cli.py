from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

from .corpus import check_corpus, pick_seed
from .fs import read_json
from .outputs import save_dream_outputs
from .qmd import semantic_search
from .schemas import validate_constellation, validate_seed_card


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
    search.add_argument("--limit", type=int, default=12)
    search.add_argument("--no-rerank", action="store_true")

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
            limit=args.limit,
            no_rerank=args.no_rerank,
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
    return Path(__file__).resolve().parents[2] / "skills" / "daydream" / "output"


if __name__ == "__main__":
    raise SystemExit(main())
