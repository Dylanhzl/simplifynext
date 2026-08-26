"""Feature flags from .env. Read these, do not scatter os.getenv across services."""

from __future__ import annotations

import os

_TRUE = {"1", "true", "yes", "on"}


def _flag(name: str, default: str) -> bool:
    return os.getenv(name, default).strip().lower() in _TRUE


def use_fixtures() -> bool:
    """Serve demo/maya seed data instead of live tools. Keep on until day 5."""
    return _flag("USE_FIXTURES", "1")


def pause_before_send() -> bool:
    """Human-in-the-loop gate before outreach goes out. Demo default: off."""
    return _flag("PAUSE_BEFORE_SEND", "0")
