"""AG-UI endpoint: stream STEP_* / RUN_* events for CopilotKit generative UI."""

from __future__ import annotations

import asyncio
import json

from fastapi import APIRouter, Request
from fastapi.responses import StreamingResponse

from cdr.runtime import get_run, queue
from cdr.service import execute_run, start_run

router = APIRouter()


@router.post("/ag-ui")
async def ag_ui_run(request: Request) -> StreamingResponse:
    body = {}
    try:
        body = await request.json()
    except Exception:
        body = {}
    run_id = str(body.get("runId") or body.get("run_id") or "")
    if not run_id:
        run_id = start_run(body)
        asyncio.create_task(execute_run(run_id, body))

    async def gen():
        rec = get_run(run_id)
        if rec:
            yield f"data: {json.dumps({'type': 'RUN_STARTED', 'runId': run_id})}\n\n"
            for ev in rec.get("agui") or []:
                yield f"data: {json.dumps(ev)}\n\n"
        q = queue(run_id)
        while True:
            item = await q.get()
            if item is None:
                break
            if item.get("agui"):
                yield f"data: {json.dumps(item['agui'])}\n\n"

    return StreamingResponse(gen(), media_type="text/event-stream")
