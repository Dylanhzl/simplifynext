from typing import Any

from cdr.agents._util import ping, with_span
from cdr.llm import complete_json
from harness.claude_agent import run_claude_specialist
from shared.agent_base import Agent
from shared.schemas import QAVerdict


class FactCheckerAgent(Agent):
    name = "FactCheckerAgent"
    kind = "llm"

    async def run(self, state: dict[str, Any]) -> dict[str, Any]:
        with with_span(self.name, self.kind, state):
            pkg = state.get("package") or {}
            script = str(pkg.get("hero_script", ""))
            ping(state, self.name, "llm", "Structured pass/fail on claims.")
            data = await run_claude_specialist(
                f"Fact-check this script. JSON {{verdict, issues, must_fix}}.\n{script}"
            )
            if not data:
                data = await complete_json(
                    "You are FactCheckerAgent. Return {verdict: pass|fail, issues[], must_fix[]}. "
                    "Fail unsourced calorie or health claims.",
                    f"hero_script={script}\nsources={pkg.get('sources')}",
                    agent=self.name,
                )
            iteration = int(state.get("iteration") or 1)
            verdict = QAVerdict(
                agent=self.name,
                verdict="fail" if str(data.get("verdict", "fail")).lower() == "fail" else "pass",
                issues=list(data.get("issues") or []),
                must_fix=list(data.get("must_fix") or []),
                iteration=iteration,
            )
            state.setdefault("qa", []).append(verdict.model_dump())
            state["must_fix"] = verdict.must_fix
            state["fact_pass"] = verdict.verdict == "pass"
            ping(
                state,
                self.name,
                "loop",
                f"{verdict.verdict}: {verdict.must_fix or 'clean'}",
                status="fail" if verdict.verdict == "fail" else "ok",
                artifact_ref="QAVerdict",
            )
        return state
