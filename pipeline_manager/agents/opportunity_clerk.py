from typing import Any

from pipeline_manager import db
from shared.agent_base import Agent
from shared.agent_util import ping, with_span
from shared.llm import complete_json, seed_opportunities


def _oid(state: dict[str, Any]) -> str:
    return str(
        state.get("opportunity_id")
        or (state.get("opportunity") or {}).get("id")
        or (state.get("current") or {}).get("id")
        or (state.get("package") or {}).get("opportunity_id")
        or "unknown"
    )


class OpportunityClerkAgent(Agent):
    name = "OpportunityClerkAgent"
    kind = "llm"

    async def run(self, state: dict[str, Any]) -> dict[str, Any]:
        with with_span(self.name, self.kind, state):
            ping(state, self.name, "llm", "Idempotent upsert.")
            await complete_json(
                "You are OpportunityClerkAgent. Confirm upsert. Return {ok, action}.",
                f"payload_keys={list(state.keys())}",
                agent=self.name,
            )
            oid = _oid(state)
            payload = dict(state.get("opportunity") or state.get("current") or {})
            seed = {o["id"]: o for o in seed_opportunities()}
            if oid in seed:
                merged = dict(seed[oid])
                merged.update({k: v for k, v in payload.items() if v not in (None, "", [], {})})
                payload = merged
            if not payload.get("id"):
                payload = dict(
                    seed.get(oid)
                    or {
                        "id": oid,
                        "title": oid,
                        "type": "brand",
                        "why_now": "",
                        "city": "Singapore",
                        "niche": "singapore hawker food",
                        "score": 80,
                        "source_agent": "OpportunityClerkAgent",
                    }
                )
            for key in ("package", "brief", "outreach", "qa"):
                if state.get(key):
                    db.add_artifact(oid, key, state[key])
                    payload[key] = state[key]
            if state.get("run_id"):
                payload["last_run_id"] = state["run_id"]
            payload.pop("status", None)
            row = db.upsert_opportunity(oid, payload)
            state["opportunity_id"] = oid
            state["opportunity"] = row
            state["clerk"] = {"ok": True, "id": oid}
            ping(state, self.name, "tool", f"Upserted {oid}.", artifact_ref=oid)
        return state
