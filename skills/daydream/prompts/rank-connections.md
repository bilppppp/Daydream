# Rank Connections

Build the ranked connection set for the constellation before article selection.

For each ranked connection, decide:

1. its `connection_kind`,
2. its strength from `0` to `1`,
3. why it matters to the dream,
4. why it is not just topic overlap,
5. where the article could use it if selected,
6. which documents support it.

Prefer connections that move thought forward: a mechanism discovered in another domain, a failure rhyme, a bridge between two far ideas, or a contrast that makes the article sharper.

Do not keep a connection only because qmd ranked it highly.

Do not prune a meaningful connection only because the final article chooses another route. Keep it in the constellation and set `used_in_article_section` to `null` when the article does not use it.

Topic-only overlap can appear in search results. Remove it here so it does not enter the article or constellation JSON.
