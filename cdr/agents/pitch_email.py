from typing import Any

from shared.agent_base import Agent


class PitchEmailAgent(Agent):
    name = "PitchEmailAgent"
    kind = "llm"

    async def run(self, state: dict[str, Any]) -> dict[str, Any]:
        """Brand pitch email."""
        raise NotImplementedError("PitchEmailAgent is scaffold-only")
