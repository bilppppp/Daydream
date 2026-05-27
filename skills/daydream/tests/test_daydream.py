from __future__ import annotations

import csv
import importlib.util
import json
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path
from unittest.mock import patch


SCRIPT_PATH = Path(__file__).resolve().parents[1] / "scripts" / "daydream.py"
SPEC = importlib.util.spec_from_file_location("daydream_script", SCRIPT_PATH)
assert SPEC and SPEC.loader
daydream = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(daydream)


class DaydreamScriptTests(unittest.TestCase):
    def write_valid_dream_inputs(self, directory: Path) -> tuple[Path, Path, Path]:
        article_path = directory / "article.md"
        seed_card_path = directory / "seed-card.json"
        constellation_path = directory / "constellation.json"
        article_path.write_text(self.valid_article(), encoding="utf-8")
        seed_card_path.write_text(json.dumps(self.valid_seed_card(), ensure_ascii=False), encoding="utf-8")
        constellation_path.write_text(json.dumps(self.valid_constellation(), ensure_ascii=False), encoding="utf-8")
        return article_path, seed_card_path, constellation_path

    def valid_article(self) -> str:
        return (
            "# Article\n\n"
            "Body.\n\n"
            "## Participating Documents And Concepts\n\n"
            "| Document | Concepts Used |\n"
            "| --- | --- |\n"
            "| Seed (`/tmp/seed.md`) | Feedback memory |\n"
        )

    def valid_seed_card(self) -> dict[str, object]:
        return {
            "card_type": "dream_seed_card",
            "seed_document": {
                "title": "Seed",
                "path": "/tmp/seed.md",
                "source_layer": "notes",
            },
            "origin_vision": {
                "vision": "A system keeps its memory until memory becomes the system.",
                "emotional_pressure": "The useful past hardens into present inertia.",
                "simple_truth": "What helps a system remember can also keep it trapped.",
                "search_text": [
                    "a useful memory becoming a trap for future action",
                    "the past preserved so strongly that adaptation becomes difficult",
                ],
            },
            "core_summary": "A compact summary of the seed.",
            "core_claim": "The seed makes one central claim.",
            "core_concepts": [
                {
                    "name": "Feedback memory",
                    "meaning": "A mechanism that preserves prior signals.",
                    "search_text": ["memory feedback as a coordination mechanism"],
                    "keywords": ["memory", "feedback"],
                    "abstraction_level": "mechanism",
                }
            ],
            "tensions": [
                {
                    "description": "Memory helps coordination but can freeze old mistakes.",
                    "why_it_matters": "This tension can echo in other systems.",
                }
            ],
            "mechanisms": [
                {
                    "name": "Delayed correction",
                    "description": "Corrections arrive after the system has already adapted.",
                    "search_text": ["delayed correction in adaptive systems"],
                }
            ],
            "failure_modes": [
                {
                    "description": "The loop amplifies stale assumptions.",
                    "search_text": ["feedback loops that amplify stale assumptions"],
                }
            ],
            "questions_to_dream_on": [
                {
                    "question": "Where else does useful memory become inertia?",
                    "preferred_strategy": "same_problem_different_domain",
                }
            ],
            "avoid_searching_for": ["generic memory metaphors"],
            "evidence_spans": ["The seed says memory can become inertia."],
        }

    def valid_constellation(self) -> dict[str, object]:
        return {
            "graph_type": "daydream_constellation",
            "article": {
                "title": "Article",
                "path": "/tmp/article.md",
                "thesis": "Memory can help or trap a system.",
            },
            "seed_document": {
                "title": "Seed",
                "path": "/tmp/seed.md",
                "source_layer": "notes",
            },
            "nodes": [
                {
                    "id": "seed-doc",
                    "type": "document",
                    "title": "Seed",
                    "path": "/tmp/seed.md",
                    "source_layer": "notes",
                    "role": "seed",
                },
                {
                    "id": "feedback-memory",
                    "type": "concept",
                    "label": "Feedback memory",
                    "meaning": "Memory that shapes future behavior.",
                    "abstraction_level": "mechanism",
                },
            ],
            "edges": [
                {
                    "from": "seed-doc",
                    "to": "feedback-memory",
                    "type": "contains",
                    "strength": 0.9,
                    "reason": "The seed grounds the concept.",
                    "evidence": ["The seed discusses memory and feedback."],
                }
            ],
            "ranked_connections": [
                {
                    "rank": 1,
                    "from_node": "seed-doc",
                    "to_node": "feedback-memory",
                    "strength": 0.9,
                    "connection_name": "Memory as coordination",
                    "connection_kind": "mechanism_match",
                    "why_it_matters": "It gives the article its central mechanism.",
                    "why_not_topic_overlap": "The match is about loop behavior, not the word memory.",
                    "used_in_article_section": "Opening mechanism",
                    "documents_involved": ["Seed"],
                }
            ],
            "search_coverage": {
                "connection_count": 1,
                "documents_considered": 2,
                "documents_used": 1,
                "notes": "Minimal valid constellation for helper tests.",
            },
        }

    def read_ledger_rows(self, ledger_path: Path) -> list[dict[str, str]]:
        with ledger_path.open("r", encoding="utf-8", newline="") as handle:
            return list(csv.DictReader(handle))

    def test_check_corpus_can_probe_real_qmd_search(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            corpus = Path(temp_dir)
            (corpus / "seed.md").write_text("Enough seed text to pass eligibility checks.", encoding="utf-8")

            calls: list[list[str]] = []

            def runner(args: list[str], cwd: Path, env: dict[str, str] | None = None) -> str:
                calls.append(args)
                self.assertEqual(cwd, corpus.resolve())
                return json.dumps([{"path": "qmd://notes/seed.md", "score": 0.9}])

            result = daydream.check_corpus(
                corpus,
                qmd_path="/usr/local/bin/qmd",
                qmd_collection="notes",
                qmd_probe_query="semantic smoke test",
                qmd_runner=runner,
            )

        self.assertEqual(result["qmd"]["probe"]["status"], "passed")
        self.assertEqual(result["qmd"]["probe"]["result_count"], 1)
        self.assertEqual(calls[0][:3], ["qmd", "query", "semantic smoke test"])
        self.assertIn("notes", calls[0])

    def test_qmd_env_file_merges_runtime_variables(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            env_file = Path(temp_dir) / "qmd.env"
            env_file.write_text(
                "# qmd runtime\nQMD_FORCE_CPU=1\nHF_ENDPOINT=https://hf-mirror.com\n",
                encoding="utf-8",
            )

            env = daydream.qmd_env_from_file(env_file, base_env={"PATH": "/bin"})

        self.assertEqual(env["PATH"], "/bin")
        self.assertEqual(env["QMD_FORCE_CPU"], "1")
        self.assertEqual(env["HF_ENDPOINT"], "https://hf-mirror.com")

    def test_check_corpus_uses_qmd_env_path_for_binary_detection(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            corpus = Path(temp_dir)
            (corpus / "seed.md").write_text("Enough seed text to pass eligibility checks.", encoding="utf-8")

            with patch.object(daydream.shutil, "which", return_value="/custom/bin/qmd") as which:
                result = daydream.check_corpus(corpus, qmd_env={"PATH": "/custom/bin"})

        which.assert_called_once_with("qmd", path="/custom/bin")
        self.assertEqual(result["qmd"]["path"], "/custom/bin/qmd")

    def test_search_recovers_to_cpu_query_after_gpu_runtime_failure(self) -> None:
        calls: list[list[str]] = []

        def runner(args: list[str], cwd: Path, env: dict[str, str] | None = None) -> str:
            calls.append(args)
            if "--no-gpu" not in args:
                raise RuntimeError("Vulkan OOM while loading reranker")
            return json.dumps([{"path": "qmd://notes/cpu.md", "score": 0.8}])

        results = daydream.semantic_search(
            Path("."),
            "semantic route",
            collection="notes",
            runner=runner,
            recovery="auto",
        )

        self.assertEqual(results[0]["path"], "qmd://notes/cpu.md")
        self.assertEqual(calls[0][1], "query")
        self.assertIn("--no-gpu", calls[1])

    def test_search_recovers_to_vsearch_when_query_path_still_fails(self) -> None:
        calls: list[list[str]] = []

        def runner(args: list[str], cwd: Path, env: dict[str, str] | None = None) -> str:
            calls.append(args)
            if args[1] == "query":
                raise RuntimeError("query rerank timed out")
            return json.dumps([{"path": "qmd://notes/vector.md", "score": 0.7}])

        results = daydream.semantic_search(
            Path("."),
            "semantic route",
            collection="notes",
            runner=runner,
            recovery="auto",
        )

        self.assertEqual(results[0]["path"], "qmd://notes/vector.md")
        self.assertEqual(calls[-1][1], "vsearch")

    def test_validate_seed_card_requires_origin_vision(self) -> None:
        payload = self.valid_seed_card()
        payload.pop("origin_vision")

        with self.assertRaisesRegex(ValueError, "origin_vision"):
            daydream.validate_seed_card(payload)

    def test_validate_seed_card_requires_origin_vision_search_text(self) -> None:
        payload = self.valid_seed_card()
        payload["origin_vision"]["search_text"] = []

        with self.assertRaisesRegex(ValueError, "search_text"):
            daydream.validate_seed_card(payload)

    def test_runs_start_creates_ledger_header_and_running_row(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            output_root = Path(temp_dir) / "skill-output"
            ledger_path = output_root / "daydream-runs.csv"
            started_at = datetime(2026, 5, 26, 12, 0, tzinfo=timezone.utc)

            result = daydream.start_run(
                trigger="cron",
                output_dir=output_root,
                ledger_path=ledger_path,
                started_at=started_at,
                run_id="abc123def4567890",
            )
            rows = self.read_ledger_rows(ledger_path)
            ledger_exists = ledger_path.exists()

        self.assertEqual(daydream.RUN_LEDGER_FIELDS, list(rows[0].keys()))
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["run_id"], "abc123def4567890")
        self.assertEqual(rows[0]["status"], "running")
        self.assertEqual(rows[0]["trigger"], "cron")
        self.assertEqual(rows[0]["ended_at"], "")
        self.assertIn("20260526-120000-abc123def4567890", rows[0]["dream_dir"])
        self.assertEqual(result["run_id"], "abc123def4567890")
        self.assertTrue(ledger_exists)

    def test_runs_finish_updates_same_row(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            output_root = Path(temp_dir) / "skill-output"
            ledger_path = output_root / "daydream-runs.csv"
            daydream.start_run(
                output_dir=output_root,
                ledger_path=ledger_path,
                started_at=datetime(2026, 5, 26, 12, 0, tzinfo=timezone.utc),
                run_id="run-to-finish",
            )

            daydream.finish_run("run-to-finish", "success", ledger_path=ledger_path)
            rows = self.read_ledger_rows(ledger_path)

        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["run_id"], "run-to-finish")
        self.assertEqual(rows[0]["status"], "success")
        self.assertNotEqual(rows[0]["ended_at"], "")

    def test_runs_list_filters_sorts_and_limits_json_ready_rows(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            output_root = Path(temp_dir) / "skill-output"
            ledger_path = output_root / "daydream-runs.csv"
            base = datetime(2026, 5, 26, 12, 0, tzinfo=timezone.utc)
            for offset, run_id, status in [
                (0, "old-success", "success"),
                (1, "failed-run", "failed"),
                (2, "middle-success", "success"),
                (3, "new-success", "success"),
            ]:
                daydream.start_run(
                    output_dir=output_root,
                    ledger_path=ledger_path,
                    started_at=base + timedelta(minutes=offset),
                    run_id=run_id,
                )
                daydream.finish_run(run_id, status, ledger_path=ledger_path)

            result = daydream.list_runs(status="success", limit=2, ledger_path=ledger_path)

        self.assertEqual([row["run_id"] for row in result["runs"]], ["new-success", "middle-success"])

    def test_ledger_fields_stay_minimal(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            output_root = Path(temp_dir) / "skill-output"
            ledger_path = output_root / "daydream-runs.csv"
            daydream.start_run(output_dir=output_root, ledger_path=ledger_path, run_id="minimal-fields")
            rows = self.read_ledger_rows(ledger_path)

        self.assertEqual(
            list(rows[0].keys()),
            [
                "run_id",
                "started_at",
                "ended_at",
                "status",
                "trigger",
                "dream_dir",
                "article_path",
                "seed_card_path",
                "constellation_path",
            ],
        )
        for banned in ["seed_path", "corpus_path", "qmd_collection", "error_type", "error_message", "summary"]:
            self.assertNotIn(banned, rows[0])

    def test_save_dream_without_run_id_appends_success_row_to_fixed_ledger(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_root = Path(temp_dir)
            article_path, seed_card_path, constellation_path = self.write_valid_dream_inputs(temp_root)
            custom_output = temp_root / "custom-output"
            fixed_ledger_dir = temp_root / "skill-output"
            ledger_path = fixed_ledger_dir / "daydream-runs.csv"

            result = daydream.save_dream_outputs(
                output_dir=custom_output,
                article_path=article_path,
                seed_card_path=seed_card_path,
                constellation_path=constellation_path,
                keywords="Memory Feedback",
                ledger_path=ledger_path,
            )
            rows = self.read_ledger_rows(ledger_path)

        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["status"], "success")
        self.assertEqual(rows[0]["dream_dir"], result["dream_dir"])
        self.assertTrue(rows[0]["article_path"].startswith(str(custom_output)))
        self.assertFalse((custom_output / "daydream-runs.csv").exists())

    def test_save_dream_with_run_id_updates_final_keyword_paths(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_root = Path(temp_dir)
            article_path, seed_card_path, constellation_path = self.write_valid_dream_inputs(temp_root)
            output_root = temp_root / "skill-output"
            ledger_path = output_root / "daydream-runs.csv"
            started_at = datetime(2026, 5, 26, 12, 0, tzinfo=timezone.utc)
            daydream.start_run(
                output_dir=output_root,
                ledger_path=ledger_path,
                started_at=started_at,
                run_id="abc123def4567890",
            )

            result = daydream.save_dream_outputs(
                output_dir=output_root,
                article_path=article_path,
                seed_card_path=seed_card_path,
                constellation_path=constellation_path,
                keywords="记忆 feedback",
                run_id="abc123def4567890",
                ledger_path=ledger_path,
            )
            rows = self.read_ledger_rows(ledger_path)
            article_exists = Path(result["article"]).exists()

        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["status"], "success")
        self.assertIn("20260526-120000-记忆-feedback-abc123def4567890", result["dream_dir"])
        self.assertEqual(rows[0]["dream_dir"], result["dream_dir"])
        self.assertEqual(rows[0]["article_path"], result["article"])
        self.assertTrue(article_exists)

    def test_save_dream_rejects_article_without_participating_documents_appendix(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_root = Path(temp_dir)
            article_path, seed_card_path, constellation_path = self.write_valid_dream_inputs(temp_root)
            article_path.write_text("# Article\n\nBody without the required appendix.\n", encoding="utf-8")

            with self.assertRaisesRegex(ValueError, "Participating Documents And Concepts"):
                daydream.save_dream_outputs(
                    output_dir=temp_root / "output",
                    article_path=article_path,
                    seed_card_path=seed_card_path,
                    constellation_path=constellation_path,
                    keywords="Memory Feedback",
                    ledger_path=temp_root / "ledger" / "daydream-runs.csv",
                )

    def test_save_dream_with_run_id_uses_started_output_dir_without_override(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_root = Path(temp_dir)
            article_path, seed_card_path, constellation_path = self.write_valid_dream_inputs(temp_root)
            planned_output = temp_root / "planned-output"
            ledger_path = temp_root / "skill-output" / "daydream-runs.csv"
            daydream.start_run(
                output_dir=planned_output,
                ledger_path=ledger_path,
                started_at=datetime(2026, 5, 26, 12, 0, tzinfo=timezone.utc),
                run_id="planned-output-run",
            )

            result = daydream.save_dream_outputs(
                output_dir=None,
                article_path=article_path,
                seed_card_path=seed_card_path,
                constellation_path=constellation_path,
                keywords="Memory Feedback",
                run_id="planned-output-run",
                ledger_path=ledger_path,
            )

        self.assertTrue(result["dream_dir"].startswith(str(planned_output)))


if __name__ == "__main__":
    unittest.main()
