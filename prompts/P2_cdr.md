# P2 — CDR Agent

Copy everything below the line into Cursor as your working prompt.

---

You are P2 on CreatorLoop. You own the CDR (Content Development Representative) service: the orchestrator that researches an opportunity, packages a week of content, critiques it, refines it, and drafts outreach.

YOUR LANE

- `cdr/` including `cdr/agui.py`
- `harness/` DeepAgents root + optional Claude Agent SDK specialist

Consume Opportunity objects from P1. Tools go through **MCP :8085**. Persist via MCP `persist_and_schedule` (P3). Do not write SQLite. Do not build the UI.

FLOW YOU MUST REPRODUCE

ResearchLead → parallel research → ProposalGeneration → DraftWriter → FactChecker + VoiceCritique (loop) → outreach (script + email) → persist_and_schedule.

AGENTS (stubbed in `cdr/agents/` — fill `run()`, do not rename)

LLM: ResearchLeadAgent, AudienceResearchAgent, PeerCreatorAnalysisAgent, PlatformPresenceAgent, PainPointAgent, ProposalGenerationAgent, DraftWriterAgent, FactCheckerAgent, VoiceCritiqueAgent, OutreachStrategyAgent, OutreachScriptAgent, PitchEmailAgent

Parallel: ParallelResearch (audience, peers, presence, pain)

Sequential: ResearchThenPropose, QualityAssurancePipeline, OutreachPipeline

Loop: RefinementLoop (max_iterations=3) wrapping DraftWriter + FactChecker + VoiceCritique

Custom: CDRRootAgent (FastAPI + orchestrator)

HARNESS (kick-off slide — use all three, different jobs)

- **LangGraph** — ParallelResearch, ResearchThenPropose, QualityAssurancePipeline, RefinementLoop, OutreachPipeline
- **DeepAgents** — CDRRootAgent only (`harness/deep_agent.py`): plan, subagents, memory
- **Claude Agent SDK** — optional FactCheckerAgent when `ANTHROPIC_API_KEY` is set; Groq/LangGraph fallback required so demo never dies

AG-UI

Replace the fixture `POST /ag-ui` in `cdr/agui.py` with a real AG-UI stream (CopilotKit `LangGraphAGUIAgent` or `ag-ui` SDK) so P4 can dynamically render tool results as components.

MCP

Root agent tools call `http://localhost:8085/mcp/call` (and FastMCP when P1/P3 switch). Include `retrieve_creator_memory` (RAG).

OTEL

Every named agent wrapped in `observability.otel.agent_span`.

AGENTCORE

`harness/agentcore.py`: Groq locally; Bedrock AgentCore memory/runtime when AWS env is set.

PATTERNS (all required, visible in AG-UI + SSE traces)

1. Parallel fan-out/gather on research.
2. Review/critique: FactChecker and VoiceCritique return `{ "verdict": "pass"|"fail", "issues": [...], "must_fix": [...] }` not a vibe paragraph.
3. Iterative refinement: loop reruns writer with issues until pass or 3.
4. Agent-as-tool: CDRRootAgent is a tool-calling agent. Its tools are:
   - `find_opportunities` → HTTP P1 `:8081/tools/find_opportunities`
   - `research_opportunity` → ParallelResearch subgraph
   - `generate_proposal` → ProposalGenerationAgent
   - `run_qa` → RefinementLoop
   - `draft_outreach` → OutreachPipeline
   - `persist_and_schedule` → MCP `:8085` (and HTTP P3 `:8082/tools/persist_and_schedule` as fallback)
   ResearchLeadAgent must ALSO call the four research LLMAgents as tools (not one concatenated prompt).

HTTP

POST http://localhost:8084/cdr/run

body: `{ "profile": CreatorProfile, "opportunity_ids": ["..."] }` or `{ "profile": ..., "opportunities": [Opportunity, ...] }` if P1 is down

return: `{ "run_id": "..." }`

GET /cdr/runs/{id}/events  text/event-stream — events: `{ts, agent, pattern, status, artifact_ref, summary, run_id}`

POST /ag-ui  AG-UI protocol stream for CopilotKit (required, not optional)

GET /cdr/runs/{id} full RunState

ContentPackage: week_plan (exactly 3 items: hook, format, platform, posting_slot), hero_script, captions{}, cta, sources[], opportunity_id

OutreachDraft: channel (email|dm|call_script), to, subject, body, status=drafted

BEHAVIOR FOR EACH OPPORTUNITY

1. ResearchLeadAgent plans, then tools the four researchers in parallel.
2. ProposalGenerationAgent writes ContentPackage from ResearchBrief.
3. QualityAssurancePipeline + RefinementLoop. Force at least one fail-then-fix in the Maya demo (unsourced calorie claim) so critique is visible.
4. OutreachPipeline writes email + DM/call script.
5. Call persist_and_schedule. Do not wait for a human.

HITL

None inside your service. If env PAUSE_BEFORE_SEND=true, stop after drafts and emit `awaiting_send`. Default false.

FIXTURES

Until P1/P3 are live, read `demo/maya/opportunities_seed.json` and write artifacts to `demo/outbox/cdr/{run_id}/`. Keep USE_FIXTURES=1 working all week. Scaffold already streams `demo/fixtures/run_events.jsonl`.

DONE WHEN

- 12 LLM agents + 1 Parallel + 3 Sequential + 1 Loop + 1 Custom have real implementations
- A run on Maya seed produces research brief, package, qa trace with a rewrite, email, and call/DM script
- SSE **and** `/ag-ui` events name the agent and the pattern (parallel|sequential|loop|tool)
- `cdr/README.md` documents agent-as-tool, DeepAgents root, and AG-UI

DO NOT

- Own the dashboard (P4 renders AG-UI)
- Send real email unless P3 mock SMTP is ready
- Collapse fact check + voice into one “critic” agent
- Skip MCP and call random URLs from prompts

Stack: LangGraph + DeepAgents + Claude Agent SDK (optional) + AG-UI + MCP + OTEL + Groq/AgentCore. Port 8084. Branch `p2-cdr`.
