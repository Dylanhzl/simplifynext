from pathlib import Path
from typing import Any

from opportunity_finder.normalize import coerce_many
from opportunity_finder.tools import load_seed
from shared.agent_base import Agent
from shared.agent_util import ping, with_span
from shared.llm import complete_json, seed_opportunities

MEMORY = Path(__file__).resolve().parents[2] / "demo" / "maya" / "memory.json"


def _apply_memory_bias(opps: list[dict[str, Any]]) -> list[dict[str, Any]]:
    bias: list[str] = []
    if MEMORY.exists():
        import json

        bias = list(json.loads(MEMORY.read_text()).get("next_bias") or [])
    blob = " ".join(bias).lower()
    out = []
    for opp in opps:
        item = dict(opp)
        title = f"{item.get('title', '')} {item.get('id', '')}".lower()
        if "dessert" in blob and ("chendol" in title or "dessert" in title):
            item["score"] = min(int(item.get("score") or 62), 55)
            item["raw_notes"] = (item.get("raw_notes") or "") + " Week-2: dessert deprioritized."
        if "leftover-stock" in blob or "hawker how-to" in blob:
            if "laksa" in title and int(item.get("score") or 0) < 95:
                item["score"] = min(100, int(item.get("score") or 0) + 2)
        out.append(item)
    return out


class OpportunityScorerAgent(Agent):
    name = "OpportunityScorerAgent"
    kind = "llm"

    async def run(self, state: dict[str, Any]) -> dict[str, Any]:
        with with_span(self.name, self.kind, state):
            ping(state, self.name, "llm", "Scoring and ranking for profile fit.")
            city = str(state.get("city") or "Singapore")
            niche = str(state.get("niche") or "singapore hawker food")
            raw = list(state.get("raw_finds") or [])
            if not any(r.get("id") == "opp-gap-dessert" for r in raw):
                raw.extend(seed_opportunities("OpportunityScorerAgent"))
            data = await complete_json(
                "You are OpportunityScorerAgent. Return {opportunities: Opportunity[]} with score 0-100.",
                f"opportunities={raw}\nclusters={state.get('clusters')}\nmemory_bias={state.get('memory')}",
                agent=self.name,
            )
            scored = coerce_many(
                list(data.get("opportunities") or []) or load_seed(),
                source_agent=self.name,
                city=city,
                niche=niche,
            )
            # keep original source_agent when the scorer only ranks
            by_id = {r["id"]: r for r in raw if r.get("id")}
            merged = []
            seen: set[str] = set()
            for item in scored:
                base = dict(by_id.get(item["id"]) or item)
                base["score"] = int(item.get("score") or base.get("score") or 70)
                if item["id"] not in seen:
                    seen.add(item["id"])
                    merged.append(base)
            for row in load_seed():
                if row["id"] not in seen:
                    merged.append(row)
                    seen.add(row["id"])
            merged = _apply_memory_bias(merged)
            merged.sort(key=lambda o: int(o.get("score") or 0), reverse=True)
            limit = int(state.get("limit") or 8)
            state["opportunities"] = merged[:limit]
            ping(state, self.name, "llm", f"Ranked {len(state['opportunities'])}.", artifact_ref="ranked")
        return state
