from typing import Any

from shared.agent_base import Agent


class OpportunityClusterAgent(Agent):
    name = "OpportunityClusterAgent"
    kind = "llm"

    async def run(self, state: dict[str, Any]) -> dict[str, Any]:
        """Cluster similar finds."""
        raise NotImplementedError("OpportunityClusterAgent is scaffold-only")
