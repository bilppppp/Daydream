# Scheduled Dreams

Use the host tool's own scheduler when the user asks for recurring dreams.

A scheduled dream needs:

1. the corpus path,
2. the qmd collection name that represents that corpus,
3. an output directory when the default skill output is not desired,
4. `no_qmd_policy`,
5. a return or delivery instruction for completed results,
6. the runtime environment the scheduler must pass to qmd,
7. a run ledger lifecycle: `runs start` at the beginning, `save-dream --run-id` on success, and `runs finish --status failed` or `cancelled` when the scheduled task stops before saving.

Default `no_qmd_policy` is `fail`.

The scheduled prompt should still tell the host to use this skill and follow `dream-flow.md`. Scheduling changes when the dream runs, not what a dream is.

Before enabling recurring runs:

1. Confirm the scheduler can find `python3`, this installed skill, and `qmd`. A shell where qmd works does not prove the scheduler has the same `PATH`.
2. Start every scheduled execution with:

   ```bash
   python3 <skill-dir>/scripts/daydream.py runs start --trigger cron
   ```

   Keep the returned `run_id`. This is required even when the run later fails, because the fixed ledger is how hosts discover successful and incomplete scheduled executions.
3. Pass required qmd runtime values from the host or an env file. Common examples are `PATH`, `QMD_FORCE_CPU=1`, and `HF_ENDPOINT=...`.
4. Run a real check from the scheduled environment:

   ```bash
   python3 <skill-dir>/scripts/daydream.py check \
     --corpus <path> \
     --collection <name> \
     --qmd-probe-query "semantic smoke test" \
     --scheduled \
     --no-qmd-policy fail \
     --env-file <qmd.env>
   ```

5. Decide the timeout and overlap policy in the host scheduler. Do not start a new dream while the previous one still owns the same qmd resources unless that concurrency has been tested.
6. Prefer the helper's qmd-only search recovery before allowing degraded host-only continuation. GPU failures may recover on CPU; expensive hybrid query paths may recover through the lighter qmd vector path.
7. Save successful runs with `save-dream --run-id <run_id>` so the ledger row is updated from the planned path to the final keyword path.
8. Finish failed or cancelled runs with `runs finish --run-id <run_id> --status failed` or `--status cancelled`. Return enough failure detail to the user or scheduler logs, but do not put error details into `daydream-runs.csv`.

If the scheduled environment cannot complete the probe reliably, fix that environment before increasing dream frequency.

When the host schedules dreams through Linux `cron`, read `cron-linux-setup.md` after this file for Linux runtime setup checks and common deployment traps.
