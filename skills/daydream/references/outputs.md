# Outputs

Save one article and two JSON companions for each completed dream.

Default output names:

```text
output/
  YYYYMMDD-HHMMSS-keywords.md
  YYYYMMDD-HHMMSS-keywords.seed-card.json
  YYYYMMDD-HHMMSS-keywords.constellation.json
```

The helper CLI writes to this skill's `output/` directory unless `--output-dir` overrides it:

```bash
daydream save-dream \
  --article <article.md> \
  --seed-card <seed-card.json> \
  --constellation <constellation.json> \
  --keywords "<short keywords>"
```

Before saving:

```bash
daydream validate-seed-card <seed-card.json>
daydream validate-constellation <constellation.json>
```

When reporting back, return the article, a short description of the strongest constellation connections, and the saved paths.
