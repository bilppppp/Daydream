import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from daydream.schemas import validate_constellation, validate_seed_card


def valid_seed_card():
    return {
        "card_type": "dream_seed_card",
        "seed_document": {
            "title": "Seed",
            "path": "/notes/seed.md",
            "source_layer": "notes",
        },
        "core_summary": "A note about control.",
        "core_claim": "Useful systems expose the state that matters.",
        "core_concepts": [
            {
                "name": "legibility",
                "meaning": "state a reader can inspect",
                "search_text": ["systems that expose state to preserve judgment"],
                "keywords": ["state", "judgment"],
                "abstraction_level": "mechanism",
            }
        ],
        "tensions": [
            {
                "description": "automation vs judgment",
                "why_it_matters": "it shapes trust",
            }
        ],
        "mechanisms": [
            {
                "name": "inspection",
                "description": "show state",
                "search_text": ["inspection restores control"],
            }
        ],
        "failure_modes": [
            {
                "description": "hidden drift",
                "search_text": ["opaque systems drift"],
            }
        ],
        "questions_to_dream_on": [
            {
                "question": "Where else does legibility restore control?",
                "preferred_strategy": "same_problem_different_domain",
            }
        ],
        "avoid_searching_for": ["generic AI tooling"],
        "evidence_spans": ["Operators need to see state."],
    }


def valid_constellation():
    return {
        "graph_type": "daydream_constellation",
        "article": {
            "title": "Dream",
            "path": "/output/dream.md",
            "thesis": "Legibility preserves judgment.",
        },
        "seed_document": {
            "title": "Seed",
            "path": "/notes/seed.md",
            "source_layer": "notes",
        },
        "nodes": [
            {
                "id": "seed-doc",
                "type": "document",
                "title": "Seed",
                "path": "/notes/seed.md",
                "source_layer": "notes",
                "role": "seed",
            },
            {
                "id": "concept-a",
                "type": "concept",
                "label": "Legibility",
                "meaning": "Inspectable state",
                "abstraction_level": "mechanism",
            },
        ],
        "edges": [
            {
                "from": "seed-doc",
                "to": "concept-a",
                "type": "expresses",
                "strength": 0.8,
                "reason": "The seed argues for inspectable state.",
                "evidence": ["Operators need to see state."],
            }
        ],
        "ranked_connections": [
            {
                "rank": 1,
                "from_node": "seed-doc",
                "to_node": "concept-a",
                "strength": 0.8,
                "connection_name": "Legibility keeps judgment active",
                "connection_kind": "mechanism_match",
                "why_it_matters": "It gives the article its opening mechanism.",
                "why_not_topic_overlap": "The connection is about inspectability, not shared vocabulary.",
                "used_in_article_section": "Opening section on legible tools",
                "documents_involved": ["seed-doc"],
            }
        ],
        "search_coverage": {
            "connection_count": 1,
            "documents_considered": 1,
            "documents_used": 1,
            "notes": "Fixture network.",
        },
    }


class SeedCardSchemaTests(unittest.TestCase):
    def test_valid_seed_card_is_accepted(self):
        self.assertEqual(validate_seed_card(valid_seed_card())["card_type"], "dream_seed_card")

    def test_seed_card_requires_dream_seed_type(self):
        payload = valid_seed_card()
        payload["card_type"] = "structure_card"

        with self.assertRaisesRegex(ValueError, "card_type"):
            validate_seed_card(payload)

    def test_seed_card_requires_semantic_search_text(self):
        payload = valid_seed_card()
        payload["core_concepts"][0]["search_text"] = []

        with self.assertRaisesRegex(ValueError, "search_text"):
            validate_seed_card(payload)

    def test_constellation_ranked_connections_prove_non_topical_use(self):
        payload = valid_constellation()
        payload["ranked_connections"][0].pop("why_not_topic_overlap")

        with self.assertRaisesRegex(ValueError, "why_not_topic_overlap"):
            validate_constellation(payload)

    def test_constellation_rejects_edges_with_unknown_nodes(self):
        payload = valid_constellation()
        payload["edges"][0]["to"] = "missing"

        with self.assertRaisesRegex(ValueError, "unknown node"):
            validate_constellation(payload)


if __name__ == "__main__":
    unittest.main()
