from typing import Any

from opportunity_finder.normalize import coerce_many
from opportunity_finder.tools import search_web
from shared.agent_base import Agent
from shared.agent_util import ping, with_span
from shared.llm import complete_json, seed_opportunities


class TrendHarvesterAgent(Agent):
    name = "TrendHarvesterAgent"
    kind = "llm"

    async def run(self, state: dict[str, Any]) -> dict[str, Any]:
        with with_span(self.name, self.kind, state):
            ping(state, self.name, "llm", "Harvesting trending hooks.")
            city = str(state.get("city") or "Singapore")
            niche = str(state.get("niche") or "singapore hawker food")
            hits = []
            for q in (state.get("queries") or ["easy laksa Singapore"])[:6]:
                hits.extend(search_web(str(q)).get("results") or [])
            data = await complete_json(
                "You are TrendHarvesterAgent. Return {opportunities: Opportunity[] } type=trend.",
                f"hits={hits[:12]}\ncity={city}\nniche={niche}",
                agent=self.name,
            )
            opps = coerce_many(
                list(data.get("opportunities") or []) or seed_opportunities("TrendHarvesterAgent"),
                source_agent=self.name,
                city=city,
                niche=niche,
            )
            state["trend_opps"] = opps
            ping(state, self.name, "tool", f"{len(opps)} trend finds.", artifact_ref="trend")
        return state
