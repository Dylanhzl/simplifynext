from typing import Any

from cdr.agents._util import ping, with_span
from cdr.llm import complete_json
from shared.agent_base import Agent


class OutreachStrategyAgent(Agent):
    name = "OutreachStrategyAgent"
    kind = "llm"

    async def run(self, state: dict[str, Any]) -> dict[str, Any]:
        with with_span(self.name, self.kind, state):
            ping(state, self.name, "llm", "Choose channel and angle.")
            data = await complete_json(
                "You are OutreachStrategyAgent. Return {channel_order, angle, to}.",
                f"opp={state.get('current')}\npackage={state.get('package')}",
                agent=self.name,
            )
            state["outreach_strategy"] = data
        return state
