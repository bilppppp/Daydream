# Critic

Return strict JSON only.

Judge whether the proposed pair deserves a synthesis draft.

Required JSON fields:

- `run_id`
- `scores`
- `mismatch_notes`
- `verdict`
- `rationale`

Scoring dimensions:

- `grounded_evidence`
- `role_alignment`
- `non_triviality`
- `surface_independence`
- `causal_alignment`

Verdict values:

- `accept`
- `reject`
- `near_miss`

Rules:

Before accepting, compare this pair against recent rejected and near-miss cases from `calibration/near_miss_archive.jsonl` when available. If the current pair repeats a known rejection tag such as surface lexical trap, contradictory causality, same-domain summary, textbook metaphor, or cliché analogy, do not accept.

- `accept` requires mean score >= 4.0.
- `accept` requires `grounded_evidence >= 4`.
- `accept` requires `surface_independence >= 3`.
- `near_miss` is mandatory for plausible but same-domain, clichéd, or low-novelty pairs.
- Reject if the pair is mostly same-topic similarity.
- Reject if evidence spans do not support the role map.
- Use `near_miss` when the connection is interesting but not strong enough for an essay.
- A draft is allowed only when the verdict is `accept`.
