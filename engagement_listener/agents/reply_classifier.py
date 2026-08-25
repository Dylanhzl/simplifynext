from typing import Any

from shared.agent_base import Agent


class ReplyClassifierAgent(Agent):
    name = "ReplyClassifierAgent"
    kind = "llm"

    async def run(self, state: dict[str, Any]) -> dict[str, Any]:
        """interested / not / meeting / noise."""
        raise NotImplementedError("ReplyClassifierAgent is scaffold-only")
