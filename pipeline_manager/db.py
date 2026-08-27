"""SQLite persistence for Pipeline Manager. Single writer: this service."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import aiosqlite

from shared.events import now_utc

DB_PATH = Path(__file__).resolve().parent / "pipeline.db"

_SCHEMA = """
CREATE TABLE IF NOT EXISTS opportunities (
    id TEXT PRIMARY KEY,
    record TEXT NOT NULL,
    status TEXT NOT NULL,
    qualification TEXT,
    updated_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS artifacts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    opportunity_id TEXT,
    kind TEXT NOT NULL,
    record TEXT NOT NULL,
    created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS calendar_events (
    id TEXT PRIMARY KEY,
    opportunity_id TEXT,
    slot TEXT NOT NULL,
    kind TEXT NOT NULL,
    title TEXT NOT NULL,
    created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS memory (
    id INTEGER PRIMARY KEY CHECK (id = 1),
    wins TEXT NOT NULL,
    losses TEXT NOT NULL,
    next_bias TEXT NOT NULL,
    updated_at TEXT NOT NULL
);
"""


def _now() -> str:
    return now_utc().isoformat()


async def init_db() -> None:
    async with aiosqlite.connect(DB_PATH) as db:
        await db.executescript(_SCHEMA)
        await db.commit()


async def upsert_opportunity(record: dict[str, Any]) -> dict[str, Any]:
    oid = record["id"]
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute(
            "SELECT record, status, qualification FROM opportunities WHERE id = ?", (oid,)
        )
        row = await cursor.fetchone()
        if row is not None:
            merged = json.loads(row[0])
            merged.update(record)
            record = merged
            status = record.get("status") or row[1] or "new"
            qualification = row[2]
        else:
            status = record.get("status", "new")
            qualification = None
        record["status"] = status
        await db.execute(
            "INSERT INTO opportunities (id, record, status, qualification, updated_at) "
            "VALUES (?, ?, ?, ?, ?) "
            "ON CONFLICT(id) DO UPDATE SET record=excluded.record, status=excluded.status, "
            "updated_at=excluded.updated_at",
            (oid, json.dumps(record), status, qualification, _now()),
        )
        await db.commit()
    return record


async def get_opportunity(oid: str) -> dict[str, Any] | None:
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute(
            "SELECT record, status, qualification FROM opportunities WHERE id = ?", (oid,)
        )
        row = await cursor.fetchone()
    if row is None:
        return None
    record = json.loads(row[0])
    record["status"] = row[1]
    if row[2]:
        record["qualification"] = row[2]
    return record


async def list_opportunities() -> list[dict[str, Any]]:
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute(
            "SELECT record, status, qualification FROM opportunities ORDER BY updated_at DESC"
        )
        rows = await cursor.fetchall()
    out = []
    for record_json, status, qualification in rows:
        record = json.loads(record_json)
        record["status"] = status
        if qualification:
            record["qualification"] = qualification
        out.append(record)
    return out


async def update_status(oid: str, status: str) -> dict[str, Any] | None:
    record = await get_opportunity(oid)
    if record is None:
        return None
    record["status"] = status
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "UPDATE opportunities SET status = ?, record = ?, updated_at = ? WHERE id = ?",
            (status, json.dumps(record), _now(), oid),
        )
        await db.commit()
    return record


async def set_qualification(oid: str, qualification: str) -> None:
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "UPDATE opportunities SET qualification = ?, updated_at = ? WHERE id = ?",
            (qualification, _now(), oid),
        )
        await db.commit()


async def save_artifact(opportunity_id: str | None, kind: str, record: dict[str, Any]) -> int:
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute(
            "INSERT INTO artifacts (opportunity_id, kind, record, created_at) VALUES (?, ?, ?, ?)",
            (opportunity_id, kind, json.dumps(record), _now()),
        )
        await db.commit()
        return cursor.lastrowid


async def save_calendar_event(event: dict[str, Any]) -> dict[str, Any]:
    eid = event.get("id") or f"cal-{event.get('opportunity_id')}-{event['kind']}-{event['slot']}"
    event = {**event, "id": eid}
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "INSERT INTO calendar_events (id, opportunity_id, slot, kind, title, created_at) "
            "VALUES (?, ?, ?, ?, ?, ?) "
            "ON CONFLICT(id) DO UPDATE SET slot=excluded.slot, title=excluded.title",
            (
                eid,
                event.get("opportunity_id"),
                str(event["slot"]),
                event["kind"],
                event.get("title", ""),
                _now(),
            ),
        )
        await db.commit()
    return event


async def get_memory() -> dict[str, Any] | None:
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute("SELECT wins, losses, next_bias FROM memory WHERE id = 1")
        row = await cursor.fetchone()
    if row is None:
        return None
    wins, losses, next_bias = row
    return {"wins": json.loads(wins), "losses": json.loads(losses), "next_bias": json.loads(next_bias)}


async def write_memory(memory: dict[str, Any]) -> dict[str, Any]:
    normalized = {
        "wins": memory.get("wins", []),
        "losses": memory.get("losses", []),
        "next_bias": memory.get("next_bias", []),
    }
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "INSERT INTO memory (id, wins, losses, next_bias, updated_at) VALUES (1, ?, ?, ?, ?) "
            "ON CONFLICT(id) DO UPDATE SET wins=excluded.wins, losses=excluded.losses, "
            "next_bias=excluded.next_bias, updated_at=excluded.updated_at",
            (
                json.dumps(normalized["wins"]),
                json.dumps(normalized["losses"]),
                json.dumps(normalized["next_bias"]),
                _now(),
            ),
        )
        await db.commit()
    return normalized
