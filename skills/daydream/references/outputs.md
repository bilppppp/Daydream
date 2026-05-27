# Outputs

Save one article and two JSON companions for each completed dream.

The article must end with a compact `Participating Documents And Concepts` appendix that lists the seed and linked documents actually used in the writing plus the concepts each document contributed. Keep broader accepted-but-unused connections in the constellation JSON instead of padding the article appendix.

`save-dream` rejects an article when this appendix is missing, not the final section, missing its table header, or missing document rows.

The completed dream content contract does not change: the content layer is still exactly the article Markdown, seed-card JSON, and constellation JSON. The CSV ledger is a separate run layer.

Default output names:

```text
output/
  daydream-runs.csv
  YYYYMMDD-HHMMSS-keywords/
    YYYYMMDD-HHMMSS-keywords.md
    YYYYMMDD-HHMMSS-keywords.seed-card.json
    YYYYMMDD-HHMMSS-keywords.constellation.json
```

When a run is registered first with `runs start`, the final saved folder becomes `YYYYMMDD-HHMMSS-keywords-run_id/`. Calls that omit `--run-id` keep the older `YYYYMMDD-HHMMSS-keywords/` folder name.

`daydream-runs.csv` is fixed at `<skill-dir>/output/daydream-runs.csv`. It records run ids, run status, and paths. It is not a dream artifact and must not contain summaries, errors, seed paths, corpus paths, qmd collections, dream weather, anti-dream notes, or other semantic material.

The bundled helper script writes one folder per completed dream under this skill's `output/` directory unless `--output-dir` overrides the content output location:

```bash
python3 <skill-dir>/scripts/daydream.py save-dream \
  --article <article.md> \
  --seed-card <seed-card.json> \
  --constellation <constellation.json> \
  --keywords "<short keywords>"
```

When a run has already been registered, save with its run id:

```bash
python3 <skill-dir>/scripts/daydream.py save-dream \
  --article <article.md> \
  --seed-card <seed-card.json> \
  --constellation <constellation.json> \
  --keywords "<short keywords>" \
  --run-id <run_id>
```

`runs start` first records a planned path named from `started_at` and `run_id`. After `save-dream --run-id`, the helper saves to the final `started_at-keywords-run_id` folder and updates the same CSV row with the final article, seed-card, and constellation paths. If the run fails before saving, the planned paths remain in the CSV and the host should finish the row as `failed` or `cancelled`.

When `save-dream` is called without `--run-id`, it keeps the older `started_at-keywords` folder name and appends one `success` row to the fixed run ledger so hosts can still discover that completed dream.

Before saving:

```bash
python3 <skill-dir>/scripts/daydream.py validate-seed-card <seed-card.json>
python3 <skill-dir>/scripts/daydream.py validate-constellation <constellation.json>
```

The article itself is checked during `save-dream`; there is no separate article validation command.

Hosts should discover completed runs through:

```bash
python3 <skill-dir>/scripts/daydream.py runs list --status success --limit 5 --json
```

When reporting back, return the article, a short description of the strongest constellation connections, and the saved paths.
