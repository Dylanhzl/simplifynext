from typing import Any

from shared.agent_base import Agent
from pipeline_manager import db


class StatusTrackerAgent(Agent):
    name = "StatusTrackerAgent"
    kind = "llm"

    async def run(self, state: dict[str, Any]) -> dict[str, Any]:
        """Only writer of opportunity status besides clerk."""
        oid = state["opportunity_id"]
        status = state["status"]
        record = await db.update_status(oid, status)
        state["stored"] = record
        state["record_kind"] = "opportunity" if record is not None else None
        return state
