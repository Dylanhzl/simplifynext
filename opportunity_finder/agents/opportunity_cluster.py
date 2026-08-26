from typing import Any

from shared.agent_base import Agent
from shared.agent_util import ping, with_span
from shared.llm import complete_json


class OpportunityClusterAgent(Agent):
    name = "OpportunityClusterAgent"
    kind = "llm"

    async def run(self, state: dict[str, Any]) -> dict[str, Any]:
        with with_span(self.name, self.kind, state):
            ping(state, self.name, "llm", "Clustering similar finds.")
            raw = list(state.get("raw_finds") or [])
            data = await complete_json(
                "You are OpportunityClusterAgent. Return {clusters: [{theme, ids}] }.",
                f"opportunities={raw}",
                agent=self.name,
            )
            state["clusters"] = list(data.get("clusters") or [])
            ping(state, self.name, "llm", f"{len(state['clusters'])} clusters.", artifact_ref="clusters")
        return state
