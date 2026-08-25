"""Base class for every named agent. Fill in `run`; do not rename classes."""

from __future__ import annotations

from typing import Any


class Agent:
    name: str = "Agent"
    kind: str = "llm"

    async def run(self, state: dict[str, Any]) -> dict[str, Any]:
        raise NotImplementedError(f"{self.name} is scaffold-only. Implement in your service.")
