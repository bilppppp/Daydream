# Daydream V3 Cognitive Resonance Architecture Blueprint

**Status:** final target architecture  
**Date:** 2026-05-20

## 1. Product Generations

Daydream is not meant to be a pairwise analogy finder. The final product goal is closer to a human dream: a local corpus keeps activating itself in the background, forming clusters, contradictions, repeated structures, and unexpected multi-document patterns.

The generations are therefore redefined as:

| Generation | Role | What It Proves | Long-Term Status |
|---|---|---|---|
| V1 / MVP | feasibility proof | qmd, CLI, cards, runs, drafts can work together | replaced by later flows |
| V2 / scaffolding | safety scaffold | evidence binding, hard rejection, causal graphs, near-miss archive, audit trail | kept as internal machinery |
| V3 / final shape | real Daydream | unsupervised corpus field, resonance clusters, adversarial review, hypergraph writing | only user-facing target |

When V3 stabilizes, V2-facing commands such as pair reports should be hidden from the main skill flow or treated as internal debugging and edge-strength checks.

## 2. Core Principle

V3 starts from a corpus field, not from a seed.

The main user-facing question changes from:

```text
Which document resonates with this seed?
```

to:

```text
What resonance clusters emerged from this corpus field today?
```

Pairwise comparison still exists, but only as a way to detect graph edges. It is not the product experience and should not be the main writing unit.

## 3. Final Flow

```text
subset of corpus, usually 25-50 docs
  -> parallel structure-card extraction
  -> matrix cross-alignment
  -> multi-tier edge pruning
  -> weighted resonance graph
  -> community detection
  -> resonance clusters
  -> systemic archetype analysis
  -> hypergraph / mesh draft
```

The default V3 run should produce clusters first. Drafts should be generated only after a cluster survives adversarial review.

## 4. Matrix Alignment

V3 removes seed-first discovery.

For a selected corpus subset:

1. Extract or refresh one structure card per document.
2. Build candidate edges across the whole subset.
3. Score edges using causal graph shape, roles, failure modes, evidence, surface distance, and novelty.
4. Build a weighted undirected resonance graph.
5. Detect communities and return the strongest clusters.

For 25 documents, there are 300 unique undirected pairs. For 50 documents, there are 1,225. V3 must not send every edge to an expensive model. It should use a multi-tier pruning pipeline:

1. **Tier 1:** deterministic topology and metadata filter.
2. **Tier 2:** cheap heuristic or small-model scoring.
3. **Tier 3:** adversarial review only for top edges and clusters.

## 5. Red-Blue Adversarial Review

V3 should treat forced resonance as the central failure mode.

Each high-value edge or cluster should have three reports:

1. `ProponentReport`: the strongest case that the resonance is real.
2. `OpponentReport`: the strongest case that it is forced, shallow, or misleading.
3. `AdjudicationReport`: the final decision after considering both.

The opponent must search for:

1. lexical traps,
2. causal-arrow reversals,
3. missing functional roles,
4. forced abstraction labels,
5. same-domain summaries,
6. cliche metaphors,
7. archived near-miss repetition.

The adjudicator should hard reject when the opponent proves causal reversal, unsupported evidence, or missing core roles. This does not guarantee perfect truth, but it makes false acceptance much harder.

## 6. Active Negative Edge Learning

Rejected edges should become useful memory.

When the opponent or adjudicator rejects a resonance edge, V3 should archive an abstracted negative edge:

1. rejected edge endpoints,
2. rejection reason,
3. causal mismatch pattern,
4. lexical trap or cliche tag,
5. evidence spans that failed to support the mapping.

Future runs can use this archive during Tier 1 pruning. If a new edge repeats a known rejected topology, the system can drop it before expensive review.

This makes the system more immune over time without turning the original negative samples into brittle topic-specific rules.

## 7. Hypergraph Constellation

V2 constellations are still seed-centered. V3 constellations should be mesh-centered.

In V3:

1. documents are nodes,
2. causal roles can also be nodes,
3. pairwise resonance is a graph edge,
4. a systemic archetype is a hyperedge connecting three or more documents.

The main object is not "A is like B". It is:

```text
A, B, and C are different parameterizations of the same systemic archetype.
```

Examples of possible archetype labels:

1. shifting the burden,
2. tragedy of the commons,
3. escalation,
4. success to the successful,
5. delayed feedback,
6. local optimization causing global failure,
7. control through constrained variety.

The system should not need a fixed archetype library on day one. A small library can help naming, but the report must still be grounded in evidence from the corpus.

## 8. Writing Model

V3 writing should be archetype-oriented, not pair-oriented.

The draft should organize itself around:

1. the systemic archetype,
2. its causal loop or delayed feedback,
3. how each document instantiates part of the pattern,
4. where the documents disagree,
5. why the cluster matters now.

Documents become parameters in a larger system model. The dream is the model that emerges, not any single document pair.

## 9. Proposed V3 Artifacts

Under `runs/<run_id>/`, V3 should save:

1. `corpus_field.json`
2. `structure_cards.jsonl`
3. `matrix_report.json`
4. `edge_pruning_report.json`
5. `opponent_reports.jsonl`
6. `adjudication_reports.jsonl`
7. `resonance_graph.json`
8. `cluster_reports.json`
9. `mesh_report.json`
10. `mesh_draft.md`

The old pair report can still exist internally as an edge report, but should not be the main public output.

## 10. Proposed V3 Commands

Candidate user-facing commands:

```bash
daydream dream-run --limit 25 --collection corpus
daydream inspect-dream --run latest
daydream save-mesh-report --run <run_id> --input <json_file>
daydream save-mesh-draft --run <run_id> --title <title> --input <md_file>
```

Candidate internal commands:

```bash
daydream edge-report --run <run_id> --doc-a <doc_id> --doc-b <doc_id>
daydream save-opponent-report --run <run_id> --input <json_file>
daydream save-adjudication-report --run <run_id> --input <json_file>
```

## 11. Implementation Order

### Phase 1: Make V3 the Product Shape in the Skill

1. Change the main skill flow from pair discovery to corpus-field dream run.
2. Keep V2 commands as internal support.
3. Make the user-facing output "clusters found", not "pair accepted".

### Phase 2: Adversarial Edge Review

1. Add `prompts/devil_advocate.md`.
2. Add `OpponentReport`.
3. Add `AdjudicationReport`.
4. Require adjudication before any mesh draft.

### Phase 3: Matrix and Resonance Graph

1. Add bounded corpus subset selection.
2. Add cheap edge prefilter.
3. Add matrix report.
4. Add graph report.
5. Add simple community detection.

### Phase 4: Hypergraph Mesh Drafts

1. Add `MeshReport`.
2. Add hyperedge representation.
3. Add multi-document evidence mesh.
4. Add mesh-oriented writing prompt.

## 12. Recommendation

The next major plan should not extend V2 pairwise output. It should begin V3 by replacing the main user-facing skill flow with `dream-run`.

V2 is still useful as internal machinery, but it should stop being the conceptual center of the project.

