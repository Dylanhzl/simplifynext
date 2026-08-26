"""Claude Agent SDK path. Returns None unless ANTHROPIC_API_KEY is set so Groq/fixtures always work."""

from __future__ import annotations

import os
from typing import Any


async def run_claude_specialist(prompt: str) -> dict[str, Any] | None:
    if not os.getenv("ANTHROPIC_API_KEY"):
        return None
    try:
        from claude_agent_sdk import query  # type: ignore
    except Exception:
        return None
    text = ""
    async for msg in query(prompt=prompt):
        text += str(getattr(msg, "text", msg) or "")
    if not text.strip():
        return None
    import json
    import re

    raw = text.strip()
    if raw.startswith("```"):
        raw = re.sub(r"^```(?:json)?", "", raw).removesuffix("```").strip()
    try:
        data = json.loads(raw)
        return data if isinstance(data, dict) else None
    except Exception:
        return None
