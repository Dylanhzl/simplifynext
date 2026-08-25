from typing import Any

from shared.agent_base import Agent


class TrendHarvesterAgent(Agent):
    name = "TrendHarvesterAgent"
    kind = "llm"

    async def run(self, state: dict[str, Any]) -> dict[str, Any]:
        """Find trending topics and hooks."""
        raise NotImplementedError("TrendHarvesterAgent is scaffold-only")
