# Without qmd

For a manual dream, warn the user before continuing when qmd is unavailable:

```text
qmd semantic search is not available right now. I can continue by reading and reasoning over the corpus directly, but that can use more context and may be slower or less complete. Should I continue?
```

Continue only after the user allows it.

The fallback still follows semantic intent. Read for concepts, mechanisms, tensions, failure patterns, bridges, and contrasts. Do not quietly switch to grep or keyword-only file matching as a substitute for semantic search.

Scheduled dreams cannot wait for that answer. Use `no_qmd_policy`:

- `fail`: stop when qmd is unavailable.
- `warn_and_continue`: continue and report the warning.
- `continue_silent`: continue without requiring a warning in the run result.

The default scheduled policy is `fail`.
