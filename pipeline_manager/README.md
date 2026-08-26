# Pipeline Manager (P3)

Port **8082**. Persist opportunities and artifacts, qualify, calendar, expose memory for the next CDR run.

SQLite: `demo/maya/pipeline.db`

## Agents

LLM: `OpportunityClerkAgent`, `QualificationAgent`, `FollowUpPlannerAgent`, `CalendarAssistantAgent`, `StatusTrackerAgent`

Sequential: `PersistAndSchedule` — clerk → qualify → follow-up → calendar → status

Clerk and StatusTracker are the only status writers (`new → researched → packaged → outreached → engaged → meeting → won|lost`).

## HTTP

- `POST /pipeline/upsert`
- `GET /pipeline/opportunities`
- `GET /pipeline/opportunities/{id}`
- `POST /pipeline/calendar`
- `POST /tools/persist_and_schedule`
- `GET /pipeline/memory`
