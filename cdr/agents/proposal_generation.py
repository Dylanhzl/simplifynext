from typing import Any

from shared.agent_base import Agent


class ProposalGenerationAgent(Agent):
    name = "ProposalGenerationAgent"
    kind = "llm"

    async def run(self, state: dict[str, Any]) -> dict[str, Any]:
        """Week plan + hero script + captions + CTA."""
        raise NotImplementedError("ProposalGenerationAgent is scaffold-only")
