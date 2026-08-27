from typing import Any

from shared.agent_base import Agent
from pipeline_manager import db


def classify_kind(payload: dict[str, Any]) -> str:
    if "week_plan" in payload:
        return "content_package"
    if "audience_insight" in payload:
        return "research_brief"
    if "channel" in payload and "body" in payload and "to" in payload:
        return "outreach_draft"
    if "type" in payload and "score" in payload and "why_now" in payload:
        return "opportunity"
    return "unknown"


class OpportunityClerkAgent(Agent):
    name = "OpportunityClerkAgent"
    kind = "llm"

    async def run(self, state: dict[str, Any]) -> dict[str, Any]:
        """Idempotent upsert of pipeline records."""
        payload = state["payload"]
        record_kind = classify_kind(payload)
        state["record_kind"] = record_kind

        if record_kind == "opportunity":
            stored = await db.upsert_opportunity(payload)
            state["id"] = stored["id"]
            state["stored"] = stored
        else:
            opportunity_id = payload.get("opportunity_id")
            artifact_id = await db.save_artifact(opportunity_id, record_kind, payload)
            state["id"] = opportunity_id
            state["artifact_id"] = artifact_id
            state["stored"] = payload
        return state
