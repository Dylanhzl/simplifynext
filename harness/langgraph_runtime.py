"""LangGraph is the primary harness (training: LangGraph and Beyond)."""

from typing import Any

from cdr.graph import compiled


def build_state_graph() -> Any:
    return compiled()
