import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from daydream.cli import build_parser, dispatch
from daydream.qmd import semantic_search


class DaydreamCliTests(unittest.TestCase):
    def test_parser_exposes_portable_helper_commands(self):
        parser = build_parser()

        self.assertEqual(parser.parse_args(["check", "--corpus", "/tmp/notes"]).command, "check")
        self.assertEqual(parser.parse_args(["pick-seed", "--corpus", "/tmp/notes"]).command, "pick-seed")
        self.assertEqual(parser.parse_args(["search", "--corpus", "/tmp/notes", "legible control"]).command, "search")
        self.assertEqual(parser.parse_args(["validate-seed-card", "seed.json"]).command, "validate-seed-card")
        self.assertEqual(parser.parse_args(["validate-constellation", "graph.json"]).command, "validate-constellation")
        self.assertEqual(
            parser.parse_args(
                [
                    "save-dream",
                    "--article",
                    "a.md",
                    "--seed-card",
                    "s.json",
                    "--constellation",
                    "c.json",
                    "--keywords",
                    "state",
                ]
            ).command,
            "save-dream",
        )

    def test_validate_seed_card_dispatch_returns_valid_marker(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            seed_path = root / "seed.json"
            seed_path.write_text(
                json.dumps(
                    {
                        "card_type": "dream_seed_card",
                        "seed_document": {"title": "Seed", "path": "/notes/seed.md", "source_layer": "notes"},
                        "core_summary": "A note about control.",
                        "core_claim": "Useful systems expose the state that matters.",
                        "core_concepts": [
                            {
                                "name": "legibility",
                                "meaning": "state a reader can inspect",
                                "search_text": ["systems that expose state"],
                                "keywords": ["state"],
                                "abstraction_level": "mechanism",
                            }
                        ],
                        "tensions": [{"description": "automation vs judgment", "why_it_matters": "it shapes trust"}],
                        "mechanisms": [{"name": "inspection", "description": "show state", "search_text": ["inspection restores control"]}],
                        "failure_modes": [{"description": "hidden drift", "search_text": ["opaque systems drift"]}],
                        "questions_to_dream_on": [{"question": "Where else?", "preferred_strategy": "random_collision"}],
                        "avoid_searching_for": [],
                        "evidence_spans": ["Operators need to see state."],
                    }
                ),
                encoding="utf-8",
            )
            args = build_parser().parse_args(["validate-seed-card", str(seed_path)])

            result = dispatch(args)

            self.assertEqual(result["valid"], "seed_card")

    def test_semantic_search_runs_qmd_without_run_artifacts(self):
        with tempfile.TemporaryDirectory() as td:
            corpus = Path(td)
            seen_args = []

            def fake_runner(args, cwd):
                seen_args.extend(args)
                self.assertEqual(cwd, corpus)
                return json.dumps([{"file": "qmd://notes/a.md", "score": 0.9}])

            result = semantic_search(corpus, "legible control", limit=4, runner=fake_runner)

            self.assertEqual(result[0]["score"], 0.9)
            self.assertEqual(
                seen_args,
                ["qmd", "query", "legible control", "--json", "-n", "4"],
            )
            self.assertEqual(list(corpus.iterdir()), [])


if __name__ == "__main__":
    unittest.main()
