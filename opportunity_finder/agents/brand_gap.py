from typing import Any

from opportunity_finder.normalize import coerce_many
from opportunity_finder.tools import search_local_places
from shared.agent_base import Agent
from shared.agent_util import ping, with_span
from shared.llm import complete_json, seed_opportunities


class BrandGapAgent(Agent):
    name = "BrandGapAgent"
    kind = "llm"

    async def run(self, state: dict[str, Any]) -> dict[str, Any]:
        with with_span(self.name, self.kind, state):
            ping(state, self.name, "llm", "Scouting local brands with weak short-form.")
            city = str(state.get("city") or "Singapore")
            niche = str(state.get("niche") or "singapore hawker food")
            places = search_local_places(city)
            weak = [p for p in places if not p.get("has_short_form")]
            data = await complete_json(
                "You are BrandGapAgent. Return {opportunities: Opportunity[]} type=brand for places with missing short-form.",
                f"places={weak or places}\ncity={city}\nniche={niche}",
                agent=self.name,
            )
            opps = coerce_many(
                list(data.get("opportunities") or []) or seed_opportunities("BrandGapAgent"),
                source_agent=self.name,
                city=city,
                niche=niche,
            )
            state["brand_opps"] = opps
            ping(state, self.name, "tool", f"{len(opps)} brand-gap finds.", artifact_ref="brand")
        return state
