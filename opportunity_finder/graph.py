"""LangGraph sequential finder: query → parallel harvest → cluster → score."""

from __future__ import annotations

import asyncio
from typing import Any, Callable

from opportunity_finder.agents.brand_gap import BrandGapAgent
from opportunity_finder.agents.collab_scout import CollabScoutAgent
from opportunity_finder.agents.niche_query import NicheQueryAgent
from opportunity_finder.agents.opportunity_cluster import OpportunityClusterAgent
from opportunity_finder.agents.opportunity_scorer import OpportunityScorerAgent
from opportunity_finder.agents.root import OpportunityFinderRoot
from opportunity_finder.agents.trend_harvester import TrendHarvesterAgent


async def harvest(state: dict[str, Any]) -> dict[str, Any]:
    await asyncio.gather(
        TrendHarvesterAgent().run(state),
        BrandGapAgent().run(state),
        CollabScoutAgent().run(state),
    )
    raw = [
        *(state.get("trend_opps") or []),
        *(state.get("brand_opps") or []),
        *(state.get("collab_opps") or []),
    ]
    seen: set[str] = set()
    deduped = []
    for opp in raw:
        oid = str(opp.get("id") or "")
        if oid and oid not in seen:
            seen.add(oid)
            deduped.append(opp)
    state["raw_finds"] = deduped
    return state


def build_graph() -> Callable | None:
    try:
        from langgraph.graph import END, START, StateGraph
    except Exception:
        return None

    g = StateGraph(dict)
    g.add_node("query", NicheQueryAgent().run)
    g.add_node("harvest", harvest)
    g.add_node("cluster", OpportunityClusterAgent().run)
    g.add_node("score", OpportunityScorerAgent().run)
    g.add_edge(START, "query")
    g.add_edge("query", "harvest")
    g.add_edge("harvest", "cluster")
    g.add_edge("cluster", "score")
    g.add_edge("score", END)
    return g.compile()


_COMPILED = None


def compiled():
    global _COMPILED
    if _COMPILED is None:
        _COMPILED = build_graph()
    return _COMPILED


async def run_search(state: dict[str, Any]) -> dict[str, Any]:
    graph = compiled()
    if graph is not None:
        return await graph.ainvoke(state)
    return await OpportunityFinderRoot().run(state)
