from typing import Any

from shared.agent_base import Agent


class ResearchLeadAgent(Agent):
    name = "ResearchLeadAgent"
    kind = "llm"

    async def run(self, state: dict[str, Any]) -> dict[str, Any]:
        """Plan research; call the four research agents as tools."""
        raise NotImplementedError("ResearchLeadAgent is scaffold-only")
