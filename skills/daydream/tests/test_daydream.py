from __future__ import annotations

import importlib.util
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch


SCRIPT_PATH = Path(__file__).resolve().parents[1] / "scripts" / "daydream.py"
SPEC = importlib.util.spec_from_file_location("daydream_script", SCRIPT_PATH)
assert SPEC and SPEC.loader
daydream = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(daydream)


class DaydreamScriptTests(unittest.TestCase):
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


if __name__ == "__main__":
    unittest.main()
