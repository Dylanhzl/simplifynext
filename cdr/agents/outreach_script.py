from typing import Any

from shared.agent_base import Agent


class OutreachScriptAgent(Agent):
    name = "OutreachScriptAgent"
    kind = "llm"

    async def run(self, state: dict[str, Any]) -> dict[str, Any]:
        """DM + 30s collab-call script."""
        raise NotImplementedError("OutreachScriptAgent is scaffold-only")
