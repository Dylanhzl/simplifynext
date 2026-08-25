from typing import Any

from shared.agent_base import Agent


class OpportunityScorerAgent(Agent):
    name = "OpportunityScorerAgent"
    kind = "llm"

    async def run(self, state: dict[str, Any]) -> dict[str, Any]:
        """Rank opportunities 0-100 for profile fit."""
        raise NotImplementedError("OpportunityScorerAgent is scaffold-only")
