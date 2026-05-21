# Constellation Format

The constellation is JSON. It records the concept network formed by the article.

Use `../templates/constellation.json` as the shape.

The graph may contain document nodes and concept nodes. The seed is the starting document, but retrieved documents and concepts may connect to one another when the article uses that connection.

Each edge must include:

- source node,
- destination node,
- relation type,
- strength from `0` to `1`,
- reason,
- evidence.

Each ranked connection must include:

- `connection_kind`,
- `why_it_matters`,
- `why_not_topic_overlap`,
- `used_in_article_section`,
- involved documents.

Do not create all pairwise edges just to make the graph dense. Keep the connections that matter to the final thought network.
