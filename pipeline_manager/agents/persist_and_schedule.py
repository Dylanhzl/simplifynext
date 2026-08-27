from typing import Any

from shared.agent_base import Agent
from observability.otel import agent_span
from pipeline_manager.agents.opportunity_clerk import OpportunityClerkAgent
from pipeline_manager.agents.qualification import QualificationAgent
from pipeline_manager.agents.follow_up_planner import FollowUpPlannerAgent
from pipeline_manager.agents.calendar_assistant import CalendarAssistantAgent


class PersistAndSchedule(Agent):
    name = "PersistAndSchedule"
    kind = "sequential"

    async def run(self, state: dict[str, Any]) -> dict[str, Any]:
        """Clerk → qualify → follow-up → calendar."""
        run_id = state.get("run_id", "")
        steps = (
            OpportunityClerkAgent(),
            QualificationAgent(),
            FollowUpPlannerAgent(),
            CalendarAssistantAgent(),
        )
        for step in steps:
            with agent_span(step.name, step.kind, run_id):
                state = await step.run(state)
        return state
