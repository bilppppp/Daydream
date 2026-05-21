import json
import sys
import tempfile
import unittest
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from daydream.outputs import save_dream_outputs
from tests.test_seed_cards import valid_constellation, valid_seed_card


class DreamOutputTests(unittest.TestCase):
    def test_save_dream_writes_linked_article_seed_card_and_constellation(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            article = root / "article.md"
            article.write_text("# Dream\n\nReadable article.", encoding="utf-8")
            seed = root / "seed.json"
            seed.write_text(json.dumps(valid_seed_card()), encoding="utf-8")
            graph = root / "graph.json"
            graph.write_text(json.dumps(valid_constellation()), encoding="utf-8")

            result = save_dream_outputs(
                output_dir=root / "output",
                article_path=article,
                seed_card_path=seed,
                constellation_path=graph,
                keywords="state judgment",
                completed_at=datetime(2026, 5, 21, 14, 30, 12),
            )

            article_out = Path(result["article"])
            seed_out = Path(result["seed_card"])
            constellation_out = Path(result["constellation"])
            self.assertEqual(article_out.name, "20260521-143012-state-judgment.md")
            self.assertEqual(seed_out.name, "20260521-143012-state-judgment.seed-card.json")
            self.assertEqual(constellation_out.name, "20260521-143012-state-judgment.constellation.json")
            self.assertIn("Readable article", article_out.read_text(encoding="utf-8"))
            self.assertEqual(json.loads(seed_out.read_text(encoding="utf-8"))["card_type"], "dream_seed_card")
            self.assertEqual(
                json.loads(constellation_out.read_text(encoding="utf-8"))["graph_type"],
                "daydream_constellation",
            )

    def test_save_dream_rejects_invalid_seed_card_before_writing_outputs(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            article = root / "article.md"
            article.write_text("# Dream\n", encoding="utf-8")
            seed = root / "seed.json"
            seed.write_text('{"card_type": "broken"}', encoding="utf-8")
            graph = root / "graph.json"
            graph.write_text(json.dumps(valid_constellation()), encoding="utf-8")
            output_dir = root / "output"

            with self.assertRaisesRegex(ValueError, "Seed card"):
                save_dream_outputs(
                    output_dir=output_dir,
                    article_path=article,
                    seed_card_path=seed,
                    constellation_path=graph,
                    keywords="broken",
                )

            self.assertFalse(output_dir.exists())


if __name__ == "__main__":
    unittest.main()
