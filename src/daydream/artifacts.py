from __future__ import annotations

from pathlib import Path
from typing import Any

from .fs import append_jsonl, read_json, read_text_or_literal, slugify, write_json
from .runs import resolve_run_dir, update_manifest
from .schemas import (
    normalize_verdict,
    validate_card,
    validate_adjudication_report,
    validate_constellation_report,
    validate_critic_report,
    validate_mesh_report,
    validate_opponent_report,
    validate_pair_report,
)


def save_card(root: Path, run: str, doc: str, input_path: Path) -> dict[str, Any]:
    payload = validate_card(read_json(input_path))
    run_path = resolve_run_dir(root, run)
    doc_slug = slugify(doc)
    card_path = root / "cards" / "by_doc" / f"{doc_slug}.md"
    card_content = "# " + str(payload["title"]) + "\n\n```json\n" + _json_line(payload, pretty=True) + "\n```\n"
    card_path.write_text(card_content, encoding="utf-8")
    append_jsonl(root / "cards" / "cards.jsonl", payload)
    append_jsonl(run_path / "cards.jsonl", payload)
    update_manifest(root, run, artifacts={"cards": "cards.jsonl"})
    return {"saved": str(card_path)}


def save_pair_report(root: Path, run: str, input_path: Path) -> dict[str, Any]:
    payload = validate_pair_report(read_json(input_path))
    run_path = resolve_run_dir(root, run)
    out = run_path / "pair_report.json"
    write_json(out, payload)
    update_manifest(root, run, artifacts={"pair_report": "pair_report.json"})
    return {"saved": str(out)}


def save_critic_report(root: Path, run: str, input_path: Path) -> dict[str, Any]:
    payload = validate_critic_report(read_json(input_path))
    run_path = resolve_run_dir(root, run)
    out = run_path / "critic_report.json"
    write_json(out, payload)
    status = normalize_verdict(str(payload["verdict"]))
    update_manifest(root, run, status=status, artifacts={"critic_report": "critic_report.json"})
    if status in {"rejected", "near_miss"}:
        append_jsonl(
            root / "calibration" / "near_miss_archive.jsonl",
            {
                "run_id": payload["run_id"],
                "status": status,
                "scores": payload["scores"],
                "mismatch_notes": payload["mismatch_notes"],
                "rationale": payload["rationale"],
            },
        )
    return {"saved": str(out), "status": status}


def save_constellation_report(root: Path, run: str, input_path: Path) -> dict[str, Any]:
    payload = validate_constellation_report(read_json(input_path))
    run_path = resolve_run_dir(root, run)
    out = run_path / "constellation_report.json"
    write_json(out, payload)
    update_manifest(root, run, artifacts={"constellation_report": "constellation_report.json"})
    return {"saved": str(out)}


def save_opponent_report(root: Path, run: str, input_path: Path) -> dict[str, Any]:
    payload = validate_opponent_report(read_json(input_path))
    run_path = resolve_run_dir(root, run)
    out = run_path / "opponent_reports.jsonl"
    append_jsonl(out, payload)
    update_manifest(root, run, artifacts={"opponent_reports": "opponent_reports.jsonl"})
    return {"saved": str(out)}


def save_adjudication_report(root: Path, run: str, input_path: Path) -> dict[str, Any]:
    payload = validate_adjudication_report(read_json(input_path))
    run_path = resolve_run_dir(root, run)
    out = run_path / "adjudication_reports.jsonl"
    append_jsonl(out, payload)
    update_manifest(root, run, artifacts={"adjudication_reports": "adjudication_reports.jsonl"})
    return {"saved": str(out), "verdict": normalize_verdict(str(payload["verdict"]))}


def save_mesh_report(root: Path, run: str, input_path: Path) -> dict[str, Any]:
    payload = validate_mesh_report(read_json(input_path))
    run_path = resolve_run_dir(root, run)
    out = run_path / "mesh_report.json"
    write_json(out, payload)
    update_manifest(root, run, artifacts={"mesh_report": "mesh_report.json"})
    return {"saved": str(out)}


def save_mesh_draft(root: Path, run: str, title: str, input_value: str | Path) -> dict[str, Any]:
    run_path = resolve_run_dir(root, run)
    if not _has_accepted_adjudication(run_path / "adjudication_reports.jsonl"):
        raise ValueError("Cannot save mesh draft before an accepted adjudication exists")
    content = read_text_or_literal(input_value)
    out = run_path / "mesh_draft.md"
    out.write_text(content, encoding="utf-8")
    draft_path = root / "drafts" / f"{slugify(title)}.md"
    draft_path.parent.mkdir(parents=True, exist_ok=True)
    draft_path.write_text(content, encoding="utf-8")
    update_manifest(root, run, status="accepted", artifacts={"mesh_draft": "mesh_draft.md", "mesh_draft_copy": str(draft_path)})
    return {"saved": str(out), "draft": str(draft_path)}


def save_draft(root: Path, run: str, title: str, input_value: str | Path) -> dict[str, Any]:
    run_path = resolve_run_dir(root, run)
    critic_path = run_path / "critic_report.json"
    if not critic_path.exists():
        raise ValueError("Cannot save draft before critic_report.json exists")
    critic = read_json(critic_path)
    if normalize_verdict(str(critic.get("verdict", ""))) != "accepted":
        raise ValueError("Cannot save draft unless critic verdict is accepted")
    validate_critic_report(critic)

    content = read_text_or_literal(input_value)
    run_draft = run_path / "draft.md"
    run_draft.write_text(content, encoding="utf-8")
    draft_path = root / "drafts" / f"{slugify(title)}.md"
    draft_path.parent.mkdir(parents=True, exist_ok=True)
    draft_path.write_text(content, encoding="utf-8")
    update_manifest(root, run, status="accepted", artifacts={"draft": "draft.md", "draft_copy": str(draft_path)})
    return {"saved": str(run_draft), "draft": str(draft_path)}


def save_rejection(root: Path, run: str, input_value: str | Path) -> dict[str, Any]:
    content = read_text_or_literal(input_value)
    run_path = resolve_run_dir(root, run)
    out = run_path / "rejection_report.md"
    out.write_text(content, encoding="utf-8")
    update_manifest(root, run, status="rejected", artifacts={"rejection_report": "rejection_report.md"})
    return {"saved": str(out)}


def validate_run(root: Path, run: str = "latest") -> dict[str, Any]:
    issues: list[str] = []
    try:
        run_path = resolve_run_dir(root, run)
        manifest = read_json(run_path / "manifest.json")
    except Exception as exc:
        return {"ok": False, "issues": [str(exc)]}

    status = manifest.get("status")
    if not manifest.get("run_id"):
        issues.append("manifest missing run_id")
    if not manifest.get("strategy"):
        issues.append("manifest missing strategy")
    if (run_path / "critic_report.json").exists():
        try:
            validate_critic_report(read_json(run_path / "critic_report.json"))
        except ValueError as exc:
            issues.append(str(exc))
    if (run_path / "pair_report.json").exists():
        try:
            validate_pair_report(read_json(run_path / "pair_report.json"))
        except ValueError as exc:
            issues.append(str(exc))
    if status == "accepted" and not (run_path / "draft.md").exists():
        issues.append("accepted run missing draft.md")
    if status in {"rejected", "near_miss"} and not (run_path / "rejection_report.md").exists():
        issues.append(f"{status} run missing rejection_report.md")
    return {"ok": not issues, "issues": issues, "run_dir": str(run_path), "status": status}


def _json_line(payload: dict[str, Any], pretty: bool = False) -> str:
    import json

    if pretty:
        return json.dumps(payload, ensure_ascii=False, indent=2)
    return json.dumps(payload, ensure_ascii=False, sort_keys=True)


def _has_accepted_adjudication(path: Path) -> bool:
    if not path.exists():
        return False
    import json

    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        payload = json.loads(line)
        if normalize_verdict(str(payload.get("verdict", ""))) == "accepted":
            return True
    return False
