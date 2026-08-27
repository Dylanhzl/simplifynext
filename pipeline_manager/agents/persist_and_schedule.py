from typing import Any

from pipeline_manager.agents.calendar_assistant import CalendarAssistantAgent
from pipeline_manager.agents.follow_up_planner import FollowUpPlannerAgent
from pipeline_manager.agents.opportunity_clerk import OpportunityClerkAgent
from pipeline_manager.agents.qualification import QualificationAgent
from pipeline_manager.agents.status_tracker import StatusTrackerAgent
from shared.agent_base import Agent
from shared.agent_util import ping, with_span


class PersistAndSchedule(Agent):
    name = "PersistAndSchedule"
    kind = "sequential"

    async def run(self, state: dict[str, Any]) -> dict[str, Any]:
        with with_span(self.name, self.kind, state):
            ping(state, self.name, "sequential", "Clerk → qualify → follow-up → calendar → status.")
            await OpportunityClerkAgent().run(state)
            await QualificationAgent().run(state)
            await FollowUpPlannerAgent().run(state)
            await CalendarAssistantAgent().run(state)
            if not state.get("target_status") and not state.get("status"):
                state["target_status"] = "outreached"
            await StatusTrackerAgent().run(state)
            ping(state, self.name, "sequential", f"Persisted {state.get('opportunity_id')}.")
        return state
