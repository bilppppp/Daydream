# Dream Flow

Use this sequence for a manual dream.

1. Ask for a corpus path and its qmd collection name if the user did not provide them.
2. Run `python3 <skill-dir>/scripts/daydream.py runs start --trigger manual` and keep the returned `run_id`. Add `--output-dir <dir>` only when the completed dream content should be saved outside the default skill output directory.
3. Run `python3 <skill-dir>/scripts/daydream.py check --corpus <path> --collection <name> --qmd-probe-query "<light semantic smoke query>"`. Add `--env-file <qmd.env>` when the host needs qmd runtime environment values.
4. If qmd is unavailable, follow `fallback-without-qmd.md` before continuing.
5. Run `python3 <skill-dir>/scripts/daydream.py pick-seed --corpus <path>` and read the selected document.
6. Read `seed-card-format.md` and `../prompts/extract-seed-card.md`.
7. Save a JSON seed card that matches `../templates/seed-card.json`.
8. Run `python3 <skill-dir>/scripts/daydream.py validate-seed-card <seed-card.json>`.
9. Read `qmd-search.md` and `../prompts/expand-with-semantic-search.md`.
10. Search repeatedly within the named qmd collection with semantic text from seed concepts, mechanisms, failure modes, tensions, and dream questions.
11. Read the retrieved source material needed to understand near echoes, bridges, contrasts, and distant echoes.
12. Read `ranking.md` and `../prompts/rank-connections.md`.
13. Rank every connection that survives reading and anti-overlap filtering. Keep it for the constellation even when the article may use only a subset.
14. Read `constellation-format.md`, `outputs.md`, and `../prompts/write-daydream-article.md`.
15. Write the Markdown article from the seed and the ranked references it chooses to use, then write a JSON constellation with the full ranked connection set.
16. Perform a seed alignment check: compare the article's treatment of the seed with `core_claim` and `evidence_spans` from the seed card. Revise before saving if the article twists the seed to chase a distant echo.
17. Run `python3 <skill-dir>/scripts/daydream.py validate-constellation <constellation.json>`.
18. Run `python3 <skill-dir>/scripts/daydream.py save-dream --article <article.md> --seed-card <seed-card.json> --constellation <constellation.json> --keywords "<keywords>" --run-id <run_id>`.
19. Return the article, a short constellation summary, and the saved paths.

The article should be complete enough to read on its own. The constellation should explain the concept network behind it.

If any step after `runs start` fails before saving, run `python3 <skill-dir>/scripts/daydream.py runs finish --run-id <run_id> --status failed`. If the host or user cancels the run, finish it with `--status cancelled`. Do not add error details to the CSV ledger.
