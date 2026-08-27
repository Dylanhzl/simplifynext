from typing import Any

from cdr.agents._util import ping, with_span
from cdr.llm import complete_json
from shared.agent_base import Agent


class PlatformPresenceAgent(Agent):
    name = "PlatformPresenceAgent"
    kind = "llm"

    async def run(self, state: dict[str, Any]) -> dict[str, Any]:
        with with_span(self.name, self.kind, state):
            ping(state, self.name, "llm", "Brand/platform presence gaps.")
            data = await complete_json(
                "You are PlatformPresenceAgent. Return JSON {platform_presence}.",
                f"opp={state.get('current')}",
                agent=self.name,
            )
            state["platform_presence"] = data.get("platform_presence", "")
        return state
