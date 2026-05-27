# qmd Search

Use qmd as the required semantic search path for a normal dream.

Search from the seed card, not from a single topic label. Strong query sources are:

1. `origin_vision.search_text`
2. `core_concepts[].search_text`
3. `mechanisms[].search_text`
4. `failure_modes[].search_text`
5. `questions_to_dream_on[].question`
6. `core_claim`
7. `tensions[].description`

This is a query fanout, not one whole-card query. Pass one semantic search string to the bundled search command at a time; each call becomes one qmd hybrid query over the corpus. Start from the strongest seed-card search strings, issue multiple qmd searches across the search-bearing fields, then branch from meaningful returned routes when the dream needs more connections.

Use `origin_vision.search_text` early. It carries the seed's distilled original seeing, so it is often the best route for finding distant structural echoes rather than only topical neighbors.

Use `keywords` to understand the seed, not as a keyword-only retrieval substitute.

Scope qmd explicitly. `--corpus` is not a qmd result filter; it gives Daydream the target directory and command working directory. To keep results inside that target corpus, pass the qmd collection that represents it:

```bash
python3 <skill-dir>/scripts/daydream.py search --corpus <path> --collection <name> "<semantic query>"
```

The search command refuses an unscoped qmd search by default. Use `--allow-cross-collection` only when the user explicitly wants to search the wider qmd index instead of the named corpus collection.

The bundled search command uses qmd-only recovery by default:

1. try qmd hybrid `query`,
2. retry qmd hybrid `query` with CPU forced,
3. try qmd `vsearch` as the lighter vector-only path.

This recovery stays inside qmd. It is not the degraded host-only fallback. Use `--recovery off` when debugging one qmd path explicitly.

On macOS or servers with unstable GPU runtime, the host can also choose qmd's CPU-only path directly:

```bash
python3 <skill-dir>/scripts/daydream.py search --corpus <path> --collection <name> --no-gpu "<semantic query>"
```

This keeps qmd semantic retrieval in the dream while avoiding the local Metal path. It may run slower.

Use `--env-file <qmd.env>` when search needs deployment-specific qmd environment values such as `PATH`, `QMD_FORCE_CPU`, or `HF_ENDPOINT`.

Use `--limit <n>` when you need a specific retrieval batch size. Search more than once. Follow:

- close conceptual echoes,
- similar mechanisms in different source material,
- matching failure patterns,
- bridges between concepts,
- distant echoes that change the article,
- contrasts that sharpen the claim.

Treat `avoid_searching_for` as an exclusion list. Do not search those directions, do not use them as branches for a later search, and do not let them become constellation nodes.

qmd order is retrieval evidence, not the final constellation rank. Read the material before deciding whether a connection survives.

Send every meaningful non-topical connection that survives reading into ranking. Do not withhold one only because another route already looks sufficient for the article.

Corpus size changes connection density. A small or narrow corpus plus strict topic-overlap rejection can produce only a few valid connections. Treat that as a coverage limit, not an automatic quality failure. A larger and more varied corpus usually gives qmd more chances to surface bridges, contrasts, and distant echoes.
