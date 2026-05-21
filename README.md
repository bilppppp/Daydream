# Daydream

Daydream is a portable agent skill plus a thin helper CLI. It lets an agent host start from one random seed document, expand the seed through qmd semantic search, write a daydream article, and save the concept network behind the article.

The skill is the product surface. Hermes, OpenClaw, Claude Code, Codex, and similar hosts read the skill, understand the seed, judge connections, and write. The CLI only handles mechanical steps that should stay consistent.

## What A Dream Produces

Each completed dream saves three linked outputs:

```text
skills/daydream/output/
  YYYYMMDD-HHMMSS-keywords.md
  YYYYMMDD-HHMMSS-keywords.seed-card.json
  YYYYMMDD-HHMMSS-keywords.constellation.json
```

The Markdown file is the article. The seed card records how the seed document was understood for search. The constellation records the concept network used by the article.

## Install

Requirements:

- Python 3.11 or newer for the helper CLI
- qmd for preferred semantic search
- an agent host that can read an installed skill and work with local files

Install the helper CLI from this repository:

```bash
python3 -m pip install -e .
```

Install or copy the portable skill directory into the host skill location:

```text
skills/daydream/
```

## Start A Dream

Ask the host to use the Daydream skill and give it a corpus path. The skill tells the host when to read each reference, prompt, and JSON template.

The helper CLI exposes the mechanical steps:

```bash
daydream check --corpus /path/to/corpus
daydream pick-seed --corpus /path/to/corpus
daydream search --corpus /path/to/corpus "semantic search text from the seed card"
daydream validate-seed-card /path/to/seed-card.json
daydream validate-constellation /path/to/constellation.json
daydream save-dream \
  --article /path/to/article.md \
  --seed-card /path/to/seed-card.json \
  --constellation /path/to/constellation.json \
  --keywords "memory feedback"
```

`daydream save-dream` writes to `skills/daydream/output/` unless `--output-dir` overrides it.

## Search Behavior

qmd is the preferred search path. Daydream searches with semantic search text derived from concepts, mechanisms, failure modes, and dream questions in the seed card.

If qmd is unavailable during a manual dream, the host must warn the user before continuing with direct reading. Scheduled dreams use a `no_qmd_policy`; the default policy is `fail`.

Daydream should not fall back to grep or keyword-only file matching as a substitute for semantic expansion.
