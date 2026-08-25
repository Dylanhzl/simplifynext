from typing import Any

from shared.agent_base import Agent


class OutreachPipeline(Agent):
    name = "OutreachPipeline"
    kind = "sequential"

    async def run(self, state: dict[str, Any]) -> dict[str, Any]:
        """Strategy → script → email."""
        raise NotImplementedError("OutreachPipeline is scaffold-only")
