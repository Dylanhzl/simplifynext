# Official hackathon stack (kick-off slide 13)

Software AI track. We are **not** using Songying ORCA / Unitree (Physical AI track).

Kick-off “Our Tech Stack” maps onto this repo as follows.

## MCP — Model Context Protocol

How agents talk to APIs, databases, and files.

- Folder: [`mcp/`](mcp/)
- Port: **8085**
- Tools: `search_web`, `search_local_places`, `fetch_url`, `persist_and_schedule`, `save_calendar_event`, `read_engagement_inbox`, `retrieve_creator_memory` (RAG)

P1 and P3 implement tools. P2’s agents **call MCP**, they do not scrape ad-hoc.

## AWS Bedrock AgentCore

Managed runtime, session isolation, and long-term memory for the recorded / deployed demo.

- Folder: [`harness/agentcore.py`](harness/agentcore.py)
- Local: Groq (training asked everyone to sign up)
- Demo/deploy: Bedrock models + AgentCore Runtime when AWS keys exist

## AG-UI — Agent-UI Protocol

Agentic UI. Stream agent events to the frontend and **expose frontend tools for dynamic rendering** (content cards, QA verdicts, calendar, kanban — not a chat blob).

- Backend: [`cdr/agui.py`](cdr/agui.py) → `POST /ag-ui` on **8084**
- Frontend: [`ui_client/agui/`](ui_client/agui/) CopilotKit + `@ag-ui/client`
- P4 owns generative UI: when an agent emits a tool/artifact, render a real component

The static HTML board is a fallback until CopilotKit is wired.

## OTEL — OpenTelemetry

Traceability and observability. Every named agent starts/ends a span (`agent`, `pattern`, `run_id`).

- Folder: [`observability/`](observability/)
- Export: console in local; OTLP when `OTEL_EXPORTER_OTLP_ENDPOINT` is set

## Agentic harness (all three from the slide)

| Harness | Role in CreatorLoop |
|---|---|
| **LangGraph** | Primary. Sequential / Parallel / Loop graphs. Training: “LangGraph and Beyond”. |
| **DeepAgents** | `CDRRootAgent` long-horizon harness (plan, subagents, memory) on LangGraph. |
| **Claude Agent SDK** | One specialist path (FactChecker or Outreach) when `ANTHROPIC_API_KEY` is set; otherwise Groq/LangGraph does the same job. |

Stubs: [`harness/`](harness/).

## Also from the slides (not the stack box)

- **Plan, act, adapt over time** — week-2 memory after engagement replay
- **Supervise the agent, not do the task** — one Run campaign click
- **Tools: search, databases, APIs, self-correct** — MCP + critique loop
- **Multi-agent RAG** — [`shared/rag.py`](shared/rag.py) over Maya past posts / research briefs
- **Groq** — daily LLM (`GROQ_API_KEY`)
