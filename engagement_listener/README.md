# Engagement Listener (P3)

Port **8083**. Inbound replies and analytics. Classify, update pipeline status, write adapt memory.

Named agents live in `agents/`. Prompt: [`../prompts/P3_pipeline_engagement.md`](../prompts/P3_pipeline_engagement.md).

`POST /engagement/replay_maya_week2` should load `demo/maya/inbox.json` + `analytics_week1.json`.
