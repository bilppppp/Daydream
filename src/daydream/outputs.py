from __future__ import annotations

from datetime import datetime
from pathlib import Path

from .fs import ensure_dir, read_json, slugify, write_json
from .schemas import validate_constellation, validate_seed_card


def save_dream_outputs(
    output_dir: Path,
    article_path: Path,
    seed_card_path: Path,
    constellation_path: Path,
    keywords: str,
    completed_at: datetime | None = None,
) -> dict[str, str]:
    article = article_path.read_text(encoding="utf-8")
    seed_card = validate_seed_card(read_json(seed_card_path))
    constellation = validate_constellation(read_json(constellation_path))

    stamp = (completed_at or datetime.now()).strftime("%Y%m%d-%H%M%S")
    prefix = f"{stamp}-{slugify(keywords)}"
    output_dir = ensure_dir(output_dir)
    article_out = output_dir / f"{prefix}.md"
    seed_out = output_dir / f"{prefix}.seed-card.json"
    constellation_out = output_dir / f"{prefix}.constellation.json"

    article_out.write_text(article, encoding="utf-8")
    write_json(seed_out, seed_card)
    write_json(constellation_out, constellation)
    return {
        "article": str(article_out),
        "seed_card": str(seed_out),
        "constellation": str(constellation_out),
        "prefix": prefix,
    }
