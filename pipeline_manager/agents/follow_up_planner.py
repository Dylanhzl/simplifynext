from typing import Any

from shared.agent_base import Agent
from shared.agent_util import ping, with_span
from shared.llm import complete_json


class FollowUpPlannerAgent(Agent):
    name = "FollowUpPlannerAgent"
    kind = "llm"

    async def run(self, state: dict[str, Any]) -> dict[str, Any]:
        with with_span(self.name, self.kind, state):
            ping(state, self.name, "llm", "Plan next action after outreach.")
            data = await complete_json(
                "You are FollowUpPlannerAgent. Return {actions: [...], meeting_ask: bool}.",
                f"opportunity={state.get('opportunity')}\nqualification={state.get('qualification')}",
                agent=self.name,
            )
            qual = (state.get("qualification") or {}).get("label")
            if qual == "hot":
                data["meeting_ask"] = True
            state["follow_up"] = data
            ping(state, self.name, "llm", f"meeting_ask={data.get('meeting_ask')}.")
        return state
