from typing import Any

from shared.agent_base import Agent


class PeerCreatorAnalysisAgent(Agent):
    name = "PeerCreatorAnalysisAgent"
    kind = "llm"

    async def run(self, state: dict[str, Any]) -> dict[str, Any]:
        """What peer creators are doing."""
        raise NotImplementedError("PeerCreatorAnalysisAgent is scaffold-only")
