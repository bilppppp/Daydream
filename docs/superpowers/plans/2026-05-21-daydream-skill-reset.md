# Daydream Skill Reset Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Reset Daydream into one portable dream-writing skill with a thin helper CLI for seed selection, qmd semantic search, JSON validation, and linked output saving.

**Architecture:** The portable artifact lives in `skills/daydream/` and progressively discloses the dream flow through references, prompts, and templates. The Python package stops modeling long analysis runs and instead exposes narrow helper functions and CLI commands for mechanical work while the host agent remains responsible for reading, judgment, and writing.

**Tech Stack:** Python 3.11 standard library, `unittest`, qmd CLI, Markdown skill assets, JSON templates.

---

## File Map

New skill files:

- `skills/daydream/SKILL.md`: short portable entrypoint and progressive-disclosure routing.
- `skills/daydream/references/dream-flow.md`: manual dream sequence and host responsibilities.
- `skills/daydream/references/qmd-search.md`: qmd-first semantic-search rules.
- `skills/daydream/references/fallback-without-qmd.md`: manual fallback and scheduled `no_qmd_policy`.
- `skills/daydream/references/seed-card-format.md`: JSON seed-card contract.
- `skills/daydream/references/constellation-format.md`: JSON constellation contract.
- `skills/daydream/references/ranking.md`: connection kinds and anti-overlap ranking rules.
- `skills/daydream/references/outputs.md`: output files and save command.
- `skills/daydream/references/cron.md`: generic scheduled-dream guidance.
- `skills/daydream/prompts/extract-seed-card.md`: host prompt for seed-card extraction.
- `skills/daydream/prompts/expand-with-semantic-search.md`: host prompt for multi-direction semantic expansion.
- `skills/daydream/prompts/rank-connections.md`: host prompt for ranking final connections.
- `skills/daydream/prompts/write-daydream-article.md`: host writing prompt.
- `skills/daydream/templates/seed-card.json`: seed-card template.
- `skills/daydream/templates/constellation.json`: constellation template.
- `skills/daydream/templates/article.md`: article template.
- `skills/daydream/output/.gitkeep`: tracked default output directory marker.

Python helper files:

- `src/daydream/corpus.py`: corpus checks and eligible seed selection.
- `src/daydream/outputs.py`: linked article, seed-card, and constellation saving.
- `src/daydream/schemas.py`: seed-card and constellation validation.
- `src/daydream/qmd.py`: qmd status and semantic-search wrapper without run-ledger writes.
- `src/daydream/cli.py`: thin helper commands.

Tests and docs:

- `tests/test_seed_cards.py`: seed-card and constellation schema checks.
- `tests/test_corpus_tools.py`: seed eligibility and environment checks.
- `tests/test_outputs.py`: linked output save behavior.
- `tests/test_cli.py`: helper command dispatch.
- `tests/test_core_behaviors.py`: replace old workspace expectations with portable-skill expectations.
- `tests/test_v2_gates.py`, `tests/test_v3_dream.py`, `tests/test_candidate_pool.py`, `tests/test_constellation.py`, `tests/test_evaluation_samples.py`: remove tests that only protect retired old flows.
- `README.md`: install and usage flow for the portable skill and helper CLI.

### Task 1: Lock New JSON Contracts

**Files:**
- Create: `tests/test_seed_cards.py`
- Modify: `src/daydream/schemas.py`

- [ ] **Step 1: Write failing seed-card and constellation tests**

Create `tests/test_seed_cards.py` with focused contract checks:

```python
import unittest

from daydream.schemas import validate_constellation, validate_seed_card


def valid_seed_card():
    return {
        "card_type": "dream_seed_card",
        "seed_document": {"title": "Seed", "path": "/notes/seed.md", "source_layer": "notes"},
        "core_summary": "A note about control.",
        "core_claim": "Useful systems expose the state that matters.",
        "core_concepts": [{
            "name": "legibility",
            "meaning": "state a reader can inspect",
            "search_text": ["systems that expose state to preserve judgment"],
            "keywords": ["state", "judgment"],
            "abstraction_level": "mechanism",
        }],
        "tensions": [{"description": "automation vs judgment", "why_it_matters": "it shapes trust"}],
        "mechanisms": [{"name": "inspection", "description": "show state", "search_text": ["inspection restores control"]}],
        "failure_modes": [{"description": "hidden drift", "search_text": ["opaque systems drift"]}],
        "questions_to_dream_on": [{"question": "Where else does legibility restore control?", "preferred_strategy": "same_problem_different_domain"}],
        "avoid_searching_for": ["generic AI tooling"],
        "evidence_spans": ["Operators need to see state."],
    }


class SeedCardSchemaTests(unittest.TestCase):
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
        payload = {
            "graph_type": "daydream_constellation",
            "article": {"title": "Dream", "path": "/output/dream.md", "thesis": "State matters."},
            "seed_document": {"title": "Seed", "path": "/notes/seed.md", "source_layer": "notes"},
            "nodes": [{"id": "concept-a", "type": "concept", "label": "Legibility", "meaning": "Inspectable state", "abstraction_level": "mechanism"}],
            "edges": [{"from": "concept-a", "to": "concept-a", "type": "echoes", "strength": 0.5, "reason": "self example", "evidence": ["span"]}],
            "ranked_connections": [{
                "rank": 1,
                "from_node": "concept-a",
                "to_node": "concept-a",
                "strength": 0.5,
                "connection_name": "Legibility loop",
                "connection_kind": "mechanism_match",
                "why_it_matters": "It frames the article.",
                "documents_involved": ["seed-doc"],
            }],
            "search_coverage": {"connection_count": 1, "documents_considered": 1, "documents_used": 1, "notes": "small fixture"},
        }

        with self.assertRaisesRegex(ValueError, "why_not_topic_overlap"):
            validate_constellation(payload)
```

- [ ] **Step 2: Run the schema tests and verify they fail**

Run:

```bash
PYTHONPATH=src python3 -m unittest tests.test_seed_cards -v
```

Expected: failure because `validate_seed_card` and `validate_constellation` do not exist yet.

- [ ] **Step 3: Replace old schema validators with seed-card and constellation validators**

Implement narrow validators in `src/daydream/schemas.py`:

```python
SEED_CARD_REQUIRED = {
    "card_type", "seed_document", "core_summary", "core_claim", "core_concepts",
    "tensions", "mechanisms", "failure_modes", "questions_to_dream_on",
    "avoid_searching_for", "evidence_spans",
}

CONSTELLATION_REQUIRED = {
    "graph_type", "article", "seed_document", "nodes", "edges",
    "ranked_connections", "search_coverage",
}


def validate_seed_card(payload: dict[str, Any]) -> dict[str, Any]:
    missing = _missing(payload, SEED_CARD_REQUIRED)
    if missing:
        raise ValueError(f"Seed card missing required fields: {', '.join(missing)}")
    if payload["card_type"] != "dream_seed_card":
        raise ValueError("card_type must be dream_seed_card")
    _require_object_fields(payload["seed_document"], "seed_document", {"title", "path", "source_layer"})
    _require_non_empty_dict_list(payload, "core_concepts")
    for concept in payload["core_concepts"]:
        _require_object_fields(concept, "core_concepts item", {"name", "meaning", "search_text", "keywords", "abstraction_level"})
        _require_non_empty_list_value(concept, "search_text")
    _require_non_empty_list_value(payload, "evidence_spans")
    return payload
```

Add matching constellation checks for required article fields, node ids, edge references, numeric strengths, `connection_kind`, `why_not_topic_overlap`, and `used_in_article_section`.

- [ ] **Step 4: Run the schema tests and verify they pass**

Run:

```bash
PYTHONPATH=src python3 -m unittest tests.test_seed_cards -v
```

Expected: all schema tests pass.

### Task 2: Build Corpus Checks and Seed Selection

**Files:**
- Create: `tests/test_corpus_tools.py`
- Create: `src/daydream/corpus.py`

- [ ] **Step 1: Write failing corpus tests**

Create tests for corpus checks and seed eligibility:

```python
class CorpusToolTests(unittest.TestCase):
    def test_pick_seed_skips_output_json_readme_and_empty_files(self):
        with tempfile.TemporaryDirectory() as td:
            corpus = Path(td)
            (corpus / "README.md").write_text("# Index\n", encoding="utf-8")
            (corpus / "empty.md").write_text("", encoding="utf-8")
            (corpus / "output").mkdir()
            (corpus / "output" / "dream.md").write_text("generated dream", encoding="utf-8")
            (corpus / "graph.json").write_text("{}", encoding="utf-8")
            wanted = corpus / "essay.md"
            wanted.write_text("# Essay\n\nA real claim with a mechanism and tension.", encoding="utf-8")

            result = pick_seed(corpus, chooser=lambda paths: paths[0])

            self.assertEqual(Path(result["path"]), wanted)

    def test_check_corpus_reports_qmd_and_policy(self):
        with tempfile.TemporaryDirectory() as td:
            corpus = Path(td)
            (corpus / "note.md").write_text("A real note.", encoding="utf-8")

            result = check_corpus(corpus, qmd_path=None, scheduled=True, no_qmd_policy="fail")

            self.assertFalse(result["qmd"]["available"])
            self.assertEqual(result["no_qmd_policy"], "fail")
```

- [ ] **Step 2: Run the corpus tests and verify they fail**

Run:

```bash
PYTHONPATH=src python3 -m unittest tests.test_corpus_tools -v
```

Expected: failure because `daydream.corpus` does not exist yet.

- [ ] **Step 3: Implement eligibility and environment checks**

Create `src/daydream/corpus.py` with:

```python
TEXT_SUFFIXES = {".md", ".markdown", ".txt"}
NO_QMD_POLICIES = {"fail", "warn_and_continue", "continue_silent"}


def eligible_seed_paths(corpus: Path, allow_json: bool = False) -> list[Path]:
    paths: list[Path] = []
    for path in sorted(corpus.rglob("*")):
        if not path.is_file() or "output" in path.relative_to(corpus).parts:
            continue
        if path.name.lower().startswith("readme"):
            continue
        if path.suffix.lower() not in TEXT_SUFFIXES and not (allow_json and path.suffix.lower() == ".json"):
            continue
        text = path.read_text(encoding="utf-8").strip()
        if len(text) < 24:
            continue
        paths.append(path)
    return paths
```

Add `pick_seed()` that accepts an injectable chooser and `check_corpus()` that validates path, readable documents, output path, qmd status, and scheduled no-qmd policy.

- [ ] **Step 4: Run corpus tests and verify they pass**

Run:

```bash
PYTHONPATH=src python3 -m unittest tests.test_corpus_tools -v
```

Expected: all corpus tests pass.

### Task 3: Save Linked Dream Outputs

**Files:**
- Create: `tests/test_outputs.py`
- Create: `src/daydream/outputs.py`
- Modify: `src/daydream/fs.py`

- [ ] **Step 1: Write failing output save tests**

Use representative files and a fixed completion time:

```python
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

            self.assertTrue(Path(result["article"]).name.startswith("20260521-143012-state-judgment"))
            self.assertTrue(Path(result["seed_card"]).name.endswith(".seed-card.json"))
            self.assertTrue(Path(result["constellation"]).name.endswith(".constellation.json"))
```

- [ ] **Step 2: Run output tests and verify they fail**

Run:

```bash
PYTHONPATH=src python3 -m unittest tests.test_outputs -v
```

Expected: failure because `save_dream_outputs` does not exist yet.

- [ ] **Step 3: Implement linked output saving**

Create `src/daydream/outputs.py`:

```python
def save_dream_outputs(
    output_dir: Path,
    article_path: Path,
    seed_card_path: Path,
    constellation_path: Path,
    keywords: str,
    completed_at: datetime | None = None,
) -> dict[str, str]:
    validate_seed_card(read_json(seed_card_path))
    validate_constellation(read_json(constellation_path))
    stamp = (completed_at or datetime.now()).strftime("%Y%m%d-%H%M%S")
    prefix = f"{stamp}-{slugify(keywords)}"
    article_out = output_dir / f"{prefix}.md"
    seed_out = output_dir / f"{prefix}.seed-card.json"
    constellation_out = output_dir / f"{prefix}.constellation.json"
    ensure_dir(output_dir)
    article_out.write_text(article_path.read_text(encoding="utf-8"), encoding="utf-8")
    write_json(seed_out, read_json(seed_card_path))
    write_json(constellation_out, read_json(constellation_path))
    return {
        "article": str(article_out),
        "seed_card": str(seed_out),
        "constellation": str(constellation_out),
        "prefix": prefix,
    }
```

Copy validated payloads with `write_json()` and article text with UTF-8 file reads.

- [ ] **Step 4: Run output tests and verify they pass**

Run:

```bash
PYTHONPATH=src python3 -m unittest tests.test_outputs -v
```

Expected: all output tests pass.

### Task 4: Expose the Thin Helper CLI and qmd Search

**Files:**
- Create: `tests/test_cli.py`
- Modify: `src/daydream/cli.py`
- Modify: `src/daydream/qmd.py`
- Modify: `README.md`

- [ ] **Step 1: Write failing CLI and qmd tests**

Cover the new public commands:

```python
class DaydreamCliTests(unittest.TestCase):
    def test_parser_exposes_portable_helper_commands(self):
        parser = build_parser()
        self.assertEqual(parser.parse_args(["check", "--corpus", "/tmp/notes"]).command, "check")
        self.assertEqual(parser.parse_args(["pick-seed", "--corpus", "/tmp/notes"]).command, "pick-seed")
        self.assertEqual(parser.parse_args(["search", "--corpus", "/tmp/notes", "legible control"]).command, "search")
        self.assertEqual(parser.parse_args(["validate-seed-card", "seed.json"]).command, "validate-seed-card")
        self.assertEqual(parser.parse_args(["validate-constellation", "graph.json"]).command, "validate-constellation")
        self.assertEqual(parser.parse_args(["save-dream", "--article", "a.md", "--seed-card", "s.json", "--constellation", "c.json", "--keywords", "state"]).command, "save-dream")
```

Add a qmd search test that asserts the runner receives `["qmd", "query", query, "--json", "-n", limit]` and does not write run artifacts.

- [ ] **Step 2: Run CLI tests and verify they fail**

Run:

```bash
PYTHONPATH=src python3 -m unittest tests.test_cli -v
```

Expected: failure because old parser commands do not match the reset.

- [ ] **Step 3: Replace public CLI dispatch**

Expose:

```text
daydream check --corpus <path> [--output-dir <path>] [--scheduled] [--no-qmd-policy fail]
daydream pick-seed --corpus <path> [--allow-json]
daydream search --corpus <path> [--collection <name>] [--limit <n>] "<semantic query>"
daydream validate-seed-card <json-path>
daydream validate-constellation <json-path>
daydream save-dream --article <md> --seed-card <json> --constellation <json> --keywords "<words>" [--output-dir <path>]
```

Change `src/daydream/qmd.py` so the search helper only runs qmd and returns parsed JSON. It must not require a Daydream run directory or write qmd results into one.

- [ ] **Step 4: Update README for the reset flow**

Document:

```markdown
Daydream is a portable skill plus a thin helper CLI.

1. Install or copy `skills/daydream/`.
2. Give the host a corpus path and ask it to dream.
3. The host uses `daydream check`, `daydream pick-seed`, and `daydream search`.
4. The host saves a Markdown article, JSON seed card, and JSON constellation with `daydream save-dream`.
```

- [ ] **Step 5: Run CLI tests and verify they pass**

Run:

```bash
PYTHONPATH=src python3 -m unittest tests.test_cli -v
```

Expected: all CLI tests pass.

### Task 5: Build the Portable Skill Assets

**Files:**
- Create: `skills/daydream/SKILL.md`
- Create: `skills/daydream/references/*.md`
- Create: `skills/daydream/prompts/*.md`
- Create: `skills/daydream/templates/seed-card.json`
- Create: `skills/daydream/templates/constellation.json`
- Create: `skills/daydream/templates/article.md`
- Create: `skills/daydream/output/.gitkeep`
- Modify: `tests/test_core_behaviors.py`

- [ ] **Step 1: Write failing skill asset tests**

Replace old workspace assertions with portable skill assertions:

```python
class DaydreamSkillAssetTests(unittest.TestCase):
    def test_portable_skill_has_progressive_disclosure_assets(self):
        skill = Path("skills/daydream")
        self.assertIn("read references/dream-flow.md", (skill / "SKILL.md").read_text(encoding="utf-8").lower())
        self.assertTrue((skill / "references/qmd-search.md").exists())
        self.assertTrue((skill / "references/fallback-without-qmd.md").exists())
        self.assertTrue((skill / "prompts/extract-seed-card.md").exists())
        self.assertTrue((skill / "prompts/write-daydream-article.md").exists())
        self.assertIn("why_not_topic_overlap", (skill / "templates/constellation.json").read_text(encoding="utf-8"))
```

- [ ] **Step 2: Run skill asset tests and verify they fail**

Run:

```bash
PYTHONPATH=src python3 -m unittest tests.test_core_behaviors -v
```

Expected: failure because the portable skill files do not exist yet.

- [ ] **Step 3: Create skill entrypoint, references, prompts, and templates**

Write `skills/daydream/SKILL.md` with:

```markdown
---
name: daydream
description: Dream over a local corpus by expanding concepts from one random seed with qmd semantic search and writing an article plus a constellation.
---

# Daydream

Use this when the user asks an agent host to dream over a corpus manually or on a schedule.

Read `references/dream-flow.md` before a dream. Read only the format, prompt, search, ranking, output, or fallback references needed for the current stage.
```

Populate the references and prompts from the approved design. Templates must match the validators exactly and use `.seed-card.json` naming language.

- [ ] **Step 4: Run skill asset tests and verify they pass**

Run:

```bash
PYTHONPATH=src python3 -m unittest tests.test_core_behaviors -v
```

Expected: portable skill asset tests pass.

### Task 6: Remove Retired Main-Path Machinery and Verify the Reset

**Files:**
- Delete: `src/daydream/artifacts.py`, `src/daydream/candidates.py`, `src/daydream/dream.py`, `src/daydream/evaluation.py`, `src/daydream/runs.py`, `src/daydream/scoring.py`, `src/daydream/workspace.py`.
- Delete: `qmd.yml`, `scripts/daydream-cron.sh`, old `prompts/`, old `skills/common/daydream/`, old `skills/hermes/daydream/`, and old `skills/openclaw/daydream/`.
- Delete obsolete tests that only defend retired V2/V3 flows.
- Modify: `README.md`

- [ ] **Step 1: Remove old CLI imports and obsolete tests**

Retire old public commands such as `dream-run`, `start-run`, pair reports, critic reports, mesh reports, and run inspection from the reset CLI. Remove tests that only assert those commands and artifacts.

- [ ] **Step 2: Run full tests**

Run:

```bash
PYTHONPATH=src python3 -m unittest discover -s tests -v
```

Expected: all retained tests pass.

- [ ] **Step 3: Run a representative helper flow**

Create a temporary corpus with one eligible Markdown seed, one README, one JSON output, and one output-dir document. Run:

```bash
PYTHONPATH=src python3 -m daydream check --corpus <temp-corpus>
PYTHONPATH=src python3 -m daydream pick-seed --corpus <temp-corpus>
PYTHONPATH=src python3 -m daydream validate-seed-card <fixture-seed-card.json>
PYTHONPATH=src python3 -m daydream validate-constellation <fixture-constellation.json>
PYTHONPATH=src python3 -m daydream save-dream --article <fixture-article.md> --seed-card <fixture-seed-card.json> --constellation <fixture-constellation.json> --keywords "state judgment" --output-dir <temp-output>
```

Expected: checks produce JSON, seed selection returns the eligible seed, validators accept the fixtures, and save command writes the three linked outputs.

- [ ] **Step 4: Verify qmd command shape without relying on external corpus state**

Run the qmd wrapper test from Task 4 and inspect the assertion that the runner invokes the semantic `qmd query` command rather than grep or filename search.

- [ ] **Step 5: Inspect final diff**

Run:

```bash
git diff --stat
git diff --check
git status --short
```

Expected: diff is scoped to the reset, whitespace checks pass, and status shows only intentional changes.
