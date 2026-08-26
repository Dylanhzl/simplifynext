from typing import Any

from cdr.agents._util import ping, with_span
from cdr.llm import complete_json
from shared.agent_base import Agent


class PainPointAgent(Agent):
    name = "PainPointAgent"
    kind = "llm"

    async def run(self, state: dict[str, Any]) -> dict[str, Any]:
        with with_span(self.name, self.kind, state):
            ping(state, self.name, "llm", "Pain points the content should address.")
            data = await complete_json(
                "You are PainPointAgent. Return JSON {pain_points}.",
                f"opp={state.get('current')}\nprofile={state.get('profile')}",
                agent=self.name,
            )
            state["pain_points"] = data.get("pain_points", "")
        return state
