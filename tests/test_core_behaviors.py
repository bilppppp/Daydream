import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from daydream.artifacts import (
    save_card,
    save_critic_report,
    save_pair_report,
    save_rejection,
    validate_run,
)
from daydream.qmd import qmd_query
from daydream.runs import inspect_run, resolve_run_dir, start_run
from daydream.workspace import init_workspace


def write_json(path: Path, payload: dict) -> Path:
    path.write_text(json.dumps(payload), encoding="utf-8")
    return path


class DaydreamCoreBehaviorTests(unittest.TestCase):
    def test_init_workspace_creates_expected_layout_and_docs(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)

            result = init_workspace(root)

            self.assertEqual(Path(result["root"]), root.resolve())
            for relpath in [
                "corpus",
                "cards/by_doc",
                "runs",
                "drafts",
                "prompts",
                "scripts",
                "skills/common/daydream",
                "skills/hermes/daydream",
                "skills/openclaw/daydream",
            ]:
                self.assertTrue((root / relpath).exists(), relpath)
            self.assertTrue((root / "cards/cards.jsonl").exists())
            qmd_config = (root / "qmd.yml").read_text(encoding="utf-8")
            self.assertIn("drafts", qmd_config)
            self.assertIn("exclude", qmd_config)
            self.assertIn("Daydream", (root / "README.md").read_text(encoding="utf-8"))
            self.assertTrue((root / "scripts/daydream-cron.sh").exists())
            self.assertIn("candidate-pool", (root / "skills/common/daydream/SKILL.md").read_text(encoding="utf-8"))
            self.assertIn("causal_graph", (root / "prompts/extract_structure.md").read_text(encoding="utf-8"))
            self.assertIn("seed_evidence_spans", (root / "prompts/compare_cards.md").read_text(encoding="utf-8"))
            self.assertIn("mean score >= 4.0", (root / "prompts/critic.md").read_text(encoding="utf-8"))
            self.assertTrue((root / "prompts/constellation.md").exists())

    def test_start_run_balances_strategies_and_updates_latest(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            init_workspace(root)

            first = start_run(root, "auto")
            second = start_run(root, "auto")

            self.assertEqual(first["strategy"], "random-collision")
            self.assertEqual(second["strategy"], "tag-bridge")
            self.assertEqual(resolve_run_dir(root, "latest").name, second["run_id"])
            manifest = json.loads((resolve_run_dir(root, "latest") / "manifest.json").read_text())
            self.assertEqual(manifest["run_id"], second["run_id"])
            self.assertEqual(manifest["status"], "started")

    def test_save_rejected_run_artifacts_and_validate(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            init_workspace(root)
            run = start_run(root, "temporal-bridge")
            inputs = root / "inputs"
            inputs.mkdir()

            card_path = write_json(
                inputs / "card.json",
                {
                    "card_id": "card-1",
                    "doc_id": "doc-1",
                    "title": "A note",
                    "source_type": "note",
                    "surface_topic": "tools",
                    "central_tension": "Control vs opacity",
                    "mechanism": "Expose inner state",
                    "failure_mode": "Black box drift",
                    "solution_pattern": "Local inspection",
                    "roles": [{"id": "R1", "label": "operator", "function": "regulator"}],
                    "relations": [{"src": "R1", "rel": "enables", "dst": "R1"}],
                    "abstractions": {"l3_functional_roles": ["Regulator"]},
                    "evidence_spans": ["The operator can inspect every state."],
                    "causal_graph": {
                        "nodes": [
                            {"id": "N1", "label": "Opaque state", "role": "failure_source"},
                            {"id": "N2", "label": "Inspection", "role": "control_surface"},
                        ],
                        "edges": [{"src": "N1", "rel": "enables", "dst": "N2"}],
                    },
                },
            )
            pair_path = write_json(
                inputs / "pair.json",
                {
                    "run_id": run["run_id"],
                    "seed_doc_id": "doc-1",
                    "candidate_doc_id": "doc-2",
                    "shared_structure": "Bounded visibility restores control.",
                    "role_alignments": [
                        {
                            "src_role_id": "R1",
                            "dst_role_id": "R2",
                            "alignment_justification": "Both inspect state.",
                        }
                    ],
                    "surface_distance": 0.8,
                    "structural_alignment_score": 0.3,
                    "novelty_score": 0.7,
                    "mismatch_notes": "The second document has weaker evidence.",
                    "seed_evidence_spans": [
                        "The operator can inspect every state.",
                        "Bounded visibility restores control.",
                    ],
                    "candidate_evidence_spans": [
                        "The second document has weaker evidence.",
                        "The analogy breaks when evidence is too thin.",
                    ],
                },
            )
            critic_path = write_json(
                inputs / "critic.json",
                {
                    "run_id": run["run_id"],
                    "scores": {
                        "grounded_evidence": 3,
                        "role_alignment": 2,
                        "non_triviality": 3,
                        "surface_independence": 4,
                        "causal_alignment": 2,
                    },
                    "mismatch_notes": "Evidence is too thin.",
                    "verdict": "reject",
                    "rationale": "Reject until stronger evidence exists.",
                },
            )

            save_card(root, run["run_id"], "doc-1", card_path)
            save_pair_report(root, run["run_id"], pair_path)
            save_critic_report(root, run["run_id"], critic_path)
            save_rejection(root, run["run_id"], "Rejected because evidence is thin.")

            validation = validate_run(root, "latest")
            inspection = inspect_run(root, "latest")

            self.assertTrue(validation["ok"], validation)
            self.assertEqual(inspection["status"], "rejected")
            self.assertTrue((resolve_run_dir(root, "latest") / "rejection_report.md").exists())

    def test_invalid_card_is_rejected_without_partial_artifact(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            init_workspace(root)
            run = start_run(root, "random-collision")
            invalid_path = write_json(root / "invalid_card.json", {"card_id": "missing-fields"})

            with self.assertRaises(ValueError):
                save_card(root, run["run_id"], "bad-doc", invalid_path)

            self.assertFalse((resolve_run_dir(root, run["run_id"]) / "cards.jsonl").exists())
            self.assertFalse((root / "cards/by_doc/bad-doc.md").exists())

    def test_card_requires_failure_mode_and_solution_pattern(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            init_workspace(root)
            run = start_run(root, "random-collision")
            invalid_path = write_json(
                root / "invalid_card.json",
                {
                    "card_id": "card-1",
                    "doc_id": "doc-1",
                    "title": "A note",
                    "source_type": "note",
                    "surface_topic": "tools",
                    "central_tension": "Control vs opacity",
                    "mechanism": "Expose inner state",
                    "roles": [{"id": "R1", "label": "operator", "function": "regulator"}],
                    "relations": [{"src": "R1", "rel": "enables", "dst": "R1"}],
                    "abstractions": {"l3_functional_roles": ["Regulator"]},
                    "evidence_spans": ["The operator can inspect every state."],
                },
            )

            with self.assertRaises(ValueError) as raised:
                save_card(root, run["run_id"], "doc-1", invalid_path)

            self.assertIn("failure_mode", str(raised.exception))
            self.assertFalse((resolve_run_dir(root, run["run_id"]) / "cards.jsonl").exists())

    def test_qmd_query_stores_json_results_in_latest_run(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            init_workspace(root)
            start_run(root, "random-collision")

            def fake_runner(args, cwd):
                self.assertIn("qmd", args[0])
                self.assertIn("--json", args)
                self.assertEqual(cwd, root)
                return json.dumps([{"file": "qmd://corpus/a.md", "score": 0.9}])

            result = qmd_query(
                root,
                "control opacity",
                collection="corpus",
                limit=3,
                runner=fake_runner,
                no_rerank=True,
            )

            self.assertEqual(result[0]["score"], 0.9)
            stored = json.loads((resolve_run_dir(root, "latest") / "qmd_results.json").read_text())
            self.assertEqual(stored[0]["file"], "qmd://corpus/a.md")

    def test_qmd_query_can_disable_reranking_for_offline_smoke_tests(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            init_workspace(root)
            start_run(root, "random-collision")
            seen_args = []

            def fake_runner(args, cwd):
                seen_args.extend(args)
                return "[]"

            qmd_query(root, "lex: Regulator", runner=fake_runner, no_rerank=True)

            self.assertIn("--no-rerank", seen_args)


if __name__ == "__main__":
    unittest.main()
