"""SQLite store for opportunities, artifacts, calendar, memory."""

from __future__ import annotations

import json
import sqlite3
import threading
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

DB_PATH = Path(__file__).resolve().parents[1] / "demo" / "maya" / "pipeline.db"
MEMORY_PATH = Path(__file__).resolve().parents[1] / "demo" / "maya" / "memory.json"

_lock = threading.Lock()
_init = False

ALLOWED_STATUS = {
    "new": {"researched", "packaged", "outreached", "engaged", "meeting", "won", "lost"},
    "researched": {"packaged", "outreached", "engaged", "lost"},
    "packaged": {"outreached", "engaged", "lost"},
    "outreached": {"engaged", "meeting", "lost"},
    "engaged": {"meeting", "won", "lost"},
    "meeting": {"won", "lost"},
    "won": set(),
    "lost": set(),
}


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def connect() -> sqlite3.Connection:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(DB_PATH), check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


def init() -> None:
    global _init
    with _lock:
        if _init:
            return
        conn = connect()
        try:
            conn.executescript(
                """
                CREATE TABLE IF NOT EXISTS opportunities (
                    id TEXT PRIMARY KEY,
                    payload TEXT NOT NULL,
                    status TEXT NOT NULL DEFAULT 'new',
                    qualification TEXT,
                    updated_at TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS artifacts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    opportunity_id TEXT NOT NULL,
                    kind TEXT NOT NULL,
                    payload TEXT NOT NULL,
                    created_at TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS calendar_events (
                    id TEXT PRIMARY KEY,
                    opportunity_id TEXT NOT NULL,
                    slot TEXT NOT NULL,
                    kind TEXT NOT NULL,
                    title TEXT NOT NULL,
                    payload TEXT
                );
                CREATE TABLE IF NOT EXISTS memory (
                    id INTEGER PRIMARY KEY CHECK (id = 1),
                    wins TEXT NOT NULL DEFAULT '[]',
                    losses TEXT NOT NULL DEFAULT '[]',
                    next_bias TEXT NOT NULL DEFAULT '[]',
                    updated_at TEXT NOT NULL
                );
                """
            )
            conn.commit()
        finally:
            conn.close()
        _init = True


def upsert_opportunity(oid: str, payload: dict[str, Any], status: str | None = None) -> dict[str, Any]:
    init()
    body = dict(payload)
    body["id"] = oid
    with _lock:
        conn = connect()
        try:
            row = conn.execute("SELECT status, payload FROM opportunities WHERE id = ?", (oid,)).fetchone()
            if row:
                existing = json.loads(row["payload"])
                existing.update(body)
                next_status = status or row["status"] or existing.get("status") or "new"
                existing["status"] = next_status
                conn.execute(
                    "UPDATE opportunities SET payload = ?, status = ?, updated_at = ? WHERE id = ?",
                    (json.dumps(existing, default=str), next_status, _now(), oid),
                )
                out = existing
            else:
                next_status = status or body.get("status") or "new"
                body["status"] = next_status
                conn.execute(
                    "INSERT INTO opportunities (id, payload, status, updated_at) VALUES (?, ?, ?, ?)",
                    (oid, json.dumps(body, default=str), next_status, _now()),
                )
                out = body
            conn.commit()
            return out
        finally:
            conn.close()


def set_qualification(oid: str, label: str, reason: str = "") -> None:
    init()
    with _lock:
        conn = connect()
        try:
            conn.execute(
                "UPDATE opportunities SET qualification = ?, updated_at = ? WHERE id = ?",
                (json.dumps({"label": label, "reason": reason}), _now(), oid),
            )
            conn.commit()
        finally:
            conn.close()


def set_status(oid: str, status: str) -> dict[str, Any]:
    init()
    with _lock:
        conn = connect()
        try:
            row = conn.execute("SELECT status, payload FROM opportunities WHERE id = ?", (oid,)).fetchone()
            if not row:
                return {"ok": False, "error": "not found", "id": oid}
            current = row["status"] or "new"
            allowed = ALLOWED_STATUS.get(current, set())
            if status != current and status not in allowed:
                # still apply for demo if jumping forward from missing prior steps
                if status not in {"new", "researched", "packaged", "outreached", "engaged", "meeting", "won", "lost"}:
                    return {"ok": False, "error": "invalid status", "id": oid, "from": current}
            payload = json.loads(row["payload"])
            payload["status"] = status
            conn.execute(
                "UPDATE opportunities SET status = ?, payload = ?, updated_at = ? WHERE id = ?",
                (status, json.dumps(payload, default=str), _now(), oid),
            )
            conn.commit()
            return {"ok": True, "id": oid, "status": status, "from": current}
        finally:
            conn.close()


def add_artifact(oid: str, kind: str, payload: Any) -> None:
    init()
    with _lock:
        conn = connect()
        try:
            conn.execute(
                "INSERT INTO artifacts (opportunity_id, kind, payload, created_at) VALUES (?, ?, ?, ?)",
                (oid, kind, json.dumps(payload, default=str), _now()),
            )
            conn.commit()
        finally:
            conn.close()


def save_calendar_event(event: dict[str, Any]) -> dict[str, Any]:
    init()
    eid = str(event.get("id") or f"cal-{event.get('opportunity_id', 'x')}-{event.get('kind', 'post')}")
    event = {**event, "id": eid}
    with _lock:
        conn = connect()
        try:
            conn.execute(
                """
                INSERT INTO calendar_events (id, opportunity_id, slot, kind, title, payload)
                VALUES (?, ?, ?, ?, ?, ?)
                ON CONFLICT(id) DO UPDATE SET
                    slot = excluded.slot,
                    kind = excluded.kind,
                    title = excluded.title,
                    payload = excluded.payload
                """,
                (
                    eid,
                    str(event.get("opportunity_id") or ""),
                    str(event.get("slot") or ""),
                    str(event.get("kind") or "post"),
                    str(event.get("title") or ""),
                    json.dumps(event, default=str),
                ),
            )
            conn.commit()
            return event
        finally:
            conn.close()


def get_opportunity(oid: str) -> dict[str, Any] | None:
    init()
    conn = connect()
    try:
        row = conn.execute(
            "SELECT payload, status, qualification FROM opportunities WHERE id = ?",
            (oid,),
        ).fetchone()
        if not row:
            return None
        data = json.loads(row["payload"])
        data["status"] = row["status"]
        if row["qualification"]:
            data["qualification"] = json.loads(row["qualification"])
        return data
    finally:
        conn.close()


def list_opportunities() -> list[dict[str, Any]]:
    init()
    conn = connect()
    try:
        rows = conn.execute("SELECT payload, status, qualification FROM opportunities ORDER BY updated_at DESC").fetchall()
        out = []
        for row in rows:
            data = json.loads(row["payload"])
            data["status"] = row["status"]
            if row["qualification"]:
                data["qualification"] = json.loads(row["qualification"])
            out.append(data)
        return out
    finally:
        conn.close()


def list_calendar() -> list[dict[str, Any]]:
    init()
    conn = connect()
    try:
        rows = conn.execute("SELECT payload FROM calendar_events").fetchall()
        return [json.loads(r["payload"]) for r in rows]
    finally:
        conn.close()


def write_memory(wins: list[str], losses: list[str], next_bias: list[str]) -> dict[str, Any]:
    init()
    payload = {"wins": wins, "losses": losses, "next_bias": next_bias}
    MEMORY_PATH.write_text(json.dumps(payload, indent=2))
    with _lock:
        conn = connect()
        try:
            conn.execute(
                """
                INSERT INTO memory (id, wins, losses, next_bias, updated_at)
                VALUES (1, ?, ?, ?, ?)
                ON CONFLICT(id) DO UPDATE SET
                    wins = excluded.wins,
                    losses = excluded.losses,
                    next_bias = excluded.next_bias,
                    updated_at = excluded.updated_at
                """,
                (json.dumps(wins), json.dumps(losses), json.dumps(next_bias), _now()),
            )
            conn.commit()
        finally:
            conn.close()
    try:
        from harness.agentcore import put_memory

        put_memory(payload)
    except Exception:
        pass
    return payload


def read_memory() -> dict[str, Any]:
    init()
    conn = connect()
    try:
        row = conn.execute("SELECT wins, losses, next_bias FROM memory WHERE id = 1").fetchone()
        if row:
            return {
                "wins": json.loads(row["wins"] or "[]"),
                "losses": json.loads(row["losses"] or "[]"),
                "next_bias": json.loads(row["next_bias"] or "[]"),
            }
    finally:
        conn.close()
    if MEMORY_PATH.exists():
        return json.loads(MEMORY_PATH.read_text())
    return {"wins": [], "losses": [], "next_bias": []}
