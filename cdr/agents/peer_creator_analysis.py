from typing import Any

from cdr.agents._util import ping, with_span
from cdr.llm import complete_json
from shared.agent_base import Agent


class PeerCreatorAnalysisAgent(Agent):
    name = "PeerCreatorAnalysisAgent"
    kind = "llm"

    async def run(self, state: dict[str, Any]) -> dict[str, Any]:
        with with_span(self.name, self.kind, state):
            ping(state, self.name, "llm", "What peer creators are doing.")
            data = await complete_json(
                "You are PeerCreatorAnalysisAgent. Return JSON {peer_moves}.",
                f"opp={state.get('current')}",
                agent=self.name,
            )
            state["peer_moves"] = data.get("peer_moves", "")
        return state
