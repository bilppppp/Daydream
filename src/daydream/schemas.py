from __future__ import annotations

from typing import Any

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
CONSTELLATION_REQUIRED = {
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
    missing = _missing(payload, CONSTELLATION_REQUIRED)
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
        elif node["type"] == "tension":
            _require_object_fields(node, "tension node", {"description", "why_it_matters"})
        elif node["type"] == "question":
            _require_object_fields(node, "question node", {"question", "preferred_strategy"})
            if node["preferred_strategy"] not in DREAM_STRATEGIES:
                raise ValueError("question node preferred_strategy is unsupported")
        else:
            raise ValueError("nodes item type must be document, concept, tension, or question")

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


def _missing(payload: dict[str, Any], required: set[str]) -> list[str]:
    return sorted(key for key in required if key not in payload)


def _require_list(payload: dict[str, Any], key: str) -> None:
    if not isinstance(payload.get(key), list) or not payload[key]:
        raise ValueError(f"{key} must be a non-empty list")


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


def _require_object_fields(payload: Any, label: str, fields: set[str]) -> None:
    if not isinstance(payload, dict):
        raise ValueError(f"{label} must be an object")
    missing = _missing(payload, fields)
    if missing:
        raise ValueError(f"{label} missing required fields: {', '.join(missing)}")


def _require_unit_number(payload: dict[str, Any], key: str) -> None:
    value = payload.get(key)
    if not isinstance(value, int | float):
        raise ValueError(f"{key} must be a number")
    if value < 0 or value > 1:
        raise ValueError(f"{key} must be between 0 and 1")
