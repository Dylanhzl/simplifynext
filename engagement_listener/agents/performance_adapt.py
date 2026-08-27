from pathlib import Path
from typing import Any

from pipeline_manager import db
from shared.agent_base import Agent
from shared.agent_util import ping, with_span
from shared.llm import complete_json
from shared.schemas import MemoryState

ANALYTICS = Path(__file__).resolve().parents[2] / "demo" / "maya" / "analytics_week1.json"


class PerformanceAdaptAgent(Agent):
    name = "PerformanceAdaptAgent"
    kind = "llm"

    async def run(self, state: dict[str, Any]) -> dict[str, Any]:
        with with_span(self.name, self.kind, state):
            ping(state, self.name, "llm", "Write week-2 memory for the next CDR run.")
            analytics = state.get("analytics")
            if analytics is None and ANALYTICS.exists():
                import json

                analytics = json.loads(ANALYTICS.read_text())
            data = await complete_json(
                "You are PerformanceAdaptAgent. Return {wins: string[], losses: string[], next_bias: string[]}.",
                f"analytics={analytics}\nclassified={state.get('classified')}",
                agent=self.name,
            )
            memory = MemoryState(
                wins=list(data.get("wins") or []),
                losses=list(data.get("losses") or []),
                next_bias=list(data.get("next_bias") or []),
            ).model_dump()
            db.write_memory(memory["wins"], memory["losses"], memory["next_bias"])
            state["memory"] = memory
            ping(state, self.name, "tool", "Memory written.", artifact_ref="memory")
        return state
