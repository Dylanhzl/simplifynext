# Opportunity Finder (P1)

Port **8081**. Discover ranked opportunities for a creator niche + city.

## Agents

LLM: `NicheQueryAgent`, `TrendHarvesterAgent`, `BrandGapAgent`, `CollabScoutAgent`, `OpportunityClusterAgent`, `OpportunityScorerAgent`

Sequential: `OpportunityFinderPipeline` — query → parallel harvest (trend / brand-gap / collab) → cluster → score

Custom: `OpportunityFinderRoot` — FastAPI entry

## HTTP

- `POST /opportunities/search` and `POST /tools/find_opportunities`
- `GET /opportunities/last`
- `GET /health`

## Tools (MCP :8085)

`search_web`, `search_local_places`, `fetch_url`, `find_opportunities`

Live search falls back to `demo/maya/opportunities_seed.json` + `places_sg_food.json`.
