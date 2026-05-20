---
name: daydream
description: Run Daydream over a local corpus field, find resonance clusters, and save mesh drafts or rejection records.
platforms: [macos, linux]
---

# Daydream

Use this skill when the user wants a curated local Markdown corpus to daydream over itself, forming resonance clusters without a single seed document.

## Procedure

1. Run `daydream doctor`.
2. Run `daydream dream-run --collection corpus --limit 25`.
3. Treat the saved `corpus_field.json` as the working field, not as a seed list.
4. Extract or refresh structure cards for the field using `prompts/extract_structure.md`.
5. Build candidate resonance edges across the field. Pairwise reports are internal edge checks only.
6. Prune weak edges before expensive reasoning.
7. For promising clusters, run the proponent analysis, then the opponent using `prompts/devil_advocate.md`.
8. Run adjudication using `prompts/adjudicator.md`.
9. Save opponent and adjudication reports with `daydream save-opponent-report` and `daydream save-adjudication-report`.
10. Save a mesh report with `daydream save-mesh-report`.
11. Write a mesh draft only after accepted adjudication using `prompts/mesh_draft.md`.
12. Save the draft with `daydream save-mesh-draft`.
13. Run `daydream inspect-dream --run latest`.

## Required Card Shape

Structure cards must include central tension, mechanism, failure mode, solution pattern, roles, relations, abstractions, causal graph, and exact evidence spans.

## Internal V2 Machinery

`start-run`, `candidate-pool`, `save-pair-report`, and `save-draft` are internal support/debug commands. They are not the main Daydream user flow after V3.

## Draft Gate

Draft only when cluster-level adjudication accepts. For reject or near miss, write a short rejection record explaining what was tempting and why it failed.

## Verification

- Do not draft unless adjudication accepts.
- Always include evidence spans from at least three documents for mesh reports.
- Always include mismatch notes.
- Treat rejection as a valid run result.
- Inspect the latest dream before reporting completion.
