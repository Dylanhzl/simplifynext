# CreatorLoop

Agentic studio manager for content creators. It **plans** a week of work, **acts** on the pipeline (research, package, critique, outreach), and **adapts** the next run from what came back.

Built for the SimplifyNext Agentic AI Hackathon 2026. Kick-off problem: a solution that **plans, acts, and adapts over time**; we chose creators going from irregular posting to a repeatable studio. The human **supervises the agent** — one Run click. Named agents do the grind.

Software AI track. The official kick-off stack — **MCP, AWS Bedrock AgentCore, AG-UI, OpenTelemetry, LangGraph / DeepAgents / Claude Agent SDK**, plus Groq — is mapped to where it appears on screen in [`STACK.md`](STACK.md).

## Who it serves

Maya Tan (seed persona): Singapore home-cook / hawker-style TikTok + Instagram. Goal: 3 posts per week and a first small local brand deal. Full persona in [`demo/maya/profile.json`](demo/maya/profile.json).

## Run the demo

Fixture mode needs **no LLM keys, no pip install, and no other service running**. The UI server is standard library Python.

```bash
python3 ui_client/server.py
```

Open [http://localhost:8000](http://localhost:8000) and click **Run campaign**. Click it a second time for the week-2 replay. That is the whole demo.

To record the 3-minute video, use the pacing the cue sheet is measured against:

```bash
DEMO_SPEED=0.6 python3 ui_client/server.py
```

### Full stack (UAT)

Install deps once, then bring up Finder / Pipeline / Engagement / CDR / MCP / UI together:

```bash
python -m venv .venv
# Windows: .\.venv\Scripts\Activate.ps1
# macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# Windows:
.\scripts\run_local.ps1
# macOS/Linux:
./scripts/run_local.sh
```

With services up, run the frozen-HTTP smoke suite:

```powershell
.\scripts\uat_smoke.ps1
```

`USE_FIXTURES=1` (default) keeps Finder/MCP on seed data so UAT does not need Groq keys.

### The AG-UI client (CopilotKit)

The static board above is the no-keys fallback. The AG-UI client is the real one:

```bash
cd ui_client/agui && npm install && npm run dev
```

Open [http://localhost:5173](http://localhost:5173). Same board, plus a CopilotKit
sidebar — ask the CDR agent for something and the tool calls it makes render as
the same components inline. It connects with `@ag-ui/client`'s `HttpAgent` and
registers every card on `CopilotKitProvider`'s `renderToolCalls`.

`package.json` pins `@ag-ui/client` to `0.0.57` under `overrides` on purpose:
CopilotKit 1.69 depends on that exact version, and a second copy in the tree
makes `HttpAgent` fail to typecheck as an `AbstractAgent`. Bump both together.

### Going live on day 5

```bash
USE_FIXTURES=0 python3 ui_client/server.py       # proxies POST http://localhost:8084/ag-ui
```

No component changes. The browser receives the same AG-UI event stream either
way; only the source changes. If the CDR agent does not answer, the run falls
back to fixtures and says so on screen instead of dying mid-demo.

| Variable | Default | Meaning |
|---|---|---|
| `USE_FIXTURES` | `1` | `0` proxies the live CDR agent |
| `CDR_AGUI_URL` | `http://localhost:8084/ag-ui` | Live AG-UI endpoint |
| `DEMO_SPEED` | `1.0` | Replay pacing. `0.6` matches the demo cue sheet |
| `PAUSE_BEFORE_SEND` | `0` | Optional HITL toggle. Off by design |
| `UI_PORT` | `8000` | Board port |

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

About **34 distinct named agents** (llm, sequential, parallel, loop, tool, custom). Do not collapse them into one mega-prompt. The list per service lives in each service's `agents/` folder; **39** appear by name across the two demo runs.

### Patterns that must show up in the demo

- Parallel fan-out/gather on research
- Review/critique with structured `{verdict, issues, must_fix}`
- Iterative refinement loop (max 3), including a visible fail-then-fix on Maya
- Agent-as-tool (parent agent calls subgraphs / other services as tools)
- Human-in-the-loop is **minimal**: one Run click. Optional `PAUSE_BEFORE_SEND` defaults off
- **AG-UI dynamic rendering**: artifacts show up as UI components, not only chat text
- **OTEL** spans named by agent + pattern

## What the board shows

| Panel | Source |
|---|---|
| Campaign bar | niche, city, profile = Maya, **Run campaign** — the only required human action |
| Live agent trace | `CUSTOM/agent_trace` — agent name, pattern badge, service, summary. OTEL span names, on screen |
| MCP tool calls | `CUSTOM/mcp_call` — which MCP tool ran with what arguments |
| Opportunity table | `CUSTOM/opportunities` — type, title, score, status |
| Pipeline kanban | `CUSTOM/pipeline` — P3's `OpportunityStatus` values |
| Calendar strip | `render_calendar_week` tool call |
| Engagement inbox | `CUSTOM/engagement` — week-2 inbound with classification |
| Memory panel | `CUSTOM/memory` — "what we learned", with `was:` showing what a week-2 entry replaced |
| Artifact drawer | `TOOL_CALL_*` — research brief, content package, critique fail → rewrite, email, DM, call script, analytics, plan adaptation |

The full event contract, including how to add a new render tool, is in [`demo/fixtures/README.md`](demo/fixtures/README.md).

## Team

Work on your own branch, merge to `main` every night. P1 is merge captain for `shared/`.

| Person | Branch | Prompt |
|---|---|---|
| P1 Opportunity Finder + platform | `p1-finder` | `prompts/P1_opportunity_finder.md` |
| P2 CDR orchestrator | `p2-cdr` | `prompts/P2_cdr.md` |
| P3 Pipeline + engagement | `p3-pipeline` | `prompts/P3_pipeline_engagement.md` |
| P4 UI + demo story | `p4-ui` | `prompts/P4_ui_demo.md` |

**Rule:** if a field is not in `shared/schemas.py`, it does not exist. Schema changes go through a PR that P1 merges.

> **Note for P3:** the kanban columns in
> [`ui_client/static/app.js`](ui_client/static/app.js) and
> [`ui_client/agui/src/state/types.ts`](ui_client/agui/src/state/types.ts) mirror an
> assumed `OpportunityStatus` enum: `new, qualified, packaged, scheduled, published,
> outreach_sent, replied, negotiating, won, lost` (with `parked` folded into `lost`).
> If the real enum differs, change that one list and the board follows.

## Frozen HTTP

- `POST /opportunities/search` and `POST /tools/find_opportunities` → `{opportunities[]}` (8081)
- `POST /cdr/run` → `{run_id}` ; `GET /cdr/runs/{id}/events` SSE (8084)
- `POST /pipeline/upsert` ; `GET /pipeline/opportunities` ; `POST /pipeline/calendar` ; `POST /tools/persist_and_schedule` ; `GET /pipeline/memory` (8082)
- `POST /engagement/ingest` ; `POST /engagement/replay_maya_week2` ; `GET /engagement/inbox` (8083)
- `POST /ag-ui` AG-UI event stream (8084)
- `GET /mcp/tools` ; `POST /mcp/call` (8085)

The UI client also serves `POST /ag-ui` on 8000 — same protocol, backed by fixtures or by a proxy to 8084 — plus `GET /api/config`, `GET /api/profile`, `GET /api/rag_corpus` and `POST /api/stop`.

## Stack

See [`STACK.md`](STACK.md) for the kick-off slide mapping and where each item is visible on screen.

- **Harness:** LangGraph (graphs) · DeepAgents (`CDRRootAgent`) · Claude Agent SDK (optional specialist)
- **Protocols:** MCP (tools) · AG-UI (CopilotKit UI) · OTEL (traces)
- **Runtime:** Groq locally · AWS Bedrock AgentCore for the recorded/deployed demo
- **Data:** SQLite in Pipeline Manager · RAG corpus in [`demo/maya/rag_corpus.json`](demo/maya/rag_corpus.json)

## Demo story

See [`demo/DEMO_SCRIPT.md`](demo/DEMO_SCRIPT.md) for the 3:00 cue sheet, timed against `DEMO_SPEED=0.6`.

Week 1: run campaign, parallel research, critique fails the hook at 0.42, rewrite passes at 0.86, outreach sends itself.
Week 2: Laksa Lab replied interested; noodle posts do 3.1× median and dessert does 0.4×; memory promotes that to a rule and the next week's plan changes on its own.
