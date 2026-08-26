# Engagement Listener (P3)

Port **8083**. Inbound replies and analytics. Classify, update pipeline status, write adapt memory.

## Agents

LLM: `EngagementIngestAgent`, `ReplyClassifierAgent`, `PerformanceAdaptAgent`

`POST /engagement/replay_maya_week2` loads `demo/maya/inbox.json` + `analytics_week1.json`, moves Laksa Lab to **engaged**, and writes `demo/maya/memory.json` (noodles win, dessert loses).
