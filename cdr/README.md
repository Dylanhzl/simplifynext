# CDR Agent (P2)

Port **8084**. Content Development Representative. LangGraph graphs, DeepAgents root, `POST /ag-ui`.

Named agents live in `agents/`. AG-UI: `agui.py`. Prompt: [`../prompts/P2_cdr.md`](../prompts/P2_cdr.md).

Scaffold: `POST /cdr/run`, `GET /cdr/runs/{id}`, `GET /cdr/runs/{id}/events` (streams `demo/fixtures/run_events.jsonl`).
