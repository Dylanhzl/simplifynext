from typing import Any

from shared.agent_base import Agent


class PersistAndSchedule(Agent):
    name = "PersistAndSchedule"
    kind = "sequential"

    async def run(self, state: dict[str, Any]) -> dict[str, Any]:
        """Clerk → qualify → follow-up → calendar."""
        raise NotImplementedError("PersistAndSchedule is scaffold-only")
