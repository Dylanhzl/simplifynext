# Engagement Listener (P3)

Port **8083**. Inbound replies and analytics. Classify, update pipeline status, write adapt memory.

Named agents live in `agents/`. Prompt: [`../prompts/P3_pipeline_engagement.md`](../prompts/P3_pipeline_engagement.md).

`POST /engagement/replay_maya_week2` loads `demo/maya/inbox.json` + `analytics_week1.json`, classifies replies, pushes status updates to Pipeline Manager (`POST :8082/tools/update_status`), and writes memory to both `demo/maya/memory.json` and Pipeline Manager's `memory` table (`POST :8082/pipeline/memory`).

## Agents

| Agent | Kind | Job |
|---|---|---|
| `EngagementIngestAgent` | llm | Normalizes inbound email/analytics/comment payloads. |
| `ReplyClassifierAgent` | llm | Maps a reply to interested / meeting / lost / noise → opportunity status. |
| `PerformanceAdaptAgent` | llm | Reads week-1 analytics, writes wins/losses/next_bias memory. |
