# Pipeline Manager (P3)

Port **8082**. Persist opportunities and artifacts, qualify, calendar, expose memory for the next CDR run.

Named agents live in `agents/`. Prompt: [`../prompts/P3_pipeline_engagement.md`](../prompts/P3_pipeline_engagement.md).

Persisted to SQLite (`pipeline.db`, gitignored): `opportunities`, `artifacts`, `calendar_events`, `memory`. Keep `/tools/persist_and_schedule` as the agent-as-tool entry for P2.

## Agents

| Agent | Kind | Job |
|---|---|---|
| `OpportunityClerkAgent` | llm | Idempotent upsert of whatever CDR posts, into `opportunities` or `artifacts`. |
| `QualificationAgent` | llm | Labels hot / warm / cold (brand-gap + score ≥ 80, or score ≥ 90, is hot). |
| `FollowUpPlannerAgent` | llm | Suggests next action for the current status; schedules follow-up/meeting slots. |
| `CalendarAssistantAgent` | llm | Proposes 3 posting slots this week (Asia/Singapore, 18:00 SGT). |
| `StatusTrackerAgent` | llm | Only other writer of opportunity status besides the clerk. |
| `PersistAndSchedule` | sequential | Clerk → Qualification → FollowUpPlanner → CalendarAssistant. |
