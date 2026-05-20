import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from daydream.artifacts import (
    save_adjudication_report,
    save_mesh_draft,
    save_mesh_report,
    save_opponent_report,
)
from daydream.dream import dream_run, inspect_dream
from daydream.workspace import init_workspace


class V3DreamRunTests(unittest.TestCase):
    def test_dream_run_creates_corpus_field_without_seed(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            init_workspace(root)
            (root / "corpus/a.md").write_text("# Alpha\n\nControl through limits.", encoding="utf-8")
            (root / "corpus/b.md").write_text("# Beta\n\nDelayed feedback causes drift.", encoding="utf-8")
            (root / "corpus/c.md").write_text("# Gamma\n\nLocal optimization breaks global coordination.", encoding="utf-8")

            result = dream_run(root, collection="corpus", limit=2)

            self.assertEqual(result["mode"], "dream-field")
            self.assertEqual(result["document_count"], 2)
            self.assertNotIn("seed_doc_id", result)

            field_path = Path(result["corpus_field"])
            payload = json.loads(field_path.read_text(encoding="utf-8"))
            self.assertEqual(payload["mode"], "dream-field")
            self.assertEqual(payload["collection"], "corpus")
            self.assertEqual(len(payload["documents"]), 2)
            self.assertNotIn("seed_doc_id", payload)

    def test_inspect_dream_reports_v3_artifacts(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            init_workspace(root)
            (root / "corpus/a.md").write_text("# Alpha\n\nControl through limits.", encoding="utf-8")
            (root / "corpus/b.md").write_text("# Beta\n\nDelayed feedback causes drift.", encoding="utf-8")

            dream_run(root, collection="corpus", limit=10)
            summary = inspect_dream(root, "latest")

            self.assertEqual(summary["mode"], "dream-field")
            self.assertEqual(summary["document_count"], 2)
            self.assertTrue(summary["artifacts"]["corpus_field"])
            self.assertFalse(summary["artifacts"]["mesh_draft"])

    def test_v3_reports_and_mesh_draft_require_adjudication(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            init_workspace(root)
            (root / "corpus/a.md").write_text("# Alpha\n\nControl through limits.", encoding="utf-8")
            (root / "corpus/b.md").write_text("# Beta\n\nDelayed feedback causes drift.", encoding="utf-8")
            (root / "corpus/c.md").write_text("# Gamma\n\nLocal optimization breaks global coordination.", encoding="utf-8")
            run = dream_run(root, collection="corpus", limit=3)

            opponent = root / "opponent.json"
            opponent.write_text(
                json.dumps(
                    {
                        "run_id": run["run_id"],
                        "target_type": "cluster",
                        "target_id": "cluster-1",
                        "objections": ["The second edge may be same-domain summary."],
                        "strongest_objection": "The causal role mapping is under-evidenced.",
                        "recommendation": "near_miss",
                    }
                ),
                encoding="utf-8",
            )
            save_opponent_report(root, run["run_id"], opponent)

            mesh = root / "mesh.json"
            mesh.write_text(
                json.dumps(
                    {
                        "run_id": run["run_id"],
                        "cluster_id": "cluster-1",
                        "systemic_archetype": "control through constrained variety",
                        "participating_doc_ids": ["a", "b", "c"],
                        "hyperedges": [{"id": "H1", "doc_ids": ["a", "b", "c"], "pattern": "constraint restores control"}],
                        "evidence_mesh": [
                            {"doc_id": "a", "span": "first evidence"},
                            {"doc_id": "b", "span": "second evidence"},
                            {"doc_id": "c", "span": "third evidence"},
                        ],
                        "mismatch_notes": "The third document is weaker.",
                    }
                ),
                encoding="utf-8",
            )
            save_mesh_report(root, run["run_id"], mesh)

            draft = root / "draft.md"
            draft.write_text("# Mesh Draft\n", encoding="utf-8")
            with self.assertRaises(ValueError):
                save_mesh_draft(root, run["run_id"], "mesh", draft)

            adjudication = root / "adjudication.json"
            adjudication.write_text(
                json.dumps(
                    {
                        "run_id": run["run_id"],
                        "target_type": "cluster",
                        "target_id": "cluster-1",
                        "verdict": "accept",
                        "proponent_summary": "The cluster shares a control-through-constraint pattern.",
                        "opponent_summary": "The weakest edge is acknowledged but not fatal.",
                        "hard_reject_reasons": [],
                        "rationale": "Accept for mesh drafting because all three documents have evidence.",
                    }
                ),
                encoding="utf-8",
            )
            save_adjudication_report(root, run["run_id"], adjudication)
            result = save_mesh_draft(root, run["run_id"], "mesh", draft)

            summary = inspect_dream(root, run["run_id"])
            self.assertTrue(summary["artifacts"]["opponent_reports"])
            self.assertTrue(summary["artifacts"]["adjudication_reports"])
            self.assertTrue(summary["artifacts"]["mesh_report"])
            self.assertTrue(summary["artifacts"]["mesh_draft"])
            self.assertIn("mesh_draft.md", result["saved"])


if __name__ == "__main__":
    unittest.main()
