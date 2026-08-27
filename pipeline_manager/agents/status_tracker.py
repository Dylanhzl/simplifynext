from typing import Any

from pipeline_manager import db
from pipeline_manager.agents.opportunity_clerk import _oid
from shared.agent_base import Agent
from shared.agent_util import ping, with_span
from shared.llm import complete_json, seed_opportunities


class StatusTrackerAgent(Agent):
    name = "StatusTrackerAgent"
    kind = "llm"

    async def run(self, state: dict[str, Any]) -> dict[str, Any]:
        with with_span(self.name, self.kind, state):
            ping(state, self.name, "llm", "Advance opportunity status.")
            oid = _oid(state)
            target = str(state.get("target_status") or state.get("status") or "")
            data = await complete_json(
                "You are StatusTrackerAgent. Return {ok, status} using the status machine.",
                f"id={oid} requested={target} classifier={state.get('reply_label')}",
                agent=self.name,
            )
            status = target or str(data.get("status") or "outreached")
            row = db.get_opportunity(oid)
            if not row:
                seed = {o["id"]: o for o in seed_opportunities()}
                payload = dict(seed.get(oid) or {"id": oid, "title": oid, "type": "brand", "why_now": "", "city": "Singapore", "niche": "singapore hawker food", "score": 80, "source_agent": "StatusTrackerAgent"})
                db.upsert_opportunity(oid, payload, status="new")
            result = db.set_status(oid, status)
            state["status_result"] = result
            ping(state, self.name, "tool", f"{oid} → {result.get('status')}.")
        return state
