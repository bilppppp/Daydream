---
name: daydream
description: Dream over a local corpus by expanding concepts from one random seed with qmd semantic search and writing an article plus a constellation.
platforms: [macos, linux]
---

# Daydream

Use this skill when the user asks an agent host to dream over a local corpus manually or on a schedule.

Daydream starts from one eligible random seed document. Extract a seed card, use its concepts and mechanisms for semantic expansion, write a readable article with associative movement, and save the article with its JSON seed card and JSON constellation.

## Progressive Disclosure

1. Read `references/dream-flow.md` before a dream.
2. Read `references/seed-card-format.md` and `prompts/extract-seed-card.md` only when you are ready to understand the seed.
3. Read `references/qmd-search.md` and `prompts/expand-with-semantic-search.md` only when you are ready to search.
4. Read `references/ranking.md` and `prompts/rank-connections.md` only when you are choosing final connections.
5. Read `references/constellation-format.md`, `references/outputs.md`, and `prompts/write-daydream-article.md` only when you are writing and saving.
6. Read `references/fallback-without-qmd.md` when qmd is unavailable.
7. Read `references/cron.md` when the user asks for scheduled dreams.

## Boundaries

- Prefer qmd semantic search. Do not replace semantic expansion with grep or keyword-only file matching.
- Do not drop useful connections only to save tokens.
- Do not build a corpus-wide cluster system before writing.
- Do not narrate the Daydream pipeline inside the article.
- The helper CLI selects seeds, checks readiness, runs qmd search, validates JSON, and saves outputs. You do the reading, judgment, ranking, and writing.
