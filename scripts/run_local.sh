#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
export PYTHONPATH="${PYTHONPATH:-.}"
export USE_FIXTURES="${USE_FIXTURES:-1}"
if [ ! -f .env ]; then
  cp .env.example .env
fi

# Prefer project venv if present
if [ -x .venv/bin/python ]; then
  PY=.venv/bin/python
elif [ -x .venv/Scripts/python.exe ]; then
  PY=.venv/Scripts/python.exe
else
  PY=python
fi

$PY -m uvicorn mcp.server:app --port 8085 --reload &
$PY -m uvicorn opportunity_finder.app:app --port 8081 --reload &
$PY -m uvicorn pipeline_manager.app:app --port 8082 --reload &
$PY -m uvicorn engagement_listener.app:app --port 8083 --reload &
$PY -m uvicorn cdr.app:app --port 8084 --reload &
# P4 board: stdlib server with fixture AG-UI replay (not the thin FastAPI static app)
$PY ui_client/server.py &
echo "UI http://localhost:8000  AG-UI POST :8084/ag-ui  MCP :8085"
echo "Finder :8081  Pipeline :8082  Engagement :8083  CDR :8084"
echo "USE_FIXTURES=$USE_FIXTURES"
wait
