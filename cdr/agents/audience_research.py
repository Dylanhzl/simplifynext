from typing import Any

from cdr.agents._util import ping, with_span
from cdr.llm import complete_json
from cdr.mcp_client import retrieve_creator_memory
from shared.agent_base import Agent


class AudienceResearchAgent(Agent):
    name = "AudienceResearchAgent"
    kind = "llm"

    async def run(self, state: dict[str, Any]) -> dict[str, Any]:
        with with_span(self.name, self.kind, state):
            ping(state, self.name, "llm", "Audience insight for current opportunity.")
            mem = await retrieve_creator_memory("maya audience laksa hostel")
            data = await complete_json(
                "You are AudienceResearchAgent. Return JSON {audience_insight}.",
                f"opp={state.get('current')}\nmemory={mem}",
                agent=self.name,
            )
            state["audience_insight"] = data.get("audience_insight", "")
            ping(state, self.name, "tool", "retrieve_creator_memory used", artifact_ref="rag")
        return state
