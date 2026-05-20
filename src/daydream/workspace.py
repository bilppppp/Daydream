from __future__ import annotations

import shutil
from pathlib import Path
from typing import Any

from .fs import ensure_dir

PROMPTS = {
    "extract_structure.md": """# Extract Structure Card

Return strict JSON only.

Extract a structure card from the provided source text. Do not summarize the text as a topic. Extract the roles, relations, constraints, mechanism, failure mode, solution pattern, abstraction levels, and evidence spans that make the document structurally useful.

Required JSON fields:

- `card_id`
- `doc_id`
- `title`
- `source_type`
- `surface_topic`
- `central_tension`
- `mechanism`
- `failure_mode`
- `solution_pattern`
- `roles`
- `relations`
- `abstractions`
- `evidence_spans`
- `causal_graph`

Rules:

- Keep concrete fields in the source language.
- Normalize high-level abstractions into concise English labels.
- Evidence spans must be exact snippets from the source text.
- Represent the mechanism as a small directed causal graph. Use 3-7 nodes. Edges must describe cause, enablement, blocking, dependency, reversal, containment, or contrast.
- If evidence is thin, say so in the fields instead of inventing support.
""",
    "compare_cards.md": """# Compare Structure Cards

Return strict JSON only.

Compare two structure cards for structural resonance. Prefer relation, role, constraint, causal graph, and failure-mode alignment over topical similarity.

Required JSON fields:

- `run_id`
- `seed_doc_id`
- `candidate_doc_id`
- `shared_structure`
- `role_alignments`
- `surface_distance`
- `structural_alignment_score`
- `novelty_score`
- `mismatch_notes`
- `seed_evidence_spans`
- `candidate_evidence_spans`

Rules:

- Compare the causal graphs before writing `shared_structure`. If causal arrows point in opposite directions, reject or near_miss even when vocabulary overlaps.
- Reward cross-domain distance only after structural alignment is real.
- Penalize same-topic overlap.
- Always explain where the analogy breaks.
- Include at least two exact evidence spans from the seed document and two from the candidate document.
- If either side lacks evidence, set low scores and prefer reject or near_miss.
- Do not write an essay in this step.
""",
    "critic.md": """# Critic

Return strict JSON only.

Judge whether the proposed pair deserves a synthesis draft.

Required JSON fields:

- `run_id`
- `scores`
- `mismatch_notes`
- `verdict`
- `rationale`

Scoring dimensions:

- `grounded_evidence`
- `role_alignment`
- `non_triviality`
- `surface_independence`
- `causal_alignment`

Verdict values:

- `accept`
- `reject`
- `near_miss`

Rules:

Before accepting, compare this pair against recent rejected and near-miss cases from `calibration/near_miss_archive.jsonl` when available. If the current pair repeats a known rejection tag such as surface lexical trap, contradictory causality, same-domain summary, textbook metaphor, or cliché analogy, do not accept.

- `accept` requires mean score >= 4.0.
- `accept` requires `grounded_evidence >= 4`.
- `accept` requires `surface_independence >= 3`.
- `near_miss` is mandatory for plausible but same-domain, clichéd, or low-novelty pairs.
- Reject if the pair is mostly same-topic similarity.
- Reject if evidence spans do not support the role map.
- Use `near_miss` when the connection is interesting but not strong enough for an essay.
- A draft is allowed only when the verdict is `accept`.
""",
    "draft_essay.md": """# Draft Essay

Write a grounded Markdown draft only after the critic accepts.

Rules:

- Include frontmatter with run id, strategy, source documents, verdict, and timestamp.
- Open from a concrete example.
- Explain the shared structure.
- Include a section on where the analogy breaks.
- Do not describe the Daydream pipeline to the reader.
- Do not sound like a generic research summary.
""",
    "constellation.md": """# Constellation Report

Return strict JSON only.

Build this only after at least one pairwise resonance has passed hard gates. A constellation must include one seed document and at least two additional documents from different surface domains. The output must explain the epistemic nexus that unifies the cluster, list pairwise limits, and include an evidence network with exact spans from at least three documents.
""",
}

COMMON_SKILL = """---
name: daydream
description: Find structural resonance in a local corpus and save grounded drafts or rejection reports.
platforms: [macos, linux]
---

# Daydream

Use this skill when the user wants a curated local Markdown corpus to search for non-obvious structural connections and save a grounded draft or rejection report.

## Procedure

1. Run `daydream doctor`.
2. Run `daydream start-run --strategy auto`.
3. Select a seed document or theme from `corpus/`.
4. Produce 3-5 abstract search queries that target mechanisms, roles, tensions, constraints, and failure modes rather than surface topic.
5. Run `daydream candidate-pool --collection corpus --target-size 50 "<query1>" "<query2>" "<query3>"`.
6. Select candidates from the saved pool, preferring structural fit plus surface distance.
7. Read the retrieved snippets and source passages needed for evidence.
8. Extract structure cards using `prompts/extract_structure.md`.
9. Save cards with `daydream save-card`.
10. Compare cards using `prompts/compare_cards.md`.
11. Save the pair report.
12. Run the critic using `prompts/critic.md`.
13. Save either a draft with `daydream save-draft` or a rejection with `daydream save-rejection`.
14. Run `daydream inspect --run latest` and `daydream validate --run latest`.

## Required Card Shape

Structure cards must include central tension, mechanism, failure mode, solution pattern, roles, relations, abstractions, causal graph, and exact evidence spans.

## Draft Gate

Draft only when the critic accepts. For reject or near miss, write a short rejection report explaining what was tempting and why it failed.

## Verification

- Do not draft unless the critic accepts.
- Always include evidence spans from both sides.
- Always include mismatch notes.
- Treat rejection as a valid run result.
- Validate the latest run before reporting completion.
"""

HERMES_SKILL = """---
name: daydream
description: Hermes wrapper for Daydream structural resonance.
version: 0.1.0
platforms: [macos, linux]
metadata:
  hermes:
    category: research
    tags: [resonance, qmd, writing, local-corpus]
    requires_toolsets: [terminal]
---

# Daydream Hermes Wrapper

Follow the common Daydream procedure. Use Hermes as the brain and the Daydream CLI as the local tool layer.

## Setup

1. Put this wrapper where Hermes discovers skills.
2. Keep `skills/common/daydream/SKILL.md` available as the shared procedure.
3. Set the working directory to the Daydream project root.
4. Confirm `daydream doctor` and `daydream index` work before scheduling.

## Cron Example

```text
/cron add "0 6 * * *" "Run Daydream over my local corpus. Save a draft only if the critic accepts; otherwise save a rejection report." --skill daydream --deliver local
```

After a cron run, inspect the result with `daydream inspect --run latest` and check `logs/` if the scheduled host writes local logs.
"""

OPENCLAW_SKILL = """---
name: daydream
description: OpenClaw wrapper for Daydream structural resonance.
version: 0.1.0
---

# Daydream OpenClaw Wrapper

Use the terminal tool to run the Daydream CLI. Keep all generated artifacts local.

## Setup

1. Put this wrapper where OpenClaw discovers skills.
2. Keep `skills/common/daydream/SKILL.md` available as the shared procedure.
3. Set the working directory to the Daydream project root.
4. Confirm `daydream doctor`, `daydream index`, and one manual run work before scheduling.

For scheduled runs, ask OpenClaw to follow the common Daydream procedure and finish by running `daydream inspect --run latest` and `daydream validate --run latest`.
"""


def init_workspace(root: Path) -> dict[str, Any]:
    root = root.resolve()
    for relpath in [
        "corpus",
        "calibration",
        "cards/by_doc",
        "runs",
        "drafts",
        "prompts",
        "scripts",
        "skills/common/daydream",
        "skills/hermes/daydream",
        "skills/openclaw/daydream",
        "tests",
    ]:
        ensure_dir(root / relpath)

    _write_if_missing(root / "cards/cards.jsonl", "")
    _write_if_missing(root / "README.md", _readme_text())
    _write_if_missing(root / "qmd.yml", _qmd_config())
    _write_if_missing(root / "scripts/daydream-cron.sh", _cron_script_text())
    for filename, content in PROMPTS.items():
        _write_if_missing(root / "prompts" / filename, content)
    _write_if_missing(root / "skills/common/daydream/SKILL.md", COMMON_SKILL)
    _write_if_missing(root / "skills/hermes/daydream/SKILL.md", HERMES_SKILL)
    _write_if_missing(root / "skills/openclaw/daydream/SKILL.md", OPENCLAW_SKILL)
    return {"root": str(root), "created": True}


def doctor(root: Path) -> dict[str, Any]:
    root = root.resolve()
    tools = {name: shutil.which(name) for name in ["qmd", "hermes", "openclaw", "codex", "claude"]}
    required_dirs = ["corpus", "cards", "runs", "drafts", "prompts"]
    prompt_files = [root / "prompts" / name for name in PROMPTS]
    return {
        "root": str(root),
        "tools": {name: {"available": path is not None, "path": path} for name, path in tools.items()},
        "workspace": {
            "initialized": all((root / relpath).exists() for relpath in required_dirs),
            "qmd_initialized": (root / ".qmd").exists(),
            "prompt_files_ok": all(path.exists() for path in prompt_files),
            "corpus_files": len(list((root / "corpus").glob("**/*.md"))) if (root / "corpus").exists() else 0,
        },
    }


def _write_if_missing(path: Path, content: str) -> None:
    ensure_dir(path.parent)
    if not path.exists():
        path.write_text(content, encoding="utf-8")


def _qmd_config() -> str:
    return """# Daydream qmd configuration
collections:
  corpus:
    path: corpus
    include:
      - "**/*.md"
    exclude:
      - "../drafts/**"
      - "drafts/**"
  cards:
    path: cards
    include:
      - "**/*.md"
      - "**/*.jsonl"
"""


def _readme_text() -> str:
    return """# Daydream Workspace

This workspace stores a curated corpus, generated structure cards, run history, logs, and drafts.

Start with:

```bash
daydream doctor
daydream index
daydream start-run --strategy auto
```

Then let the host agent follow `skills/common/daydream/SKILL.md`.

Generated drafts are excluded from primary corpus indexing by default.
"""


def _cron_script_text() -> str:
    return """#!/usr/bin/env sh
set -eu

SCRIPT_DIR=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
ROOT=${DAYDREAM_ROOT:-$(CDPATH= cd -- "$SCRIPT_DIR/.." && pwd)}
LOG_DIR=${DAYDREAM_LOG_DIR:-"$ROOT/logs"}
STAMP=$(date "+%Y%m%d_%H%M%S")
LOG_FILE="$LOG_DIR/daydream_$STAMP.log"

mkdir -p "$LOG_DIR"

run_daydream() {
  cd "$ROOT"
  export PYTHONPATH=${DAYDREAM_PYTHONPATH:-"$ROOT/src"}

  echo "daydream root: $ROOT"
  echo "started at: $(date)"
  python3 -m daydream doctor
  python3 -m daydream index

  if [ -z "${DAYDREAM_AGENT_CMD:-}" ]; then
    echo "DAYDREAM_AGENT_CMD is not set. Configure it to run your host agent with the daydream skill."
    return 2
  fi

  sh -c "$DAYDREAM_AGENT_CMD"
  python3 -m daydream inspect --run latest
  python3 -m daydream validate --run latest
}

if run_daydream >"$LOG_FILE" 2>&1; then
  echo "daydream cron run ok: $LOG_FILE"
else
  status=$?
  echo "daydream cron run failed with status $status: $LOG_FILE" >&2
  exit "$status"
fi
"""
