from typing import Any

from shared.agent_base import Agent


class PainPointAgent(Agent):
    name = "PainPointAgent"
    kind = "llm"

    async def run(self, state: dict[str, Any]) -> dict[str, Any]:
        """Pain points the content should address."""
        raise NotImplementedError("PainPointAgent is scaffold-only")
