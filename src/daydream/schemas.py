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

SEED_CARD_REQUIRED = {
    "card_type",
    "seed_document",
    "core_summary",
    "core_claim",
    "core_concepts",
    "tensions",
    "mechanisms",
    "failure_modes",
    "questions_to_dream_on",
    "avoid_searching_for",
    "evidence_spans",
}

DAYDREAM_CONSTELLATION_REQUIRED = {
    "graph_type",
    "article",
    "seed_document",
    "nodes",
    "edges",
    "ranked_connections",
    "search_coverage",
}

ABSTRACTION_LEVELS = {"surface", "mechanism", "meta"}
DREAM_STRATEGIES = {
    "random_collision",
    "tag_bridge",
    "temporal_bridge",
    "same_problem_different_domain",
}
CONNECTION_KINDS = {
    "close_echo",
    "mechanism_match",
    "failure_rhyme",
    "bridge",
    "distant_echo",
    "contrast",
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
OPPONENT_REQUIRED = {
    "run_id",
    "target_type",
    "target_id",
    "objections",
    "strongest_objection",
    "recommendation",
}
ADJUDICATION_REQUIRED = {
    "run_id",
    "target_type",
    "target_id",
    "verdict",
    "proponent_summary",
    "opponent_summary",
    "hard_reject_reasons",
    "rationale",
}
MESH_REQUIRED = {
    "run_id",
    "cluster_id",
    "systemic_archetype",
    "participating_doc_ids",
    "hyperedges",
    "evidence_mesh",
    "mismatch_notes",
}
VALID_VERDICTS = {"accept", "accepted", "reject", "rejected", "near_miss", "borderline"}
ADVERSARIAL_RECOMMENDATIONS = {"reject", "near_miss", "pass"}


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


def validate_seed_card(payload: dict[str, Any]) -> dict[str, Any]:
    missing = _missing(payload, SEED_CARD_REQUIRED)
    if missing:
        raise ValueError(f"Seed card missing required fields: {', '.join(missing)}")
    if payload["card_type"] != "dream_seed_card":
        raise ValueError("card_type must be dream_seed_card")

    _require_object_fields(payload["seed_document"], "seed_document", {"title", "path", "source_layer"})
    _require_non_empty_text(payload, "core_summary")
    _require_non_empty_text(payload, "core_claim")
    _require_non_empty_dict_list(payload, "core_concepts")
    _require_non_empty_dict_list(payload, "tensions")
    _require_non_empty_dict_list(payload, "mechanisms")
    _require_non_empty_dict_list(payload, "failure_modes")
    _require_non_empty_dict_list(payload, "questions_to_dream_on")
    _require_string_list(payload, "avoid_searching_for")
    _require_non_empty_text_list(payload, "evidence_spans")

    for concept in payload["core_concepts"]:
        _require_object_fields(
            concept,
            "core_concepts item",
            {"name", "meaning", "search_text", "keywords", "abstraction_level"},
        )
        _require_non_empty_text_list(concept, "search_text")
        _require_string_list(concept, "keywords")
        if concept["abstraction_level"] not in ABSTRACTION_LEVELS:
            raise ValueError("core_concepts item abstraction_level must be surface, mechanism, or meta")

    for tension in payload["tensions"]:
        _require_object_fields(tension, "tensions item", {"description", "why_it_matters"})

    for mechanism in payload["mechanisms"]:
        _require_object_fields(mechanism, "mechanisms item", {"name", "description", "search_text"})
        _require_non_empty_text_list(mechanism, "search_text")

    for failure_mode in payload["failure_modes"]:
        _require_object_fields(failure_mode, "failure_modes item", {"description", "search_text"})
        _require_non_empty_text_list(failure_mode, "search_text")

    for question in payload["questions_to_dream_on"]:
        _require_object_fields(question, "questions_to_dream_on item", {"question", "preferred_strategy"})
        if question["preferred_strategy"] not in DREAM_STRATEGIES:
            raise ValueError("questions_to_dream_on item preferred_strategy is unsupported")
    return payload


def validate_constellation(payload: dict[str, Any]) -> dict[str, Any]:
    missing = _missing(payload, DAYDREAM_CONSTELLATION_REQUIRED)
    if missing:
        raise ValueError(f"Constellation missing required fields: {', '.join(missing)}")
    if payload["graph_type"] != "daydream_constellation":
        raise ValueError("graph_type must be daydream_constellation")

    _require_object_fields(payload["article"], "article", {"title", "path", "thesis"})
    _require_object_fields(payload["seed_document"], "seed_document", {"title", "path", "source_layer"})
    _require_non_empty_dict_list(payload, "nodes")
    _require_non_empty_dict_list(payload, "edges")
    _require_non_empty_dict_list(payload, "ranked_connections")
    _require_object_fields(
        payload["search_coverage"],
        "search_coverage",
        {"connection_count", "documents_considered", "documents_used", "notes"},
    )

    node_ids: set[str] = set()
    for node in payload["nodes"]:
        _require_object_fields(node, "nodes item", {"id", "type"})
        node_id = str(node["id"])
        if not node_id:
            raise ValueError("nodes item id must not be empty")
        node_ids.add(node_id)
        if node["type"] == "document":
            _require_object_fields(node, "document node", {"title", "path", "source_layer", "role"})
        elif node["type"] == "concept":
            _require_object_fields(node, "concept node", {"label", "meaning", "abstraction_level"})
            if node["abstraction_level"] not in ABSTRACTION_LEVELS:
                raise ValueError("concept node abstraction_level must be surface, mechanism, or meta")
        else:
            raise ValueError("nodes item type must be document or concept")

    for edge in payload["edges"]:
        _require_object_fields(edge, "edges item", {"from", "to", "type", "strength", "reason", "evidence"})
        if edge["from"] not in node_ids or edge["to"] not in node_ids:
            raise ValueError("edges item references unknown node")
        _require_unit_number(edge, "strength")
        _require_non_empty_text_list(edge, "evidence")

    for connection in payload["ranked_connections"]:
        _require_object_fields(
            connection,
            "ranked_connections item",
            {
                "rank",
                "from_node",
                "to_node",
                "strength",
                "connection_name",
                "connection_kind",
                "why_it_matters",
                "why_not_topic_overlap",
                "used_in_article_section",
                "documents_involved",
            },
        )
        if connection["from_node"] not in node_ids or connection["to_node"] not in node_ids:
            raise ValueError("ranked_connections item references unknown node")
        _require_unit_number(connection, "strength")
        if connection["connection_kind"] not in CONNECTION_KINDS:
            raise ValueError("ranked_connections item connection_kind is unsupported")
        _require_non_empty_text_list(connection, "documents_involved")
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


def validate_opponent_report(payload: dict[str, Any]) -> dict[str, Any]:
    missing = _missing(payload, OPPONENT_REQUIRED)
    if missing:
        raise ValueError(f"Opponent report missing required fields: {', '.join(missing)}")
    _require_min_list(payload, "objections", 1)
    if str(payload["recommendation"]).lower() not in ADVERSARIAL_RECOMMENDATIONS:
        raise ValueError(f"Unsupported opponent recommendation: {payload['recommendation']}")
    return payload


def validate_adjudication_report(payload: dict[str, Any]) -> dict[str, Any]:
    missing = _missing(payload, ADJUDICATION_REQUIRED)
    if missing:
        raise ValueError(f"Adjudication report missing required fields: {', '.join(missing)}")
    verdict = str(payload["verdict"]).lower()
    if verdict not in VALID_VERDICTS:
        raise ValueError(f"Unsupported adjudication verdict: {payload['verdict']}")
    if not isinstance(payload.get("hard_reject_reasons"), list):
        raise ValueError("hard_reject_reasons must be a list")
    if verdict in {"accept", "accepted"} and payload["hard_reject_reasons"]:
        raise ValueError("accepted adjudication cannot include hard_reject_reasons")
    return payload


def validate_mesh_report(payload: dict[str, Any]) -> dict[str, Any]:
    missing = _missing(payload, MESH_REQUIRED)
    if missing:
        raise ValueError(f"Mesh report missing required fields: {', '.join(missing)}")
    _require_min_list(payload, "participating_doc_ids", 3)
    _require_min_list(payload, "hyperedges", 1)
    _require_min_list(payload, "evidence_mesh", 3)
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


def _require_unit_number(payload: dict[str, Any], key: str) -> None:
    _require_number(payload, key)


def _require_object_fields(payload: Any, label: str, fields: set[str]) -> None:
    if not isinstance(payload, dict):
        raise ValueError(f"{label} must be an object")
    missing = _missing(payload, fields)
    if missing:
        raise ValueError(f"{label} missing required fields: {', '.join(missing)}")


def _require_non_empty_dict_list(payload: dict[str, Any], key: str) -> None:
    _require_list(payload, key)
    if not all(isinstance(item, dict) for item in payload[key]):
        raise ValueError(f"{key} items must be objects")


def _require_non_empty_text(payload: dict[str, Any], key: str) -> None:
    value = payload.get(key)
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{key} must be a non-empty string")


def _require_non_empty_text_list(payload: dict[str, Any], key: str) -> None:
    _require_list(payload, key)
    if not all(isinstance(item, str) and item.strip() for item in payload[key]):
        raise ValueError(f"{key} must contain non-empty strings")


def _require_string_list(payload: dict[str, Any], key: str) -> None:
    value = payload.get(key)
    if not isinstance(value, list) or not all(isinstance(item, str) for item in value):
        raise ValueError(f"{key} must be a list of strings")


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
