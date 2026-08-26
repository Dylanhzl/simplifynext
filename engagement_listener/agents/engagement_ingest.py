from pathlib import Path
from typing import Any

from shared.agent_base import Agent
from shared.agent_util import ping, with_span
from shared.llm import complete_json
from shared.schemas import EngagementEvent

INBOX = Path(__file__).resolve().parents[2] / "demo" / "maya" / "inbox.json"
ANALYTICS = Path(__file__).resolve().parents[2] / "demo" / "maya" / "analytics_week1.json"


class EngagementIngestAgent(Agent):
    name = "EngagementIngestAgent"
    kind = "llm"

    async def run(self, state: dict[str, Any]) -> dict[str, Any]:
        with with_span(self.name, self.kind, state):
            ping(state, self.name, "llm", "Normalize inbound email / analytics / comments.")
            await complete_json(
                "You are EngagementIngestAgent. Acknowledge normalized events. Return {ok, normalized}.",
                f"source={state.get('source')} payload={state.get('payload')}",
                agent=self.name,
            )
            items = list(state.get("items") or [])
            source = state.get("source")
            payload = state.get("payload")
            if payload and not items:
                event = EngagementEvent(
                    source=source or "email",  # type: ignore[arg-type]
                    payload=payload if isinstance(payload, dict) else {"raw": payload},
                    opportunity_id=state.get("opportunity_id"),
                )
                items.append(event.model_dump(mode="json"))
            if not items and INBOX.exists():
                import json

                for raw in json.loads(INBOX.read_text()).get("items") or []:
                    items.append(
                        EngagementEvent(
                            source="email",
                            payload=raw,
                            opportunity_id=raw.get("opportunity_id"),
                        ).model_dump(mode="json")
                    )
            if ANALYTICS.exists() and (source == "analytics" or state.get("include_analytics")):
                import json

                items.append(
                    EngagementEvent(
                        source="analytics",
                        payload=json.loads(ANALYTICS.read_text()),
                        opportunity_id=None,
                    ).model_dump(mode="json")
                )
            state["items"] = items
            ping(state, self.name, "llm", f"Ingested {len(items)} events.")
        return state
