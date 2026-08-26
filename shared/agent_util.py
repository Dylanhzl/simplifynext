"""OTEL span + run-event ping for named agents outside CDR."""

from __future__ import annotations

from contextlib import contextmanager
from typing import Any

from shared.events import make_run_event
from shared.schemas import PatternKind

try:
    from observability.otel import agent_span as _agent_span
except Exception:  # pragma: no cover

    @contextmanager
    def _agent_span(agent: str, pattern: str, run_id: str = ""):
        yield None


def with_span(agent: str, pattern: str, state: dict[str, Any]):
    return _agent_span(agent, pattern, str(state.get("run_id", "")))


def ping(
    state: dict[str, Any],
    agent: str,
    pattern: str,
    summary: str,
    status: str = "ok",
    artifact_ref: str | None = None,
) -> None:
    try:
        pk = PatternKind(pattern)
    except ValueError:
        pk = PatternKind.custom
    events = state.setdefault("events", [])
    events.append(
        make_run_event(
            str(state.get("run_id", "")),
            agent,
            pk,
            summary,
            status=status,
            artifact_ref=artifact_ref,
        ).model_dump(mode="json")
    )
