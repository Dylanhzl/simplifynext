from typing import Any

from shared.agent_base import Agent


class VoiceCritiqueAgent(Agent):
    name = "VoiceCritiqueAgent"
    kind = "llm"

    async def run(self, state: dict[str, Any]) -> dict[str, Any]:
        """Structured pass/fail on brand voice."""
        raise NotImplementedError("VoiceCritiqueAgent is scaffold-only")
