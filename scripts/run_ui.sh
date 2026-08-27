#!/usr/bin/env bash
# Start the CreatorLoop board on :8000.
#
#   ./scripts/run_ui.sh              fixture mode, demo pacing
#   ./scripts/run_ui.sh --live       proxy the CDR agent on :8084
#   DEMO_SPEED=0.6 ./scripts/run_ui.sh   pacing used by demo/DEMO_SCRIPT.md
#
# No pip install. The server is standard library only.
set -euo pipefail
cd "$(dirname "$0")/.."

export USE_FIXTURES="${USE_FIXTURES:-1}"
export DEMO_SPEED="${DEMO_SPEED:-1.0}"
export UI_PORT="${UI_PORT:-8000}"

if [[ "${1:-}" == "--live" ]]; then
  export USE_FIXTURES=0
  echo "live mode: streaming from ${CDR_AGUI_URL:-http://localhost:8084/ag-ui}"
  echo "(falls back to fixtures if the CDR agent does not answer)"
fi

exec python3 ui_client/server.py
