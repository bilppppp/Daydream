# Scheduled Dreams

Use the host tool's own scheduler when the user asks for recurring dreams.

A scheduled dream needs:

1. the corpus path,
2. an output directory when the default skill output is not desired,
3. `no_qmd_policy`,
4. a return or delivery instruction for completed results.

Default `no_qmd_policy` is `fail`.

The scheduled prompt should still tell the host to use this skill and follow `dream-flow.md`. Scheduling changes when the dream runs, not what a dream is.
