from typing import Any

from cdr.agents._util import ping, with_span
from cdr.llm import complete_json
from shared.agent_base import Agent


class ResearchLeadAgent(Agent):
    name = "ResearchLeadAgent"
    kind = "llm"

    async def run(self, state: dict[str, Any]) -> dict[str, Any]:
        with with_span(self.name, self.kind, state):
            ping(state, self.name, "llm", "Planning research; will tool the four specialists.")
            opp = state.get("current") or {}
            profile = state.get("profile") or {}
            data = await complete_json(
                "You are ResearchLeadAgent. Plan which research tools to call.",
                f"profile={profile}\nopportunity={opp}",
                agent=self.name,
            )
            state["research_plan"] = data
            ping(state, self.name, "tool", f"Plan: {data.get('plan', data)}")
        return state
