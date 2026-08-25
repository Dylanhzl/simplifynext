from typing import Any

from shared.agent_base import Agent


class DraftWriterAgent(Agent):
    name = "DraftWriterAgent"
    kind = "llm"

    async def run(self, state: dict[str, Any]) -> dict[str, Any]:
        """Rewrite package from QA issues."""
        raise NotImplementedError("DraftWriterAgent is scaffold-only")
