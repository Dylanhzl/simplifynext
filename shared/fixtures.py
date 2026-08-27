"""Deterministic Maya demo fixtures (USE_FIXTURES=1).

Authored by alric as part of the 34-agent implementation; lifted out of
shared/llm.py so the LLM client and the demo data can evolve separately.
Every named agent has an entry keyed by its class name -- add yours here when
you want a service to demo without burning Groq tokens.

shared/llm.py re-exports `fixture_json` and `seed_opportunities`, so existing
imports keep working:

    from shared.llm import complete_json, fixture_json, seed_opportunities
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

SEED = Path(__file__).resolve().parents[1] / "demo" / "maya" / "opportunities_seed.json"


def seed_opportunities(*source_agents: str) -> list[dict[str, Any]]:
    if not SEED.exists():
        return []
    rows = json.loads(SEED.read_text()).get("opportunities") or []
    if not source_agents:
        return list(rows)
    wanted = set(source_agents)
    return [r for r in rows if r.get("source_agent") in wanted]



def fixture_json(agent: str, user: str) -> dict[str, Any]:
    oid = "opp-laksa-weeknight"
    if "opp-brand-gap-laksa-lab" in user:
        oid = "opp-brand-gap-laksa-lab"

    # --- P1 finder ---
    if agent == "NicheQueryAgent":
        return {
            "queries": [
                "easy laksa weeknight Singapore",
                "leftover stock laksa tiktok",
                "laksa paste brand Singapore short form",
                "katong laksa correct order reel",
                "air fryer otah hostel kitchen",
                "home chendol hawker how to",
                "singapore hawker stall collab",
                "hawker sauce brand weak instagram",
            ]
        }
    if agent == "TrendHarvesterAgent":
        return {"opportunities": seed_opportunities("TrendHarvesterAgent")}
    if agent == "BrandGapAgent":
        return {"opportunities": seed_opportunities("BrandGapAgent")}
    if agent == "CollabScoutAgent":
        return {"opportunities": seed_opportunities("CollabScoutAgent")}
    if agent == "OpportunityClusterAgent":
        return {
            "clusters": [
                {
                    "theme": "weeknight laksa / leftover stock",
                    "ids": ["opp-laksa-weeknight", "opp-brand-gap-laksa-lab"],
                },
                {"theme": "hostel hawker hacks", "ids": ["opp-trend-otah-airfryer"]},
                {"theme": "local stall collab", "ids": ["opp-collab-hawker-auntie"]},
                {"theme": "dessert (weak)", "ids": ["opp-gap-dessert"]},
            ]
        }
    if agent == "OpportunityScorerAgent":
        return {"opportunities": seed_opportunities()}
    if agent == "OpportunityFinderRoot":
        return {"ok": True}

    # --- P3 pipeline ---
    if agent == "OpportunityClerkAgent":
        return {"ok": True, "action": "upsert"}
    if agent == "QualificationAgent":
        blob = user.lower()
        if "brand" in blob and ("laksa lab" in blob or "88" in user or oid.endswith("laksa-lab")):
            return {"label": "hot", "reason": "Brand-gap plus high fit score."}
        if "chendol" in blob or "dessert" in blob or "opp-gap-dessert" in user:
            return {"label": "cold", "reason": "Dessert how-tos underperform in Maya's niche."}
        if "91" in user or "laksa-weeknight" in user:
            return {"label": "hot", "reason": "Top trend, hostel-friendly hawker hack."}
        return {"label": "warm", "reason": "Solid niche fit."}
    if agent == "FollowUpPlannerAgent":
        return {
            "actions": [
                {
                    "when": "+2d",
                    "channel": "email",
                    "note": "If Laksa Lab is silent, nudge with the leftover-stock reel still attached.",
                }
            ],
            "meeting_ask": True,
        }
    if agent == "CalendarAssistantAgent":
        return {
            "slots": [
                {"kind": "post", "weekday": "Tue", "time": "19:30", "title": "Weeknight leftover-stock laksa"},
                {"kind": "post", "weekday": "Thu", "time": "19:30", "title": "Air-fryer otah hostel kitchen"},
                {"kind": "post", "weekday": "Sat", "time": "11:00", "title": "Laksa Lab paste — what I'd buy"},
                {"kind": "followup", "weekday": "Wed", "time": "10:00", "title": "Follow up Laksa Lab"},
            ]
        }
    if agent == "StatusTrackerAgent":
        status = "outreached"
        if "engaged" in user.lower() or "interested" in user.lower():
            status = "engaged"
        elif "meeting" in user.lower():
            status = "meeting"
        elif "lost" in user.lower():
            status = "lost"
        elif "packaged" in user.lower():
            status = "packaged"
        elif "researched" in user.lower():
            status = "researched"
        return {"ok": True, "status": status}

    # --- P3 engagement ---
    if agent == "EngagementIngestAgent":
        return {"ok": True, "normalized": True}
    if agent == "ReplyClassifierAgent":
        blob = user.lower()
        if any(w in blob for w in ("interested", "3-post", "15-min call", "hop on", "loved")):
            return {
                "label": "interested",
                "opportunity_id": "opp-brand-gap-laksa-lab",
                "next_status": "engaged",
            }
        if "unsubscribe" in blob or "not interested" in blob:
            return {"label": "not_interested", "opportunity_id": oid, "next_status": "lost"}
        if "meeting" in blob or "calendar" in blob:
            return {"label": "meeting", "opportunity_id": oid, "next_status": "meeting"}
        return {"label": "noise", "opportunity_id": None, "next_status": None}
    if agent == "PerformanceAdaptAgent":
        return {
            "wins": [
                "Noodle / hawker how-tos (weekday laksa) win on saves and watch time.",
            ],
            "losses": [
                "Dessert how-tos (home chendol) drop off; low watch time.",
            ],
            "next_bias": [
                "Prefer hawker how-tos and leftover-stock angles.",
                "Deprioritize dessert how-tos.",
                "Keep Laksa Lab brand-gap hot.",
            ],
        }

    # --- P2 CDR ---
    if agent == "ResearchLeadAgent":
        return {
            "plan": ["audience", "peers", "presence", "pain"],
            "why": "Maya's saves cluster on hostel-friendly hawker hacks.",
        }
    if agent == "AudienceResearchAgent":
        return {
            "audience_insight": "20–30s in SG want weeknight hawker flavour without a 40-min simmer. High save intent on 'leftover stock' hacks."
        }
    if agent == "PeerCreatorAnalysisAgent":
        return {
            "peer_moves": "Peer hawker accounts over-index tourist Katong shots. Gap: hostel kitchen / leftover stock angles."
        }
    if agent == "PlatformPresenceAgent":
        return {
            "platform_presence": "Laksa Lab has a shopfront and almost no short-form. Maya can own the recipe slot they are not filling."
        }
    if agent == "PainPointAgent":
        return {
            "pain_points": "Long cook time, fear of 'inauthentic' laksa, unsourced health claims that get Maya in trouble."
        }
    if agent == "ProposalGenerationAgent":
        return {
            "opportunity_id": oid,
            "week_plan": [
                {
                    "hook": "Weeknight laksa from leftover stock in 15 min",
                    "format": "talking-head + overhead cook",
                    "platform": "tiktok",
                    "posting_slot": "Tue 19:30 SGT",
                },
                {
                    "hook": "Air-fryer otah for hostel kitchens",
                    "format": "quick cuts",
                    "platform": "tiktok",
                    "posting_slot": "Thu 19:30 SGT",
                },
                {
                    "hook": "Laksa Lab paste — what I'd actually buy",
                    "format": "shelf + cook",
                    "platform": "instagram",
                    "posting_slot": "Sat 11:00 SGT",
                },
            ],
            "hero_script": (
                "Leftover chicken stock in the fridge? That's a 15-minute laksa, not a sad soup. "
                "I'm Maya. This is the Katong-style coconut hit without the queue. "
                "This bowl is 320 calories so it's 'healthy'. Grab the rempah, leftover stock, "
                "and a handful of bee hoon. Tell me who still gates laksa behind a Sunday."
            ),
            "captions": {
                "tiktok": "15-min leftover-stock laksa. Katong vibe, hostel kitchen. #sgfood",
                "instagram": "Weeknight laksa from leftover stock. Named ingredient: rempah + bee hoon.",
            },
            "cta": "Save this for the next leftover-stock night. Brand friends: Laksa Lab, DMs open.",
            "sources": [],
        }
    if agent == "DraftWriterAgent":
        return {
            "hero_script": (
                "Leftover chicken stock in the fridge? That's a 15-minute laksa, not a sad soup. "
                "I'm Maya. Katong-style coconut hit, hostel stove, no queue. "
                "Rempah, leftover stock, bee hoon. I don't do mystery calorie claims — just a bowl that tastes like the stall. "
                "Tell me who still gates laksa behind a Sunday."
            ),
            "captions": {
                "tiktok": "15-min leftover-stock laksa. Rempah + bee hoon. #sgfood",
                "instagram": "Weeknight laksa. Named ingredients only. No unsourced health claims.",
            },
            "cta": "Save this. Laksa Lab — if you want the paste in shot, say the word.",
            "sources": ["Maya kitchen test", "Katong-style method (home)"],
        }
    if agent == "FactCheckerAgent":
        unsourced = ("320 calories" in user) or (
            "calorie" in user.lower() and "I don't do mystery calorie" not in user
        )
        if unsourced:
            return {
                "verdict": "fail",
                "issues": ["Unsourced calorie claim (320 calories)."],
                "must_fix": ["cite or remove calories"],
            }
        return {"verdict": "pass", "issues": [], "must_fix": []}
    if agent == "VoiceCritiqueAgent":
        if "Maya" in user and ("rempah" in user.lower() or "bee hoon" in user.lower() or "laksa" in user.lower()):
            return {"verdict": "pass", "issues": [], "must_fix": []}
        return {
            "verdict": "fail",
            "issues": ["Voice missing named ingredient / Maya warmth."],
            "must_fix": ["name rempah or stall-style ingredient"],
        }
    if agent == "OutreachStrategyAgent":
        return {
            "channel_order": ["email", "dm", "call_script"],
            "angle": "Maya fills Laksa Lab's missing short-form with a leftover-stock weeknight recipe.",
            "to": "hello@laksalab.sg",
        }
    if agent == "OutreachScriptAgent":
        return {
            "channel": "call_script",
            "to": "Laksa Lab",
            "subject": "",
            "body": (
                "30s: Hi, I'm Maya — hawker-style TikTok in Singapore. "
                "Your paste is strong, your short-form is quiet. "
                "I have a 15-min leftover-stock laksa ready. 3-post trial next month?"
            ),
        }
    if agent == "PitchEmailAgent":
        return {
            "channel": "email",
            "to": "hello@laksalab.sg",
            "subject": "Maya x Laksa Lab — 3-post leftover-stock laksa trial",
            "body": (
                "Hi Laksa Lab team,\n\n"
                "I'm Maya Tan. I cook hawker-style food for 20–30s in Singapore who miss stall flavour on a weeknight. "
                "Your paste is the product; the feed is the gap. I'd like a 3-post trial: leftover-stock laksa, "
                "hostel otah, and an honest 'what I'd actually buy' shelf clip. No unsourced health claims.\n\n"
                "15 min call this week?\nMaya"
            ),
        }
    if agent == "CDRRootAgent":
        return {
            "plan": [
                "select top opportunities",
                "research in parallel",
                "package + critique loop",
                "outreach",
                "persist_and_schedule",
            ],
            "selected_ids": ["opp-laksa-weeknight", "opp-brand-gap-laksa-lab"],
        }
    return {"ok": True, "agent": agent}
