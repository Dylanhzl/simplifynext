"""LangGraph / harness entry for Opportunity Finder.

Delegates to OpportunityFinderRoot so MCP `find_opportunities` and service
callers share the same pipeline (agents/state.py + agents/pipeline.py).
"""

from __future__ import annotations

from typing import Any

from opportunity_finder.agents.root import OpportunityFinderRoot


async def run_search(state: dict[str, Any]) -> dict[str, Any]:
    """Run the finder pipeline. Used by MCP and optional harness callers."""
    return await OpportunityFinderRoot().run(state)
