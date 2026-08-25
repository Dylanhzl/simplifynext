from typing import Any

from shared.agent_base import Agent


class CalendarAssistantAgent(Agent):
    name = "CalendarAssistantAgent"
    kind = "llm"

    async def run(self, state: dict[str, Any]) -> dict[str, Any]:
        """Propose posting and follow-up slots (Asia/Singapore)."""
        raise NotImplementedError("CalendarAssistantAgent is scaffold-only")
