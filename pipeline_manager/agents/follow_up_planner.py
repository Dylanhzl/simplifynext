from typing import Any

from shared.agent_base import Agent


class FollowUpPlannerAgent(Agent):
    name = "FollowUpPlannerAgent"
    kind = "llm"

    async def run(self, state: dict[str, Any]) -> dict[str, Any]:
        """Next action after outreach."""
        raise NotImplementedError("FollowUpPlannerAgent is scaffold-only")
