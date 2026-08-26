# MCP (P1 + P3)

Port **8085**. Model Context Protocol: agents call tools here instead of ad-hoc APIs.

Scaffold: FastAPI `/mcp/tools` + `/mcp/call`. Same tool names if you later swap in FastMCP.

## Tools

P1: `search_web`, `search_local_places`, `fetch_url`, `find_opportunities`

P3: `retrieve_creator_memory`, `save_opportunity`, `get_opportunity`, `update_status`, `persist_and_schedule`, `save_calendar_event`, `send_email`, `read_engagement_inbox`, `write_memory`
