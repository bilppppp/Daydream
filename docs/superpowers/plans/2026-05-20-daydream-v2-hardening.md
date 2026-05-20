# Daydream V2 Hardening Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Turn the current Daydream MVP into a V2-safe loop that rejects forced resonance, avoids early stopping, and can generalize beyond the seed evaluation themes.

**Architecture:** Keep the current split: host agent does cognition, Python CLI enforces contracts and records evidence. Add hard validation gates first, then add broad candidate-pool discovery, then add optional constellation and causal graph checks. Evaluation samples calibrate the system; they must not become topic-specific rules.

**Tech Stack:** Python 3.11+ stdlib, qmd, unittest, Markdown skill prompts, local file ledger.

---

## Requirement Mapping

| Concern | Current State | V2 Target | Plan Task |
|---|---|---|---|
| Forced resonance | Prompts ask for evidence and mismatch notes, but validation is light | Pair and critic cannot accept without evidence from both sides and score thresholds | Tasks 1, 2 |
| Negative and near-miss samples | Files exist under `docs/resonance_samples/` | Samples become regression tests and calibration examples | Task 1 |
| Early stopping | Current loop can inspect a small qmd result set | Loop must build a wider candidate pool and save why candidates were kept or dropped | Task 3 |
| Same-domain boring results | `surface_distance` and `novelty_score` exist, but the model self-reports them | Accept path must reject low-span or low-novelty pairs | Task 2 |
| Thin pairwise essays | Current output is pairwise | Add constellation schema after hard gates work | Task 6 |
| Causal topology mismatch | Roles and relations exist, but no graph check | Add lightweight causal graph validation before full graph isomorphism | Task 5 |
| Overfitting to sample themes | No topic hardcoding today | Keep samples as labels and rubrics only; test generic behavior, not domain names | Tasks 1, 4 |
| Self-improving rejection memory | Rejected runs are saved only per run | Add a small near-miss archive for future critic context | Task 4 |

## File Structure

- Modify `src/daydream/schemas.py`: stricter structure-card, pair-report, critic-report validation.
- Modify `src/daydream/artifacts.py`: enforce draft gate, archive rejected and near-miss runs.
- Modify `src/daydream/cli.py`: add evaluation and candidate-pool commands.
- Create `src/daydream/evaluation.py`: parse `docs/resonance_samples/` and summarize expected labels.
- Create `src/daydream/candidates.py`: build wide qmd candidate pools and save them to a run.
- Create `src/daydream/scoring.py`: deterministic threshold helpers for pair and critic gates.
- Modify `prompts/compare_cards.md`: require per-side evidence and reject weak mappings.
- Modify `prompts/critic.md`: include exact thresholds and near-miss archive context.
- Modify `skills/common/daydream/SKILL.md`: replace single small query flow with candidate-pool flow.
- Create `tests/test_v2_gates.py`: hard acceptance and draft-gate tests.
- Create `tests/test_evaluation_samples.py`: sample parser and label coverage tests.
- Create `tests/test_candidate_pool.py`: fake-qmd pool and dedupe tests.

---

### Task 1: Turn Gold Samples Into Regression Fixtures

**Files:**
- Create: `src/daydream/evaluation.py`
- Modify: `src/daydream/cli.py`
- Test: `tests/test_evaluation_samples.py`

- [x] **Step 1: Write the failing sample parser tests**

Add `tests/test_evaluation_samples.py`:

```python
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
```

- [x] **Step 2: Run the tests and verify they fail**

Run:

```bash
python3 -m unittest tests/test_evaluation_samples.py
```

Expected: import failure for `daydream.evaluation`.

- [x] **Step 3: Implement the parser**

Create `src/daydream/evaluation.py`:

```python
from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class ResonanceSample:
    path: Path
    group: str
    expected_verdict: str
    isomorphism_score: float | None
    rejection_tags: list[str]
    evidence_excerpts: list[str]


VERDICT_MAP = {
    "ACCEPTED": "accepted",
    "REJECTED": "rejected",
    "BORDERLINE": "near_miss",
}


def load_resonance_samples(samples_root: Path) -> list[ResonanceSample]:
    items: list[ResonanceSample] = []
    for group in ("positive", "negative", "near_miss"):
        for path in sorted((samples_root / group).glob("*.md")):
            text = path.read_text(encoding="utf-8")
            items.append(
                ResonanceSample(
                    path=path,
                    group=group,
                    expected_verdict=_extract_verdict(text, group),
                    isomorphism_score=_extract_float(text, r"isomorphism_score=([0-9.]+)"),
                    rejection_tags=_extract_tags(text),
                    evidence_excerpts=_extract_evidence(text),
                )
            )
    return items


def summarize_sample_labels(samples: list[ResonanceSample]) -> dict[str, int]:
    counts = {"accepted": 0, "rejected": 0, "near_miss": 0}
    for sample in samples:
        counts[sample.expected_verdict] += 1
    return counts


def _extract_verdict(text: str, group: str) -> str:
    match = re.search(r"resonance_verdict=Verdict\.([A-Z_]+)", text)
    if match:
        return VERDICT_MAP[match.group(1)]
    if group == "positive":
        return "accepted"
    if group == "near_miss":
        return "near_miss"
    return "rejected"


def _extract_float(text: str, pattern: str) -> float | None:
    match = re.search(pattern, text)
    return float(match.group(1)) if match else None


def _extract_tags(text: str) -> list[str]:
    match = re.search(r"rejection_tags=\[([^\]]*)\]", text)
    if not match:
        return []
    return re.findall(r"['\"]([^'\"]+)['\"]", match.group(1))


def _extract_evidence(text: str) -> list[str]:
    block = re.search(r"evidence_excerpts=\[(.*?)\]\s*\)", text, re.S)
    if not block:
        return []
    return re.findall(r"['\"]([^'\"]{20,}?)['\"]", block.group(1), re.S)
```

- [x] **Step 4: Add a CLI summary command**

Modify `src/daydream/cli.py`:

```python
from .evaluation import load_resonance_samples, summarize_sample_labels
```

Add parser:

```python
    sub.add_parser("eval-samples")
```

Add dispatch branch:

```python
    if args.command == "eval-samples":
        samples = load_resonance_samples(root / "docs/resonance_samples")
        return {"total": len(samples), "labels": summarize_sample_labels(samples)}
```

- [x] **Step 5: Verify sample coverage**

Run:

```bash
python3 -m unittest tests/test_evaluation_samples.py
PYTHONPATH=src python3 -m daydream eval-samples
```

Expected: tests pass, CLI reports 30 total samples with 10 accepted, 10 rejected, 10 near_miss.

---

### Task 2: Add Hard Accept Gates

**Files:**
- Create: `src/daydream/scoring.py`
- Modify: `src/daydream/schemas.py`
- Modify: `src/daydream/artifacts.py`
- Modify: `prompts/compare_cards.md`
- Modify: `prompts/critic.md`
- Test: `tests/test_v2_gates.py`

- [x] **Step 1: Write failing tests for evidence, score, and draft gates**

Add `tests/test_v2_gates.py`:

```python
import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from daydream.artifacts import save_critic_report, save_draft, save_pair_report
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
```

- [x] **Step 2: Run tests and verify they fail**

Run:

```bash
python3 -m unittest tests/test_v2_gates.py
```

Expected: at least the first and third tests fail because current gates are too permissive.

- [x] **Step 3: Add deterministic scoring helpers**

Create `src/daydream/scoring.py`:

```python
from __future__ import annotations

from typing import Any


CRITIC_SCORE_KEYS = {
    "grounded_evidence",
    "role_alignment",
    "non_triviality",
    "surface_independence",
    "causal_alignment",
}


def require_critic_thresholds(payload: dict[str, Any]) -> None:
    scores = payload.get("scores")
    if not isinstance(scores, dict):
        raise ValueError("scores must be an object")
    missing = sorted(CRITIC_SCORE_KEYS - scores.keys())
    if missing:
        raise ValueError(f"critic scores missing required keys: {', '.join(missing)}")
    numeric = []
    for key in sorted(CRITIC_SCORE_KEYS):
        value = scores[key]
        if not isinstance(value, int | float):
            raise ValueError(f"critic score {key} must be numeric")
        if value < 1 or value > 5:
            raise ValueError(f"critic score {key} must be between 1 and 5")
        numeric.append(float(value))
    verdict = str(payload.get("verdict", "")).lower()
    if verdict in {"accept", "accepted"}:
        mean = sum(numeric) / len(numeric)
        if mean < 4.0:
            raise ValueError("accepted critic mean score must be at least 4.0")
        if float(scores["grounded_evidence"]) < 4:
            raise ValueError("accepted critic grounded_evidence must be at least 4")
        if float(scores["surface_independence"]) < 3:
            raise ValueError("accepted critic surface_independence must be at least 3")


def require_pair_acceptability(payload: dict[str, Any]) -> None:
    if payload["surface_distance"] < 0.35:
        raise ValueError("surface_distance too low for a non-trivial resonance")
    if payload["novelty_score"] < 0.55:
        raise ValueError("novelty_score too low for a non-trivial resonance")
    if payload["structural_alignment_score"] < 0.65:
        raise ValueError("structural_alignment_score too low for acceptance")
```

- [x] **Step 4: Harden schema validation**

Modify `src/daydream/schemas.py`:

```python
from .scoring import require_critic_thresholds

PAIR_REQUIRED = {
    "run_id",
    "seed_doc_id",
    "candidate_doc_id",
    "shared_structure",
    "role_alignments",
    "surface_distance",
    "structural_alignment_score",
    "novelty_score",
    "mismatch_notes",
    "seed_evidence_spans",
    "candidate_evidence_spans",
}
```

Inside `validate_pair_report` after score validation:

```python
    _require_min_list(payload, "seed_evidence_spans", 2)
    _require_min_list(payload, "candidate_evidence_spans", 2)
```

Add helper:

```python
def _require_min_list(payload: dict[str, Any], key: str, min_count: int) -> None:
    value = payload.get(key)
    if not isinstance(value, list) or len(value) < min_count:
        raise ValueError(f"{key} must include at least {min_count} items")
```

Inside `validate_critic_report`:

```python
    require_critic_thresholds(payload)
```

- [x] **Step 5: Harden draft saving**

Modify `src/daydream/artifacts.py` inside `save_draft` before writing files:

```python
    critic_path = resolve_run_dir(root, run) / "critic_report.json"
    if not critic_path.exists():
        raise ValueError("Cannot save draft before critic_report.json exists")
    critic = read_json(critic_path)
    if normalize_verdict(str(critic.get("verdict", ""))) != "accepted":
        raise ValueError("Cannot save draft unless critic verdict is accepted")
    validate_critic_report(critic)
```

- [x] **Step 6: Update prompts to match gates**

Modify `prompts/compare_cards.md` required fields:

```markdown
- `seed_evidence_spans`
- `candidate_evidence_spans`
```

Add rules:

```markdown
- Include at least two exact evidence spans from the seed document and two from the candidate document.
- If either side lacks evidence, set low scores and prefer reject or near_miss.
```

Modify `prompts/critic.md` rules:

```markdown
- `accept` requires mean score >= 4.0.
- `accept` requires `grounded_evidence >= 4`.
- `accept` requires `surface_independence >= 3`.
- `near_miss` is mandatory for plausible but same-domain, clichéd, or low-novelty pairs.
```

- [x] **Step 7: Verify hard gates**

Run:

```bash
python3 -m unittest tests/test_v2_gates.py tests/test_core_behaviors.py
```

Expected: all tests pass after updating the existing core test pair payloads to include `seed_evidence_spans` and `candidate_evidence_spans`.

---

### Task 3: Add Wide Candidate Pool to Prevent Early Stopping

**Files:**
- Create: `src/daydream/candidates.py`
- Modify: `src/daydream/cli.py`
- Modify: `skills/common/daydream/SKILL.md`
- Test: `tests/test_candidate_pool.py`

- [x] **Step 1: Write failing candidate-pool tests**

Add `tests/test_candidate_pool.py`:

```python
import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from daydream.candidates import build_candidate_pool
from daydream.runs import resolve_run_dir, start_run
from daydream.workspace import init_workspace


class CandidatePoolTests(unittest.TestCase):
    def test_candidate_pool_dedupes_and_saves_results(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            init_workspace(root)
            start_run(root, "random-collision")

            calls = []

            def runner(args, cwd):
                calls.append(args)
                return json.dumps(
                    [
                        {"file": "qmd://corpus/a.md", "score": 0.9, "snippet": "control loop"},
                        {"file": "qmd://corpus/a.md", "score": 0.8, "snippet": "duplicate"},
                        {"file": "qmd://corpus/b.md", "score": 0.7, "snippet": "constraint"},
                    ]
                )

            result = build_candidate_pool(
                root,
                queries=["control loop", "constraint failure"],
                collection="corpus",
                per_query_limit=10,
                target_size=50,
                runner=runner,
                no_rerank=True,
            )

            self.assertEqual(result["candidate_count"], 2)
            self.assertEqual(len(calls), 2)
            stored = json.loads((resolve_run_dir(root, "latest") / "candidate_pool.json").read_text())
            self.assertEqual(len(stored["candidates"]), 2)
```

- [x] **Step 2: Run tests and verify they fail**

Run:

```bash
python3 -m unittest tests/test_candidate_pool.py
```

Expected: import failure for `daydream.candidates`.

- [x] **Step 3: Implement candidate pool builder**

Create `src/daydream/candidates.py`:

```python
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .fs import write_json
from .qmd import Runner, default_runner
from .runs import resolve_run_dir, update_manifest


def build_candidate_pool(
    root: Path,
    queries: list[str],
    collection: str = "corpus",
    per_query_limit: int = 25,
    target_size: int = 50,
    runner: Runner = default_runner,
    no_rerank: bool = False,
) -> dict[str, Any]:
    candidates_by_file: dict[str, dict[str, Any]] = {}
    for query in queries:
        args = ["qmd", "query", query, "--json", "-n", str(per_query_limit), "-c", collection]
        if no_rerank:
            args.append("--no-rerank")
        data = json.loads(runner(args, root) or "[]")
        for item in data:
            file_id = str(item.get("file", ""))
            if not file_id:
                continue
            current = candidates_by_file.get(file_id)
            if current is None or float(item.get("score", 0)) > float(current.get("score", 0)):
                enriched = dict(item)
                enriched["query"] = query
                candidates_by_file[file_id] = enriched
    candidates = sorted(candidates_by_file.values(), key=lambda item: float(item.get("score", 0)), reverse=True)
    candidates = candidates[:target_size]
    payload = {"queries": queries, "collection": collection, "candidates": candidates}
    run_path = resolve_run_dir(root, "latest")
    write_json(run_path / "candidate_pool.json", payload)
    update_manifest(root, "latest", artifacts={"candidate_pool": "candidate_pool.json"})
    return {"candidate_count": len(candidates), "saved": str(run_path / "candidate_pool.json")}
```

- [x] **Step 4: Add CLI command**

Modify `src/daydream/cli.py`:

```python
from .candidates import build_candidate_pool
```

Add parser:

```python
    pool = sub.add_parser("candidate-pool")
    pool.add_argument("queries", nargs="+")
    pool.add_argument("--collection", default="corpus")
    pool.add_argument("--per-query-limit", type=int, default=25)
    pool.add_argument("--target-size", type=int, default=50)
    pool.add_argument("--no-rerank", action="store_true")
```

Add dispatch branch:

```python
    if args.command == "candidate-pool":
        return build_candidate_pool(
            root,
            queries=args.queries,
            collection=args.collection,
            per_query_limit=args.per_query_limit,
            target_size=args.target_size,
            no_rerank=args.no_rerank,
        )
```

- [x] **Step 5: Update skill flow**

Modify `skills/common/daydream/SKILL.md` so the run procedure uses:

```markdown
5. Produce 3-5 abstract search queries that target different mechanisms, roles, tensions, and failure modes.
6. Run `daydream candidate-pool --collection corpus --target-size 50 "<query1>" "<query2>" "<query3>"`.
7. Select candidates from the saved pool, preferring structural fit plus surface distance.
```

- [x] **Step 6: Verify candidate pool**

Run:

```bash
python3 -m unittest tests/test_candidate_pool.py
PYTHONPATH=src python3 -m daydream candidate-pool --collection corpus --target-size 20 --no-rerank "lex: 统帅" "lex: 流水线"
PYTHONPATH=src python3 -m daydream inspect --run latest
```

Expected: tests pass, `candidate_pool.json` exists in the latest run, inspect reports a candidate-pool artifact after inspect is updated in Task 3 if needed.

---

### Task 4: Add Near-Miss Archive and Critic Calibration Context

**Files:**
- Modify: `src/daydream/artifacts.py`
- Modify: `src/daydream/workspace.py`
- Modify: `prompts/critic.md`
- Test: `tests/test_v2_gates.py`

- [x] **Step 1: Add a failing archive test**

Append to `tests/test_v2_gates.py`:

```python
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
```

- [x] **Step 2: Create calibration directory during init**

Modify `src/daydream/workspace.py` in the init directory list:

```python
        "calibration",
```

- [x] **Step 3: Archive rejected and near-miss critic reports**

Modify `src/daydream/artifacts.py` inside `save_critic_report` after manifest update:

```python
    if status in {"rejected", "near_miss"}:
        append_jsonl(
            root / "calibration" / "near_miss_archive.jsonl",
            {
                "run_id": payload["run_id"],
                "status": status,
                "scores": payload["scores"],
                "mismatch_notes": payload["mismatch_notes"],
                "rationale": payload["rationale"],
            },
        )
```

- [x] **Step 4: Update critic prompt**

Add to `prompts/critic.md`:

```markdown
Before accepting, compare this pair against recent rejected and near-miss cases from `calibration/near_miss_archive.jsonl` when available. If the current pair repeats a known rejection tag such as surface lexical trap, contradictory causality, same-domain summary, textbook metaphor, or cliché analogy, do not accept.
```

- [x] **Step 5: Verify archive behavior**

Run:

```bash
python3 -m unittest tests/test_v2_gates.py
```

Expected: archive test passes and rejected runs append one JSON line.

---

### Task 5: Add Causal Graph Consistency Lite

**Files:**
- Modify: `src/daydream/schemas.py`
- Modify: `prompts/extract_structure.md`
- Modify: `prompts/compare_cards.md`
- Test: `tests/test_v2_gates.py`

- [x] **Step 1: Require causal graph on new structure cards**

Add `causal_graph` to `CARD_REQUIRED` in `src/daydream/schemas.py`.

Expected card shape:

```json
{
  "causal_graph": {
    "nodes": [{"id": "N1", "label": "Constraint", "role": "limiter"}],
    "edges": [{"src": "N1", "rel": "causes", "dst": "N2"}]
  }
}
```

- [x] **Step 2: Add validation helper**

In `src/daydream/schemas.py`:

```python
def _validate_causal_graph(payload: dict[str, Any]) -> None:
    graph = payload.get("causal_graph")
    if not isinstance(graph, dict):
        raise ValueError("causal_graph must be an object")
    nodes = graph.get("nodes")
    edges = graph.get("edges")
    if not isinstance(nodes, list) or not nodes:
        raise ValueError("causal_graph.nodes must be a non-empty list")
    if not isinstance(edges, list) or not edges:
        raise ValueError("causal_graph.edges must be a non-empty list")
    node_ids = {node.get("id") for node in nodes if isinstance(node, dict)}
    for edge in edges:
        if edge.get("src") not in node_ids or edge.get("dst") not in node_ids:
            raise ValueError("causal_graph edge references unknown node")
```

Call it inside `validate_card`.

- [x] **Step 3: Update extraction prompt**

Modify `prompts/extract_structure.md`:

```markdown
- `causal_graph`
```

Add:

```markdown
Represent the mechanism as a small directed causal graph. Use 3-7 nodes. Edges must describe cause, enablement, blocking, dependency, reversal, containment, or contrast.
```

- [x] **Step 4: Update comparison prompt**

Add to `prompts/compare_cards.md`:

```markdown
Compare the causal graphs before writing `shared_structure`. If causal arrows point in opposite directions, reject or near_miss even when vocabulary overlaps.
```

- [x] **Step 5: Verify card validation**

Run:

```bash
python3 -m unittest tests/test_core_behaviors.py tests/test_v2_gates.py
```

Expected: all fixture cards in tests now include valid causal graphs and pass.

---

### Task 6: Add Constellation Model After Pairwise Gates Pass

**Files:**
- Modify: `src/daydream/schemas.py`
- Modify: `src/daydream/artifacts.py`
- Modify: `src/daydream/cli.py`
- Create: `prompts/constellation.md`
- Test: `tests/test_constellation.py`

- [x] **Step 1: Add a schema-level test**

Create `tests/test_constellation.py`:

```python
import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from daydream.artifacts import save_constellation_report
from daydream.runs import resolve_run_dir, start_run
from daydream.workspace import init_workspace


class ConstellationTests(unittest.TestCase):
    def test_constellation_requires_three_or_more_documents_and_evidence_network(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            init_workspace(root)
            run = start_run(root, "tag-bridge")
            report = root / "constellation.json"
            report.write_text(
                json.dumps(
                    {
                        "run_id": run["run_id"],
                        "seed_doc_id": "a",
                        "resonance_doc_ids": ["b", "c"],
                        "epistemic_nexus": "Local constraints restore global control.",
                        "isomorphism_network": {"a": {"b": 0.82, "c": 0.78}},
                        "evidence_network": [
                            {"doc_id": "a", "span": "first evidence"},
                            {"doc_id": "b", "span": "second evidence"},
                            {"doc_id": "c", "span": "third evidence"},
                        ],
                        "mismatch_notes": "The third document is weaker on causality.",
                    }
                ),
                encoding="utf-8",
            )

            result = save_constellation_report(root, run["run_id"], report)

            self.assertTrue((resolve_run_dir(root, "latest") / "constellation_report.json").exists())
            self.assertIn("constellation_report.json", result["saved"])
```

- [x] **Step 2: Implement constellation validation**

Add to `src/daydream/schemas.py`:

```python
CONSTELLATION_REQUIRED = {
    "run_id",
    "seed_doc_id",
    "resonance_doc_ids",
    "epistemic_nexus",
    "isomorphism_network",
    "evidence_network",
    "mismatch_notes",
}


def validate_constellation_report(payload: dict[str, Any]) -> dict[str, Any]:
    missing = _missing(payload, CONSTELLATION_REQUIRED)
    if missing:
        raise ValueError(f"Constellation report missing required fields: {', '.join(missing)}")
    if not isinstance(payload.get("resonance_doc_ids"), list) or len(payload["resonance_doc_ids"]) < 2:
        raise ValueError("resonance_doc_ids must include at least two documents")
    if not isinstance(payload.get("evidence_network"), list) or len(payload["evidence_network"]) < 3:
        raise ValueError("evidence_network must include at least three evidence links")
    return payload
```

- [x] **Step 3: Add save command**

Modify `src/daydream/artifacts.py`:

```python
from .schemas import validate_constellation_report


def save_constellation_report(root: Path, run: str, input_path: Path) -> dict[str, Any]:
    payload = validate_constellation_report(read_json(input_path))
    run_path = resolve_run_dir(root, run)
    out = run_path / "constellation_report.json"
    write_json(out, payload)
    update_manifest(root, run, artifacts={"constellation_report": "constellation_report.json"})
    return {"saved": str(out)}
```

Modify `src/daydream/cli.py` to add `save-constellation-report`.

- [x] **Step 4: Add constellation prompt**

Create `prompts/constellation.md`:

```markdown
# Constellation Report

Return strict JSON only.

Build this only after at least one pairwise resonance has passed hard gates. A constellation must include one seed document and at least two additional documents from different surface domains. The output must explain the epistemic nexus that unifies the cluster, list pairwise limits, and include an evidence network with exact spans from at least three documents.
```

- [x] **Step 5: Verify constellation support**

Run:

```bash
python3 -m unittest tests/test_constellation.py tests/test_core_behaviors.py
```

Expected: constellation report saves and existing run behavior still passes.

---

## Execution Order

1. Task 1: sample parser, because it creates the calibration surface.
2. Task 2: hard gates, because false positives are more damaging than missed discoveries.
3. Task 3: candidate pool, because it reduces early stopping after the gate is safe.
4. Task 4: near-miss archive, because it improves unattended runs over time.
5. Task 5: causal graph lite, because it adds topology checking without jumping straight to heavy graph algorithms.
6. Task 6: constellation model, because multi-document synthesis is only valuable after pairwise judgment is trustworthy.

## Verification Before Calling V2 Done

Run:

```bash
python3 -m unittest discover -s tests
PYTHONPATH=src python3 -m daydream eval-samples
PYTHONPATH=src python3 -m daydream doctor
PYTHONPATH=src python3 -m daydream index
PYTHONPATH=src python3 -m daydream start-run --strategy auto
PYTHONPATH=src python3 -m daydream candidate-pool --collection corpus --target-size 50 --no-rerank "lex: 统帅" "lex: 流水线" "lex: 验收"
```

V2 is complete only when:

- The 30 sample fixtures load with correct labels.
- Negative and near-miss examples cannot be saved as accepted without test failure.
- Accepted runs require evidence from both sides and critic thresholds.
- Draft saving fails unless the critic accepted.
- Candidate pools are saved before pair selection.
- Rejected and near-miss reports are archived for future calibration.
- Current real corpus can still produce either an accepted draft or a useful rejection.
