from __future__ import annotations

import json
from pathlib import Path

from fastapi import FastAPI, Request

from shared.cors import add_cors

MEMORY_PATH = Path(__file__).resolve().parents[1] / "demo" / "maya" / "memory.json"
STORE: dict = {"opportunities": {}, "calendar": [], "memory": None}

app = FastAPI(title="Pipeline Manager", version="0.1.0")
add_cors(app)


@app.get("/health")
def health() -> dict:
    return {"service": "pipeline_manager", "status": "ok"}


@app.post("/pipeline/upsert")
async def upsert(request: Request) -> dict:
    body = await request.json()
    oid = body.get("id") or body.get("opportunity_id")
    if oid:
        STORE["opportunities"][oid] = body
    return {"ok": True, "id": oid, "note": "scaffold in-memory store — P3 replaces with SQLite"}


@app.get("/pipeline/opportunities")
def list_opportunities() -> dict:
    return {"opportunities": list(STORE["opportunities"].values())}


@app.get("/pipeline/opportunities/{oid}")
def get_opportunity(oid: str) -> dict:
    return STORE["opportunities"].get(oid, {"error": "not found", "id": oid})


@app.post("/pipeline/calendar")
async def calendar(request: Request) -> dict:
    body = await request.json()
    STORE["calendar"].append(body)
    return {"ok": True, "event": body}


@app.post("/tools/persist_and_schedule")
async def persist_and_schedule(request: Request) -> dict:
    body = await request.json()
    oid = body.get("id") or body.get("opportunity_id") or "unknown"
    STORE["opportunities"][oid] = body
    return {"ok": True, "id": oid, "note": "scaffold — P3 implements PersistAndSchedule"}


@app.get("/pipeline/memory")
def memory() -> dict:
    if MEMORY_PATH.exists():
        return json.loads(MEMORY_PATH.read_text())
    return {"wins": [], "losses": [], "next_bias": []}
