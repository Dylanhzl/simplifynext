from typing import Any

from shared.agent_base import Agent


class ResearchThenPropose(Agent):
    name = "ResearchThenPropose"
    kind = "sequential"

    async def run(self, state: dict[str, Any]) -> dict[str, Any]:
        """Gather research then generate proposal."""
        raise NotImplementedError("ResearchThenPropose is scaffold-only")
