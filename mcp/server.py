"""MCP tool server (kick-off stack: Model Context Protocol).

P1 fills search tools. P3 fills persist / calendar / inbox.
Agents in CDR must call these tools via MCP, not random HTTP from prompts.
"""

from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from pathlib import Path

import httpx
from fastapi import FastAPI
from pydantic import BaseModel, Field

from shared.cors import add_cors
from shared.http_clients import PIPELINE_MANAGER_URL
from shared.rag import retrieve

PLACES = Path(__file__).resolve().parents[1] / "demo" / "maya" / "places_sg_food.json"
INBOX = Path(__file__).resolve().parents[1] / "demo" / "maya" / "inbox.json"
MAIL_OUTBOX = Path(__file__).resolve().parents[1] / "demo" / "outbox" / "mail"

app = FastAPI(title="CreatorLoop MCP", version="0.1.0")
add_cors(app)


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
            {"name": "retrieve_creator_memory", "owner": "P2/P3", "kind": "rag"},
            {"name": "save_opportunity", "owner": "P3"},
            {"name": "get_opportunity", "owner": "P3"},
            {"name": "update_status", "owner": "P3"},
            {"name": "persist_and_schedule", "owner": "P3"},
            {"name": "save_calendar_event", "owner": "P3"},
            {"name": "read_engagement_inbox", "owner": "P3"},
            {"name": "write_memory", "owner": "P3"},
            {"name": "send_email", "owner": "P3"},
        ]
    }


async def _pipeline_call(method: str, path: str, **kwargs) -> dict:
    async with httpx.AsyncClient(timeout=15.0) as client:
        r = await client.request(method, f"{PIPELINE_MANAGER_URL}{path}", **kwargs)
        r.raise_for_status()
        return r.json()


def _send_email_tool(args: dict) -> dict:
    to = args.get("to", "unknown@local")
    subject = args.get("subject", "")
    body = args.get("body", "")
    opportunity_id = args.get("opportunity_id", "draft")
    from_addr = os.getenv("FROM_EMAIL", "maya@creatorloop.local")

    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    MAIL_OUTBOX.mkdir(parents=True, exist_ok=True)
    eml_path = MAIL_OUTBOX / f"{opportunity_id}-{ts}.eml"
    eml_path.write_text(f"From: {from_addr}\nTo: {to}\nSubject: {subject}\n\n{body}\n")

    status = "sent_mock"
    smtp_host = os.getenv("SMTP_HOST")
    if smtp_host:
        try:
            import smtplib
            from email.message import EmailMessage

            msg = EmailMessage()
            msg["From"] = from_addr
            msg["To"] = to
            msg["Subject"] = subject
            msg.set_content(body)
            with smtplib.SMTP(smtp_host) as smtp:
                user = os.getenv("SMTP_USER")
                password = os.getenv("SMTP_PASSWORD")
                if user and password:
                    smtp.starttls()
                    smtp.login(user, password)
                smtp.send_message(msg)
            status = "sent"
        except Exception as exc:  # best effort in demo — .eml is already on disk
            status = f"smtp_failed: {exc}"

    return {"status": status, "eml_path": str(eml_path)}


@app.post("/mcp/call")
async def call_tool(req: ToolCall) -> dict:
    """JSON stand-in until FastMCP stdio/SSE is wired. Same tool names."""
    name = req.name
    args = req.arguments

    if name == "search_local_places" and PLACES.exists():
        return {"name": name, "result": json.loads(PLACES.read_text())}

    if name == "read_engagement_inbox":
        result = json.loads(INBOX.read_text()) if INBOX.exists() else {"items": []}
        return {"name": name, "result": result}

    if name == "retrieve_creator_memory":
        result = retrieve(args.get("query", ""), args.get("k", 4))
        return {"name": name, "result": result}

    if name == "save_opportunity":
        result = await _pipeline_call("POST", "/pipeline/upsert", json=args)
        return {"name": name, "result": result}

    if name == "get_opportunity":
        result = await _pipeline_call("GET", f"/pipeline/opportunities/{args.get('id')}")
        return {"name": name, "result": result}

    if name == "update_status":
        result = await _pipeline_call("POST", "/tools/update_status", json=args)
        return {"name": name, "result": result}

    if name == "persist_and_schedule":
        result = await _pipeline_call("POST", "/tools/persist_and_schedule", json=args)
        return {"name": name, "result": result}

    if name == "save_calendar_event":
        result = await _pipeline_call("POST", "/pipeline/calendar", json=args)
        return {"name": name, "result": result}

    if name == "write_memory":
        result = await _pipeline_call("POST", "/pipeline/memory", json=args)
        return {"name": name, "result": result}

    if name == "send_email":
        result = _send_email_tool(args)
        return {"name": name, "result": result}

    return {
        "name": name,
        "result": None,
        "note": "scaffold — implement in mcp/server.py / FastMCP",
    }
