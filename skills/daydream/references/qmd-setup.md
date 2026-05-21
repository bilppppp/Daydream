# qmd Setup

Daydream uses qmd as its preferred semantic search path over the user's corpus. qmd is an on-device search tool for local notes, documents, transcripts, and knowledge bases; its upstream README describes keyword search, semantic search, hybrid search, collection setup, agent-facing output, and host integrations.

Use the upstream project as the source of truth for installation and setup:

- Repository: https://github.com/tobi/qmd
- README: https://github.com/tobi/qmd/blob/main/README.md

For Daydream, the host should use that upstream guidance to:

1. install qmd,
2. add the user's target corpus as a qmd collection with a known collection name,
3. prepare semantic search for that collection,
4. keep that collection name with the corpus path for Daydream searches,
5. verify collection-scoped qmd search works before starting or scheduling dreams.

Use qmd's path-first collection command shape:

```bash
qmd collection add /path/to/corpus --name corpus-name
```

The first positional argument is the corpus path. The collection name belongs after `--name`. Do not swap those roles when wiring Daydream, or qmd may index a path you did not mean to search. After collection setup, inspect it before dreaming:

```bash
qmd ls corpus-name
python3 <skill-dir>/scripts/daydream.py check \
  --corpus /path/to/corpus \
  --collection corpus-name \
  --qmd-probe-query "semantic smoke test"
```

If qmd needs deployment-specific environment values, pass them from the host or scheduler. The bundled helper accepts an env file for qmd-facing commands:

```text
# qmd.env
PATH=/usr/local/bin:/opt/homebrew/bin:/usr/bin:/bin
QMD_FORCE_CPU=1
HF_ENDPOINT=https://hf-mirror.com
```

```bash
python3 <skill-dir>/scripts/daydream.py check \
  --corpus /path/to/corpus \
  --collection corpus-name \
  --qmd-probe-query "semantic smoke test" \
  --env-file /path/to/qmd.env
```

Treat that probe as a runtime check, not just an install check. Finding a `qmd` binary does not prove that model access, device memory, or the scheduler environment is ready.

Do not duplicate or guess changing qmd installation details here. Follow the upstream README for the user's platform and current qmd version.
