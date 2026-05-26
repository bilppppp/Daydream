---
name: daydream
description: Dream over a local corpus by expanding concepts from one random seed with qmd semantic search and writing an article plus a constellation.
platforms: [macos, linux]
---

# Daydream

Daydream turns a local corpus into a bounded dreaming surface. Start from one eligible random seed document, extract a seed card that exposes its concepts, mechanisms, tensions, failure modes, and questions, use qmd to search the user's intended corpus for semantic echoes, rank the valid connections, then write a readable article with its JSON seed card and JSON constellation.

This is not a summary skill and not a host-only free association exercise. A normal dream is grounded in qmd retrieval from the corpus the user asked to dream over. The host can wander in the writing, but the search trail, connection strengths, and constellation must remain inspectable.

## When This Skill Activates

Use this skill when the user asks an agent host to:

- dream, daydream, free-associate, or write from a local corpus,
- find unexpected resonance across notes, essays, transcripts, bookmarks, or other local documents,
- run the same dreaming workflow manually or on a schedule,
- produce an article plus a saved map of the source concepts and connections behind it.

## Required Inputs

Normal Daydream needs:

1. a corpus directory for seed selection and source reading,
2. the qmd collection name that represents that intended corpus,
3. whether the dream is manual or scheduled,
4. qmd runtime environment details when the host or scheduler needs them, such as `PATH`, `QMD_FORCE_CPU`, or `HF_ENDPOINT`,
5. an output directory only when the default skill `output/` directory should be overridden.

Do not treat a corpus path and a qmd collection as interchangeable. The corpus path bounds local seed handling. The qmd collection bounds normal semantic search.

## Division Of Labor

- The user chooses the corpus, qmd collection, schedule intent, and any explicit permission to widen search scope or accept degraded output.
- qmd retrieves semantically related corpus material and supplies the retrieval ordering and scores that seed ranking judgment.
- The bundled helper script fixes repeatable mechanical steps: corpus checks, eligible seed selection, qmd command invocation, JSON validation, and linked output saving.
- The host reads the seed and retrieved material, writes the seed card, chooses semantic search directions, rejects topic-only overlap, ranks surviving connections, writes the article, and creates the constellation.

The helper script must not decide what a seed means, invent connections, or write the article. The host must not pretend it performed normal Daydream when qmd did not provide the search surface.

Use the bundled helper script for repeatable mechanical steps. Resolve `<skill-dir>` to this installed Daydream skill directory:

```bash
python3 <skill-dir>/scripts/daydream.py --help
```

## Core Workflow

1. Get the corpus path and qmd collection name. For scheduled dreams, also resolve `no_qmd_policy`.
2. Start a run ledger row with `runs start` so failures and cancellations remain discoverable.
3. Check the corpus and qmd readiness, then randomly select one eligible seed document.
4. Read the seed and create a JSON seed card that matches the template.
5. Expand the seed card into multiple qmd hybrid searches inside the named collection. Search from concepts, mechanisms, failure modes, tensions, claims, and dream questions rather than one surface topic.
6. Read retrieved material. Drop directions in `avoid_searching_for` and reject results that stay at topic-only overlap.
7. Rank every meaningful surviving connection. The constellation keeps the accepted ranked set even when the article uses only a subset.
8. Write the article, then check that its treatment of the seed still aligns with the seed card `core_claim` and `evidence_spans`.
9. Validate and save the Markdown article, JSON seed card, and JSON constellation together under one completion-time and keyword folder, using the run id when one was started.

Read `references/dream-flow.md` before executing the full sequence.

## Run Ledger

The helper keeps a fixed CSV run ledger at `<skill-dir>/output/daydream-runs.csv`. This is a run index, not a dream artifact and not a semantic log.

The ledger only helps hosts discover runs and the saved three-file paths. Keep it to these fields: `run_id`, `started_at`, `ended_at`, `status`, `trigger`, `dream_dir`, `article_path`, `seed_card_path`, and `constellation_path`.

Do not write dream summaries, weather, year rings, anti-dream notes, seed paths, corpus paths, qmd collection names, error types, or error messages into the CSV. A host that wants to read a completed dream should call `runs list --status success --limit <n> --json`, then read the article, seed card, and constellation paths from that result.

## qmd Contract

Daydream requires qmd for a normal dream. qmd is the semantic search layer over the user's corpus. It lets the host search from concepts, mechanisms, tensions, failures, and dream questions instead of relying on grep, filenames, or surface keyword overlap.

Read `references/qmd-setup.md` when the user needs qmd setup guidance. Read `references/fallback-without-qmd.md` when qmd is unavailable and the dream must decide whether to continue without it.

Keep these rules explicit:

- qmd uses Markdown for the normal Daydream corpus path. If the corpus contains `.txt` files, rename their suffixes to `.md` before qmd corpus setup.
- If the corpus contains `.doc` or `.docx` files, ask the user whether to convert them to Markdown before including them in the dream corpus.
- Search the user's intended qmd collection. `--corpus` alone is not a qmd result filter.
- Use multiple semantic searches from the seed card. Do not collapse the whole card into one query or search only a topic label.
- qmd order and scores are retrieval evidence. The host reads the material before deciding which connections survive ranking.
- A host-only fallback is degraded output. Manual runs need explicit user permission; scheduled runs follow `no_qmd_policy` and default to failure.
- Keep qmd recovery inside qmd first. The helper search command automatically retries the qmd query path on CPU and then a lighter qmd vector search before normal Daydream is considered blocked.

## Known Pitfalls And Recovery

- On macOS, a real qmd semantic search can still crash the host Node.js process after setup and readiness checks pass. Treat Metal failures, C++ aborts, and signatures such as `GGML_ASSERT([rsets->data count] == 0) failed` from Metal-backed `node-llama-cpp` or `ggml` as qmd runtime failures, not proof that the corpus or Daydream JSON is bad. They may appear during embedding, reranking, concurrency, or resource cleanup.
- `--corpus` selects the target document directory for Daydream seed handling and the helper command working directory. It does not by itself restrict qmd to that directory. Keep the dream inside the intended corpus by passing the matching qmd `--collection <name>` on semantic searches; use `--allow-cross-collection` only when the user explicitly wants a wider qmd index search.
- Do not loop the same crashing Metal path. After this failure, keep qmd in the loop and retry by forcing qmd off GPU while preserving semantic search:

  ```bash
  python3 <skill-dir>/scripts/daydream.py search --corpus <path> --collection <name> --no-gpu "<semantic query>"
  ```

  `--no-gpu` is a qmd path, not a host-only fallback. It bypasses the local Metal path and may be slower, but qmd still performs the retrieval and ranking work for the dream. Keep reranking unless the user or qmd troubleshooting specifically calls for another experiment.
- If CPU-only qmd still fails, do not silently replace qmd with host intuition. Tell the user that normal Daydream is blocked, report the qmd failure, and follow `references/fallback-without-qmd.md` only when the user explicitly accepts degraded output. Scheduled dreams should fail unless their configured `no_qmd_policy` explicitly allows continuation.
- Daydream JSON validation is intentionally strict. When writing seed cards or constellations, compare fields and enum values against `templates/` before validation; invented `abstraction_level` or unsupported `preferred_strategy` values will be rejected.
- The bundled `check` command reports qmd binary presence by default. Presence is not readiness: a host or scheduler can still miss runtime environment, model access, or a working inference path. Before relying on scheduled dreams, run `check` with the target collection and `--qmd-probe-query` so it performs one real collection-scoped semantic-search smoke test.

## Progressive Disclosure

1. Read `references/dream-flow.md` before a dream.
2. Read `references/seed-card-format.md` and `prompts/extract-seed-card.md` only when you are ready to understand the seed.
3. Read `references/qmd-search.md` and `prompts/expand-with-semantic-search.md` only when you are ready to search.
4. Read `references/ranking.md` and `prompts/rank-connections.md` only when you are choosing final connections.
5. Read `references/constellation-format.md`, `references/outputs.md`, and `prompts/write-daydream-article.md` only when you are writing and saving.
6. Read `references/qmd-setup.md` only when qmd needs setup or installation guidance.
7. Read `references/fallback-without-qmd.md` when qmd is unavailable.
8. Read `references/cron.md` when the user asks for scheduled dreams.

## Core Contract

- Use qmd semantic search for normal Daydream. Do not replace semantic expansion with grep or keyword-only file matching.
- Keep qmd search inside the user's intended collection unless the user explicitly authorizes cross-collection search.
- Treat the seed card as the dream's search surface, not as the final article or a decorative summary.
- Do not drop useful connections only to save tokens.
- Keep every connection that survives reading and anti-overlap filtering in the ranked constellation. The article may use a subset.
- Treat `avoid_searching_for` as blocked branch directions, not prompts for later search.
- Save each completed dream in its own completion-time and keyword folder under `output/`; when a run id was started, include that run id in the final folder name. Keep its article, seed card, and constellation together.
- Record run status in the fixed CSV ledger, but do not treat that ledger as a fourth content artifact.
- Do not build a corpus-wide cluster system before writing.
- Do not narrate the Daydream pipeline inside the article.
- The bundled helper script selects seeds, checks readiness, runs qmd search, validates JSON, saves outputs, and maintains the run ledger. You do the reading, judgment, ranking, and writing.
