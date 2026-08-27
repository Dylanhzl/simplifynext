"""LangGraph sequential persist: clerk → qualify → follow-up → calendar → status."""

from __future__ import annotations

from typing import Any, Callable

from pipeline_manager.agents.calendar_assistant import CalendarAssistantAgent
from pipeline_manager.agents.follow_up_planner import FollowUpPlannerAgent
from pipeline_manager.agents.opportunity_clerk import OpportunityClerkAgent
from pipeline_manager.agents.persist_and_schedule import PersistAndSchedule
from pipeline_manager.agents.qualification import QualificationAgent
from pipeline_manager.agents.status_tracker import StatusTrackerAgent


def build_graph() -> Callable | None:
    try:
        from langgraph.graph import END, START, StateGraph
    except Exception:
        return None

    g = StateGraph(dict)
    g.add_node("clerk", OpportunityClerkAgent().run)
    g.add_node("qualify", QualificationAgent().run)
    g.add_node("followup", FollowUpPlannerAgent().run)
    g.add_node("calendar", CalendarAssistantAgent().run)
    g.add_node("status", StatusTrackerAgent().run)
    g.add_edge(START, "clerk")
    g.add_edge("clerk", "qualify")
    g.add_edge("qualify", "followup")
    g.add_edge("followup", "calendar")
    g.add_edge("calendar", "status")
    g.add_edge("status", END)
    return g.compile()


_COMPILED = None


def compiled():
    global _COMPILED
    if _COMPILED is None:
        _COMPILED = build_graph()
    return _COMPILED


async def run_persist(state: dict[str, Any]) -> dict[str, Any]:
    if not state.get("target_status") and not state.get("status"):
        state["target_status"] = "outreached"
    graph = compiled()
    if graph is not None:
        return await graph.ainvoke(state)
    return await PersistAndSchedule().run(state)
