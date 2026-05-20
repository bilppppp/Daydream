# Extract Structure Card

Return strict JSON only.

Extract a structure card from the provided source text. Do not summarize the text as a topic. Extract the roles, relations, constraints, mechanism, failure mode, solution pattern, abstraction levels, and evidence spans that make the document structurally useful.

Required JSON fields:

- `card_id`
- `doc_id`
- `title`
- `source_type`
- `surface_topic`
- `central_tension`
- `mechanism`
- `failure_mode`
- `solution_pattern`
- `roles`
- `relations`
- `abstractions`
- `evidence_spans`
- `causal_graph`

Rules:

- Keep concrete fields in the source language.
- Normalize high-level abstractions into concise English labels.
- Evidence spans must be exact snippets from the source text.
- Represent the mechanism as a small directed causal graph. Use 3-7 nodes. Edges must describe cause, enablement, blocking, dependency, reversal, containment, or contrast.
- If evidence is thin, say so in the fields instead of inventing support.
