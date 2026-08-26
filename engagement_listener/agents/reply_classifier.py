from typing import Any

from pipeline_manager.agents.status_tracker import StatusTrackerAgent
from shared.agent_base import Agent
from shared.agent_util import ping, with_span
from shared.llm import complete_json


class ReplyClassifierAgent(Agent):
    name = "ReplyClassifierAgent"
    kind = "llm"

    async def run(self, state: dict[str, Any]) -> dict[str, Any]:
        with with_span(self.name, self.kind, state):
            ping(state, self.name, "llm", "Classify replies: interested / not / meeting / noise.")
            classified = []
            for item in state.get("items") or []:
                if (item.get("source") or "") == "analytics":
                    continue
                payload = item.get("payload") or {}
                blob = f"{payload.get('subject', '')} {payload.get('body', '')} {payload.get('label_hint', '')}"
                data = await complete_json(
                    "You are ReplyClassifierAgent. Return {label, opportunity_id, next_status}.",
                    blob,
                    agent=self.name,
                )
                oid = data.get("opportunity_id") or payload.get("opportunity_id") or item.get("opportunity_id")
                label = data.get("label") or payload.get("label_hint") or "noise"
                next_status = data.get("next_status")
                if label == "interested":
                    next_status = "engaged"
                elif label in ("not_interested", "not"):
                    next_status = "lost"
                elif label == "meeting":
                    next_status = "meeting"
                row = {**item, "label": label, "opportunity_id": oid, "next_status": next_status}
                classified.append(row)
                if oid and next_status:
                    await StatusTrackerAgent().run(
                        {
                            "run_id": state.get("run_id"),
                            "opportunity_id": oid,
                            "target_status": next_status,
                            "reply_label": label,
                        }
                    )
            state["classified"] = classified
            ping(state, self.name, "llm", f"Classified {len(classified)} replies.")
        return state
