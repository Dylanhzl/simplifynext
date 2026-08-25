# P4 — UI Client + demo story

Copy everything below the line into Cursor as your working prompt.

---

You are P4 on CreatorLoop. You own the dashboard and the hackathon story. HITL is MINIMAL: one **Run campaign** button. The human watches named agents work.

YOUR LANE

- `ui_client/` port 8000 including `ui_client/agui/` (CopilotKit + AG-UI)
- `demo/` Maya persona, seeds, screenshots, video script
- Root `README.md` narrative (keep contracts accurate)

Do not implement LangGraph agents. If backends are down, play fixture events.

AG-UI IS REQUIRED (kick-off stack: “Agentic UI. Exposing tools to agents for dynamic rendering.”)

Do not ship a chatbot-only UI. Connect CopilotKit to `POST http://localhost:8084/ag-ui`. When the agent emits a tool/artifact, render a real component (package card, QA fail/rewrite, email, calendar). Frontend tools are allowed so the agent can *show* a card. Static HTML in `ui_client/static/` is the no-keys fallback only.

UI MUST SHOW

1. Campaign bar: niche, city, profile=Maya, button “Run campaign”. That is the ONLY required human action.
2. Live agent trace: `{agent, pattern, summary}` ticker. Pattern badges: parallel | sequential | loop | tool | custom | llm
3. Opportunity table: type, title, score, status
4. Artifact drawer: research brief, content package, qa verdicts (show fail→rewrite), email, DM/call script
5. Pipeline kanban using P3 statuses
6. Calendar strip for the week
7. Engagement inbox + memory panel (“what we learned”) for week 2

Optional: Pause-before-send toggle default OFF. Stop button.

TECH

1. `ui_client/agui/` — CopilotKit (`@copilotkit/react-core`, `@copilotkit/react-ui`) + `@ag-ui/client`
2. Runtime target: P2 `POST /ag-ui`
3. Keep `ui_client/static/` working with `demo/fixtures/run_events.jsonl` so the story runs with no LLM keys
4. Also show OTEL-friendly agent names and pattern badges on screen

Until `/ag-ui` is live, replay fixture events. Swap on day 5.

MAYA DEMO

Persona is in `demo/maya/profile.json`. Keep `demo/DEMO_SCRIPT.md` to 3:00:

- 0:00 problem (manual grind)
- 0:25 architecture (5 services / ~34 agents / patterns)
- 0:50 click Run campaign, show parallel research
- 1:20 critique fail then rewrite
- 1:40 email + call script auto-sent
- 2:00 pipeline + calendar
- 2:20 week 2 replay: brand replied, memory adapts plan
- 2:45 plan / act / adapt closer

Root README must mention: SimplifyNext problem (plan, act, adapt); STACK.md (MCP, AgentCore, AG-UI, OTEL, LangGraph/DeepAgents/Claude Agent SDK); Groq; how to run.

DONE WHEN

- Fresh clone, fixture mode: UI tells the Maya story with no LLM keys
- Live mode: Run campaign shows AG-UI generative components from P2, not only a ticker
- 3-minute video recorded from this UI
- Judges can understand the system without reading code
- STACK.md items visible in the demo (MCP tools, AG-UI cards, named agents)

DO NOT

- Add multi-step approval wizards
- Hide agent names behind “AI is thinking…”
- Block on P2 quality — fixtures first, swap to live on day 5
- Ship chat-only UI without AG-UI rendering

Port 8000. Branch `p4-ui`. Named agents on screen. Dynamic tool cards.
