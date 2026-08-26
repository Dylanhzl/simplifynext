# shared

Frozen contracts. P1 is merge captain.

- `schemas.py` — Pydantic models. If a field is not here, it does not exist.
- `events.py` — `RunEvent` helper
- `http_clients.py` — Finder + Pipeline tool calls
- `ports.py` — 8000 / 8081 / 8082 / 8083 / 8084
- `agent_base.py` — every named agent subclasses `Agent`
- `rag.py` — multi-agent RAG retrieve
- `llm.py` — Groq JSON client + Maya fixtures (`USE_FIXTURES=1`)
- `agent_util.py` — OTEL span + run-event ping
- `cors.py` — permissive CORS for local UI
