from typing import Any

from shared.agent_base import Agent


def _extract_text(source: str, payload: dict[str, Any]) -> str:
    if source == "email":
        return f"{payload.get('subject', '')} {payload.get('body', '')}".strip()
    if source == "comment":
        return payload.get("text", "") or payload.get("body", "")
    return ""


class EngagementIngestAgent(Agent):
    name = "EngagementIngestAgent"
    kind = "llm"

    async def run(self, state: dict[str, Any]) -> dict[str, Any]:
        """Normalize inbound email/analytics/comments."""
        source = state.get("source", "email")
        payload = state.get("payload", {})
        state["source"] = source
        state["opportunity_id"] = payload.get("opportunity_id")
        state["text"] = _extract_text(source, payload)
        state["label_hint"] = payload.get("label_hint")
        return state
