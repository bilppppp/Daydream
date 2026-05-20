---
name: daydream
description: Hermes wrapper for Daydream structural resonance.
version: 0.1.0
platforms: [macos, linux]
metadata:
  hermes:
    category: research
    tags: [resonance, qmd, writing, local-corpus]
    requires_toolsets: [terminal]
    config:
      - key: daydream.project_root
        description: Daydream project root path
        default: "~/Desktop/AI/daydream"
---

# Daydream Hermes Wrapper

Follow the common Daydream procedure. Use Hermes as the brain and the Daydream CLI as the local tool layer.

## Setup

1. Put this wrapper where Hermes discovers skills.
2. Keep `skills/common/daydream/SKILL.md` available as the shared procedure.
3. Set the working directory to the Daydream project root.
4. Confirm `daydream doctor` and `daydream index` work before scheduling.

## Cron Example

```text
/cron add "0 6 * * *" "Run Daydream over my local corpus. Save a draft only if the critic accepts; otherwise save a rejection report." --skill daydream --deliver local
```

After a cron run, inspect the result with `daydream inspect --run latest` and check `logs/` if the scheduled host writes local logs.
