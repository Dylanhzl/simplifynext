from __future__ import annotations

from datetime import datetime, timedelta
from typing import Any
from zoneinfo import ZoneInfo

from pipeline_manager import db
from pipeline_manager.agents.opportunity_clerk import _oid
from shared.agent_base import Agent
from shared.agent_util import ping, with_span
from shared.llm import complete_json
from shared.schemas import CalendarEvent

SG = ZoneInfo("Asia/Singapore")
WEEKDAY = {"Mon": 0, "Tue": 1, "Wed": 2, "Thu": 3, "Fri": 4, "Sat": 5, "Sun": 6}


def next_slot(weekday_name: str, hhmm: str) -> datetime:
    hour, minute = [int(x) for x in hhmm.split(":")[:2]]
    now = datetime.now(SG)
    target = WEEKDAY[weekday_name]
    days = (target - now.weekday()) % 7
    candidate = now.replace(hour=hour, minute=minute, second=0, microsecond=0) + timedelta(days=days)
    if candidate <= now:
        candidate += timedelta(days=7)
    return candidate


class CalendarAssistantAgent(Agent):
    name = "CalendarAssistantAgent"
    kind = "llm"

    async def run(self, state: dict[str, Any]) -> dict[str, Any]:
        with with_span(self.name, self.kind, state):
            ping(state, self.name, "llm", "Propose posting and follow-up slots (Asia/Singapore).")
            data = await complete_json(
                "You are CalendarAssistantAgent. Return {slots: [{kind, weekday, time, title}] } for this week SGT.",
                f"package={state.get('package')}\nfollow_up={state.get('follow_up')}",
                agent=self.name,
            )
            oid = _oid(state)
            events = []
            for i, slot in enumerate(data.get("slots") or []):
                kind = str(slot.get("kind") or "post")
                if kind not in ("post", "followup", "meeting"):
                    kind = "post"
                when = next_slot(str(slot.get("weekday") or "Tue"), str(slot.get("time") or "19:30"))
                event = CalendarEvent(
                    id=f"cal-{oid}-{kind}-{i}",
                    opportunity_id=oid,
                    slot=when,
                    kind=kind,  # type: ignore[arg-type]
                    title=str(slot.get("title") or kind),
                ).model_dump(mode="json")
                db.save_calendar_event(event)
                events.append(event)
            state["calendar"] = events
            ping(state, self.name, "tool", f"{len(events)} calendar events.", artifact_ref="calendar")
        return state
