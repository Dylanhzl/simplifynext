"""LangGraph sequential persist: clerk → qualify → follow-up → calendar → status."""

from __future__ import annotations

from typing import Any, Callable

from pipeline_manager.agents.calendar_assistant import CalendarAssistantAgent
from pipeline_manager.agents.follow_up_planner import FollowUpPlannerAgent
from pipeline_manager.agents.opportunity_clerk import OpportunityClerkAgent
from pipeline_manager.agents.persist_and_schedule import PersistAndSchedule
from pipeline_manager.agents.qualification import QualificationAgent
from pipeline_manager.agents.status_tracker import StatusTrackerAgent


def _normalize_persist_state(state: dict[str, Any]) -> dict[str, Any]:
    """Map legacy/MCP shapes onto David's agent contracts (payload / status keys)."""
    if "payload" not in state:
        payload = dict(state.get("opportunity") or {})
        oid = (
            state.get("opportunity_id")
            or payload.get("id")
            or state.get("id")
            or (state.get("current") or {}).get("id")
        )
        if oid and "id" not in payload:
            payload["id"] = oid
        if not payload:
            for key in ("package", "brief", "outreach", "qa"):
                blob = state.get(key)
                if isinstance(blob, dict) and blob:
                    payload = dict(blob)
                    if oid and "opportunity_id" not in payload:
                        payload["opportunity_id"] = oid
                    break
        state["payload"] = payload

    payload = state.get("payload") or {}
    if not state.get("opportunity_id"):
        state["opportunity_id"] = (
            payload.get("id")
            or payload.get("opportunity_id")
            or state.get("id")
            or (state.get("current") or {}).get("id")
        )

    if not state.get("status"):
        state["status"] = state.get("target_status") or payload.get("status") or "outreached"

    return state


async def _run_status(state: dict[str, Any]) -> dict[str, Any]:
    """StatusTracker needs opportunity_id + status; skip if id is missing."""
    if not state.get("opportunity_id"):
        state["opportunity_id"] = state.get("id") or (state.get("stored") or {}).get("id")
    if not state.get("status"):
        state["status"] = state.get("target_status") or "outreached"
    if not state.get("opportunity_id") or not state.get("status"):
        return state
    return await StatusTrackerAgent().run(state)


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
    g.add_node("status", _run_status)
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
    state = _normalize_persist_state(dict(state))
    graph = compiled()
    if graph is not None:
        return await graph.ainvoke(state)
    # Fallback matches David's PersistAndSchedule, then optional status write.
    state = await PersistAndSchedule().run(state)
    return await _run_status(state)
