import json
import unittest
from pathlib import Path


class DaydreamSkillAssetTests(unittest.TestCase):
    def test_portable_skill_has_progressive_disclosure_assets(self):
        skill = Path("skills/daydream")
        skill_text = (skill / "SKILL.md").read_text(encoding="utf-8").lower()

        self.assertIn("read `references/dream-flow.md`", skill_text)
        self.assertTrue((skill / "references/qmd-search.md").exists())
        self.assertTrue((skill / "references/fallback-without-qmd.md").exists())
        self.assertTrue((skill / "references/seed-card-format.md").exists())
        self.assertTrue((skill / "references/constellation-format.md").exists())
        self.assertTrue((skill / "references/cron.md").exists())
        self.assertTrue((skill / "prompts/extract-seed-card.md").exists())
        self.assertTrue((skill / "prompts/expand-with-semantic-search.md").exists())
        self.assertTrue((skill / "prompts/rank-connections.md").exists())
        self.assertTrue((skill / "prompts/write-daydream-article.md").exists())
        self.assertTrue((skill / "output/.gitkeep").exists())

    def test_templates_match_seed_card_and_constellation_names(self):
        skill = Path("skills/daydream")
        seed_template = json.loads((skill / "templates/seed-card.json").read_text(encoding="utf-8"))
        graph_text = (skill / "templates/constellation.json").read_text(encoding="utf-8")

        self.assertEqual(seed_template["card_type"], "dream_seed_card")
        self.assertIn("why_not_topic_overlap", graph_text)
        self.assertIn("used_in_article_section", graph_text)
        self.assertIn(".seed-card.json", (skill / "references/outputs.md").read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
