# Outputs

Save one article and two JSON companions for each completed dream.

The article ends with a compact `Participating Documents And Concepts` appendix that lists the seed and linked documents actually used in the writing plus the concepts each document contributed. Keep broader accepted-but-unused connections in the constellation JSON instead of padding the article appendix.

Default output names:

```text
output/
  YYYYMMDD-HHMMSS-keywords/
    YYYYMMDD-HHMMSS-keywords.md
    YYYYMMDD-HHMMSS-keywords.seed-card.json
    YYYYMMDD-HHMMSS-keywords.constellation.json
```

The bundled helper script writes one folder per completed dream under this skill's `output/` directory unless `--output-dir` overrides it:

```bash
python3 <skill-dir>/scripts/daydream.py save-dream \
  --article <article.md> \
  --seed-card <seed-card.json> \
  --constellation <constellation.json> \
  --keywords "<short keywords>"
```

Before saving:

```bash
python3 <skill-dir>/scripts/daydream.py validate-seed-card <seed-card.json>
python3 <skill-dir>/scripts/daydream.py validate-constellation <constellation.json>
```

When reporting back, return the article, a short description of the strongest constellation connections, and the saved paths.
