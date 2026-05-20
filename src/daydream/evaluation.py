from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class ResonanceSample:
    path: Path
    group: str
    expected_verdict: str
    isomorphism_score: float | None
    rejection_tags: list[str]
    evidence_excerpts: list[str]


VERDICT_MAP = {
    "ACCEPTED": "accepted",
    "REJECTED": "rejected",
    "BORDERLINE": "near_miss",
}


def load_resonance_samples(samples_root: Path) -> list[ResonanceSample]:
    items: list[ResonanceSample] = []
    for group in ("positive", "negative", "near_miss"):
        for path in sorted((samples_root / group).glob("*.md")):
            text = path.read_text(encoding="utf-8")
            items.append(
                ResonanceSample(
                    path=path,
                    group=group,
                    expected_verdict=_extract_verdict(text, group),
                    isomorphism_score=_extract_float(text, r"isomorphism_score=([0-9.]+)"),
                    rejection_tags=_extract_tags(text),
                    evidence_excerpts=_extract_evidence(text),
                )
            )
    return items


def summarize_sample_labels(samples: list[ResonanceSample]) -> dict[str, int]:
    counts = {"accepted": 0, "rejected": 0, "near_miss": 0}
    for sample in samples:
        counts[sample.expected_verdict] += 1
    return counts


def _extract_verdict(text: str, group: str) -> str:
    if group == "near_miss":
        return "near_miss"
    match = re.search(r"resonance_verdict=Verdict\.([A-Z_]+)", text)
    if match:
        return VERDICT_MAP[match.group(1)]
    if group == "positive":
        return "accepted"
    return "rejected"


def _extract_float(text: str, pattern: str) -> float | None:
    match = re.search(pattern, text)
    return float(match.group(1)) if match else None


def _extract_tags(text: str) -> list[str]:
    match = re.search(r"rejection_tags=\[([^\]]*)\]", text)
    if not match:
        return []
    return re.findall(r"['\"]([^'\"]+)['\"]", match.group(1))


def _extract_evidence(text: str) -> list[str]:
    block = re.search(r"evidence_excerpts=\[(.*?)\]\s*\)", text, re.S)
    if not block:
        return []
    return re.findall(r"['\"]([^'\"]{20,}?)['\"]", block.group(1), re.S)
