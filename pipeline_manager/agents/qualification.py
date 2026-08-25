from typing import Any

from shared.agent_base import Agent


class QualificationAgent(Agent):
    name = "QualificationAgent"
    kind = "llm"

    async def run(self, state: dict[str, Any]) -> dict[str, Any]:
        """Label hot / warm / cold."""
        raise NotImplementedError("QualificationAgent is scaffold-only")
