from __future__ import annotations

from typing import Any

from .scoring import require_critic_thresholds


CARD_REQUIRED = {
    "card_id",
    "doc_id",
    "title",
    "surface_topic",
    "central_tension",
    "mechanism",
    "failure_mode",
    "solution_pattern",
    "roles",
    "relations",
    "abstractions",
    "evidence_spans",
    "causal_graph",
}

PAIR_REQUIRED = {
    "run_id",
    "seed_doc_id",
    "candidate_doc_id",
    "shared_structure",
    "role_alignments",
    "surface_distance",
    "structural_alignment_score",
    "novelty_score",
    "mismatch_notes",
    "seed_evidence_spans",
    "candidate_evidence_spans",
}

CRITIC_REQUIRED = {"run_id", "scores", "mismatch_notes", "verdict", "rationale"}
CONSTELLATION_REQUIRED = {
    "run_id",
    "seed_doc_id",
    "resonance_doc_ids",
    "epistemic_nexus",
    "isomorphism_network",
    "evidence_network",
    "mismatch_notes",
}
VALID_VERDICTS = {"accept", "accepted", "reject", "rejected", "near_miss", "borderline"}


def _missing(payload: dict[str, Any], required: set[str]) -> list[str]:
    return sorted(key for key in required if key not in payload)


def _require_list(payload: dict[str, Any], key: str) -> None:
    if not isinstance(payload.get(key), list) or not payload[key]:
        raise ValueError(f"{key} must be a non-empty list")


def _require_min_list(payload: dict[str, Any], key: str, min_count: int) -> None:
    value = payload.get(key)
    if not isinstance(value, list) or len(value) < min_count:
        raise ValueError(f"{key} must include at least {min_count} items")


def validate_card(payload: dict[str, Any]) -> dict[str, Any]:
    missing = _missing(payload, CARD_REQUIRED)
    if missing:
        raise ValueError(f"Structure card missing required fields: {', '.join(missing)}")
    if "source_layer" not in payload and "source_type" not in payload:
        raise ValueError("Structure card must include source_layer or source_type")
    _require_list(payload, "roles")
    _require_list(payload, "relations")
    _require_list(payload, "evidence_spans")
    if not isinstance(payload.get("abstractions"), dict):
        raise ValueError("abstractions must be an object")
    _validate_causal_graph(payload)
    return payload


def validate_pair_report(payload: dict[str, Any]) -> dict[str, Any]:
    missing = _missing(payload, PAIR_REQUIRED)
    if missing:
        raise ValueError(f"Pair report missing required fields: {', '.join(missing)}")
    if not isinstance(payload.get("role_alignments"), list) or not payload["role_alignments"]:
        raise ValueError("role_alignments must be a non-empty list")
    _require_number(payload, "surface_distance")
    _require_number(payload, "structural_alignment_score")
    _require_number(payload, "novelty_score")
    _require_min_list(payload, "seed_evidence_spans", 2)
    _require_min_list(payload, "candidate_evidence_spans", 2)
    return payload


def validate_critic_report(payload: dict[str, Any]) -> dict[str, Any]:
    missing = _missing(payload, CRITIC_REQUIRED)
    if missing:
        raise ValueError(f"Critic report missing required fields: {', '.join(missing)}")
    verdict = str(payload["verdict"]).lower()
    if verdict not in VALID_VERDICTS:
        raise ValueError(f"Unsupported critic verdict: {payload['verdict']}")
    if not isinstance(payload.get("scores"), dict) or not payload["scores"]:
        raise ValueError("scores must be a non-empty object")
    if not payload.get("mismatch_notes"):
        raise ValueError("mismatch_notes is required")
    require_critic_thresholds(payload)
    return payload


def validate_constellation_report(payload: dict[str, Any]) -> dict[str, Any]:
    missing = _missing(payload, CONSTELLATION_REQUIRED)
    if missing:
        raise ValueError(f"Constellation report missing required fields: {', '.join(missing)}")
    if not isinstance(payload.get("resonance_doc_ids"), list) or len(payload["resonance_doc_ids"]) < 2:
        raise ValueError("resonance_doc_ids must include at least two documents")
    if not isinstance(payload.get("evidence_network"), list) or len(payload["evidence_network"]) < 3:
        raise ValueError("evidence_network must include at least three evidence links")
    if not isinstance(payload.get("isomorphism_network"), dict) or not payload["isomorphism_network"]:
        raise ValueError("isomorphism_network must be a non-empty object")
    return payload


def normalize_verdict(verdict: str) -> str:
    value = verdict.lower()
    if value in {"accept", "accepted"}:
        return "accepted"
    if value in {"near_miss", "borderline"}:
        return "near_miss"
    return "rejected"


def _require_number(payload: dict[str, Any], key: str) -> None:
    value = payload.get(key)
    if not isinstance(value, int | float):
        raise ValueError(f"{key} must be a number")
    if value < 0 or value > 1:
        raise ValueError(f"{key} must be between 0 and 1")


def _validate_causal_graph(payload: dict[str, Any]) -> None:
    graph = payload.get("causal_graph")
    if not isinstance(graph, dict):
        raise ValueError("causal_graph must be an object")
    nodes = graph.get("nodes")
    edges = graph.get("edges")
    if not isinstance(nodes, list) or not nodes:
        raise ValueError("causal_graph.nodes must be a non-empty list")
    if not isinstance(edges, list) or not edges:
        raise ValueError("causal_graph.edges must be a non-empty list")
    node_ids = {node.get("id") for node in nodes if isinstance(node, dict)}
    for edge in edges:
        if not isinstance(edge, dict):
            raise ValueError("causal_graph edges must be objects")
        if edge.get("src") not in node_ids or edge.get("dst") not in node_ids:
            raise ValueError("causal_graph edge references unknown node")
