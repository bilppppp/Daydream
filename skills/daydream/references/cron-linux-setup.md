# Linux Cron Setup

Read this after `cron.md` when the host schedules Daydream through Linux `cron`.

This is the Linux deployment path that commonly needs extra care:

- qmd must avoid a limited-VRAM or unstable GPU,
- the corpus contains Chinese `.txt` source material,
- qmd or its Node runtime lives outside cron's default `PATH`, such as a brew or nix install.

Linux `cron` changes the runtime around the host. It does not change the Daydream workflow. The scheduled command must still invoke a host that can read the installed Daydream skill, carry the corpus path and qmd collection name, and follow the scheduled rules in `cron.md`.

Do not schedule `scripts/daydream.py` by itself as the full dream runner. The helper checks the corpus, calls qmd, validates JSON, and saves outputs; the host still reads, ranks, writes, and returns the result.

## Pre-flight Checklist

1. Use absolute paths for the installed skill, corpus, output directory, qmd env file, and host command.
2. Rename `.txt` source files to `.md` before qmd collection setup. The normal Daydream corpus path assumes qmd indexes Markdown.
3. Ask before converting `.doc` or `.docx` source files to Markdown.
4. Confirm the cron user can read the corpus and write the chosen output directory.
5. Confirm the cron user resolves the intended qmd index and collection, not a different home directory or cache.
6. Force CPU mode when the scheduled machine should not use its GPU. Put `QMD_FORCE_CPU=1` in the qmd env passed by the host, and keep `--no-gpu` available for explicit search probes.
7. Add the actual qmd and Node runtime paths to the scheduled environment. A Linux brew install may need a value such as `/home/linuxbrew/.linuxbrew/bin` in `PATH`.

## qmd Environment

Prefer a qmd env file the host can pass to Daydream:

```text
# qmd.env
PATH=/home/linuxbrew/.linuxbrew/bin:/usr/local/bin:/usr/bin:/bin
QMD_FORCE_CPU=1
HF_ENDPOINT=https://hf-mirror.com
```

Adjust `PATH` and `HF_ENDPOINT` for the real host. Do not assume the cron shell sees the same values as an interactive shell.

## Collection Setup

Prepare the Markdown corpus and collection before trusting the cron job. Use the path-first collection form from `qmd-setup.md`:

```bash
qmd collection add /path/to/markdown-corpus --name corpus-name
qmd embed -c corpus-name --no-gpu
```

For a bounded smoke test over sampled `.txt` source material, it is acceptable to copy a sample into a temporary corpus while renaming the suffix:

```bash
SOURCE_TXT_DIR="/home/gravity/docs/laoliang"
CORPUS_ROOT="/tmp/daydream-corpus-$(date +%Y%m%d-%H%M%S)"
CORPUS_DIR="$CORPUS_ROOT/laoliang-temp"
mkdir -p "$CORPUS_DIR"

ls "$SOURCE_TXT_DIR"/*.txt | shuf -n 30 | while read f; do
  base=$(basename "$f" .txt)
  cp "$f" "$CORPUS_DIR/${base}.md"
done

qmd collection add "$CORPUS_DIR" --name laoliang-dream
qmd embed -c laoliang-dream --no-gpu
```

That temporary sample is for smoke testing or bounded experiments. A recurring dream should use the intended corpus and named collection unless the user explicitly asks the host to sample and rebuild each run.

## Scheduled Probe

Run a real probe from the same user and environment before enabling recurring output:

```bash
python3 <skill-dir>/scripts/daydream.py check \
  --corpus <path> \
  --collection <name> \
  --qmd-probe-query "semantic smoke test" \
  --scheduled \
  --no-qmd-policy fail \
  --env-file <qmd.env>
```

For a direct CPU search probe, use Daydream's helper or qmd itself:

```bash
python3 <skill-dir>/scripts/daydream.py search \
  --corpus <path> \
  --collection <name> \
  --no-gpu \
  --env-file <qmd.env> \
  "<semantic query>"
```

On slow CPU hosts, the helper may fall back inside qmd from the hybrid query path to the lighter vector path. If the host deliberately chooses a direct qmd probe for timing, `qmd vsearch --no-rerank --no-gpu` is the lighter path to measure.

## Cron Job Parameters

The scheduled host prompt should state:

- use the installed Daydream skill,
- use the intended corpus path and qmd collection,
- carry the qmd env recipe, especially `PATH` and CPU mode when needed,
- keep `no_qmd_policy` explicit,
- save the article, seed card, and constellation together,
- return or deliver the saved result or failure details.

Host-specific scheduler parameters belong to that host. For example, a host may support a local delivery mode, bounded repeat counts, or a skill auto-load list; use those controls when they exist instead of baking one host's parameter names into the Daydream contract.

## Cleanup

Remove temporary smoke-test collections and temporary corpus copies after the test:

```bash
qmd collection remove laoliang-dream
rm -rf "$CORPUS_ROOT"
```

Do not remove the real recurring corpus or its collection as part of a normal scheduled dream.

Check these Linux cron traps before increasing frequency:

- Cron may have a shorter `PATH` than an interactive shell, so a manual qmd success may not reproduce there.
- Cron may set a different `HOME`, which can point qmd at a different index or model cache.
- qmd model access, CPU or GPU mode, and mirrors must work from the cron runtime, not only from a login shell.
- CPU reranking can be much slower than lighter vector search on some machines. Measure the scheduled host before choosing frequency and timeout.
- Overlapping dreams can compete for qmd resources or output attention. Keep a non-overlap policy unless concurrency has been tested.
- A quiet cron failure is still a failed dream. Return enough detail to separate missing paths, qmd runtime failure, no eligible seed, and output failure.
