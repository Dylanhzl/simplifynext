from typing import Any

from opportunity_finder.normalize import coerce_many
from opportunity_finder.tools import search_local_places
from shared.agent_base import Agent
from shared.agent_util import ping, with_span
from shared.llm import complete_json, seed_opportunities


class CollabScoutAgent(Agent):
    name = "CollabScoutAgent"
    kind = "llm"

    async def run(self, state: dict[str, Any]) -> dict[str, Any]:
        with with_span(self.name, self.kind, state):
            ping(state, self.name, "llm", "Scouting stall / peer collabs.")
            city = str(state.get("city") or "Singapore")
            niche = str(state.get("niche") or "singapore hawker food")
            places = [p for p in search_local_places(city) if p.get("category") == "hawker"]
            data = await complete_json(
                "You are CollabScoutAgent. Return {opportunities: Opportunity[]} type=collab.",
                f"places={places}\ncity={city}\nniche={niche}",
                agent=self.name,
            )
            opps = coerce_many(
                list(data.get("opportunities") or []) or seed_opportunities("CollabScoutAgent"),
                source_agent=self.name,
                city=city,
                niche=niche,
            )
            state["collab_opps"] = opps
            ping(state, self.name, "tool", f"{len(opps)} collab finds.", artifact_ref="collab")
        return state
