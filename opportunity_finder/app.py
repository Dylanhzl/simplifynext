from pathlib import Path

from fastapi import FastAPI

from shared.cors import add_cors
from shared.schemas import SearchRequest

SEED = Path(__file__).resolve().parents[1] / "demo" / "maya" / "opportunities_seed.json"

app = FastAPI(title="Opportunity Finder", version="0.1.0")
add_cors(app)


@app.get("/health")
def health() -> dict:
    return {"service": "opportunity_finder", "status": "ok"}


@app.get("/opportunities/last")
def last() -> dict:
    import json

    if SEED.exists():
        return json.loads(SEED.read_text())
    return {"opportunities": []}


@app.post("/opportunities/search")
@app.post("/tools/find_opportunities")
def search(req: SearchRequest) -> dict:
    import json

    data = json.loads(SEED.read_text()) if SEED.exists() else {"opportunities": []}
    data["opportunities"] = data.get("opportunities", [])[: req.limit]
    data["note"] = "scaffold fixture — P1 replaces this with OpportunityFinderPipeline"
    return data
