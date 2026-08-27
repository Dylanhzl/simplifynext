#!/usr/bin/env python3
"""Peek the first AG-UI SSE bytes without waiting for the full fixture replay."""

from __future__ import annotations

import json
import sys
import urllib.request


def main() -> int:
    url = sys.argv[1] if len(sys.argv) > 1 else "http://127.0.0.1:8000/ag-ui"
    body = {"threadId": "uat", "runId": "uat-smoke", "week": 1}
    req = urllib.request.Request(
        url,
        data=json.dumps(body).encode(),
        headers={"Content-Type": "application/json", "Accept": "text/event-stream"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=15) as resp:
        # Read a small prefix only — do not drain the whole SSE stream.
        chunk = resp.read(512).decode("utf-8", errors="replace")
    if "RUN_STARTED" not in chunk and "data:" not in chunk:
        print(f"unexpected first chunk: {chunk[:200]!r}", file=sys.stderr)
        return 1
    print(f"SSE started ({len(chunk)}B peek)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
