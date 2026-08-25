from typing import Any

from shared.agent_base import Agent


class OpportunityFinderPipeline(Agent):
    name = "OpportunityFinderPipeline"
    kind = "sequential"

    async def run(self, state: dict[str, Any]) -> dict[str, Any]:
        """Sequential: query → harvest → gap → collab → cluster → score."""
        raise NotImplementedError("OpportunityFinderPipeline is scaffold-only")
