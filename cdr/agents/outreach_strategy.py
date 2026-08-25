from typing import Any

from shared.agent_base import Agent


class OutreachStrategyAgent(Agent):
    name = "OutreachStrategyAgent"
    kind = "llm"

    async def run(self, state: dict[str, Any]) -> dict[str, Any]:
        """Choose channel and angle."""
        raise NotImplementedError("OutreachStrategyAgent is scaffold-only")
