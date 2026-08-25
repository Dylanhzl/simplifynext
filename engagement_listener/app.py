from __future__ import annotations

import json
from pathlib import Path

from fastapi import FastAPI, Request

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
    return {"ok": True, "accepted": body, "note": "scaffold — P3 implements EngagementIngestAgent"}


@app.post("/engagement/replay_maya_week2")
def replay() -> dict:
    inbox = json.loads(INBOX.read_text()) if INBOX.exists() else {"items": []}
    analytics = json.loads(ANALYTICS.read_text()) if ANALYTICS.exists() else {}
    return {
        "ok": True,
        "inbox": inbox,
        "analytics": analytics,
        "note": "scaffold — P3 should classify replies and write memory",
    }
