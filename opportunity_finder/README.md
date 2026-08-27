# Opportunity Finder (P1)

Port **8081**. Discover ranked opportunities for a creator niche + city.

Prompt: [`../prompts/P1_opportunity_finder.md`](../prompts/P1_opportunity_finder.md).

## Named agents

| Agent | Kind | Job | Model |
|---|---|---|---|
| `NicheQueryAgent` | llm | Profile → 5-10 search queries | fast |
| `TrendHarvesterAgent` | llm | Rising hooks and formats | fast |
| `BrandGapAgent` | llm | Local brands with no short-form presence | default |
| `CollabScoutAgent` | llm | Reachable collab partners | fast |
| `OpportunityClusterAgent` | llm | Merge near-duplicate finds | fast |
| `OpportunityScorerAgent` | llm | Final 0-100 ranking + memory bias | default |
| `OpportunityFinderPipeline` | sequential | LangGraph StateGraph over the six | — |
| `OpportunityFinderRoot` | custom | Service entry, memory fetch, fallback | — |

## Graph

```
        NicheQuery
             |
   +---------+---------+
   |         |         |          parallel fan-out
Trend     BrandGap  CollabScout
   |         |         |
   +---------+---------+          gather
             |
      OpportunityCluster
             |
      OpportunityScorer
```

The three harvesters are separate edges from one node, so LangGraph runs them
concurrently. They all append to `harvested`, which is declared with an
`operator.add` reducer in [`agents/state.py`](agents/state.py) — without that
reducer LangGraph raises on the concurrent writes.

[`graph.py`](graph.py) exposes `run_search()` for MCP / harness callers and
delegates to `OpportunityFinderRoot`.

## Tools

Agents call MCP (:8085) through [`shared/mcp_client.py`](../shared/mcp_client.py),
never ad-hoc HTTP:

- `search_web` — TrendHarvester, BrandGap, CollabScout
- `search_local_places` — BrandGap (`has_short_form=False`), CollabScout
- `fetch_url` — available for evidence checks

Local fixture helpers also live in [`tools.py`](tools.py) / [`normalize.py`](normalize.py)
for offline harvest paths used by MCP scaffolding.

## Routes (frozen)

```bash
curl -X POST localhost:8081/opportunities/search \
  -H 'Content-Type: application/json' \
  -d '{"profile_id":"maya","niche":"singapore hawker food","city":"Singapore","limit":8}'
```

- `POST /opportunities/search` → `{opportunities[], run_id, mode, notes}`
- `POST /tools/find_opportunities` → same (CDR calls this as agent-as-tool)
- `GET /opportunities/last` → last run
- `GET /health`

`mode` is `live` when the LangGraph pipeline ran, `seed` when it fell back.

MCP also exposes `find_opportunities` on :8085, which runs the same pipeline.

## Schema authority

LLM agents fill `OpportunityDraft` (type, title, why_now, score, evidence_urls).
We attach `id`, `city`, `niche`, `source_agent`, `status` ourselves, so those can
never drift from [`shared/schemas.py`](../shared/schemas.py).

## Failure behaviour

Nothing here is allowed to break the demo. Each agent falls back to
`demo/maya/opportunities_seed.json` when MCP is down, no `GROQ_API_KEY` is set,
or the LLM fails; `OpportunityFinderRoot` catches anything the pipeline raises
and serves seed data. Week-2 memory is fetched from the Pipeline Manager and
silently skipped if P3's service is unavailable.

## Groq rate limits

The free tier allows **8,000 tokens/minute per model**. A full run is six agents
with three firing at once, which exceeds that in a burst.
[`shared/llm.py`](../shared/llm.py) retries through 429s using Groq's own
`try again in Xs` hint, and light agents run on `GROQ_FAST_MODEL` so the load is
split across two per-model quota pools. A full live run takes ~40s.
