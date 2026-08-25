# P1 — Opportunity Finder + platform

Copy everything below the line into Cursor as your working prompt.

---

You are P1 on CreatorLoop, a 4-person hackathon project.

YOUR LANE (do not implement CDR research/QA/outreach, pipeline SQLite, or the UI):

- `shared/` — schemas, event helpers, HTTP clients. You are merge captain for this folder.
- `opportunity_finder/`
- `mcp/` search tools (`search_web`, `search_local_places`, `fetch_url`)
- `compose.yaml`
- Review PRs that touch `shared/`

GOAL

Given niche + city + creator profile, discover ranked opportunities. High-fit examples: trending hooks, peer collabs, and **local brands with weak or missing short-form content**.

AGENTS YOU MUST CREATE (distinct classes/modules, already stubbed under `opportunity_finder/agents/` — fill `run()`, do not rename):

LLM: NicheQueryAgent, TrendHarvesterAgent, BrandGapAgent, CollabScoutAgent, OpportunityClusterAgent, OpportunityScorerAgent

Sequential: OpportunityFinderPipeline in order query → harvest → gap → collab → cluster → score

Custom: OpportunityFinderRoot — FastAPI entry that runs the pipeline

TOOLS — implement on the MCP server (`mcp/server.py`, port 8085), not as one-off HTTP inside prompts:

- `search_web`
- `search_local_places` (use `demo/maya/places_sg_food.json`; optional Google Places later)
- `fetch_url`
- `save_opportunity` can still POST Pipeline Manager; also expose persist via MCP for P2

Wrap each agent `run()` with `observability.otel.agent_span`.

HARNESS

OpportunityFinderPipeline must be a **LangGraph** StateGraph (sequential + parallel harvest). Do not invent a new orchestrator.

HTTP CONTRACT (frozen)

POST http://localhost:8081/opportunities/search

body: `{ "profile_id": "maya", "niche": "singapore hawker food", "city": "Singapore", "limit": 8 }`

return: `{ "opportunities": [ Opportunity, ... ] }`

Opportunity fields must match `shared/schemas.py` exactly: id, type (trend|gap|collab|brand), title, why_now, city, niche, score 0-100, evidence_urls[], raw_notes, source_agent, status

Also keep GET /health, GET /opportunities/last, and POST /tools/find_opportunities (same body as search). CDR will call `/tools/find_opportunities` as an **agent-as-tool**.

BEHAVIOR

1. NicheQueryAgent emits 5-10 queries from profile.
2. TrendHarvester, BrandGap, CollabScout run in parallel (LangGraph Send or asyncio.gather).
3. Cluster then score. Return top `limit`.
4. If live search fails, fall back to `demo/maya/opportunities_seed.json` so the rest of the team is never blocked.

DAY 1

Scaffold already returns seed JSON on 8081. Next: LangGraph pipeline behind the same routes. Keep `USE_FIXTURES=1` working.

DONE WHEN

- 6 named LLM agents exist as separate files with real `run()` implementations
- pipeline is Sequential wrapping them
- curl search returns >=5 Maya-relevant opportunities with scores
- `opportunity_finder/README.md` lists agents + tools
- You can demo: city+niche in, ranked list out, no UI required

DO NOT

- Build the dashboard
- Call LLMs from the UI
- Invent extra schema fields without a PR to `shared/`

Stack: Python, FastAPI, LangGraph, MCP, OTEL, Groq. Ports 8081 + MCP 8085. Branch `p1-finder`.
