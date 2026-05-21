# Daydream Skill Reset Design

**Date:** 2026-05-21
**Status:** approved design for implementation planning

## 1. Product Reset

Daydream should be a portable agent skill with a thin helper tool, not a standalone resonance-analysis product.

The product loop is:

```text
pick concepts from one seed document
  -> use qmd semantic search to find related concepts across the corpus
  -> synthesize the concept network into a daydream article
  -> save the article, seed card, and constellation
```

The skill should work as the primary installable artifact for Hermes, OpenClaw, Claude Code, Codex, and similar agent hosts. The host agent performs reading, interpretation, ranking judgment, and writing. The helper tool fixes the mechanical steps that should not depend on agent improvisation.

## 2. Goals

The first implementation should:

1. Provide one portable skill as the main product surface.
2. Let a user start a dream by supplying a corpus path.
3. Let a host with scheduling support run the same skill on cron or an equivalent schedule.
4. Randomly select one corpus document as the seed for a dream.
5. Require the host to turn that seed into a structured JSON dream seed card.
6. Use semantic search, preferably through qmd, to expand the seed card into connected corpus material.
7. Rank and classify concept connections after search instead of treating retrieval order as the final constellation.
8. Write a complete article that keeps visible associative movement between materials.
9. Save three linked outputs under the skill output directory by default:
   - Markdown article
   - JSON dream seed card
   - JSON constellation graph
10. Return the result to the user as well as saving it.

## 3. Non-Goals

The first implementation should not:

1. Rebuild Daydream as a full run-tracking product.
2. Start from a corpus-wide graph or cluster-building pass.
3. Require a multi-stage critic, adversarial review, or long artifact ledger before writing.
4. Treat generated constellations as persistent memory for later dreams.
5. Replace qmd with a custom retrieval engine.
6. Search by grep, filename matching, or keyword-only lookup when semantic search is available.
7. Truncate useful connections purely to reduce token consumption.

## 4. Responsibility Split

### Skill

The skill owns:

1. Capability boundaries and trigger instructions.
2. Progressive disclosure of the dream flow.
3. Prompts for seed-card extraction, semantic expansion, ranking, and writing.
4. Required schemas and templates for outputs.
5. Rules for qmd-first semantic search and no-qmd fallback.
6. Generic scheduling guidance for host tools that support recurring jobs.

### Helper Tool

The helper tool owns only deterministic or mechanical work:

1. Check that the corpus path exists and contains readable documents.
2. Check qmd availability and output-directory writability.
3. Randomly select one seed document from the corpus.
4. Run qmd semantic searches from host-provided search text.
5. Save linked output files with a shared completion-time and keyword prefix.
6. Validate the JSON shape of dream seed cards and constellations before reporting success.

The helper tool is a guardrail. It must not decide what a seed means, invent connections, rank writing value, or draft the article.

### Host Agent

The host agent owns:

1. Reading the seed document.
2. Producing the dream seed card.
3. Choosing semantic-search text from the seed card.
4. Reading qmd results and any source material needed to understand them.
5. Continuing semantic expansion across near, bridging, and distant concept connections.
6. Ranking concept connections for the final constellation.
7. Writing the article.
8. Producing the constellation graph content.

## 5. User Flow

### Manual Dream

1. User asks a supported host to dream and provides a corpus path.
2. Host reads `SKILL.md`, then only the referenced instructions needed for this run.
3. Helper tool checks the corpus, qmd status, and output location.
4. Helper tool randomly selects one seed document.
5. Host reads the seed and writes a JSON dream seed card.
6. Host derives semantic queries from the seed card.
7. Helper tool runs qmd searches over the corpus when qmd is available.
8. Host reads and expands the retrieved material until it has enough meaningful connections for the dream.
9. Host ranks and classifies the connections that matter to the article.
10. Host writes the article and creates the constellation JSON.
11. Helper tool validates and saves all three outputs.
12. Host returns the article, a short constellation summary, and saved output locations.

### Scheduled Dream

The portable skill should define what scheduling needs:

1. corpus path,
2. output location when the default is overridden,
3. whether the host may continue without qmd after warning the user,
4. what the host should return after each completed dream.

The host provides the concrete scheduling mechanism. Hermes cron, OpenClaw scheduling, Claude Code, Codex, or any future host should reuse the same dream flow rather than fork the product logic.

## 6. Skill Layout

The skill should be organized for progressive disclosure:

```text
daydream/
  SKILL.md
  references/
    dream-flow.md
    qmd-search.md
    fallback-without-qmd.md
    structure-card-format.md
    constellation-format.md
    ranking.md
    outputs.md
    cron.md
  prompts/
    extract-structure-card.md
    expand-with-semantic-search.md
    rank-connections.md
    write-daydream-article.md
  templates/
    structure-card.json
    constellation.json
    article.md
  output/
  scripts-or-src/
    thin helper tool implementation
```

`SKILL.md` should stay short. It should tell the host when to use Daydream, what it may and may not do, and which reference or prompt to read at each stage.

`references/` should explain rules and schemas.

`prompts/` should tell the host how to perform the reasoning-heavy steps.

`templates/` should provide concrete output shapes without turning examples into rigid prose.

## 7. Dream Seed Card

The dream seed card is saved as JSON. It is not a polished summary. It is the host's structured understanding of the random seed document and the search surface for the dream.

The required first-version shape is:

```json
{
  "card_type": "dream_seed_card",
  "seed_document": {
    "title": "Seed document title",
    "path": "/path/to/document.md",
    "source_layer": "hermes | openclaw | vibe-coding | notebooklm | home-server | essay | other"
  },
  "core_summary": "The central meaning of the seed document",
  "core_claim": "The one sentence the seed most wants to prove or express",
  "core_concepts": [
    {
      "name": "Concept name",
      "meaning": "What this concept means inside the seed",
      "search_text": [
        "Semantic-search text for one expansion direction",
        "Semantic-search text for another expansion direction"
      ],
      "keywords": ["keyword-1", "keyword-2"],
      "abstraction_level": "surface | mechanism | meta"
    }
  ],
  "tensions": [
    {
      "description": "Conflict, contradiction, or tension inside the seed",
      "why_it_matters": "Why this tension deserves echoes in the corpus"
    }
  ],
  "mechanisms": [
    {
      "name": "Mechanism name",
      "description": "How the mechanism works",
      "search_text": [
        "Semantic-search text for similar mechanisms"
      ]
    }
  ],
  "failure_modes": [
    {
      "description": "How this structure can fail",
      "search_text": [
        "Semantic-search text for similar failures"
      ]
    }
  ],
  "questions_to_dream_on": [
    {
      "question": "Question worth sending back into the corpus",
      "preferred_strategy": "random_collision | tag_bridge | temporal_bridge | same_problem_different_domain"
    }
  ],
  "avoid_searching_for": [
    "Direction likely to produce topical similarity without meaningful structure"
  ],
  "evidence_spans": [
    "Short key span quoted from the seed document"
  ]
}
```

The highest-value search fields are concept `search_text`, mechanism `search_text`, failure-mode `search_text`, dream questions, core claim, and tensions. Keywords help interpretation but do not define the retrieval method.

## 8. Semantic Expansion

Daydream should use qmd semantic search when qmd is available.

The host should issue multiple semantic searches from the dream seed card instead of searching only the seed summary. Search directions should include:

1. close conceptual echoes,
2. similar mechanisms in different material,
3. similar failure modes,
4. bridges between seed concepts,
5. distant echoes that can move the article somewhere non-obvious,
6. contrasts that sharpen the article.

Search should avoid directions recorded in `avoid_searching_for`.

qmd rank is retrieval evidence, not final constellation rank. The host decides which connections survive into the article and graph after reading the material.

Useful connections should not be dropped only to conserve tokens. A connection may be excluded when it stays topical or does not participate in the final thought network.

## 9. Ranking

Final connection ranking should consider:

1. which seed concept, tension, mechanism, failure mode, or dream question activated the connection,
2. whether the connection is more than surface topic overlap,
3. whether it adds a turn, contrast, bridge, or distant echo to the article,
4. whether the host can explain the connection from the corpus material it read,
5. whether the connection is actually used in the final constellation.

First-version connection kinds are:

1. `close_echo`
2. `mechanism_match`
3. `failure_rhyme`
4. `bridge`
5. `distant_echo`
6. `contrast`

## 10. Article

The article is saved as Markdown.

It should be a finished readable piece, not a retrieval report. It should also keep some visible associative movement between source materials so it feels like a daydream rather than a conventional review.

The writing prompt should forbid:

1. narrating the tool pipeline to the reader,
2. flattening the article into a list of search results,
3. presenting a citation inventory instead of an idea,
4. forcing every connection into a tidy equivalence.

## 11. Constellation

The constellation is saved as JSON. It is an output of the current dream, not persistent memory for future dreams.

It should describe the concept network formed by the article. The seed document remains the starting point, but retrieved documents and concepts may connect to one another.

The first-version shape is:

```json
{
  "graph_type": "daydream_constellation",
  "article": {
    "title": "Article title",
    "path": "/path/to/output/article.md",
    "thesis": "The core idea formed by the article"
  },
  "seed_document": {
    "title": "Seed document title",
    "path": "/path/to/seed-document.md",
    "source_layer": "hermes | openclaw | vibe-coding | notebooklm | home-server | essay | other"
  },
  "nodes": [
    {
      "id": "seed-doc",
      "type": "document",
      "title": "Document title",
      "path": "/path/to/document.md",
      "source_layer": "essay",
      "role": "seed | source | bridge | distant_echo"
    },
    {
      "id": "concept-agent-memory",
      "type": "concept",
      "label": "Concept label",
      "meaning": "What this concept means in the current dream",
      "abstraction_level": "surface | mechanism | meta"
    }
  ],
  "edges": [
    {
      "from": "seed-doc",
      "to": "concept-agent-memory",
      "type": "expresses | reframes | tensions_with | enables | fails_by | echoes | bridges | contrasts",
      "strength": 0.91,
      "reason": "Why this edge belongs in the constellation",
      "evidence": [
        "Short corpus-grounded support for this edge"
      ]
    }
  ],
  "ranked_connections": [
    {
      "rank": 1,
      "from_node": "concept-a",
      "to_node": "concept-b",
      "strength": 0.94,
      "connection_name": "Connection name",
      "why_it_matters": "Why the article needs this connection",
      "documents_involved": [
        "seed-doc",
        "source-doc-2"
      ]
    }
  ],
  "search_coverage": {
    "connection_count": 0,
    "documents_considered": 0,
    "documents_used": 0,
    "notes": "Overall search and connection note for this dream"
  }
}
```

The graph should record connections that matter to the final thought network. It does not need to create all pairwise edges among retrieved documents.

## 12. Output Naming

By default, the helper tool saves outputs under the skill `output/` directory with one shared prefix derived from completion time and article keywords:

```text
output/
  YYYYMMDD-HHMMSS-keywords.md
  YYYYMMDD-HHMMSS-keywords.structure-card.json
  YYYYMMDD-HHMMSS-keywords.constellation.json
```

The article title and keyword prefix may be proposed by the host, but the helper tool should normalize the saved filenames.

## 13. qmd Fallback

When qmd is unavailable, the host must tell the user before continuing:

1. qmd semantic search is not currently available,
2. Daydream can continue by relying on the host to read and reason over the corpus directly,
3. this route may use more context and may be slower or less complete.

If the user permits continuation, the fallback still follows semantic intent. It must not silently become grep-driven retrieval.

## 14. Validation and Verification

The implementation should verify:

1. corpus-path checks reject unusable paths,
2. seed selection returns a real readable document from the corpus,
3. qmd search wrapper performs semantic-search calls when qmd is present,
4. JSON validation rejects malformed dream seed cards,
5. JSON validation rejects malformed constellations,
6. save flow writes three linked files with one shared prefix,
7. a representative host run can complete from seed selection to saved outputs,
8. the no-qmd branch warns before continuation.

## 15. Repository Consequences

The current repository is heavier than this product definition. Implementation planning should decide what to remove, move aside, or keep only as reference.

The first version should keep only code and documentation that directly support:

1. the portable skill,
2. qmd-first semantic expansion,
3. seed selection,
4. output saving,
5. JSON validation.

Older corpus-wide cluster flows, multi-stage adjudication artifacts, pair-report machinery, and long run ledgers should not remain in the main user path for this reset.
