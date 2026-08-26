from typing import Any

from cdr.agents._util import ping, with_span
from cdr.llm import complete_json
from shared.agent_base import Agent
from shared.schemas import QAVerdict


class VoiceCritiqueAgent(Agent):
    name = "VoiceCritiqueAgent"
    kind = "llm"

    async def run(self, state: dict[str, Any]) -> dict[str, Any]:
        with with_span(self.name, self.kind, state):
            ping(state, self.name, "llm", "Structured pass/fail on brand voice.")
            pkg = state.get("package") or {}
            profile = state.get("profile") or {}
            data = await complete_json(
                "You are VoiceCritiqueAgent. Return {verdict: pass|fail, issues[], must_fix[]}. "
                "Maya: warm, practical, named ingredient. Fail generic influencer voice.",
                f"voice={profile.get('brand_voice')}\nscript={pkg.get('hero_script')}",
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
            state["voice_pass"] = verdict.verdict == "pass"
            if verdict.must_fix:
                state.setdefault("must_fix", []).extend(verdict.must_fix)
            ping(
                state,
                self.name,
                "loop",
                f"{verdict.verdict}: {verdict.issues or 'voice ok'}",
                status="fail" if verdict.verdict == "fail" else "ok",
                artifact_ref="QAVerdict",
            )
        return state
