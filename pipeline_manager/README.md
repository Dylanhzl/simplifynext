# Pipeline Manager (P3)

Port **8082**. Persist opportunities and artifacts, qualify, calendar, expose memory for the next CDR run.

Named agents live in `agents/`. Prompt: [`../prompts/P3_pipeline_engagement.md`](../prompts/P3_pipeline_engagement.md).

Scaffold is in-memory. Replace with SQLite. Keep `/tools/persist_and_schedule` as the agent-as-tool entry for P2.
