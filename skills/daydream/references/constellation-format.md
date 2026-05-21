# Constellation Format

The constellation is JSON. It records the accepted concept network discovered for the dream, including meaningful ranked connections the article does not use.

Use `../templates/constellation.json` as the shape.

The graph may contain:

- `document` nodes for the seed and connected sources,
- `concept` nodes for ideas that survive ranking,
- `tension` nodes for conflicts or dilemmas that bridge the dream,
- `question` nodes for dream questions and their preferred search strategy.

The seed is the starting document, but retrieved documents, concepts, tensions, and questions may connect to one another when a connection survives reading and ranking.

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
- `used_in_article_section`, with a section label when used or `null` when unused,
- involved documents.

Do not create all pairwise edges just to make the graph dense. Do not drop a meaningful ranked connection only because the article uses a subset of the ranked constellation.
