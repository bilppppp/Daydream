import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from daydream.artifacts import save_card, save_critic_report, save_draft, save_pair_report
from daydream.runs import start_run
from daydream.workspace import init_workspace


def write_json(path: Path, payload: dict) -> Path:
    path.write_text(json.dumps(payload), encoding="utf-8")
    return path


class V2GateTests(unittest.TestCase):
    def test_pair_report_requires_two_evidence_spans_per_side_for_accept_path(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            init_workspace(root)
            run = start_run(root, "random-collision")
            pair = write_json(
                root / "pair.json",
                {
                    "run_id": run["run_id"],
                    "seed_doc_id": "a",
                    "candidate_doc_id": "b",
                    "shared_structure": "A weak claim.",
                    "role_alignments": [{"src_role_id": "R1", "dst_role_id": "R2", "alignment_justification": "thin"}],
                    "surface_distance": 0.8,
                    "structural_alignment_score": 0.8,
                    "novelty_score": 0.8,
                    "mismatch_notes": "Thin evidence.",
                    "seed_evidence_spans": ["only one"],
                    "candidate_evidence_spans": ["first", "second"],
                },
            )

            with self.assertRaises(ValueError):
                save_pair_report(root, run["run_id"], pair)

    def test_accept_requires_critic_thresholds(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            init_workspace(root)
            run = start_run(root, "random-collision")
            critic = write_json(
                root / "critic.json",
                {
                    "run_id": run["run_id"],
                    "scores": {
                        "grounded_evidence": 3,
                        "role_alignment": 4,
                        "non_triviality": 4,
                        "surface_independence": 4,
                        "causal_alignment": 4,
                    },
                    "mismatch_notes": "Evidence is not strong enough.",
                    "verdict": "accept",
                    "rationale": "Looks interesting but the evidence score is too low.",
                },
            )

            with self.assertRaises(ValueError):
                save_critic_report(root, run["run_id"], critic)

    def test_draft_cannot_be_saved_without_accepted_critic(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            init_workspace(root)
            run = start_run(root, "random-collision")
            draft = root / "draft.md"
            draft.write_text("# Draft\n", encoding="utf-8")

            with self.assertRaises(ValueError):
                save_draft(root, run["run_id"], "draft", draft)

    def test_rejected_critic_appends_near_miss_archive(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            init_workspace(root)
            run = start_run(root, "random-collision")
            critic = write_json(
                root / "critic.json",
                {
                    "run_id": run["run_id"],
                    "scores": {
                        "grounded_evidence": 2,
                        "role_alignment": 2,
                        "non_triviality": 2,
                        "surface_independence": 5,
                        "causal_alignment": 2,
                    },
                    "mismatch_notes": "Surface words overlap, causality conflicts.",
                    "verdict": "reject",
                    "rationale": "Reject as a surface lexical trap.",
                },
            )

            save_critic_report(root, run["run_id"], critic)

            archive = root / "calibration/near_miss_archive.jsonl"
            self.assertTrue(archive.exists())
            self.assertIn("surface lexical trap", archive.read_text(encoding="utf-8"))

    def test_card_requires_causal_graph(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            init_workspace(root)
            run = start_run(root, "random-collision")
            card = write_json(
                root / "card.json",
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
                },
            )

            with self.assertRaises(ValueError):
                save_card(root, run["run_id"], "doc-1", card)


if __name__ == "__main__":
    unittest.main()
