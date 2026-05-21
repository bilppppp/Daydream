# qmd Setup

Daydream uses qmd as its preferred semantic search path over the user's corpus. qmd is an on-device search tool for local notes, documents, transcripts, and knowledge bases; its upstream README describes keyword search, semantic search, hybrid search, collection setup, agent-facing output, and host integrations.

Use the upstream project as the source of truth for installation and setup:

- Repository: https://github.com/tobi/qmd
- README: https://github.com/tobi/qmd/blob/main/README.md

For Daydream, the host should use that upstream guidance to:

1. install qmd,
2. make the user's corpus searchable,
3. prepare semantic search for that corpus,
4. verify qmd search works before starting or scheduling dreams.

Do not duplicate or guess changing qmd installation details here. Follow the upstream README for the user's platform and current qmd version.
