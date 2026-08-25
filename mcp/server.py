"""MCP tool server (kick-off stack: Model Context Protocol).

P1 fills search tools. P3 fills persist / calendar / inbox.
Agents in CDR must call these tools via MCP, not random HTTP from prompts.
"""

from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI
from pydantic import BaseModel, Field

from shared.cors import add_cors

PLACES = Path(__file__).resolve().parents[1] / "demo" / "maya" / "places_sg_food.json"
INBOX = Path(__file__).resolve().parents[1] / "demo" / "maya" / "inbox.json"

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
            {"name": "persist_and_schedule", "owner": "P3"},
            {"name": "save_calendar_event", "owner": "P3"},
            {"name": "read_engagement_inbox", "owner": "P3"},
        ]
    }


@app.post("/mcp/call")
def call_tool(req: ToolCall) -> dict:
    """JSON stand-in until FastMCP stdio/SSE is wired. Same tool names."""
    import json

    if req.name == "search_local_places" and PLACES.exists():
        return {"name": req.name, "result": json.loads(PLACES.read_text())}
    if req.name == "read_engagement_inbox" and INBOX.exists():
        return {"name": req.name, "result": json.loads(INBOX.read_text())}
    return {
        "name": req.name,
        "result": None,
        "note": "scaffold — implement in mcp/server.py / FastMCP",
    }
