from typing import Any

from cdr.agents._util import ping, with_span
from cdr.llm import complete_json
from shared.agent_base import Agent
from shared.schemas import ResearchBrief


class ResearchThenPropose(Agent):
    name = "ResearchThenPropose"
    kind = "sequential"

    async def run(self, state: dict[str, Any]) -> dict[str, Any]:
        from cdr.agents.parallel_research import ParallelResearch
        from cdr.agents.proposal_generation import ProposalGenerationAgent
        from cdr.agents.research_lead import ResearchLeadAgent

        with with_span(self.name, self.kind, state):
            ping(state, self.name, "sequential", "Gather research then generate proposal.")
            await ResearchLeadAgent().run(state)
            await ParallelResearch().run(state)
            if "brief" not in state:
                opp = state.get("current") or {}
                state["brief"] = ResearchBrief(
                    opportunity_id=str(opp.get("id", "")),
                    audience_insight=str(state.get("audience_insight", "")),
                    peer_moves=str(state.get("peer_moves", "")),
                    platform_presence=str(state.get("platform_presence", "")),
                    pain_points=str(state.get("pain_points", "")),
                ).model_dump()
            await ProposalGenerationAgent().run(state)
        return state
