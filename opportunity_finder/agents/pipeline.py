"""OpportunityFinderPipeline -- LangGraph StateGraph.

    NicheQuery
        |
        +--> TrendHarvester --+
        +--> BrandGap --------+   (parallel fan-out / gather)
        +--> CollabScout -----+
                              |
                        OpportunityCluster
                              |
                        OpportunityScorer

The three harvest nodes are separate edges from the same source, so LangGraph
runs them concurrently and gathers before `cluster`. They all write to
`harvested`, which is why FinderState declares it with an operator.add reducer.
"""

from __future__ import annotations

from typing import Any

from langgraph.graph import END, START, StateGraph

from observability.otel import agent_span
from opportunity_finder.agents.brand_gap import BrandGapAgent
from opportunity_finder.agents.collab_scout import CollabScoutAgent
from opportunity_finder.agents.niche_query import NicheQueryAgent
from opportunity_finder.agents.opportunity_cluster import OpportunityClusterAgent
from opportunity_finder.agents.opportunity_scorer import OpportunityScorerAgent
from opportunity_finder.agents.state import FinderState
from opportunity_finder.agents.trend_harvester import TrendHarvesterAgent
from shared.agent_base import Agent

NICHE_QUERY = NicheQueryAgent()
TREND_HARVESTER = TrendHarvesterAgent()
BRAND_GAP = BrandGapAgent()
COLLAB_SCOUT = CollabScoutAgent()
CLUSTER = OpportunityClusterAgent()
SCORER = OpportunityScorerAgent()

HARVESTERS = (TREND_HARVESTER, BRAND_GAP, COLLAB_SCOUT)


def build_graph():
    """Compile the finder StateGraph. Nodes are agent.run directly."""
    g = StateGraph(FinderState)

    g.add_node("niche_query", NICHE_QUERY.run)
    g.add_node("trend_harvester", TREND_HARVESTER.run)
    g.add_node("brand_gap", BRAND_GAP.run)
    g.add_node("collab_scout", COLLAB_SCOUT.run)
    g.add_node("cluster", CLUSTER.run)
    g.add_node("scorer", SCORER.run)

    g.add_edge(START, "niche_query")

    # Fan out: three edges from one node = concurrent execution.
    for node in ("trend_harvester", "brand_gap", "collab_scout"):
        g.add_edge("niche_query", node)
        g.add_edge(node, "cluster")  # gather: cluster waits for all three

    g.add_edge("cluster", "scorer")
    g.add_edge("scorer", END)

    return g.compile()


GRAPH = build_graph()


class OpportunityFinderPipeline(Agent):
    name = "OpportunityFinderPipeline"
    kind = "sequential"

    async def run(self, state: dict[str, Any]) -> dict[str, Any]:
        """Sequential: query → harvest → gap → collab → cluster → score."""
        with agent_span(self.name, self.kind, state.get("run_id", "")):
            initial: dict[str, Any] = {
                "run_id": state.get("run_id", ""),
                "profile": state.get("profile"),
                "niche": state.get("niche", ""),
                "city": state.get("city", ""),
                "limit": int(state.get("limit", 8)),
                "memory": state.get("memory") or {},
                "harvested": [],
                "notes": [],
            }
            return await GRAPH.ainvoke(initial)
