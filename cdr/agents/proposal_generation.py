from typing import Any

from cdr.agents._util import ping, with_span
from cdr.llm import complete_json
from shared.agent_base import Agent
from shared.schemas import ContentPackage, WeekPlanItem


class ProposalGenerationAgent(Agent):
    name = "ProposalGenerationAgent"
    kind = "llm"

    async def run(self, state: dict[str, Any]) -> dict[str, Any]:
        with with_span(self.name, self.kind, state):
            ping(state, self.name, "llm", "Week plan + hero script + captions + CTA.")
            opp = state.get("current") or {}
            data = await complete_json(
                "You are ProposalGenerationAgent. Return ContentPackage JSON. "
                "week_plan must have exactly 3 items. Include an unsourced calorie claim in hero_script "
                "on first draft so QA can fail once (Maya demo).",
                f"profile={state.get('profile')}\nbrief={state.get('brief')}\nopp={opp}",
                agent=self.name,
            )
            oid = str(opp.get("id") or data.get("opportunity_id") or "")
            plan = [WeekPlanItem.model_validate(x) for x in data.get("week_plan", [])][:3]
            while len(plan) < 3:
                plan.append(
                    WeekPlanItem(
                        hook="follow-up hawker tip",
                        format="talking-head",
                        platform="tiktok",
                        posting_slot="Fri 19:30 SGT",
                    )
                )
            pkg = ContentPackage(
                opportunity_id=oid,
                week_plan=plan,
                hero_script=str(data.get("hero_script", "")),
                captions=dict(data.get("captions") or {}),
                cta=str(data.get("cta", "")),
                sources=list(data.get("sources") or []),
            )
            state["package"] = pkg.model_dump()
            ping(state, self.name, "llm", "Draft package ready.", artifact_ref="ContentPackage")
        return state
