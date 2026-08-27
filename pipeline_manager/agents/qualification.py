from typing import Any

from pipeline_manager import db
from pipeline_manager.agents.opportunity_clerk import _oid
from shared.agent_base import Agent
from shared.agent_util import ping, with_span
from shared.llm import complete_json


class QualificationAgent(Agent):
    name = "QualificationAgent"
    kind = "llm"

    async def run(self, state: dict[str, Any]) -> dict[str, Any]:
        with with_span(self.name, self.kind, state):
            ping(state, self.name, "llm", "Label hot / warm / cold.")
            opp = state.get("opportunity") or state.get("current") or {}
            data = await complete_json(
                "You are QualificationAgent. Return {label: hot|warm|cold, reason}. Brand-gap + high score = hot.",
                f"opportunity={opp}",
                agent=self.name,
            )
            label = str(data.get("label") or "warm")
            score = int(opp.get("score") or 0)
            typ = str(opp.get("type") or "")
            if typ == "brand" and score >= 85:
                label = "hot"
            elif "chendol" in str(opp.get("title") or "").lower() or score < 70:
                label = "cold"
            elif score >= 85:
                label = "hot"
            reason = str(data.get("reason") or "")
            oid = _oid(state)
            db.set_qualification(oid, label, reason)
            state["qualification"] = {"label": label, "reason": reason}
            ping(state, self.name, "llm", f"{oid} → {label}.")
        return state
