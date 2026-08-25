from typing import Any

from shared.agent_base import Agent


class PlatformPresenceAgent(Agent):
    name = "PlatformPresenceAgent"
    kind = "llm"

    async def run(self, state: dict[str, Any]) -> dict[str, Any]:
        """Brand/platform presence gaps."""
        raise NotImplementedError("PlatformPresenceAgent is scaffold-only")
