# Ranking Connections

Rank after search and reading. qmd retrieval rank is not enough.

For each connection that remains, check:

1. Which seed concept, mechanism, tension, failure mode, or dream question activated it?
2. Why is it more than surface topic overlap?
3. Does it give the article a close echo, mechanism match, failure rhyme, bridge, distant echo, or contrast?
4. Can you explain the connection from corpus material you actually read?
5. Where could the article use it if it chooses this route?

Allowed connection kinds:

- `close_echo`
- `mechanism_match`
- `failure_rhyme`
- `bridge`
- `distant_echo`
- `contrast`

Rank every connection that survives reading and anti-overlap filtering. The article may use only a subset of these ranked connections.

Do not drop a meaningful ranked connection only because the article chooses another route. Keep it in the constellation and set `used_in_article_section` to `null` when the article does not use it.

Exclude results that stay topical or cannot be explained from corpus material you actually read.

Topic-only overlap may appear during qmd retrieval. Drop it here. It must not enter the article or the constellation JSON.
