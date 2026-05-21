# qmd Search

Use qmd as the preferred semantic search path.

Search from the seed card, not from a single topic label. Strong query sources are:

1. `core_concepts[].search_text`
2. `mechanisms[].search_text`
3. `failure_modes[].search_text`
4. `questions_to_dream_on[].question`
5. `core_claim`
6. `tensions[].description`

Use `keywords` to understand the seed, not as a keyword-only retrieval substitute.

The helper command is:

```bash
daydream search --corpus <path> "<semantic query>"
```

Use `--collection <name>` only when the qmd setup requires a named collection. Use `--limit <n>` when you need a specific retrieval batch size. Search more than once. Follow:

- close conceptual echoes,
- similar mechanisms in different source material,
- matching failure patterns,
- bridges between concepts,
- distant echoes that change the article,
- contrasts that sharpen the claim.

Avoid the directions listed in `avoid_searching_for`.

qmd order is retrieval evidence, not the final constellation rank. Read the material before deciding whether a connection survives.
