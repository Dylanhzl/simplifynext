from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from fastapi import FastAPI, Request

from shared.cors import add_cors
from observability.otel import agent_span
from pipeline_manager import db
from pipeline_manager.agents.opportunity_clerk import OpportunityClerkAgent
from pipeline_manager.agents.persist_and_schedule import PersistAndSchedule
from pipeline_manager.agents.status_tracker import StatusTrackerAgent
from pipeline_manager.agents.follow_up_planner import FollowUpPlannerAgent

MEMORY_PATH = Path(__file__).resolve().parents[1] / "demo" / "maya" / "memory.json"

app = FastAPI(title="Pipeline Manager", version="0.1.0")
add_cors(app)


@app.on_event("startup")
async def startup() -> None:
    await db.init_db()


@app.get("/health")
def health() -> dict:
    return {"service": "pipeline_manager", "status": "ok"}


@app.post("/pipeline/upsert")
async def upsert(request: Request) -> dict:
    payload = await request.json()
    state: dict[str, Any] = {"payload": payload}
    with agent_span(OpportunityClerkAgent.name, OpportunityClerkAgent.kind):
        state = await OpportunityClerkAgent().run(state)
    return {"ok": True, "id": state.get("id"), "record_kind": state.get("record_kind")}


@app.get("/pipeline/opportunities")
async def list_opportunities() -> dict:
    return {"opportunities": await db.list_opportunities()}


@app.get("/pipeline/opportunities/{oid}")
async def get_opportunity(oid: str) -> dict:
    record = await db.get_opportunity(oid)
    return record or {"error": "not found", "id": oid}


@app.post("/pipeline/calendar")
async def calendar(request: Request) -> dict:
    body = await request.json()
    event = await db.save_calendar_event(body)
    return {"ok": True, "event": event}


@app.post("/tools/persist_and_schedule")
async def persist_and_schedule(request: Request) -> dict:
    payload = await request.json()
    state: dict[str, Any] = {"payload": payload, "run_id": payload.get("run_id", "")}
    state = await PersistAndSchedule().run(state)
    return {
        "ok": True,
        "id": state.get("id"),
        "record_kind": state.get("record_kind"),
        "qualification": state.get("qualification"),
        "follow_up": state.get("follow_up"),
        "calendar_slots": state.get("calendar_slots", []),
    }


@app.post("/tools/update_status")
async def update_status(request: Request) -> dict:
    """Agent-as-tool entry for Engagement Listener / MCP: StatusTracker then FollowUpPlanner."""
    body = await request.json()
    state: dict[str, Any] = {"opportunity_id": body["opportunity_id"], "status": body["status"]}

    with agent_span(StatusTrackerAgent.name, StatusTrackerAgent.kind):
        state = await StatusTrackerAgent().run(state)

    if state.get("stored") is None:
        return {"ok": False, "error": "opportunity not found", "id": body["opportunity_id"]}

    with agent_span(FollowUpPlannerAgent.name, FollowUpPlannerAgent.kind):
        state = await FollowUpPlannerAgent().run(state)

    return {
        "ok": True,
        "id": state["opportunity_id"],
        "status": state["status"],
        "follow_up": state.get("follow_up"),
        "calendar_slots": state.get("calendar_slots", []),
    }


@app.get("/pipeline/memory")
async def get_memory() -> dict:
    memory = await db.get_memory()
    if memory:
        return memory
    if MEMORY_PATH.exists():
        return json.loads(MEMORY_PATH.read_text())
    return {"wins": [], "losses": [], "next_bias": []}


@app.post("/pipeline/memory")
async def post_memory(request: Request) -> dict:
    body = await request.json()
    memory = await db.write_memory(body)
    MEMORY_PATH.write_text(json.dumps(memory, indent=2))
    return {"ok": True, "memory": memory}
