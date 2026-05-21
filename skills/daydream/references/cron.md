# Scheduled Dreams

Use the host tool's own scheduler when the user asks for recurring dreams.

A scheduled dream needs:

1. the corpus path,
2. the qmd collection name that represents that corpus,
3. an output directory when the default skill output is not desired,
4. `no_qmd_policy`,
5. a return or delivery instruction for completed results,
6. the runtime environment the scheduler must pass to qmd.

Default `no_qmd_policy` is `fail`.

The scheduled prompt should still tell the host to use this skill and follow `dream-flow.md`. Scheduling changes when the dream runs, not what a dream is.

Before enabling recurring runs:

1. Confirm the scheduler can find `python3`, this installed skill, and `qmd`. A shell where qmd works does not prove the scheduler has the same `PATH`.
2. Pass required qmd runtime values from the host or an env file. Common examples are `PATH`, `QMD_FORCE_CPU=1`, and `HF_ENDPOINT=...`.
3. Run a real check from the scheduled environment:

   ```bash
   python3 <skill-dir>/scripts/daydream.py check \
     --corpus <path> \
     --collection <name> \
     --qmd-probe-query "semantic smoke test" \
     --scheduled \
     --no-qmd-policy fail \
     --env-file <qmd.env>
   ```

4. Decide the timeout and overlap policy in the host scheduler. Do not start a new dream while the previous one still owns the same qmd resources unless that concurrency has been tested.
5. Prefer the helper's qmd-only search recovery before allowing degraded host-only continuation. GPU failures may recover on CPU; expensive hybrid query paths may recover through the lighter qmd vector path.
6. Return enough failure detail for the user to distinguish missing environment, qmd model/device failure, no eligible seed, and article/output failure.

If the scheduled environment cannot complete the probe reliably, fix that environment before increasing dream frequency.
