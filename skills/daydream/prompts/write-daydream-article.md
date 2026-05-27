# Write Daydream Article

Write a Markdown article from the seed document and the ranked connections it chooses to use.

The article should feel like a complete readable piece, but it may show associative movement between materials. Let concepts pass from one document into another when that movement produces a new thought.

Before drafting, synthesize an internal Dream-Core from `origin_vision` and the accepted ranked connections.

Dream-Core rules:

- It must be condensed from `origin_vision` and accepted ranked connections.
- It must explain at least two strong ranked connections.
- It must not be invented before qmd search.
- It must not be used to discard valid connections.
- If it cannot explain the accepted connections, discard it and make a simpler Dream-Core.
- Do not save the Dream-Core as a separate output file.

Dream-Core work:

1. Condense: compress `origin_vision` and the strongest accepted connections into one shared structure.
2. Displace: move that structure into a fresh image, scene, pressure, or symbolic action that is not just the seed topic in costume.
3. Dramatize: make the structure happen as motion, conflict, weather, architecture, ritual, tool, body, room, machine, or another concrete scene.
4. Resist secondary revision: do not explain away every symbol after creating it. Keep useful ambiguity.

Write from that Dream-Core. Let source concepts appear as transformed parts of the central image instead of as source-by-source explanation.

Rules:

- Write an article, not a retrieval report.
- Do not narrate search commands, prompts, validation, or the Daydream pipeline.
- Do not flatten the piece into one source summary after another.
- Forbidden body pattern: seed paragraph, source A paragraph, source B paragraph, source C paragraph, conclusion. If the draft has this shape, rewrite it before saving.
- Do not force every connection into equivalence. Contrasts and partial echoes are allowed.
- Use enough source material to support the thought you are forming.
- The article may use a subset of the ranked constellation. Keep the full accepted connection set in the constellation JSON.
- Keep the central idea visible even while the article wanders.
- Prefer image, pressure, motion, contradiction, and symbolic action over explanation.
- Leave some ambiguity, but do not distort the seed's core claim or evidence spans.
- Each major paragraph should map to a part, movement, pressure, or consequence of the Dream-Core, not to one source document.
- If the draft reads like a lecture, report, or orderly literature review, rewrite it around the Dream-Core with more displacement, dramatization, and silence.
- Use symbolic and dream-like writing as a literary method only. Do not present symbols as prophecy, occult knowledge, or psychological diagnosis of real people.

End the Markdown article with this mandatory appendix. The helper rejects the article if this section is missing, not final, or missing table rows:

```markdown
## Participating Documents And Concepts

| Document | Concepts Used |
| --- | --- |
| Seed or linked document title (`/path/to/document.md`) | concept-a; concept-b |
```

In that appendix:

- Include the seed document and every linked document whose concepts actually participate in the written article.
- List the document title and path together so the reader can trace the material.
- List the concepts from that document that the article actually uses. Use concise concept names or short concept labels, not long explanations.
- Do not list a retrieved document only because it appeared in search or survived ranking when the article did not use it.
- Keep the appendix factual and compact. It is an audit list after the article, not a retrieval report inside the article body.

After drafting, perform a reverse check:

1. Can the Dream-Core explain at least two strong ranked connections?
2. Can the article point back to the accepted connections without inventing new support?
3. Does the article still align with `origin_vision`, `core_claim`, and `evidence_spans`?
4. Did the draft become a lecture, report, or source-by-source summary?

Revise the Dream-Core or the article if any answer fails. Do not revise by adding pipeline narration.
