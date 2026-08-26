from typing import Any

from cdr.agents._util import ping, with_span
from cdr.agents.outreach_script import OutreachScriptAgent
from cdr.agents.outreach_strategy import OutreachStrategyAgent
from cdr.agents.pitch_email import PitchEmailAgent
from shared.agent_base import Agent


class OutreachPipeline(Agent):
    name = "OutreachPipeline"
    kind = "sequential"

    async def run(self, state: dict[str, Any]) -> dict[str, Any]:
        with with_span(self.name, self.kind, state):
            ping(state, self.name, "sequential", "Strategy → script → email.")
            await OutreachStrategyAgent().run(state)
            await OutreachScriptAgent().run(state)
            await PitchEmailAgent().run(state)
        return state
