from __future__ import annotations

from fastapi import FastAPI, Request

from pipeline_manager import db
from pipeline_manager.graph import run_persist
from shared.cors import add_cors

app = FastAPI(title="Pipeline Manager", version="0.1.0")
add_cors(app)
db.init()


@app.get("/health")
def health() -> dict:
    return {"service": "pipeline_manager", "status": "ok"}


@app.post("/pipeline/upsert")
async def upsert(request: Request) -> dict:
    body = await request.json()
    oid = body.get("id") or body.get("opportunity_id")
    if not oid:
        return {"ok": False, "error": "missing id"}
    state = await run_persist(
        {
            "run_id": body.get("run_id") or "upsert",
            "opportunity_id": oid,
            "opportunity": body,
            "package": body.get("package"),
            "brief": body.get("brief"),
            "outreach": body.get("outreach"),
            "qa": body.get("qa"),
            "status": body.get("status"),
            "target_status": body.get("status") or body.get("target_status"),
        }
    )
    return {"ok": True, "id": oid, "opportunity": state.get("opportunity"), "qualification": state.get("qualification")}


@app.get("/pipeline/opportunities")
def list_opportunities() -> dict:
    return {"opportunities": db.list_opportunities()}


@app.get("/pipeline/opportunities/{oid}")
def get_opportunity(oid: str) -> dict:
    row = db.get_opportunity(oid)
    if not row:
        return {"error": "not found", "id": oid}
    return row


@app.post("/pipeline/calendar")
async def calendar(request: Request) -> dict:
    body = await request.json()
    event = db.save_calendar_event(body)
    return {"ok": True, "event": event}


@app.post("/tools/persist_and_schedule")
async def persist_and_schedule(request: Request) -> dict:
    body = await request.json()
    state = await run_persist(
        {
            "run_id": body.get("run_id") or "persist",
            "opportunity_id": body.get("opportunity_id") or body.get("id"),
            "opportunity": body.get("opportunity"),
            "package": body.get("package"),
            "brief": body.get("brief"),
            "outreach": body.get("outreach"),
            "qa": body.get("qa"),
            "status": body.get("status"),
            "target_status": body.get("status") or "outreached",
            "current": {"id": body.get("opportunity_id") or body.get("id")},
        }
    )
    return {
        "ok": True,
        "id": state.get("opportunity_id"),
        "status": (state.get("status_result") or {}).get("status"),
        "qualification": state.get("qualification"),
        "calendar": state.get("calendar"),
    }


@app.get("/pipeline/memory")
def memory() -> dict:
    return db.read_memory()
