from typing import Any

from shared.agent_base import Agent


class RefinementLoop(Agent):
    name = "RefinementLoop"
    kind = "loop"

    async def run(self, state: dict[str, Any]) -> dict[str, Any]:
        """QA until pass or max 3 iterations."""
        raise NotImplementedError("RefinementLoop is scaffold-only")
