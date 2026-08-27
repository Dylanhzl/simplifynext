from typing import Any

from shared.agent_base import Agent
from pipeline_manager import db

HOT_TYPES = {"brand", "gap"}


class QualificationAgent(Agent):
    name = "QualificationAgent"
    kind = "llm"

    async def run(self, state: dict[str, Any]) -> dict[str, Any]:
        """Label hot / warm / cold. Brand-gap opportunities with a high score are hot."""
        if state.get("record_kind") != "opportunity":
            return state

        record = state["stored"]
        score = record.get("score", 0)
        otype = record.get("type")

        if score >= 90 or (otype in HOT_TYPES and score >= 80):
            label = "hot"
        elif score >= 65:
            label = "warm"
        else:
            label = "cold"

        await db.set_qualification(record["id"], label)
        state["qualification"] = label
        return state
