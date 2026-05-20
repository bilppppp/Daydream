import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from daydream.artifacts import save_constellation_report
from daydream.runs import inspect_run, resolve_run_dir, start_run
from daydream.workspace import init_workspace


class ConstellationTests(unittest.TestCase):
    def test_constellation_requires_three_or_more_documents_and_evidence_network(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            init_workspace(root)
            run = start_run(root, "tag-bridge")
            report = root / "constellation.json"
            report.write_text(
                json.dumps(
                    {
                        "run_id": run["run_id"],
                        "seed_doc_id": "a",
                        "resonance_doc_ids": ["b", "c"],
                        "epistemic_nexus": "Local constraints restore global control.",
                        "isomorphism_network": {"a": {"b": 0.82, "c": 0.78}},
                        "evidence_network": [
                            {"doc_id": "a", "span": "first evidence"},
                            {"doc_id": "b", "span": "second evidence"},
                            {"doc_id": "c", "span": "third evidence"},
                        ],
                        "mismatch_notes": "The third document is weaker on causality.",
                    }
                ),
                encoding="utf-8",
            )

            result = save_constellation_report(root, run["run_id"], report)

            self.assertTrue((resolve_run_dir(root, "latest") / "constellation_report.json").exists())
            self.assertIn("constellation_report.json", result["saved"])
            self.assertTrue(inspect_run(root, "latest")["artifacts"]["constellation_report"])


if __name__ == "__main__":
    unittest.main()
