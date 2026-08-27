"""Sequential ingest → classify → adapt."""

from __future__ import annotations

from typing import Any, Callable

from engagement_listener.agents.engagement_ingest import EngagementIngestAgent
from engagement_listener.agents.performance_adapt import PerformanceAdaptAgent
from engagement_listener.agents.reply_classifier import ReplyClassifierAgent


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
    graph = compiled()
    if graph is not None:
        return await graph.ainvoke(state)
    state = await EngagementIngestAgent().run(state)
    state = await ReplyClassifierAgent().run(state)
    return await PerformanceAdaptAgent().run(state)
