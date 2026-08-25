# CreatorLoop

Agentic studio manager for content creators. It **plans** a week of work, **acts** on the pipeline (research, package, critique, outreach), and **adapts** the next run from what came back.

Built for the SimplifyNext Agentic AI Hackathon 2026. Kick-off problem: a solution that **plans, acts, and adapts over time**; we chose creators going from irregular posting to a repeatable studio. The human **supervises the agent** (one Run click). Named agents do the grind.

Software AI track. Official stack from the kick-off slide is mapped in [`STACK.md`](STACK.md): **MCP, AWS Bedrock AgentCore, AG-UI, OpenTelemetry, LangGraph / DeepAgents / Claude Agent SDK**, plus Groq from training.

## Who it serves

Maya Tan (seed persona): Singapore home-cook / hawker-style TikTok + Instagram. Goal: 3 posts per week and a first small local brand deal.

## Architecture

Five application services plus MCP:

| Service | Port | Owner | Job |
|---|---|---|---|
| UI Client (AG-UI / CopilotKit) | 8000 | P4 | Campaign board + generative UI for agent tools. |
| Opportunity Finder | 8081 | P1 | Discover trends, brand-gaps, collabs. |
| Pipeline Manager | 8082 | P3 | Persist, qualify, calendar, memory, RAG corpus. |
| Engagement Listener | 8083 | P3 | Inbound replies + analytics → status + memory. |
| CDR Agent + AG-UI | 8084 | P2 | LangGraph graphs; DeepAgents root; `POST /ag-ui`. |
| MCP tool server | 8085 | P1+P3 | Search, places, persist, calendar, inbox, RAG retrieve. |

CDR = Content Development Representative.

```
AG-UI UI → CDR :8084/ag-ui
MCP :8085 ← Finder + CDR + Pipeline
Finder → CDR → critique loop → Pipeline
Engagement Listener → Pipeline memory (adapt)
OTEL spans on every named agent
```

About **34 distinct named agents** (LLM, sequential, parallel, loop, custom). Do not collapse them into one mega-prompt. List is in each service `agents/` folder.

### Patterns that must show up in the demo

- Parallel fan-out/gather on research
- Review/critique with structured `{verdict, issues, must_fix}`
- Iterative refinement loop (max 3), including a visible fail-then-fix on Maya
- Agent-as-tool (parent agent calls subgraphs / other services as tools)
- Human-in-the-loop is **minimal**: one Run click. Optional `PAUSE_BEFORE_SEND` defaults off
- **AG-UI dynamic rendering**: artifacts show up as UI components, not only chat text
- **OTEL** spans named by agent + pattern

## Team

Work on your own branch, merge to `main` every night. P1 is merge captain for [`shared/`](shared/).

| Person | Branch | Prompt |
|---|---|---|
| P1 Opportunity Finder + platform | `p1-finder` | [prompts/P1_opportunity_finder.md](prompts/P1_opportunity_finder.md) |
| P2 CDR orchestrator | `p2-cdr` | [prompts/P2_cdr.md](prompts/P2_cdr.md) |
| P3 Pipeline + engagement | `p3-pipeline` | [prompts/P3_pipeline_engagement.md](prompts/P3_pipeline_engagement.md) |
| P4 UI + demo story | `p4-ui` | [prompts/P4_ui_demo.md](prompts/P4_ui_demo.md) |

**Rule:** if a field is not in [`shared/schemas.py`](shared/schemas.py), it does not exist. Schema changes go through a PR that P1 merges.

## Quick start

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pip install -r requirements-stack.txt
cp .env.example .env
chmod +x scripts/run_local.sh
./scripts/run_local.sh
```

Open [http://localhost:8000](http://localhost:8000). Finder already returns Maya seed opportunities. CDR streams fixture events on SSE **and** `POST /ag-ui`. MCP lists tools on [http://localhost:8085/mcp/tools](http://localhost:8085/mcp/tools). Keep `USE_FIXTURES=1` until day 5.

Docker compose in this repo is a **port map sketch**. Day-1 path is `scripts/run_local.sh` after `pip install -r requirements.txt`. Add per-service Dockerfiles later if you want `docker compose up` without a local venv.

## Frozen HTTP

- `POST /opportunities/search` and `POST /tools/find_opportunities` → `{opportunities[]}` (8081)
- `POST /cdr/run` → `{run_id}` ; `GET /cdr/runs/{id}/events` SSE (8084)
- `POST /pipeline/upsert` ; `GET /pipeline/opportunities` ; `POST /pipeline/calendar` ; `POST /tools/persist_and_schedule` ; `GET /pipeline/memory` (8082)
- `POST /engagement/ingest` ; `POST /engagement/replay_maya_week2` ; `GET /engagement/inbox` (8083)
- `POST /ag-ui` AG-UI event stream (8084)
- `GET /mcp/tools` ; `POST /mcp/call` (8085)

## Stack

See [`STACK.md`](STACK.md) for the kick-off slide mapping.

- **Harness:** LangGraph (graphs) · DeepAgents (`CDRRootAgent`) · Claude Agent SDK (optional specialist)
- **Protocols:** MCP (tools) · AG-UI (CopilotKit UI) · OTEL (traces)
- **Runtime:** Groq locally · AWS Bedrock AgentCore for the recorded/deployed demo
- **Data:** SQLite in Pipeline Manager · RAG corpus in `demo/maya/rag_corpus.json`

## Demo story

See [`demo/DEMO_SCRIPT.md`](demo/DEMO_SCRIPT.md). Week 1: run campaign, show parallel research, critique fail then rewrite, auto outreach. Week 2: Laksa Lab replied interested; noodle posts win, dessert loses; memory biases the next plan.
