import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from daydream.candidates import build_candidate_pool
from daydream.runs import inspect_run, resolve_run_dir, start_run
from daydream.workspace import init_workspace


class CandidatePoolTests(unittest.TestCase):
    def test_candidate_pool_dedupes_and_saves_results(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            init_workspace(root)
            start_run(root, "random-collision")

            calls = []

            def runner(args, cwd):
                calls.append(args)
                return json.dumps(
                    [
                        {"file": "qmd://corpus/a.md", "score": 0.9, "snippet": "control loop"},
                        {"file": "qmd://corpus/a.md", "score": 0.8, "snippet": "duplicate"},
                        {"file": "qmd://corpus/b.md", "score": 0.7, "snippet": "constraint"},
                    ]
                )

            result = build_candidate_pool(
                root,
                queries=["control loop", "constraint failure"],
                collection="corpus",
                per_query_limit=10,
                target_size=50,
                runner=runner,
                no_rerank=True,
            )

            self.assertEqual(result["candidate_count"], 2)
            self.assertEqual(len(calls), 2)
            stored = json.loads((resolve_run_dir(root, "latest") / "candidate_pool.json").read_text())
            self.assertEqual(len(stored["candidates"]), 2)
            self.assertTrue(inspect_run(root, "latest")["artifacts"]["candidate_pool"])


if __name__ == "__main__":
    unittest.main()
