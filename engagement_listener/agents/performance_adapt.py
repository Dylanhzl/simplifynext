from typing import Any

from shared.agent_base import Agent


class PerformanceAdaptAgent(Agent):
    name = "PerformanceAdaptAgent"
    kind = "llm"

    async def run(self, state: dict[str, Any]) -> dict[str, Any]:
        """Write memory for the next CDR run."""
        posts = state.get("posts", [])
        if not posts:
            state["memory"] = {"wins": [], "losses": [], "next_bias": []}
            return state

        ranked = sorted(posts, key=lambda p: p.get("views", 0), reverse=True)
        best = ranked[0]
        worst = ranked[-1]

        wins = [
            f"{best['title']} outperformed ({best.get('views', 0):,} views, "
            f"{best.get('saves', 0):,} saves)"
        ]
        losses = [
            f"{worst['title']} underperformed ({worst.get('views', 0):,} views, "
            f"{worst.get('avg_watch_pct', 0)}% watch)"
        ]
        next_bias = [f"prefer content like '{best['title']}' over '{worst['title']}' formats"]

        state["memory"] = {"wins": wins, "losses": losses, "next_bias": next_bias}
        return state
