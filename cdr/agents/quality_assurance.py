from typing import Any

from shared.agent_base import Agent


class QualityAssurancePipeline(Agent):
    name = "QualityAssurancePipeline"
    kind = "sequential"

    async def run(self, state: dict[str, Any]) -> dict[str, Any]:
        """Draft → fact → voice."""
        raise NotImplementedError("QualityAssurancePipeline is scaffold-only")
