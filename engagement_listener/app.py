from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import httpx
from fastapi import FastAPI, Request

from shared.cors import add_cors
from shared.http_clients import PIPELINE_MANAGER_URL
from observability.otel import agent_span
from engagement_listener.agents.engagement_ingest import EngagementIngestAgent
from engagement_listener.agents.reply_classifier import ReplyClassifierAgent
from engagement_listener.agents.performance_adapt import PerformanceAdaptAgent

INBOX = Path(__file__).resolve().parents[1] / "demo" / "maya" / "inbox.json"
ANALYTICS = Path(__file__).resolve().parents[1] / "demo" / "maya" / "analytics_week1.json"
MEMORY_PATH = Path(__file__).resolve().parents[1] / "demo" / "maya" / "memory.json"

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


async def _update_pipeline_status(opportunity_id: str, status: str) -> dict[str, Any]:
    async with httpx.AsyncClient(timeout=10.0) as client:
        r = await client.post(
            f"{PIPELINE_MANAGER_URL}/tools/update_status",
            json={"opportunity_id": opportunity_id, "status": status},
        )
        r.raise_for_status()
        return r.json()


async def _push_memory(memory: dict[str, Any]) -> None:
    async with httpx.AsyncClient(timeout=10.0) as client:
        r = await client.post(f"{PIPELINE_MANAGER_URL}/pipeline/memory", json=memory)
        r.raise_for_status()


async def _classify_reply(source: str, payload: dict[str, Any]) -> dict[str, Any]:
    with agent_span(EngagementIngestAgent.name, EngagementIngestAgent.kind):
        state = await EngagementIngestAgent().run({"source": source, "payload": payload})
    with agent_span(ReplyClassifierAgent.name, ReplyClassifierAgent.kind):
        state = await ReplyClassifierAgent().run(state)

    if state.get("status") and state.get("opportunity_id"):
        try:
            state["pipeline_update"] = await _update_pipeline_status(
                state["opportunity_id"], state["status"]
            )
        except httpx.HTTPError as exc:
            state["pipeline_update_error"] = str(exc)

    return state


@app.post("/engagement/ingest")
async def ingest(request: Request) -> dict:
    body = await request.json()
    payload = dict(body.get("payload") or {})
    if body.get("opportunity_id") and "opportunity_id" not in payload:
        payload["opportunity_id"] = body["opportunity_id"]
    result = await _classify_reply(body.get("source", "email"), payload)
    return {"ok": True, "classification": result}


@app.post("/engagement/replay_maya_week2")
async def replay() -> dict:
    inbox_data = json.loads(INBOX.read_text()) if INBOX.exists() else {"items": []}
    analytics = json.loads(ANALYTICS.read_text()) if ANALYTICS.exists() else {"posts": []}

    replies = [
        await _classify_reply(item.get("source", "email"), item)
        for item in inbox_data.get("items", [])
    ]

    with agent_span(PerformanceAdaptAgent.name, PerformanceAdaptAgent.kind):
        adapt_state = await PerformanceAdaptAgent().run({"posts": analytics.get("posts", [])})
    memory = adapt_state["memory"]
    MEMORY_PATH.write_text(json.dumps(memory, indent=2))

    try:
        await _push_memory(memory)
    except httpx.HTTPError as exc:
        memory = {**memory, "push_error": str(exc)}

    return {"ok": True, "replies": replies, "memory": memory}
