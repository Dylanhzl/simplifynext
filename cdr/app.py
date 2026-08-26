from __future__ import annotations

import asyncio
import json

from dotenv import load_dotenv
from fastapi import FastAPI, Request
from fastapi.responses import StreamingResponse

from cdr.agui import router as agui_router
from cdr.runtime import as_run_state, get_run, queue
from cdr.service import execute_run, start_run
from harness.agentcore import runtime_payload
from shared.cors import add_cors

load_dotenv()

app = FastAPI(title="CDR Agent", version="0.2.0")
add_cors(app)
app.include_router(agui_router)


@app.get("/health")
def health() -> dict:
    return {"service": "cdr", "status": "ok", "runtime": runtime_payload()}


@app.post("/cdr/run")
async def run(request: Request) -> dict:
    body = await request.json()
    run_id = start_run(body)
    asyncio.create_task(execute_run(run_id, body))
    return {"run_id": run_id}


@app.get("/cdr/runs/{run_id}")
def get_run_http(run_id: str) -> dict:
    rec = get_run(run_id)
    if not rec:
        return {"run_id": run_id, "events": [], "note": "unknown run"}
    return as_run_state(run_id).model_dump(mode="json") | {
        "status": rec.get("status"),
        "packages": rec.get("packages", []),
        "outreach": rec.get("outreach", []),
        "qa": rec.get("qa", []),
        "error": rec.get("error"),
    }


@app.get("/cdr/runs/{run_id}/events")
async def events(run_id: str) -> StreamingResponse:
    async def gen():
        rec = get_run(run_id)
        if rec:
            for ev in rec.get("events") or []:
                yield f"data: {json.dumps(ev)}\n\n"
        q = queue(run_id)
        while True:
            item = await q.get()
            if item is None:
                yield "data: {\"status\": \"done\"}\n\n"
                break
            if item.get("sse"):
                yield f"data: {json.dumps(item['sse'])}\n\n"

    return StreamingResponse(gen(), media_type="text/event-stream")
