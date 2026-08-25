from datetime import datetime, timezone

from shared.schemas import PatternKind, RunEvent


def now_utc() -> datetime:
    return datetime.now(timezone.utc)


def make_run_event(
    run_id: str,
    agent: str,
    pattern: PatternKind,
    summary: str,
    status: str = "ok",
    artifact_ref: str | None = None,
) -> RunEvent:
    return RunEvent(
        ts=now_utc(),
        agent=agent,
        pattern=pattern,
        status=status,  # type: ignore[arg-type]
        summary=summary,
        artifact_ref=artifact_ref,
        run_id=run_id,
    )
