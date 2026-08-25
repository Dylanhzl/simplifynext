from typing import Any

from shared.agent_base import Agent


class EngagementIngestAgent(Agent):
    name = "EngagementIngestAgent"
    kind = "llm"

    async def run(self, state: dict[str, Any]) -> dict[str, Any]:
        """Normalize inbound email/analytics/comments."""
        raise NotImplementedError("EngagementIngestAgent is scaffold-only")
