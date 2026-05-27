# Rank Connections

Build the ranked connection set for the constellation before article selection.

For each ranked connection, decide:

1. its `connection_kind`,
2. its strength from `0` to `1`,
3. how it responds to, stresses, or reverses `origin_vision`,
4. why it matters to the dream,
5. why it is not just topic overlap,
6. where the article could use it if selected,
7. which documents support it.

Prefer connections that move thought forward: a mechanism discovered in another domain, a failure rhyme, a bridge between two far ideas, or a contrast that makes the article sharper.

Prefer at least one valid foreign object when the corpus supports it. A valid foreign object is structurally distant but meaningfully near: it may be a distant echo or contrast that changes how the dream understands `origin_vision`. Do not keep a result only because it feels strange.

Foreign object selection:

1. Keep the strongest close echoes, mechanism matches, bridges, failure rhymes, and contrasts that pass anti-overlap filtering.
2. Among the accepted distant echoes and contrasts, identify the one that most changes the interpretation of `origin_vision`.
3. Prefer that foreign object in the article route when it is supported by corpus material.
4. If no distant echo or contrast survives reading, state that none survived and do not invent one.

Do not keep a connection only because qmd ranked it highly.

Do not prune a meaningful connection only because the final article chooses another route. Keep it in the constellation and set `used_in_article_section` to `null` when the article does not use it.

Topic-only overlap can appear in search results. Remove it here so it does not enter the article or constellation JSON.
