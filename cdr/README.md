# CDR Agent (P2)

Port **8084**. Content Development Representative.

## Workflow

1. `CDRRootAgent` (DeepAgents-style) plans and selects opportunities.
2. Tools (agent-as-tool): `find_opportunities` → `research_opportunity` → `generate_proposal` → `run_qa` → `draft_outreach` → `persist_and_schedule`.
3. `ParallelResearch` fans out Audience / Peers / Presence / Pain.
4. `RefinementLoop` fact-checks and voice-critiques (max 3). Maya fixture **fails once** on an unsourced calorie claim, then rewrites.
5. Outreach writes email + DM + 30s call script. Persist goes to MCP `:8085`, then P3 HTTP, then `demo/outbox/cdr/{run_id}/`.

LangGraph wraps load → root. Claude Agent SDK is optional on FactChecker (`ANTHROPIC_API_KEY`); Groq/fixtures always work.

## HTTP

- `POST /cdr/run` `{profile?, opportunities?, opportunity_ids?}` → `{run_id}`
- `GET /cdr/runs/{id}` full state
- `GET /cdr/runs/{id}/events` SSE (`agent`, `pattern`, `summary`)
- `POST /ag-ui` AG-UI SSE for CopilotKit (`STEP_FINISHED` includes `pattern`)

`USE_FIXTURES=1` (default) runs Maya without a Groq key.
