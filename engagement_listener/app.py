from __future__ import annotations

import json
from pathlib import Path

from fastapi import FastAPI, Request

from engagement_listener.graph import run_engagement
from shared.cors import add_cors

INBOX = Path(__file__).resolve().parents[1] / "demo" / "maya" / "inbox.json"
ANALYTICS = Path(__file__).resolve().parents[1] / "demo" / "maya" / "analytics_week1.json"

app = FastAPI(title="Engagement Listener", version="0.1.0")
add_cors(app)


@app.get("/health")
def health() -> dict:
    return {"service": "engagement_listener", "status": "ok"}


@app.get("/engagement/inbox")
def inbox() -> dict:
    if INBOX.exists():
        return json.loads(INBOX.read_text())
    return {"items": []}


@app.post("/engagement/ingest")
async def ingest(request: Request) -> dict:
    body = await request.json()
    state = await run_engagement(
        {
            "run_id": "ingest",
            "source": body.get("source") or "email",
            "payload": body.get("payload") or body,
            "opportunity_id": body.get("opportunity_id"),
            "include_analytics": body.get("source") == "analytics",
        }
    )
    return {
        "ok": True,
        "classified": state.get("classified"),
        "memory": state.get("memory"),
    }


@app.post("/engagement/replay_maya_week2")
async def replay() -> dict:
    inbox = json.loads(INBOX.read_text()) if INBOX.exists() else {"items": []}
    analytics = json.loads(ANALYTICS.read_text()) if ANALYTICS.exists() else {}
    state = await run_engagement(
        {
            "run_id": "maya-week2",
            "items": [
                {
                    "source": "email",
                    "payload": item,
                    "opportunity_id": item.get("opportunity_id"),
                }
                for item in inbox.get("items") or []
            ],
            "analytics": analytics,
            "include_analytics": True,
            "source": "email",
        }
    )
    return {
        "ok": True,
        "inbox": inbox,
        "analytics": analytics,
        "classified": state.get("classified"),
        "memory": state.get("memory"),
    }
