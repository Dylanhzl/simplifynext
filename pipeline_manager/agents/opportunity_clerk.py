from typing import Any

from shared.agent_base import Agent


class OpportunityClerkAgent(Agent):
    name = "OpportunityClerkAgent"
    kind = "llm"

    async def run(self, state: dict[str, Any]) -> dict[str, Any]:
        """Idempotent upsert of pipeline records."""
        raise NotImplementedError("OpportunityClerkAgent is scaffold-only")
