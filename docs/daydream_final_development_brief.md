# Daydream Final Development Brief

**Date**: 2026-05-20

## 1. Project Definition

Daydream is a local, schedulable agent skill that lets a curated personal corpus keep working in the background. It samples from saved materials, searches for deep structural resonance between otherwise distant documents, rejects weak or forced connections, and writes grounded synthesis drafts when a connection is strong enough.

The project is inspired by Ambien.ai, but it should not be a clone of Ambien's private implementation. The target is behavioral reproduction and practical improvement: make the loop installable, inspectable, testable, and portable across agent tools.

### One-Sentence Product Goal

Turn a user's curated local knowledge base into an installable daydreaming skill that can run manually or on cron, discover non-obvious structural connections, and save useful synthesis drafts with an auditable trail.

## 2. Primary Users

The first user is a technically comfortable personal knowledge worker who keeps Markdown notes, saved links, transcripts, essays, and research fragments locally.

The second user is an agent-tool user who wants the same capability available inside Hermes, OpenClaw, Codex, Claude Code, or similar tools without rebuilding the project for each host.

## 3. Target Platforms

Priority order:

1. Hermes Agent
2. OpenClaw
3. Codex
4. Claude Code
5. Plain shell or system cron as fallback

The project should be built around a portable core. Hermes and OpenClaw are priority host integrations, but the core commands, file layout, prompts, and skill instructions should not be locked to one host.

## 4. What This Project Must Do

MVP must:

1. Initialize a standard local workspace.
2. Check whether required tools are installed.
3. Index a local Markdown corpus through qmd.
4. Start a daydream run and record its strategy.
5. Retrieve candidate documents from the local corpus.
6. Let the host agent model extract structure cards.
7. Save structure cards with strict validation.
8. Compare structure cards and save a resonance report.
9. Run a critic step that can accept, reject, or mark near miss.
10. Write a synthesis draft only when the critic accepts.
11. Save every important intermediate artifact.
12. Provide an inspect command for the latest run.
13. Run manually from the command line.
14. Run through Hermes skill.
15. Run unattended through Hermes cron.

The MVP is complete only when it can run end to end on a small real corpus and produce either an accepted draft or a clear rejection record.

## 5. What This Project Must Not Do In MVP

MVP must not:

1. Build a web app.
2. Build a database service.
3. Build its own embedding system.
4. Add Chroma, Faiss, LanceDB, Qdrant, or similar storage in the first version.
5. Call OpenAI, Anthropic, Ollama, OpenRouter, or any model provider directly from Python.
6. Hide model behavior inside the local CLI.
7. Treat topical similarity as structural resonance.
8. Feed generated drafts back into the primary corpus by default.
9. Publish or send drafts anywhere without explicit user configuration.

These constraints keep the project small, installable, and faithful to the desired agent-skill shape.

## 6. Core Design Principle

The project has three layers:

| Layer | Component | Responsibility |
|---|---|---|
| Brain | Host agent model | Strategy choice, abstraction, comparison, critic judgment, writing |
| Retrieval | qmd | Local search over raw corpus and structure cards |
| Hands and ledger | Python CLI | Setup, checks, qmd wrapper, validation, file saving, run history, inspection |

The Python CLI is a tool layer. It must be deterministic, fast, and boring. The host agent performs the thinking and writing.

## 7. Corpus Model

Use two searchable bodies of material:

1. `corpus/`: user-curated primary materials.
2. `cards/`: generated structure cards derived from primary materials.

Generated drafts live in `drafts/` and must be excluded from primary corpus indexing by default. Draft metadata can be used for anti-repetition, but drafts should not silently become primary evidence.

Recommended initial corpus:

1. 20-50 Markdown documents.
2. Mixed Chinese and English is allowed.
3. Documents should be manually selected for quality.
4. Avoid dumping a large uncurated archive into the first test.

Required evaluation fixtures:

1. 5 known-good resonance examples.
2. 5 known-bad or forced resonance examples.
3. A small expected-output note for each example explaining why it should pass or fail.

## 8. Standard File Layout

```text
daydream/
├─ README.md
├─ pyproject.toml
├─ qmd.yml
├─ corpus/
├─ cards/
│  ├─ cards.jsonl
│  └─ by_doc/
├─ runs/
│  ├─ latest
│  └─ <run_id>/
│     ├─ manifest.json
│     ├─ qmd_results.json
│     ├─ cards.jsonl
│     ├─ pair_report.json
│     ├─ critic_report.json
│     ├─ draft.md
│     └─ rejection_report.md
├─ drafts/
├─ prompts/
│  ├─ extract_structure.md
│  ├─ compare_cards.md
│  ├─ critic.md
│  └─ draft_essay.md
├─ src/daydream/
│  ├─ __init__.py
│  ├─ cli.py
│  ├─ config.py
│  ├─ qmd.py
│  ├─ runs.py
│  ├─ schemas.py
│  └─ fs.py
├─ skills/
│  ├─ common/daydream/SKILL.md
│  ├─ hermes/daydream/SKILL.md
│  └─ openclaw/daydream/SKILL.md
└─ tests/
```

The `common` skill is the portable source of truth. Hermes and OpenClaw wrappers may add host-specific metadata, install paths, and cron examples.

## 9. CLI Contract

The command name should be:

```bash
daydream
```

Required MVP commands:

```bash
daydream init
daydream doctor
daydream index
daydream qmd-query --collection corpus --limit 12 "query text"
daydream start-run --strategy auto
daydream save-card --run <run_id> --doc <doc_id> --input <json_file>
daydream save-pair-report --run <run_id> --input <json_file>
daydream save-critic-report --run <run_id> --input <json_file>
daydream save-draft --run <run_id> --title <title> --input <markdown_file>
daydream save-rejection --run <run_id> --input <markdown_file>
daydream inspect --run latest
daydream validate --run latest
```

Behavior rules:

1. Commands should print machine-readable JSON where host agents need to consume output.
2. Commands should print clear human summaries for `doctor`, `inspect`, and `validate`.
3. Save commands must validate input before writing.
4. Failed validation must not create partial final artifacts.
5. `runs/latest` must always point to the newest run.
6. `doctor` must report missing qmd, missing host agent tools, missing corpus, missing prompt files, and cron readiness where detectable.

## 10. Daydream Run Flow

Standard run:

1. Host agent invokes the skill.
2. Skill runs `daydream doctor`.
3. Skill runs `daydream start-run --strategy auto`.
4. CLI chooses or records one strategy.
5. Host agent selects a seed according to the strategy.
6. Host agent produces one or more abstract search queries.
7. Skill runs `daydream qmd-query`.
8. Host agent reads the retrieved candidate snippets.
9. Host agent extracts structure cards.
10. Skill saves the cards.
11. Host agent compares card pairs.
12. Skill saves the pair report.
13. Host agent runs critic judgment.
14. Skill saves critic report.
15. If accepted, host agent writes a draft and skill saves it.
16. If rejected, host agent writes a rejection report and skill saves it.
17. Skill returns a short run summary.

The system must treat "nothing good found" as a valid outcome.

## 11. Exploration Strategies

MVP strategies:

1. `random-collision`: force distant materials to meet.
2. `tag-bridge`: use tags or taxonomy-like labels to bridge vocabulary gaps.
3. `temporal-bridge`: connect older materials with newer materials.

Strategy balancing:

1. Read recent run metadata.
2. Prefer the least-used strategy.
3. Allow explicit override with `--strategy`.
4. Record strategy in run manifest and draft frontmatter.

Later strategies can be added only after MVP proves that the basic loop works.

## 12. Structure Card

A structure card is not a summary. It is a compact representation of how a document works.

Required fields:

1. `card_id`
2. `doc_id`
3. `title`
4. `source_layer` or `source_type`
5. `surface_topic`
6. `central_tension`
7. `mechanism`
8. `failure_mode`
9. `solution_pattern`
10. `roles`
11. `relations`
12. `abstractions`
13. `evidence_spans`

Multilingual rule:

1. Surface fields may keep the original language.
2. Higher-level abstractions should use normalized English labels.
3. Evidence spans must preserve exact source language.

This supports Chinese-English mixed corpora without losing original evidence.

## 13. Pair Report

The pair report explains why two documents are structurally related.

Required fields:

1. `run_id`
2. `seed_doc_id`
3. `candidate_doc_id`
4. `shared_structure`
5. `role_alignments`
6. `surface_distance`
7. `structural_alignment_score`
8. `novelty_score`
9. `mismatch_notes`

The pair report must explain both the similarity and the limits of the analogy.

## 14. Critic Report

The critic decides whether the system is allowed to write.

Required verdicts:

1. `accept`
2. `reject`
3. `near_miss`

Required scoring dimensions:

1. Grounded evidence
2. Role alignment
3. Non-triviality
4. Surface independence
5. Causal or mechanism alignment

Acceptance rule:

1. Mean score must be at least 4 out of 5.
2. Evidence must exist on both sides.
3. The pair must not be mostly same-topic similarity.
4. The critic must include mismatch notes.

If the critic rejects the pair, the run is still useful and should be saved.

## 15. Draft Rules

Drafts must:

1. Be Markdown.
2. Include frontmatter with run id, strategy, source documents, verdict, and timestamp.
3. Open from a concrete example, not abstract system language.
4. Explain the shared structure.
5. Include a section on where the analogy breaks.
6. Avoid describing the pipeline to the reader.
7. Avoid sounding like a generic research summary.

Drafts are working outputs, not final publishable essays.

## 16. Host Skill Packaging

### Common Skill

The common skill contains:

1. When to use Daydream.
2. The standard run procedure.
3. Required CLI commands.
4. Prompt references.
5. Verification rules.
6. Expected output format.

### Hermes Package

Hermes package adds:

1. Hermes metadata.
2. Required terminal toolset.
3. Project root configuration.
4. Cron examples.
5. Local delivery examples.
6. Install instructions for Hermes skill directory or tap repo.

### OpenClaw Package

OpenClaw package adds:

1. OpenClaw skill metadata if required by its current format.
2. Tool permissions needed for shell commands.
3. Cron or scheduled-run instructions.
4. Install instructions.

### Codex and Claude Code

Initial support can be documented as portable installation:

1. Install the CLI.
2. Place the common skill instructions where the host expects skills or project instructions.
3. Use system cron, host automation, or manual runs until first-class scheduling is verified.

Do not block Hermes and OpenClaw MVP on perfect support for every host.

## 17. Environment Requirements

Required:

1. macOS or Linux.
2. Python 3.11 or newer.
3. uv or another Python environment manager.
4. Node.js.
5. qmd.
6. A host agent with terminal command access.
7. A model configured in the host agent.
8. A local Markdown corpus.

Recommended:

1. Bun, if qmd or related tooling benefits from it.
2. Local embedding model suitable for Chinese-English mixed text.
3. Git, for reviewing changes to cards, runs, and drafts.
4. A long-running machine if cron is expected to fire unattended.

Current local machine status observed before this brief:

1. Python is installed.
2. Node is installed.
3. Bun is installed.
4. uv is installed.
5. qmd is not installed.
6. hermes is not installed.
7. openclaw is not installed.

## 18. Development Phases

### Phase 0: Brief and Fixtures

Deliver:

1. Final development brief.
2. Small sample corpus.
3. Five good cases.
4. Five bad cases.
5. Expected judgment notes.

Exit criteria:

1. A developer can start without reading every research document.
2. The project has clear pass/fail examples.

### Phase 1: Local CLI Skeleton

Deliver:

1. Python package.
2. CLI entrypoint.
3. `init`.
4. `doctor`.
5. run directory management.
6. schema validation.
7. inspect command.
8. base tests.

Exit criteria:

1. `daydream init` creates the expected layout.
2. `daydream doctor` reports environment status clearly.
3. `daydream start-run` creates a run.
4. `daydream inspect --run latest` works.

### Phase 2: qmd Integration

Deliver:

1. qmd config generation.
2. draft exclusion rule.
3. `index`.
4. `qmd-query`.
5. saved qmd result artifact.

Exit criteria:

1. A real Markdown corpus can be indexed.
2. qmd query results are saved under the current run.
3. generated drafts are not indexed as primary corpus.

### Phase 3: Skill Loop

Deliver:

1. common `SKILL.md`.
2. Hermes `SKILL.md`.
3. prompt files.
4. save-card command.
5. save-pair-report command.
6. save-critic-report command.
7. save-draft and save-rejection commands.

Exit criteria:

1. Hermes can discover the skill.
2. A manual skill run completes with either draft or rejection.
3. All intermediate artifacts are saved.

### Phase 4: Cron and Unattended Run

Deliver:

1. Hermes cron instructions.
2. run script for scheduled execution.
3. local delivery summary.
4. failure logging.

Exit criteria:

1. A scheduled run fires without user interaction.
2. The next morning, `daydream inspect --run latest` shows what happened.
3. A failed run leaves a useful reason instead of silently disappearing.

### Phase 5: OpenClaw and Portability

Deliver:

1. OpenClaw package.
2. OpenClaw install instructions.
3. portable skill README.
4. fallback shell cron instructions.

Exit criteria:

1. The same core project can be run from OpenClaw.
2. Host-specific differences are documented outside the core logic.

## 19. Verification Plan

Before reporting MVP as done, verify:

1. `daydream init` works in a clean test folder.
2. `daydream doctor` detects missing tools correctly.
3. qmd indexing works on a sample corpus.
4. `daydream qmd-query` returns usable JSON.
5. `daydream start-run` creates a run and updates latest.
6. valid card JSON is saved.
7. invalid card JSON is rejected.
8. pair report validation works.
9. critic report validation works.
10. accepted runs save drafts.
11. rejected runs save rejection reports.
12. inspect summarizes both accepted and rejected runs.
13. drafts are excluded from primary indexing.
14. Hermes skill can complete a manual run.
15. Hermes cron can complete an unattended run.

Good-case tests must demonstrate that the system can find at least one non-obvious connection. Bad-case tests must demonstrate that it can refuse at least one tempting but weak connection.

## 20. Release Criteria

The first usable release is ready when:

1. A user can install the CLI.
2. A user can install the Hermes skill.
3. A user can point it at a Markdown corpus.
4. A user can run one manual daydream cycle.
5. A user can schedule one unattended cycle.
6. The system writes a draft or rejection report.
7. The user can inspect what happened.
8. The docs explain setup, run, inspect, and troubleshooting.

The first release does not need a dashboard, publisher, web UI, or perfect multi-agent portability.

## 21. Main Risks

### Risk: The project becomes normal search plus summary

Mitigation:

1. Force structure cards.
2. Force role and relation comparison.
3. Reject same-topic matches unless the structural case is independently strong.
4. Keep bad cases in tests.

### Risk: The model forces analogies

Mitigation:

1. Require evidence from both sides.
2. Require mismatch notes.
3. Make rejection a normal outcome.
4. Track near misses.

### Risk: Generated output pollutes the corpus

Mitigation:

1. Exclude `drafts/` from qmd primary indexing.
2. Keep generated drafts as memory only.
3. Make re-indexing generated work an explicit future feature.

### Risk: Portability slows down MVP

Mitigation:

1. Build a portable core.
2. Ship Hermes first.
3. Add OpenClaw second.
4. Document Codex and Claude Code as later adapters.

### Risk: Setup is too hard

Mitigation:

1. Make `doctor` excellent.
2. Provide exact install steps.
3. Fail with clear messages.
4. Start with a small sample corpus.

## 22. Recommended Immediate Next Step

Create the implementation skeleton:

1. `pyproject.toml`
2. `src/daydream/`
3. `daydream init`
4. `daydream doctor`
5. `daydream start-run`
6. `daydream inspect`
7. `skills/common/daydream/SKILL.md`
8. minimal tests

Do not start with cron. First make one manual run auditable.

## 23. V2 Hardening Addendum

After the first MVP run on real corpus, the main remaining risk is not setup. It is false acceptance: forced resonance, same-domain boring analogy, and early stopping on a small candidate set.

The V2 plan is now explicit in `docs/superpowers/plans/2026-05-20-daydream-v2-hardening.md`.

Priority order:

1. Convert `docs/resonance_samples/` into regression fixtures.
2. Add hard gates for per-side evidence, critic score thresholds, and draft permission.
3. Add a wide candidate pool before pair selection.
4. Archive rejected and near-miss runs for future critic calibration.
5. Add causal graph consistency checks.
6. Add constellation reports only after pairwise gates are reliable.

V2 should not be considered complete until negative and near-miss examples fail closed, accepted runs require hard evidence from both sides, and candidate selection no longer depends on the first few qmd hits.

## 24. V3 Final Product Direction

V2 is not the final product shape. It is a temporary safety scaffold that provided evidence binding, rejection gates, causal graphs, and audit logs.

The final Daydream shape is V3: an unsupervised corpus-field system that starts from 25-50 documents, builds a resonance graph, finds clusters, rejects forced edges through adversarial review, and writes from systemic archetypes rather than document pairs.

V2 has three known structural limitations:

1. It remains mostly pairwise even after adding candidate pools.
2. A single critic can still be too cooperative with forced analogies.
3. The first constellation report is still seed-centered.

The V3 roadmap is captured in `docs/daydream_v3_architecture_blueprint.md`.

V3 should focus on:

1. Making `dream-run` the main user-facing flow.
2. Matrix alignment across a bounded corpus subset.
3. Red-blue adversarial critique before acceptance.
4. Hypergraph mesh reports that connect 3 or more documents without a permanent seed center.

After V3 stabilizes, V2 pairwise commands should be hidden from the main skill path or retained only as internal edge-debugging tools.

## 25. Source Materials

This brief consolidates the local research documents in `docs/` and the public product behavior described by:

1. Ambien.ai homepage: https://ambien.ai/
2. Ambien.ai about page: https://ambien.ai/about
3. Gwern's LLM Daydreaming essay: https://gwern.net/ai-daydreaming
4. qmd project: https://github.com/tobi/qmd
5. Hermes Agent documentation: https://hermes-agent.nousresearch.com/docs/
6. OpenClaw documentation: https://docs.openclaw.ai/
