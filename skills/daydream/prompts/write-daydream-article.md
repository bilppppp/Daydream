# Write Daydream Article

Write a Markdown article from the seed document and the ranked connections it chooses to use.

The article should feel like a complete readable piece, but it may show associative movement between materials. Let concepts pass from one document into another when that movement produces a new thought.

Rules:

- Write an article, not a retrieval report.
- Do not narrate search commands, prompts, validation, or the Daydream pipeline.
- Do not flatten the piece into one source summary after another.
- Do not force every connection into equivalence. Contrasts and partial echoes are allowed.
- Use enough source material to support the thought you are forming.
- The article may use a subset of the ranked constellation. Keep the full accepted connection set in the constellation JSON.
- Keep the central idea visible even while the article wanders.

End the Markdown article with this appendix:

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

After drafting, perform a seed alignment check. Compare the way the article uses the seed against the seed card `core_claim` and `evidence_spans`. Revise if the article overstates, reverses, or distorts the seed while chasing distant echoes.
