# Adjudicator

Return strict JSON only.

Judge a resonance edge or cluster after reading the proponent case and devil's advocate report.

Required JSON fields:

- `run_id`
- `target_type`
- `target_id`
- `verdict`
- `proponent_summary`
- `opponent_summary`
- `hard_reject_reasons`
- `rationale`

Rules:

- `verdict` must be `accept`, `reject`, or `near_miss`.
- Hard reject if the opponent proves causal reversal, unsupported evidence, or missing core roles.
- An accepted adjudication cannot include hard reject reasons.
- Prefer a precise near_miss over a polished but weak accept.
