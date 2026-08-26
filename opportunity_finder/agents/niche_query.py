from typing import Any

from shared.agent_base import Agent
from shared.agent_util import ping, with_span
from shared.llm import complete_json


class NicheQueryAgent(Agent):
    name = "NicheQueryAgent"
    kind = "llm"

    async def run(self, state: dict[str, Any]) -> dict[str, Any]:
        with with_span(self.name, self.kind, state):
            ping(state, self.name, "llm", "Turning profile into search queries.")
            profile = state.get("profile") or {}
            data = await complete_json(
                "You are NicheQueryAgent. Return {queries: string[]} of 5-10 search queries.",
                f"profile={profile}\nniche={state.get('niche')}\ncity={state.get('city')}",
                agent=self.name,
            )
            queries = list(data.get("queries") or [])
            if not queries:
                niche = state.get("niche") or profile.get("niche") or "singapore hawker food"
                city = state.get("city") or profile.get("city") or "Singapore"
                queries = [f"{niche} {city}", f"easy laksa {city}", f"hawker collab {city}"]
            state["queries"] = queries
            ping(state, self.name, "llm", f"{len(queries)} queries.", artifact_ref="queries")
        return state
