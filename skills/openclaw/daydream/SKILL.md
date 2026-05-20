---
name: daydream
description: OpenClaw wrapper for Daydream structural resonance.
version: 0.1.0
platforms: [macos, linux]
---

# Daydream OpenClaw Wrapper

Use the terminal tool to run the Daydream CLI. Keep all generated artifacts local.

## Setup

1. Put this wrapper where OpenClaw discovers skills.
2. Keep `skills/common/daydream/SKILL.md` available as the shared procedure.
3. Set the working directory to the Daydream project root.
4. Confirm `daydream doctor`, `daydream index`, and one manual run work before scheduling.

For scheduled runs, ask OpenClaw to follow the common Daydream procedure and finish by running `daydream inspect --run latest` and `daydream validate --run latest`.
