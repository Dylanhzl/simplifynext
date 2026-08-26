"""LLM helper for CDR.

Prefers a frozen `shared.llm` client if P1 already landed one.
Otherwise Groq HTTP (openai/gpt-oss-120b JSON mode).
USE_FIXTURES=1 or missing key → deterministic Maya fixtures so the demo never dies.
"""

from __future__ import annotations

import json
import os
import re
from typing import Any

import httpx
from dotenv import load_dotenv

load_dotenv()

USE_FIXTURES = os.getenv("USE_FIXTURES", "1") not in ("0", "false", "False")
GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"
DEFAULT_MODEL = os.getenv("GROQ_MODEL", "openai/gpt-oss-120b")


def _shared_complete():
    try:
        from shared.llm import complete_json  # type: ignore

        return complete_json
    except Exception:
        return None


def _strip_json(text: str) -> dict[str, Any]:
    text = text.strip()
    if text.startswith("```"):
        text = re.sub(r"^```(?:json)?", "", text).removesuffix("```").strip()
    return json.loads(text)


async def complete_json(system: str, user: str, *, agent: str = "") -> dict[str, Any]:
    if USE_FIXTURES or not os.getenv("GROQ_API_KEY"):
        return fixture_json(agent, user)

    shared = _shared_complete()
    if shared is not None:
        result = shared(system, user) if not _is_coro(shared) else await shared(system, user)
        return result if isinstance(result, dict) else _strip_json(str(result))

    headers = {
        "Authorization": f"Bearer {os.getenv('GROQ_API_KEY')}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": DEFAULT_MODEL,
        "messages": [
            {"role": "system", "content": system + "\nReply with a single JSON object only."},
            {"role": "user", "content": user},
        ],
        "temperature": 0.3,
        "response_format": {"type": "json_object"},
    }
    async with httpx.AsyncClient(timeout=60.0) as client:
        r = await client.post(GROQ_URL, headers=headers, json=payload)
        r.raise_for_status()
        content = r.json()["choices"][0]["message"]["content"]
    return _strip_json(content)


def _is_coro(fn: Any) -> bool:
    return getattr(fn, "__code__", None) is not None and bool(fn.__code__.co_flags & 0x80)


def fixture_json(agent: str, user: str) -> dict[str, Any]:
    oid = "opp-laksa-weeknight"
    if "opp-brand-gap-laksa-lab" in user:
        oid = "opp-brand-gap-laksa-lab"
    if agent == "ResearchLeadAgent":
        return {
            "plan": [
                "audience",
                "peers",
                "presence",
                "pain",
            ],
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
