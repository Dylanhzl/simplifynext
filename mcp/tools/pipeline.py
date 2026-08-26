"""P3 pipeline / engagement tools for the MCP server.

P3 owns this file -- P1 only scaffolded the registry entries so the tool names
stay live on /mcp/tools while P3 implements them. Fill in the bodies; do not
rename the tools, P2's agents call them by name.

Implemented already: read_engagement_inbox (fixture), retrieve_creator_memory
(keyword RAG via shared/rag.py). The rest are stubs.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from mcp.tools import tool
from shared.rag import retrieve

DEMO = Path(__file__).resolve().parents[2] / "demo" / "maya"
INBOX_FIXTURE = DEMO / "inbox.json"


def _not_implemented(name: str, owner: str = "P3") -> dict[str, Any]:
    return {"ok": False, "implemented": False, "tool": name, "owner": owner,
            "note": f"{name} is scaffold-only; {owner} implements it in mcp/tools/pipeline.py"}


@tool("retrieve_creator_memory", owner="P2/P3", kind="rag",
      description="Retrieve creator memory and past-post context (multi-agent RAG).")
async def retrieve_creator_memory(query: str, k: int = 4) -> dict[str, Any]:
    """Keyword RAG over demo/maya/rag_corpus.json. Swap for embeddings later."""
    return {"query": query, "documents": retrieve(query, k), "mode": "keyword"}


@tool("read_engagement_inbox", owner="P3",
      description="Read inbound replies for the creator (week-2 adapt loop).")
async def read_engagement_inbox(unread_only: bool = False) -> dict[str, Any]:
    """Inbound replies. Fixture-backed until P3 wires the Engagement Listener."""
    if not INBOX_FIXTURE.exists():
        return {"messages": [], "mode": "fixture"}

    data = json.loads(INBOX_FIXTURE.read_text())
    messages = data.get("messages", data) if isinstance(data, dict) else data
    if unread_only and isinstance(messages, list):
        messages = [m for m in messages if not m.get("read", False)]
    return {"messages": messages, "mode": "fixture"}


@tool("persist_and_schedule", owner="P3",
      description="Persist an opportunity/package and schedule its calendar slots.")
async def persist_and_schedule(**kwargs: Any) -> dict[str, Any]:
    return _not_implemented("persist_and_schedule")


@tool("save_calendar_event", owner="P3",
      description="Save a post, follow-up, or meeting to the content calendar.")
async def save_calendar_event(**kwargs: Any) -> dict[str, Any]:
    return _not_implemented("save_calendar_event")
