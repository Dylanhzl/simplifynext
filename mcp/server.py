"""MCP tool server. Agents call tools here instead of ad-hoc APIs."""

from __future__ import annotations

import json
from pathlib import Path

from fastapi import FastAPI
from pydantic import BaseModel, Field

from opportunity_finder.tools import fetch_url as local_fetch
from opportunity_finder.tools import load_places, load_seed
from opportunity_finder.tools import search_web as local_search_web
from pipeline_manager import db
from shared.cors import add_cors
from shared.rag import retrieve as rag_retrieve

INBOX = Path(__file__).resolve().parents[1] / "demo" / "maya" / "inbox.json"
OUTBOX_MAIL = Path(__file__).resolve().parents[1] / "demo" / "outbox" / "mail"

app = FastAPI(title="CreatorLoop MCP", version="0.1.0")
add_cors(app)
db.init()


class ToolCall(BaseModel):
    name: str
    arguments: dict = Field(default_factory=dict)


@app.get("/health")
def health() -> dict:
    return {"service": "mcp", "status": "ok", "protocol": "mcp"}


@app.get("/mcp/tools")
def list_tools() -> dict:
    return {
        "tools": [
            {"name": "search_web", "owner": "P1"},
            {"name": "search_local_places", "owner": "P1"},
            {"name": "fetch_url", "owner": "P1"},
            {"name": "find_opportunities", "owner": "P1"},
            {"name": "retrieve_creator_memory", "owner": "P2/P3", "kind": "rag"},
            {"name": "save_opportunity", "owner": "P3"},
            {"name": "get_opportunity", "owner": "P3"},
            {"name": "update_status", "owner": "P3"},
            {"name": "persist_and_schedule", "owner": "P3"},
            {"name": "save_calendar_event", "owner": "P3"},
            {"name": "send_email", "owner": "P3"},
            {"name": "read_engagement_inbox", "owner": "P3"},
            {"name": "write_memory", "owner": "P3"},
        ]
    }


def _send_email(args: dict) -> dict:
    OUTBOX_MAIL.mkdir(parents=True, exist_ok=True)
    to = str(args.get("to") or "unknown")
    subject = str(args.get("subject") or "")
    body = str(args.get("body") or "")
    safe = "".join(ch if ch.isalnum() else "-" for ch in to)[:40]
    path = OUTBOX_MAIL / f"{safe or 'mail'}.eml"
    path.write_text(f"To: {to}\nSubject: {subject}\n\n{body}\n")
    return {"ok": True, "path": str(path), "to": to}


@app.post("/mcp/call")
async def call_tool(req: ToolCall) -> dict:
    args = req.arguments or {}
    name = req.name

    if name == "search_web":
        return {"name": name, "result": local_search_web(str(args.get("query") or ""))}
    if name == "search_local_places":
        city = str(args.get("city") or "Singapore")
        places = [p for p in load_places() if city.lower() in str(p.get("city", "")).lower()] or load_places()
        return {"name": name, "result": places}
    if name == "fetch_url":
        return {"name": name, "result": local_fetch(str(args.get("url") or ""))}
    if name == "find_opportunities":
        from opportunity_finder.graph import run_search

        state = await run_search(
            {
                "run_id": "mcp-find",
                "profile_id": args.get("profile_id") or "maya",
                "profile": args.get("profile") or {},
                "niche": args.get("niche") or "singapore hawker food",
                "city": args.get("city") or "Singapore",
                "limit": int(args.get("limit") or 8),
            }
        )
        return {"name": name, "result": {"opportunities": state.get("opportunities") or load_seed()}}
    if name == "retrieve_creator_memory":
        return {"name": name, "result": rag_retrieve(str(args.get("query") or "maya laksa"), k=int(args.get("k") or 4))}
    if name == "save_opportunity":
        oid = str(args.get("id") or args.get("opportunity_id") or "")
        if not oid:
            return {"name": name, "result": {"ok": False, "error": "missing id"}}
        row = db.upsert_opportunity(oid, args)
        return {"name": name, "result": {"ok": True, "opportunity": row}}
    if name == "get_opportunity":
        oid = str(args.get("id") or args.get("opportunity_id") or "")
        return {"name": name, "result": db.get_opportunity(oid)}
    if name == "update_status":
        from pipeline_manager.agents.status_tracker import StatusTrackerAgent

        oid = str(args.get("id") or args.get("opportunity_id") or "")
        status = str(args.get("status") or "")
        state = await StatusTrackerAgent().run({"opportunity_id": oid, "target_status": status, "run_id": "mcp"})
        return {"name": name, "result": state.get("status_result")}
    if name == "persist_and_schedule":
        from pipeline_manager.graph import run_persist

        state = await run_persist(
            {
                "run_id": args.get("run_id") or "mcp-persist",
                "opportunity_id": args.get("opportunity_id") or args.get("id"),
                "opportunity": args.get("opportunity"),
                "package": args.get("package"),
                "brief": args.get("brief"),
                "outreach": args.get("outreach"),
                "qa": args.get("qa"),
                "status": args.get("status"),
                "target_status": args.get("status") or "outreached",
                "current": {"id": args.get("opportunity_id") or args.get("id")},
            }
        )
        return {
            "name": name,
            "result": {
                "ok": True,
                "id": state.get("opportunity_id"),
                "status": (state.get("status_result") or {}).get("status"),
                "calendar": state.get("calendar"),
            },
        }
    if name == "save_calendar_event":
        return {"name": name, "result": db.save_calendar_event(args)}
    if name == "send_email":
        return {"name": name, "result": _send_email(args)}
    if name == "read_engagement_inbox":
        if INBOX.exists():
            return {"name": name, "result": json.loads(INBOX.read_text())}
        return {"name": name, "result": {"items": []}}
    if name == "write_memory":
        return {
            "name": name,
            "result": db.write_memory(
                list(args.get("wins") or []),
                list(args.get("losses") or []),
                list(args.get("next_bias") or []),
            ),
        }
    return {"name": name, "result": None, "note": "unknown tool"}
