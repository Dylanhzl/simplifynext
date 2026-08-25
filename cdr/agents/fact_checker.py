from typing import Any

from shared.agent_base import Agent


class FactCheckerAgent(Agent):
    name = "FactCheckerAgent"
    kind = "llm"

    async def run(self, state: dict[str, Any]) -> dict[str, Any]:
        """Structured pass/fail verdict on claims."""
        raise NotImplementedError("FactCheckerAgent is scaffold-only")
