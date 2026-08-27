from typing import Any

from shared.agent_base import Agent

HINT_TO_STATUS = {
    "interested": ("interested", "engaged"),
    "meeting": ("meeting", "meeting"),
    "not_interested": ("lost", "lost"),
    "lost": ("lost", "lost"),
}


def _classify_text(text: str) -> tuple[str, str | None]:
    t = text.lower()
    if any(w in t for w in ("call", "zoom", "meeting", "hop on")):
        return "meeting", "meeting"
    if any(w in t for w in ("interested", "love", "trial", "let's collab", "would like to")):
        return "interested", "engaged"
    if any(w in t for w in ("not interested", "no thanks", "pass on this")):
        return "lost", "lost"
    return "noise", None


class ReplyClassifierAgent(Agent):
    name = "ReplyClassifierAgent"
    kind = "llm"

    async def run(self, state: dict[str, Any]) -> dict[str, Any]:
        """interested / not / meeting / noise."""
        hint = state.get("label_hint")
        if hint and hint in HINT_TO_STATUS:
            label, status = HINT_TO_STATUS[hint]
        else:
            label, status = _classify_text(state.get("text", ""))
        state["label"] = label
        state["status"] = status
        return state
