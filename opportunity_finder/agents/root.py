from typing import Any

from opportunity_finder.agents.pipeline import OpportunityFinderPipeline
from shared.agent_base import Agent
from shared.agent_util import ping, with_span


class OpportunityFinderRoot(Agent):
    name = "OpportunityFinderRoot"
    kind = "custom"

    async def run(self, state: dict[str, Any]) -> dict[str, Any]:
        with with_span(self.name, self.kind, state):
            ping(state, self.name, "custom", "Running finder pipeline.")
            state = await OpportunityFinderPipeline().run(state)
            ping(
                state,
                self.name,
                "custom",
                f"Done. {len(state.get('opportunities') or [])} ranked.",
                artifact_ref="SearchResponse",
            )
        return state
