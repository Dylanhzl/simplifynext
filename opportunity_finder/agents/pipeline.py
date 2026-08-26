import asyncio
from typing import Any

from opportunity_finder.agents.brand_gap import BrandGapAgent
from opportunity_finder.agents.collab_scout import CollabScoutAgent
from opportunity_finder.agents.niche_query import NicheQueryAgent
from opportunity_finder.agents.opportunity_cluster import OpportunityClusterAgent
from opportunity_finder.agents.opportunity_scorer import OpportunityScorerAgent
from opportunity_finder.agents.trend_harvester import TrendHarvesterAgent
from shared.agent_base import Agent
from shared.agent_util import ping, with_span


class OpportunityFinderPipeline(Agent):
    name = "OpportunityFinderPipeline"
    kind = "sequential"

    async def run(self, state: dict[str, Any]) -> dict[str, Any]:
        """Sequential: query → harvest (parallel) → cluster → score."""
        with with_span(self.name, self.kind, state):
            ping(state, self.name, "sequential", "query → harvest → cluster → score")
            await NicheQueryAgent().run(state)
            ping(state, self.name, "parallel", "Fan-out: trend, brand-gap, collab.")
            await asyncio.gather(
                TrendHarvesterAgent().run(state),
                BrandGapAgent().run(state),
                CollabScoutAgent().run(state),
            )
            raw = [
                *(state.get("trend_opps") or []),
                *(state.get("brand_opps") or []),
                *(state.get("collab_opps") or []),
            ]
            seen: set[str] = set()
            deduped = []
            for opp in raw:
                oid = str(opp.get("id") or "")
                if oid and oid not in seen:
                    seen.add(oid)
                    deduped.append(opp)
            state["raw_finds"] = deduped
            await OpportunityClusterAgent().run(state)
            await OpportunityScorerAgent().run(state)
            ping(state, self.name, "sequential", f"Returning {len(state.get('opportunities') or [])} opportunities.")
        return state
