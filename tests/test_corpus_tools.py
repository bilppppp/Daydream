import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from daydream.corpus import check_corpus, pick_seed


class CorpusToolTests(unittest.TestCase):
    def test_pick_seed_skips_output_json_readme_and_empty_files(self):
        with tempfile.TemporaryDirectory() as td:
            corpus = Path(td)
            (corpus / "README.md").write_text("# Index\n", encoding="utf-8")
            (corpus / "empty.md").write_text("", encoding="utf-8")
            (corpus / "links.md").write_text(
                "# Links\n\n- https://example.com\n- https://example.org\n",
                encoding="utf-8",
            )
            (corpus / "output").mkdir()
            (corpus / "output" / "dream.md").write_text(
                "# Generated\n\nThis old output should not seed a new dream.",
                encoding="utf-8",
            )
            (corpus / "graph.json").write_text("{}", encoding="utf-8")
            wanted = corpus / "essay.md"
            wanted.write_text(
                "# Essay\n\nA real claim with a mechanism and a tension worth following.",
                encoding="utf-8",
            )

            result = pick_seed(corpus, chooser=lambda paths: paths[0])

            self.assertEqual(Path(result["path"]), wanted.resolve())
            self.assertEqual(result["title"], "Essay")

    def test_pick_seed_can_allow_json_explicitly(self):
        with tempfile.TemporaryDirectory() as td:
            corpus = Path(td)
            wanted = corpus / "note.json"
            wanted.write_text(
                '{"claim": "This JSON note has enough text to be a deliberate seed."}',
                encoding="utf-8",
            )

            result = pick_seed(corpus, allow_json=True, chooser=lambda paths: paths[0])

            self.assertEqual(Path(result["path"]), wanted.resolve())

    def test_check_corpus_reports_qmd_and_scheduled_policy(self):
        with tempfile.TemporaryDirectory() as td:
            corpus = Path(td)
            (corpus / "note.md").write_text(
                "# Note\n\nA readable note with enough text for a dream seed.",
                encoding="utf-8",
            )

            result = check_corpus(corpus, qmd_path=None, scheduled=True, no_qmd_policy="fail")

            self.assertEqual(result["corpus"], str(corpus.resolve()))
            self.assertFalse(result["qmd"]["available"])
            self.assertEqual(result["no_qmd_policy"], "fail")
            self.assertEqual(result["eligible_seed_count"], 1)

    def test_check_corpus_rejects_unknown_scheduled_policy(self):
        with tempfile.TemporaryDirectory() as td:
            corpus = Path(td)
            (corpus / "note.md").write_text(
                "# Note\n\nA readable note with enough text for a dream seed.",
                encoding="utf-8",
            )

            with self.assertRaisesRegex(ValueError, "no_qmd_policy"):
                check_corpus(corpus, scheduled=True, no_qmd_policy="guess")


if __name__ == "__main__":
    unittest.main()
