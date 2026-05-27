# Seed Card Format

The seed card is JSON. It records how the selected seed document becomes search material for the current dream.

Use `../templates/seed-card.json` as the shape. Keep these rules:

- `card_type` is always `dream_seed_card`.
- `seed_document.source_layer` is a freeform source label such as `notes`, `essays`, `bookmarks`, `hermes`, or `openclaw`.
- `origin_vision` records the seed's distilled original way of seeing before the host explains it.
- `core_summary` explains the seed.
- `core_claim` states the sentence the seed most wants to express or prove.
- Every concept has semantic `search_text`.
- Mechanisms and failure modes carry their own semantic `search_text`.
- Dream questions carry a preferred strategy.
- `avoid_searching_for` records tempting topic-only directions.
- `evidence_spans` must be short exact spans from the seed.

## Origin Vision

`origin_vision` is the result of seed distillation. It is not a title, not a summary, and not a diagnosis of the author or any person in the document. It is the original seeing that remains after burning away defense, argument, and system.

Required fields:

- `vision`: one sentence that presents the seed's original way of seeing the world. Do not explain it.
- `emotional_pressure`: the pain, anxiety, shock, longing, or unresolved pressure behind that vision.
- `simple_truth`: the simplest judgment left after the argument is stripped away.
- `search_text`: semantic search texts that can go into qmd, including distant structural routes.

The host should treat `origin_vision` as a search surface and as later material for Dream-Core synthesis. Keep it compact. If it still needs explanation, it is not distilled enough.

The card is not the article and is not a general-purpose permanent summary. It is the dream seed for this run.
