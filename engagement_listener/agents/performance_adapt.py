from typing import Any

from shared.agent_base import Agent


class PerformanceAdaptAgent(Agent):
    name = "PerformanceAdaptAgent"
    kind = "llm"

    async def run(self, state: dict[str, Any]) -> dict[str, Any]:
        """Write memory for the next CDR run."""
        raise NotImplementedError("PerformanceAdaptAgent is scaffold-only")
