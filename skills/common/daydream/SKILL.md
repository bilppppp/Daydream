---
name: daydream
description: Find structural resonance in a local corpus and save grounded drafts or rejection reports.
platforms: [macos, linux]
---

# Daydream

Use this skill when the user wants a curated local Markdown corpus to search for non-obvious structural connections and save a grounded draft or rejection report.

## Procedure

1. Run `daydream doctor`.
2. Run `daydream start-run --strategy auto`.
3. Select a seed document or theme from `corpus/`.
4. Produce 3-5 abstract search queries that target mechanisms, roles, tensions, constraints, and failure modes rather than surface topic.
5. Run `daydream candidate-pool --collection corpus --target-size 50 "<query1>" "<query2>" "<query3>"`.
6. Select candidates from the saved pool, preferring structural fit plus surface distance.
7. Read the retrieved snippets and source passages needed for evidence.
8. Extract structure cards using `prompts/extract_structure.md`.
9. Save cards with `daydream save-card`.
10. Compare cards using `prompts/compare_cards.md`.
11. Save the pair report.
12. Run the critic using `prompts/critic.md`.
13. Save either a draft with `daydream save-draft` or a rejection with `daydream save-rejection`.
14. Run `daydream inspect --run latest` and `daydream validate --run latest`.

## Required Card Shape

Structure cards must include central tension, mechanism, failure mode, solution pattern, roles, relations, abstractions, and exact evidence spans.

## Draft Gate

Draft only when the critic accepts. For reject or near miss, write a short rejection report explaining what was tempting and why it failed.

## Verification

- Do not draft unless the critic accepts.
- Always include evidence spans from both sides.
- Always include mismatch notes.
- Treat rejection as a valid run result.
- Validate the latest run before reporting completion.
