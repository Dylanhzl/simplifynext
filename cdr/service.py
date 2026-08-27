from __future__ import annotations

import json
import os
from pathlib import Path

from cdr.graph import run_campaign
from cdr.runtime import emit_agui, finish, get_run, new_run
from uuid import uuid4

PROFILE = Path(__file__).resolve().parents[1] / "demo" / "maya" / "profile.json"
SEED = Path(__file__).resolve().parents[1] / "demo" / "maya" / "opportunities_seed.json"
OUTBOX = Path(__file__).resolve().parents[1] / "demo" / "outbox" / "cdr"


def profile_from(body: dict) -> dict:
    if isinstance(body.get("profile"), dict):
        return body["profile"]
    if PROFILE.exists():
        return json.loads(PROFILE.read_text())
    return {"id": "maya", "niche": "singapore hawker food", "city": "Singapore"}


def opportunities_from(body: dict) -> list:
    if body.get("opportunities"):
        return list(body["opportunities"])
    ids = set(body.get("opportunity_ids") or [])
    if SEED.exists():
        rows = json.loads(SEED.read_text()).get("opportunities") or []
        if ids:
            return [o for o in rows if o.get("id") in ids]
        return rows
    return []


def start_run(body: dict) -> str:
    run_id = str(uuid4())[:8]
    profile = profile_from(body)
    opps = opportunities_from(body)
    new_run(run_id, str(profile.get("id", "maya")), [o.get("id", "") for o in opps if isinstance(o, dict)])
    return run_id


async def execute_run(run_id: str, body: dict) -> None:
    profile = profile_from(body)
    opps = opportunities_from(body)
    emit_agui(run_id, {"type": "RUN_STARTED", "runId": run_id})
    state = {
        "run_id": run_id,
        "profile": profile,
        "opportunities": opps,
        "pause_before_send": os.getenv("PAUSE_BEFORE_SEND", "0") in ("1", "true", "True")
        or bool(body.get("pause_before_send")),
        "packages": [],
        "outreach": [],
        "qa": [],
    }
    try:
        result = await run_campaign(state)
        dest = OUTBOX / run_id
        dest.mkdir(parents=True, exist_ok=True)
        (dest / "result.json").write_text(json.dumps(result, indent=2, default=str))
        rec = get_run(run_id) or {}
        rec["packages"] = result.get("packages") or []
        rec["outreach"] = result.get("outreach") or []
        rec["qa"] = result.get("qa") or []
    except Exception as exc:
        rec = get_run(run_id) or {}
        rec["status"] = "error"
        rec["error"] = str(exc)
        finish(run_id, {"error": str(exc)})
