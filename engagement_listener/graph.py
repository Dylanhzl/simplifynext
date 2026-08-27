"""Sequential ingest → classify → adapt."""

from __future__ import annotations

from typing import Any, Callable

from engagement_listener.agents.engagement_ingest import EngagementIngestAgent
from engagement_listener.agents.performance_adapt import PerformanceAdaptAgent
from engagement_listener.agents.reply_classifier import ReplyClassifierAgent


def _normalize_engagement_state(state: dict[str, Any]) -> dict[str, Any]:
    """Map batch/analytics shapes onto David's agent contracts."""
    if "payload" not in state:
        items = state.get("items") or []
        if items and isinstance(items[0], dict):
            first = items[0]
            state["payload"] = first.get("payload") or first
            state.setdefault("source", first.get("source") or "email")
            if first.get("opportunity_id") and "opportunity_id" not in state["payload"]:
                state["payload"] = {
                    **state["payload"],
                    "opportunity_id": first["opportunity_id"],
                }
        else:
            state["payload"] = {}

    state.setdefault("source", "email")

    if "posts" not in state:
        analytics = state.get("analytics")
        if isinstance(analytics, dict):
            state["posts"] = analytics.get("posts", [])
        elif state.get("include_analytics") and isinstance(state.get("payload"), dict):
            state["posts"] = state["payload"].get("posts", [])
        else:
            state["posts"] = []

    return state


def build_graph() -> Callable | None:
    try:
        from langgraph.graph import END, START, StateGraph
    except Exception:
        return None

    g = StateGraph(dict)
    g.add_node("ingest", EngagementIngestAgent().run)
    g.add_node("classify", ReplyClassifierAgent().run)
    g.add_node("adapt", PerformanceAdaptAgent().run)
    g.add_edge(START, "ingest")
    g.add_edge("ingest", "classify")
    g.add_edge("classify", "adapt")
    g.add_edge("adapt", END)
    return g.compile()


_COMPILED = None


def compiled():
    global _COMPILED
    if _COMPILED is None:
        _COMPILED = build_graph()
    return _COMPILED


async def run_engagement(state: dict[str, Any]) -> dict[str, Any]:
    state = _normalize_engagement_state(dict(state))
    graph = compiled()
    if graph is not None:
        return await graph.ainvoke(state)
    state = await EngagementIngestAgent().run(state)
    state = await ReplyClassifierAgent().run(state)
    return await PerformanceAdaptAgent().run(state)
