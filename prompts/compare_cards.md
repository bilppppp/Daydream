# Compare Structure Cards

Return strict JSON only.

Compare two structure cards for structural resonance. Prefer relation, role, constraint, and failure-mode alignment over topical similarity.

Required JSON fields:

- `run_id`
- `seed_doc_id`
- `candidate_doc_id`
- `shared_structure`
- `role_alignments`
- `surface_distance`
- `structural_alignment_score`
- `novelty_score`
- `mismatch_notes`
- `seed_evidence_spans`
- `candidate_evidence_spans`

Rules:

- Compare the causal graphs before writing `shared_structure`. If causal arrows point in opposite directions, reject or near_miss even when vocabulary overlaps.
- Reward cross-domain distance only after structural alignment is real.
- Penalize same-topic overlap.
- Always explain where the analogy breaks.
- Include at least two exact evidence spans from the seed document and two from the candidate document.
- If either side lacks evidence, set low scores and prefer reject or near_miss.
- Do not write an essay in this step.
