import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from daydream.evaluation import load_resonance_samples, summarize_sample_labels


class ResonanceSampleTests(unittest.TestCase):
    def test_loads_all_three_label_groups(self):
        root = Path(__file__).resolve().parents[1]
        samples = load_resonance_samples(root / "docs/resonance_samples")

        self.assertEqual(len(samples), 30)
        labels = summarize_sample_labels(samples)
        self.assertEqual(labels["accepted"], 10)
        self.assertEqual(labels["rejected"], 10)
        self.assertEqual(labels["near_miss"], 10)

    def test_negative_sample_keeps_rejection_tags_and_evidence(self):
        root = Path(__file__).resolve().parents[1]
        samples = load_resonance_samples(root / "docs/resonance_samples")
        ovens = next(item for item in samples if item.path.name == "01_ovens_and_chips.md")

        self.assertEqual(ovens.expected_verdict, "rejected")
        self.assertIn("surface_lexical_trap", ovens.rejection_tags)
        self.assertGreaterEqual(len(ovens.evidence_excerpts), 2)

    def test_near_miss_is_not_treated_as_accept(self):
        root = Path(__file__).resolve().parents[1]
        samples = load_resonance_samples(root / "docs/resonance_samples")
        typewriter = next(item for item in samples if item.path.name == "02_automated_typewriter.md")

        self.assertEqual(typewriter.expected_verdict, "near_miss")
        self.assertNotEqual(typewriter.expected_verdict, "accepted")


if __name__ == "__main__":
    unittest.main()
