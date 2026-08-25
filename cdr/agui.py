"""AG-UI endpoint (kick-off: Agent-UI Protocol, dynamic rendering).

P2: wrap the compiled LangGraph in LangGraphAGUIAgent (CopilotKit) or ag_ui SDK.
P4: CopilotKit frontend consumes POST /ag-ui and renders tool results as components.
"""

from fastapi import APIRouter, Request
from fastapi.responses import StreamingResponse

from pathlib import Path

SEED = Path(__file__).resolve().parents[1] / "demo" / "fixtures" / "run_events.jsonl"

router = APIRouter()


@router.post("/ag-ui")
async def ag_ui_run(request: Request) -> StreamingResponse:
    """Scaffold: stream fixture events as AG-UI-shaped SSE. P2 replaces with LangGraphAGUIAgent."""
    await request.body()

    def gen():
        if SEED.exists():
            for line in SEED.read_text().splitlines():
                if line.strip():
                    yield f"data: {line}\n\n"
        yield "data: {\"type\": \"RUN_FINISHED\"}\n\n"

    return StreamingResponse(gen(), media_type="text/event-stream")
