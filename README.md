# Daydream

Daydream is a local command line tool plus a portable agent skill. It lets an agent search a curated Markdown corpus, find structural resonance between distant documents, and save either a grounded draft or a clear rejection record.

The local tool handles setup, qmd, validation, files, and run history. The host agent, such as Hermes, OpenClaw, Codex, or Claude Code, handles judgment and writing.

## Install

Requirements:

- Python 3.11 or newer
- qmd
- A terminal-capable host agent
- A local Markdown corpus in `corpus/`

From this repository:

```bash
python3 -m pip install -e .
daydream init
daydream doctor
```

For local development without installing:

```bash
PYTHONPATH=src python3 -m daydream doctor
```

## Run Manually

Index the corpus:

```bash
daydream index
```

Start a run:

```bash
daydream start-run --strategy auto
```

Then let the host agent follow `skills/common/daydream/SKILL.md`. It will use the prompts in `prompts/`, save intermediate artifacts, and finish with either a draft or a rejection.

Inspect the result:

```bash
daydream inspect --run latest
daydream validate --run latest
```

## Hermes

Install or copy `skills/hermes/daydream/` into the Hermes skill location, and keep `skills/common/daydream/` available as the shared procedure.

Use the Hermes skill manually first. After one successful manual run, schedule it with Hermes cron using the example in `skills/hermes/daydream/SKILL.md`.

## OpenClaw

Install or copy `skills/openclaw/daydream/` into the OpenClaw skill location. Use the same core commands and prompts from this repository.

## Shell Cron Fallback

For a plain cron job, configure `DAYDREAM_AGENT_CMD` to run your chosen host agent with the Daydream skill, then call:

```bash
scripts/daydream-cron.sh
```

The script writes logs under `logs/` and fails loudly if the agent command is missing or the latest run does not validate.

## Output

- `cards/`: generated structure cards
- `runs/`: every run and its evidence trail
- `drafts/`: accepted drafts only
- `logs/`: scheduled-run logs

Generated drafts are not added back into the primary corpus by default.
