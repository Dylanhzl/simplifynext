from __future__ import annotations

from typing import Any

from shared.schemas import Opportunity


def coerce_opportunity(raw: dict[str, Any], *, source_agent: str, city: str, niche: str) -> dict[str, Any] | None:
    if not raw:
        return None
    data = dict(raw)
    data.setdefault("source_agent", source_agent)
    data.setdefault("city", city)
    data.setdefault("niche", niche)
    data.setdefault("status", "new")
    data.setdefault("evidence_urls", [])
    data.setdefault("raw_notes", "")
    data.setdefault("score", 70)
    try:
        return Opportunity.model_validate(data).model_dump(mode="json")
    except Exception:
        return None


def coerce_many(
    rows: list[Any],
    *,
    source_agent: str,
    city: str,
    niche: str,
) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    seen: set[str] = set()
    for row in rows:
        if not isinstance(row, dict):
            continue
        item = coerce_opportunity(row, source_agent=source_agent, city=city, niche=niche)
        if not item or item["id"] in seen:
            continue
        seen.add(item["id"])
        out.append(item)
    return out
