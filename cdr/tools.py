"""Agent-as-tool wrappers used by CDRRootAgent."""

from __future__ import annotations

from typing import Any

from cdr.agents.outreach_pipeline import OutreachPipeline
from cdr.agents.parallel_research import ParallelResearch
from cdr.agents.proposal_generation import ProposalGenerationAgent
from cdr.agents.refinement_loop import RefinementLoop
from cdr.mcp_client import find_opportunities as mcp_find
from cdr.mcp_client import persist_and_schedule as mcp_persist
from cdr.runtime import emit


async def find_opportunities(state: dict[str, Any]) -> dict[str, Any]:
    emit(str(state.get("run_id", "")), "CDRRootAgent", "tool", "find_opportunities → P1/MCP")
    profile = state.get("profile") or {}
    data = await mcp_find(
        {
            "profile_id": profile.get("id", "maya"),
            "niche": profile.get("niche", "singapore hawker food"),
            "city": profile.get("city", "Singapore"),
            "limit": 8,
            "profile": profile,
        }
    )
    opps = data.get("opportunities") or state.get("opportunities") or []
    state["opportunities"] = opps
    return state


async def research_opportunity(state: dict[str, Any]) -> dict[str, Any]:
    emit(str(state.get("run_id", "")), "CDRRootAgent", "tool", "research_opportunity → ParallelResearch")
    from cdr.agents.research_lead import ResearchLeadAgent

    await ResearchLeadAgent().run(state)
    await ParallelResearch().run(state)
    return state


async def generate_proposal(state: dict[str, Any]) -> dict[str, Any]:
    emit(str(state.get("run_id", "")), "CDRRootAgent", "tool", "generate_proposal → ProposalGenerationAgent")
    await ProposalGenerationAgent().run(state)
    return state


async def run_qa(state: dict[str, Any]) -> dict[str, Any]:
    emit(str(state.get("run_id", "")), "CDRRootAgent", "tool", "run_qa → RefinementLoop")
    await RefinementLoop().run(state)
    return state


async def draft_outreach(state: dict[str, Any]) -> dict[str, Any]:
    emit(str(state.get("run_id", "")), "CDRRootAgent", "tool", "draft_outreach → OutreachPipeline")
    await OutreachPipeline().run(state)
    return state


async def persist_and_schedule(state: dict[str, Any]) -> dict[str, Any]:
    emit(str(state.get("run_id", "")), "CDRRootAgent", "tool", "persist_and_schedule → MCP/P3")
    payload = {
        "run_id": state.get("run_id"),
        "opportunity_id": (state.get("current") or {}).get("id"),
        "package": state.get("package"),
        "outreach": state.get("outreach"),
        "qa": state.get("qa"),
        "brief": state.get("brief"),
        "status": "outreached",
    }
    state["persist_result"] = await mcp_persist(payload)
    return state
