from typing import Any

from shared.agent_base import Agent


class BrandGapAgent(Agent):
    name = "BrandGapAgent"
    kind = "llm"

    async def run(self, state: dict[str, Any]) -> dict[str, Any]:
        """Find local brands with weak or missing content."""
        raise NotImplementedError("BrandGapAgent is scaffold-only")
