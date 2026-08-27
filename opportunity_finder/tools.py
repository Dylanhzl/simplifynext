"""Finder harvest reads local Maya fixtures (MCP exposes the same files for CDR)."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
PLACES = ROOT / "demo" / "maya" / "places_sg_food.json"
SEED = ROOT / "demo" / "maya" / "opportunities_seed.json"


def load_seed() -> list[dict[str, Any]]:
    if not SEED.exists():
        return []
    return list(json.loads(SEED.read_text()).get("opportunities") or [])


def load_places() -> list[dict[str, Any]]:
    if not PLACES.exists():
        return []
    data = json.loads(PLACES.read_text())
    return data if isinstance(data, list) else list(data.get("places") or [])


def search_web(query: str) -> dict[str, Any]:
    q = (query or "").lower()
    hits: list[dict[str, Any]] = []
    for opp in load_seed():
        blob = f"{opp.get('title', '')} {opp.get('why_now', '')} {opp.get('raw_notes', '')}".lower()
        if any(w in blob for w in q.split() if len(w) > 2):
            hits.append(opp)
    for place in load_places():
        blob = f"{place.get('name', '')} {place.get('notes', '')}".lower()
        if any(w in blob for w in q.split() if len(w) > 2):
            hits.append(place)
    return {"query": query, "results": hits or load_seed()[:3]}


def search_local_places(city: str = "Singapore") -> list[dict[str, Any]]:
    places = load_places()
    city_l = city.lower()
    filtered = [p for p in places if city_l in str(p.get("city", "")).lower()]
    return filtered or places


def fetch_url(url: str) -> dict[str, Any]:
    for opp in load_seed():
        if url in (opp.get("evidence_urls") or []):
            return {"url": url, "text": f"{opp.get('title')}. {opp.get('why_now')} {opp.get('raw_notes')}"}
    for place in load_places():
        if str(place.get("place_id", "")) in url:
            return {"url": url, "text": f"{place.get('name')}: {place.get('notes')}"}
    return {"url": url, "text": "Maya hawker niche page (fixture)."}
