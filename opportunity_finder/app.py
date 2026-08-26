from __future__ import annotations

import uuid

from fastapi import FastAPI

from opportunity_finder.graph import run_search
from opportunity_finder.tools import load_seed
from shared.cors import add_cors
from shared.schemas import SearchRequest

app = FastAPI(title="Opportunity Finder", version="0.1.0")
add_cors(app)

LAST: dict = {"opportunities": load_seed()}


@app.get("/health")
def health() -> dict:
    return {"service": "opportunity_finder", "status": "ok"}


@app.get("/opportunities/last")
def last() -> dict:
    return {"opportunities": LAST.get("opportunities") or load_seed()}


@app.post("/opportunities/search")
@app.post("/tools/find_opportunities")
async def search(req: SearchRequest) -> dict:
    profile = req.profile.model_dump() if req.profile else {"id": req.profile_id, "niche": req.niche, "city": req.city}
    state = await run_search(
        {
            "run_id": f"finder-{uuid.uuid4().hex[:8]}",
            "profile_id": req.profile_id,
            "profile": profile,
            "niche": req.niche,
            "city": req.city,
            "limit": req.limit,
        }
    )
    opps = list(state.get("opportunities") or load_seed())[: req.limit]
    LAST["opportunities"] = opps
    return {"opportunities": opps}
