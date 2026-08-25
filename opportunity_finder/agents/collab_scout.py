from typing import Any

from shared.agent_base import Agent


class CollabScoutAgent(Agent):
    name = "CollabScoutAgent"
    kind = "llm"

    async def run(self, state: dict[str, Any]) -> dict[str, Any]:
        """Find peer collab openings."""
        raise NotImplementedError("CollabScoutAgent is scaffold-only")
