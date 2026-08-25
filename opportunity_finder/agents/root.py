from typing import Any

from shared.agent_base import Agent


class OpportunityFinderRoot(Agent):
    name = "OpportunityFinderRoot"
    kind = "custom"

    async def run(self, state: dict[str, Any]) -> dict[str, Any]:
        """FastAPI entry that runs the finder pipeline."""
        raise NotImplementedError("OpportunityFinderRoot is scaffold-only")
