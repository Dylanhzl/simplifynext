from typing import Any

from cdr.agents._util import ping, with_span
from cdr.llm import complete_json
from shared.agent_base import Agent


class DraftWriterAgent(Agent):
    name = "DraftWriterAgent"
    kind = "llm"

    async def run(self, state: dict[str, Any]) -> dict[str, Any]:
        with with_span(self.name, self.kind, state):
            ping(state, self.name, "loop", "Rewrite package from QA issues.")
            pkg = dict(state.get("package") or {})
            data = await complete_json(
                "You are DraftWriterAgent. Rewrite hero_script/captions/cta/sources. "
                "Remove unsourced calorie claims. Keep Maya voice and named ingredients. JSON only.",
                f"package={pkg}\nmust_fix={state.get('must_fix')}\nrewrite=true",
                agent=self.name,
            )
            pkg["hero_script"] = data.get("hero_script", pkg.get("hero_script"))
            pkg["captions"] = data.get("captions", pkg.get("captions"))
            pkg["cta"] = data.get("cta", pkg.get("cta"))
            pkg["sources"] = data.get("sources", pkg.get("sources") or [])
            state["package"] = pkg
            ping(state, self.name, "loop", "Rewrite applied.", artifact_ref="ContentPackage")
        return state
