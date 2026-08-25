#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
export PYTHONPATH="${PYTHONPATH:-.}"
if [ ! -f .env ]; then
  cp .env.example .env
fi
python -m uvicorn mcp.server:app --port 8085 --reload &
python -m uvicorn opportunity_finder.app:app --port 8081 --reload &
python -m uvicorn pipeline_manager.app:app --port 8082 --reload &
python -m uvicorn engagement_listener.app:app --port 8083 --reload &
python -m uvicorn cdr.app:app --port 8084 --reload &
python -m uvicorn ui_client.app:app --port 8000 --reload &
echo "UI http://localhost:8000  AG-UI POST :8084/ag-ui  MCP :8085"
echo "Finder :8081  Pipeline :8082  Engagement :8083  CDR :8084"
wait
