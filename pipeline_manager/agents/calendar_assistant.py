from datetime import datetime, time, timedelta
from typing import Any
from zoneinfo import ZoneInfo

from shared.agent_base import Agent
from pipeline_manager import db

SGT = ZoneInfo("Asia/Singapore")
POST_HOUR = 18
SLOT_OFFSETS_DAYS = (1, 3, 5)


class CalendarAssistantAgent(Agent):
    name = "CalendarAssistantAgent"
    kind = "llm"

    async def run(self, state: dict[str, Any]) -> dict[str, Any]:
        """Propose posting and follow-up slots (Asia/Singapore)."""
        if state.get("record_kind") != "opportunity" or not state.get("stored"):
            return state

        record = state["stored"]
        now = datetime.now(SGT)
        slots = []
        for offset in SLOT_OFFSETS_DAYS:
            day = (now + timedelta(days=offset)).date()
            slot_dt = datetime.combine(day, time(POST_HOUR, 0), tzinfo=SGT)
            event = await db.save_calendar_event(
                {
                    "opportunity_id": record["id"],
                    "slot": slot_dt.isoformat(),
                    "kind": "post",
                    "title": f"Post: {record.get('title', record['id'])}",
                }
            )
            slots.append(event)

        state.setdefault("calendar_slots", []).extend(slots)
        return state
