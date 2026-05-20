from __future__ import annotations

from typing import Any


CRITIC_SCORE_KEYS = {
    "grounded_evidence",
    "role_alignment",
    "non_triviality",
    "surface_independence",
    "causal_alignment",
}


def require_critic_thresholds(payload: dict[str, Any]) -> None:
    scores = payload.get("scores")
    if not isinstance(scores, dict):
        raise ValueError("scores must be an object")
    missing = sorted(CRITIC_SCORE_KEYS - scores.keys())
    if missing:
        raise ValueError(f"critic scores missing required keys: {', '.join(missing)}")

    numeric: list[float] = []
    for key in sorted(CRITIC_SCORE_KEYS):
        value = scores[key]
        if not isinstance(value, int | float):
            raise ValueError(f"critic score {key} must be numeric")
        if value < 1 or value > 5:
            raise ValueError(f"critic score {key} must be between 1 and 5")
        numeric.append(float(value))

    verdict = str(payload.get("verdict", "")).lower()
    if verdict in {"accept", "accepted"}:
        mean = sum(numeric) / len(numeric)
        if mean < 4.0:
            raise ValueError("accepted critic mean score must be at least 4.0")
        if float(scores["grounded_evidence"]) < 4:
            raise ValueError("accepted critic grounded_evidence must be at least 4")
        if float(scores["surface_independence"]) < 3:
            raise ValueError("accepted critic surface_independence must be at least 3")


def require_pair_acceptability(payload: dict[str, Any]) -> None:
    if payload["surface_distance"] < 0.35:
        raise ValueError("surface_distance too low for a non-trivial resonance")
    if payload["novelty_score"] < 0.55:
        raise ValueError("novelty_score too low for a non-trivial resonance")
    if payload["structural_alignment_score"] < 0.65:
        raise ValueError("structural_alignment_score too low for acceptance")
