from typing import Any

from cdr.agents._util import ping, with_span
from cdr.agents.fact_checker import FactCheckerAgent
from cdr.agents.voice_critique import VoiceCritiqueAgent
from shared.agent_base import Agent


class QualityAssurancePipeline(Agent):
    name = "QualityAssurancePipeline"
    kind = "sequential"

    async def run(self, state: dict[str, Any]) -> dict[str, Any]:
        with with_span(self.name, self.kind, state):
            ping(state, self.name, "sequential", "Fact → voice (writer lives in RefinementLoop).")
            await FactCheckerAgent().run(state)
            await VoiceCritiqueAgent().run(state)
        return state
