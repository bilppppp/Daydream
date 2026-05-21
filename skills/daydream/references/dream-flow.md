# Dream Flow

Use this sequence for a manual dream.

1. Ask for a corpus path if the user did not provide one.
2. Run `daydream check --corpus <path>`.
3. If qmd is unavailable, follow `fallback-without-qmd.md` before continuing.
4. Run `daydream pick-seed --corpus <path>` and read the selected document.
5. Read `seed-card-format.md` and `../prompts/extract-seed-card.md`.
6. Save a JSON seed card that matches `../templates/seed-card.json`.
7. Run `daydream validate-seed-card <seed-card.json>`.
8. Read `qmd-search.md` and `../prompts/expand-with-semantic-search.md`.
9. Search repeatedly with semantic text from seed concepts, mechanisms, failure modes, tensions, and dream questions.
10. Read the retrieved source material needed to understand near echoes, bridges, contrasts, and distant echoes.
11. Read `ranking.md` and `../prompts/rank-connections.md`.
12. Keep the final connection network that the article actually uses.
13. Read `constellation-format.md`, `outputs.md`, and `../prompts/write-daydream-article.md`.
14. Write the Markdown article and JSON constellation.
15. Perform a seed alignment check: compare the article's treatment of the seed with `core_claim` and `evidence_spans` from the seed card. Revise before saving if the article twists the seed to chase a distant echo.
16. Run `daydream validate-constellation <constellation.json>`.
17. Run `daydream save-dream --article <article.md> --seed-card <seed-card.json> --constellation <constellation.json> --keywords "<keywords>"`.
18. Return the article, a short constellation summary, and the saved paths.

The article should be complete enough to read on its own. The constellation should explain the concept network behind it.
