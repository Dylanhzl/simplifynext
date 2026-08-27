from datetime import timedelta
from typing import Any

from shared.agent_base import Agent
from shared.events import now_utc
from pipeline_manager import db

SUGGESTIONS = {
    "new": "no outreach yet — package content before contacting",
    "researched": "no outreach yet — finish content package first",
    "packaged": "ready for outreach",
    "outreached": "wait for reply; follow up in 3 days if silent",
    "engaged": "schedule an intro call this week",
    "meeting": "prep talking points before the call",
    "won": "kick off the deliverables calendar",
    "lost": "no further action",
}


class FollowUpPlannerAgent(Agent):
    name = "FollowUpPlannerAgent"
    kind = "llm"

    async def run(self, state: dict[str, Any]) -> dict[str, Any]:
        """Next action after outreach."""
        if state.get("record_kind") != "opportunity" or not state.get("stored"):
            return state

        record = state["stored"]
        status = record.get("status", "new")
        state["follow_up"] = SUGGESTIONS.get(status, "no action")

        if status == "outreached":
            slot = now_utc() + timedelta(days=3)
            event = await db.save_calendar_event(
                {
                    "opportunity_id": record["id"],
                    "slot": slot.isoformat(),
                    "kind": "followup",
                    "title": f"Follow up: {record.get('title', record['id'])}",
                }
            )
            state.setdefault("calendar_slots", []).append(event)
        elif status == "engaged":
            slot = now_utc() + timedelta(days=2)
            event = await db.save_calendar_event(
                {
                    "opportunity_id": record["id"],
                    "slot": slot.isoformat(),
                    "kind": "meeting",
                    "title": f"Intro call: {record.get('title', record['id'])}",
                }
            )
            state.setdefault("calendar_slots", []).append(event)

        return state
