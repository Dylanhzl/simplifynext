from typing import Any

from shared.agent_base import Agent


class AudienceResearchAgent(Agent):
    name = "AudienceResearchAgent"
    kind = "llm"

    async def run(self, state: dict[str, Any]) -> dict[str, Any]:
        """Audience insight for one opportunity."""
        raise NotImplementedError("AudienceResearchAgent is scaffold-only")
