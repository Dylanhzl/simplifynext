from __future__ import annotations

from pathlib import Path
from uuid import uuid4

from fastapi import FastAPI, Request
from fastapi.responses import StreamingResponse

from shared.cors import add_cors
from shared.events import make_run_event
from shared.schemas import PatternKind
from cdr.agui import router as agui_router

SEED_EVENTS = Path(__file__).resolve().parents[1] / "demo" / "fixtures" / "run_events.jsonl"
RUNS: dict[str, dict] = {}

app = FastAPI(title="CDR Agent", version="0.1.0")
add_cors(app)
app.include_router(agui_router)


@app.get("/health")
def health() -> dict:
    return {"service": "cdr", "status": "ok"}


@app.post("/cdr/run")
async def run(request: Request) -> dict:
    body = await request.json()
    run_id = str(uuid4())[:8]
    RUNS[run_id] = {"run_id": run_id, "request": body, "events": []}
    return {"run_id": run_id, "note": "scaffold — P2 wires CDRRootAgent here"}


@app.get("/cdr/runs/{run_id}")
def get_run(run_id: str) -> dict:
    return RUNS.get(run_id, {"run_id": run_id, "events": [], "note": "unknown run"})


@app.get("/cdr/runs/{run_id}/events")
async def events(run_id: str) -> StreamingResponse:
    def gen():
        if SEED_EVENTS.exists():
            for line in SEED_EVENTS.read_text().splitlines():
                if line.strip():
                    yield f"data: {line}\n\n"
        else:
            ev = make_run_event(
                run_id, "CDRRootAgent", PatternKind.custom, "scaffold heartbeat"
            )
            yield f"data: {ev.model_dump_json()}\n\n"

    return StreamingResponse(gen(), media_type="text/event-stream")
