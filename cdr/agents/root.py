from typing import Any

from shared.agent_base import Agent


class CDRRootAgent(Agent):
    name = "CDRRootAgent"
    kind = "custom"

    async def run(self, state: dict[str, Any]) -> dict[str, Any]:
        """Orchestrator; other agents and services as tools."""
        raise NotImplementedError("CDRRootAgent is scaffold-only")
