from typing import Any

from shared.agent_base import Agent


class ParallelResearch(Agent):
    name = "ParallelResearch"
    kind = "parallel"

    async def run(self, state: dict[str, Any]) -> dict[str, Any]:
        """Fan-out: audience, peers, presence, pain."""
        raise NotImplementedError("ParallelResearch is scaffold-only")
