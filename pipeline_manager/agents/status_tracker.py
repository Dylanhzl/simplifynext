from typing import Any

from shared.agent_base import Agent


class StatusTrackerAgent(Agent):
    name = "StatusTrackerAgent"
    kind = "llm"

    async def run(self, state: dict[str, Any]) -> dict[str, Any]:
        """Only writer of opportunity status besides clerk."""
        raise NotImplementedError("StatusTrackerAgent is scaffold-only")
