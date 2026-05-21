# Without qmd

Normal Daydream depends on qmd. A host-only fallback is degraded because it cannot claim the same corpus coverage, connection strength, or retrieval trail.

Before using this fallback, try qmd-only recovery first. The bundled search helper retries the qmd query path on CPU and then a lighter qmd vector path unless recovery is explicitly disabled. Those paths are still normal qmd retrieval, not this degraded host-only mode.

For a manual dream, warn the user before continuing when qmd is unavailable or still failing after qmd troubleshooting:

```text
qmd semantic search is not available right now, so normal Daydream is blocked. I can continue in a degraded host-only mode by reading and reasoning over the corpus directly, but the coverage and connection strengths will be less reliable. Should I continue?
```

Continue only after the user allows it.

The fallback still follows semantic intent. Read for concepts, mechanisms, tensions, failure patterns, bridges, and contrasts. Do not quietly switch to grep or keyword-only file matching as a substitute for semantic search.

Scheduled dreams cannot wait for that answer. Use `no_qmd_policy`:

- `fail`: stop when qmd is unavailable.
- `warn_and_continue`: continue and report the warning.
- `continue_silent`: continue without requiring a warning in the run result.

The default scheduled policy is `fail`.
