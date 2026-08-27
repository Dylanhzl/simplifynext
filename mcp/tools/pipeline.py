"""P3 pipeline / engagement tools for the MCP server.

Implemented against pipeline_manager.db and the Pipeline Manager graph so CDR
and engagement agents can persist, schedule, and update status via MCP.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from mcp.tools import tool
from pipeline_manager import db
from shared.rag import retrieve

DEMO = Path(__file__).resolve().parents[2] / "demo" / "maya"
INBOX_FIXTURE = DEMO / "inbox.json"
OUTBOX_MAIL = Path(__file__).resolve().parents[2] / "demo" / "outbox" / "mail"


@tool(
    "retrieve_creator_memory",
    owner="P2/P3",
    kind="rag",
    description="Retrieve creator memory and past-post context (multi-agent RAG).",
)
async def retrieve_creator_memory(query: str, k: int = 4) -> list[dict[str, Any]]:
    """Keyword RAG over demo/maya/rag_corpus.json. Returns a document list for CDR."""
    return retrieve(query, k)


@tool(
    "read_engagement_inbox",
    owner="P3",
    description="Read inbound replies for the creator (week-2 adapt loop).",
)
async def read_engagement_inbox(unread_only: bool = False) -> dict[str, Any]:
    """Inbound replies. Fixture-backed until Engagement Listener is wired live."""
    if not INBOX_FIXTURE.exists():
        return {"messages": [], "mode": "fixture"}

    data = json.loads(INBOX_FIXTURE.read_text())
    messages = data.get("messages", data) if isinstance(data, dict) else data
    if unread_only and isinstance(messages, list):
        messages = [m for m in messages if not m.get("read", False)]
    return {"messages": messages, "mode": "fixture"}


@tool(
    "save_opportunity",
    owner="P3",
    description="Upsert an opportunity row into the pipeline SQLite store.",
)
async def save_opportunity(**kwargs: Any) -> dict[str, Any]:
    oid = str(kwargs.get("id") or kwargs.get("opportunity_id") or "")
    if not oid:
        return {"ok": False, "error": "missing id"}
    row = db.upsert_opportunity(oid, kwargs)
    return {"ok": True, "opportunity": row}


@tool(
    "get_opportunity",
    owner="P3",
    description="Fetch one opportunity by id from the pipeline store.",
)
async def get_opportunity(id: str = "", opportunity_id: str = "") -> dict[str, Any]:
    oid = str(id or opportunity_id or "")
    return db.get_opportunity(oid)


@tool(
    "update_status",
    owner="P3",
    description="Transition an opportunity status via StatusTrackerAgent.",
)
async def update_status(
    id: str = "",
    opportunity_id: str = "",
    status: str = "",
    **kwargs: Any,
) -> dict[str, Any]:
    from pipeline_manager.agents.status_tracker import StatusTrackerAgent

    oid = str(id or opportunity_id or "")
    state = await StatusTrackerAgent().run(
        {
            "opportunity_id": oid,
            "target_status": status,
            "run_id": kwargs.get("run_id") or "mcp",
        }
    )
    return state.get("status_result") or {"ok": False, "id": oid}


@tool(
    "persist_and_schedule",
    owner="P3",
    description="Persist an opportunity/package and schedule its calendar slots.",
)
async def persist_and_schedule(**kwargs: Any) -> dict[str, Any]:
    from pipeline_manager.graph import run_persist

    state = await run_persist(
        {
            "run_id": kwargs.get("run_id") or "mcp-persist",
            "opportunity_id": kwargs.get("opportunity_id") or kwargs.get("id"),
            "opportunity": kwargs.get("opportunity"),
            "package": kwargs.get("package"),
            "brief": kwargs.get("brief"),
            "outreach": kwargs.get("outreach"),
            "qa": kwargs.get("qa"),
            "status": kwargs.get("status"),
            "target_status": kwargs.get("status") or "outreached",
            "current": {"id": kwargs.get("opportunity_id") or kwargs.get("id")},
        }
    )
    return {
        "ok": True,
        "id": state.get("opportunity_id"),
        "status": (state.get("status_result") or {}).get("status"),
        "calendar": state.get("calendar"),
    }


@tool(
    "save_calendar_event",
    owner="P3",
    description="Save a post, follow-up, or meeting to the content calendar.",
)
async def save_calendar_event(**kwargs: Any) -> dict[str, Any]:
    return db.save_calendar_event(kwargs)


@tool(
    "send_email",
    owner="P3",
    description="Write an outreach email to demo/outbox/mail (fixture SMTP).",
)
async def send_email(
    to: str = "",
    subject: str = "",
    body: str = "",
    **kwargs: Any,
) -> dict[str, Any]:
    OUTBOX_MAIL.mkdir(parents=True, exist_ok=True)
    to_addr = str(to or kwargs.get("to") or "unknown")
    subj = str(subject or kwargs.get("subject") or "")
    text = str(body or kwargs.get("body") or "")
    safe = "".join(ch if ch.isalnum() else "-" for ch in to_addr)[:40]
    path = OUTBOX_MAIL / f"{safe or 'mail'}.eml"
    path.write_text(f"To: {to_addr}\nSubject: {subj}\n\n{text}\n", encoding="utf-8")
    return {"ok": True, "path": str(path), "to": to_addr}


@tool(
    "write_memory",
    owner="P3",
    description="Persist week-2 performance memory (wins/losses/next_bias).",
)
async def write_memory(
    wins: list | None = None,
    losses: list | None = None,
    next_bias: list | None = None,
    **kwargs: Any,
) -> dict[str, Any]:
    return db.write_memory(
        list(wins or kwargs.get("wins") or []),
        list(losses or kwargs.get("losses") or []),
        list(next_bias or kwargs.get("next_bias") or []),
    )
