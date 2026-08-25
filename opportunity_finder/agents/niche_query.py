from typing import Any

from shared.agent_base import Agent


class NicheQueryAgent(Agent):
    name = "NicheQueryAgent"
    kind = "llm"

    async def run(self, state: dict[str, Any]) -> dict[str, Any]:
        """Turn creator profile into search queries."""
        raise NotImplementedError("NicheQueryAgent is scaffold-only")
