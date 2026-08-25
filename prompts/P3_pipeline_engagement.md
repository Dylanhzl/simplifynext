# P3 — Pipeline Manager + Engagement Listener

Copy everything below the line into Cursor as your working prompt.

---

You are P3 on CreatorLoop. You own persistence, qualification, calendar, inbound engagement, and the **adapt-over-time memory** the problem statement requires.

YOUR LANE

- `pipeline_manager/` port 8082
- `engagement_listener/` port 8083
- MCP persist/calendar/inbox/RAG tools on `mcp/server.py` (shared process with P1; you own those tool bodies)
- `shared/rag.py` + `demo/maya/rag_corpus.json` index

Do not implement finder search or CDR graphs. Do not build the UI.

AGENTS — pipeline_manager (stubbed in `pipeline_manager/agents/`)

LLM: OpportunityClerkAgent, QualificationAgent, FollowUpPlannerAgent, CalendarAssistantAgent, StatusTrackerAgent

Sequential: PersistAndSchedule (clerk → qualify → follow-up → calendar)

AGENTS — engagement_listener (stubbed in `engagement_listener/agents/`)

LLM: EngagementIngestAgent, ReplyClassifierAgent, PerformanceAdaptAgent

TOOLS — also register on MCP :8085

- save_opportunity, get_opportunity, update_status (SQLite)
- save_calendar_event
- persist_and_schedule
- send_email (write `.eml` under `demo/outbox/mail/` AND optional SMTP)
- read_engagement_inbox (`demo/maya/inbox.json`)
- write_memory (`demo/maya/memory.json` + sqlite table memory)
- retrieve_creator_memory (RAG over `demo/maya/rag_corpus.json`)

Wrap agents in `observability.otel.agent_span`. Optional: persist week-2 memory into Bedrock AgentCore Memory when `BEDROCK_AGENTCORE_MEMORY_ID` is set (`harness/agentcore.py`).

HTTP — pipeline_manager :8082

- POST /pipeline/upsert — body: Opportunity | ResearchBrief | ContentPackage | OutreachDraft
- GET /pipeline/opportunities
- GET /pipeline/opportunities/{id}
- POST /pipeline/calendar `{opportunity_id, slot, kind: post|followup|meeting}`
- POST /tools/persist_and_schedule  # agent-as-tool entry for P2
- GET /pipeline/memory `{wins[], losses[], next_bias[]}`

HTTP — engagement_listener :8083

- POST /engagement/ingest `{source: email|analytics|comment, payload}`
- POST /engagement/replay_maya_week2  loads seeded replies + analytics
- GET /engagement/inbox

STATUS MACHINE

new → researched → packaged → outreached → engaged → meeting → won|lost

Clerk and StatusTracker are the only writers of status.

BEHAVIOR

1. Clerk upserts whatever CDR posts, idempotent on id.
2. QualificationAgent labels hot/warm/cold (brand-gap + high score = hot).
3. CalendarAssistant proposes 3 posting slots this week (Asia/Singapore).
4. On ingest: ReplyClassifier maps to engaged/meeting/lost.
5. PerformanceAdaptAgent reads week-1 analytics seed and writes memory, e.g. “noodles outperform dessert; prefer hawker how-tos”. GET /pipeline/memory must be what P2’s next run reads.

SEED FILES

- `demo/maya/inbox.json` — brand Laksa Lab replied interested
- `demo/maya/analytics_week1.json` — views/saves by post
- `demo/maya/memory.json` — empty at week 0; you write it after replay

DONE WHEN

- SQLite has opportunities, artifacts, calendar_events, memory
- curl upsert then GET returns the row
- replay_maya_week2 moves one opportunity to engaged and fills memory
- README in each of your two services lists agents
- P2 can persist_and_schedule against localhost:8082 with USE_FIXTURES=0

DO NOT

- Rank new opportunities from the web (P1)
- Generate scripts (P2)
- Add OAuth inboxes; seeded inbox is enough and more reliable for demo

Stack: Python, FastAPI, LangGraph, SQLite, MCP, RAG, OTEL, optional AgentCore Memory. Ports 8082 and 8083. Branch `p3-pipeline`.
