"""Opportunity Finder service (P1).

Frozen contract -- CDR calls /tools/find_opportunities as an agent-as-tool:

    POST /opportunities/search      -> {"opportunities": [Opportunity, ...]}
    POST /tools/find_opportunities  -> same
    GET  /opportunities/last        -> last run's result
    GET  /health

Behind those routes runs OpportunityFinderRoot -> OpportunityFinderPipeline
(LangGraph). Any failure falls back to demo/maya seed data so the rest of the
team is never blocked.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from fastapi import FastAPI

from observability.otel import setup_tracing
from opportunity_finder.agents.root import OpportunityFinderRoot
from shared.cors import add_cors
from shared.schemas import SearchRequest

SEED = Path(__file__).resolve().parents[1] / "demo" / "maya" / "opportunities_seed.json"

app = FastAPI(title="Opportunity Finder", version="0.2.0")
add_cors(app)
setup_tracing("opportunity_finder")

ROOT = OpportunityFinderRoot()
_LAST: dict[str, Any] = {}


@app.get("/health")
def health() -> dict:
    return {"service": "opportunity_finder", "status": "ok", "agents": 8}


@app.get("/opportunities/last")
def last() -> dict:
    if _LAST:
        return _LAST
    if SEED.exists():
        return json.loads(SEED.read_text())
    return {"opportunities": []}


@app.post("/opportunities/search")
@app.post("/tools/find_opportunities")
async def search(req: SearchRequest) -> dict:
    global _LAST

    result = await ROOT.run(
        {
            "profile": req.profile.model_dump() if req.profile else None,
            "niche": req.niche,
            "city": req.city,
            "limit": req.limit,
        }
    )

    _LAST = {
        "opportunities": result["opportunities"],
        "run_id": result["run_id"],
        "mode": result.get("mode", "live"),
        "notes": result.get("notes", []),
    }
    return _LAST
