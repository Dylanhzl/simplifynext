"""Groq LLM helper. One client for every named agent on the team.

Agents are async, so these are async. Three entry points:

    text   = await chat(system, user)
    data   = await chat_json(system, user)            # -> dict
    model  = await chat_model(System, user, Schema)   # -> validated pydantic

`available()` is False when GROQ_API_KEY is unset. Agents should check it and
fall back to fixtures rather than raising -- the demo must never hard-fail.

COMPATIBILITY
-------------
Agents written against the earlier fixture-first API keep working unchanged:

    from shared.llm import USE_FIXTURES, complete_json, fixture_json, seed_opportunities

`complete_json` is a shim over `chat_json`, so those agents inherit the 429
retry and connection-error backoff below for free. New agents should prefer
`chat_model`, which validates output against shared/schemas.py.
"""

from __future__ import annotations

import asyncio
import json
import os
import random
import re
from typing import Any, Awaitable, Callable, TypeVar

from dotenv import load_dotenv
from pydantic import BaseModel, ValidationError

from shared.fixtures import fixture_json, seed_opportunities
from shared.flags import use_fixtures

load_dotenv()

T = TypeVar("T", bound=BaseModel)

# Module-level constant kept for agents that import it directly. Prefer
# shared.flags.use_fixtures(), which re-reads the env instead of freezing it
# at import time.
USE_FIXTURES = use_fixtures()

DEFAULT_MODEL = os.getenv("GROQ_MODEL", "openai/gpt-oss-120b")
FAST_MODEL = os.getenv("GROQ_FAST_MODEL", "openai/gpt-oss-20b")
MAX_ATTEMPTS = 3

# Groq's free tier is 8k tokens/minute. Parallel agent fan-out blows through
# that in one burst, so every call retries on 429 instead of failing the run.
RATE_LIMIT_RETRIES = int(os.getenv("GROQ_RATE_LIMIT_RETRIES", "5"))
_RETRY_HINT = re.compile(r"try again in ([\d.]+)s", re.IGNORECASE)


class LLMError(RuntimeError):
    """Raised when the model could not produce usable output."""


def available() -> bool:
    return bool(os.getenv("GROQ_API_KEY"))


def _client():
    from groq import AsyncGroq

    key = os.getenv("GROQ_API_KEY")
    if not key:
        raise LLMError("GROQ_API_KEY is not set; call available() first")
    return AsyncGroq(api_key=key)


def _retry_delay(exc: Exception, attempt: int) -> float:
    """Groq tells us how long to wait; fall back to exponential backoff."""
    hint = _RETRY_HINT.search(str(exc))
    if hint:
        return min(float(hint.group(1)) + 0.4, 30.0)
    return min(2.0**attempt, 16.0) + random.uniform(0, 0.5)


async def _with_rate_limit_retry(call: Callable[[], Awaitable[Any]]) -> Any:
    """Retry a Groq call through 429s. Raises LLMError once retries run out."""
    from groq import APIConnectionError, InternalServerError, RateLimitError

    last: Exception | None = None
    for attempt in range(RATE_LIMIT_RETRIES):
        try:
            return await call()
        except RateLimitError as exc:
            last = exc
            await asyncio.sleep(_retry_delay(exc, attempt))
        except (APIConnectionError, InternalServerError) as exc:
            last = exc
            await asyncio.sleep(_retry_delay(exc, attempt))

    raise LLMError(f"Groq unavailable after {RATE_LIMIT_RETRIES} retries: {last}")


async def chat(
    system: str,
    user: str,
    *,
    model: str | None = None,
    temperature: float = 0.3,
    max_tokens: int = 2048,
) -> str:
    """Plain text completion."""
    resp = await _with_rate_limit_retry(
        lambda: _client().chat.completions.create(
            model=model or DEFAULT_MODEL,
            temperature=temperature,
            max_tokens=max_tokens,
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
        )
    )
    return (resp.choices[0].message.content or "").strip()


async def chat_json(
    system: str,
    user: str,
    *,
    model: str | None = None,
    temperature: float = 0.2,
    max_tokens: int = 2048,
) -> dict[str, Any]:
    """JSON-mode completion. Retries on unparseable output."""
    system = f"{system}\n\nRespond with a single valid JSON object and nothing else."
    last: Exception | None = None

    for attempt in range(MAX_ATTEMPTS):
        resp = await _with_rate_limit_retry(
            lambda: _client().chat.completions.create(
                model=model or DEFAULT_MODEL,
                temperature=temperature,
                max_tokens=max_tokens,
                response_format={"type": "json_object"},
                messages=[
                    {"role": "system", "content": system},
                    {"role": "user", "content": user},
                ],
            )
        )
        raw = (resp.choices[0].message.content or "").strip()
        try:
            return json.loads(raw)
        except json.JSONDecodeError as exc:
            last = exc
            user = f"{user}\n\nYour previous reply was not valid JSON ({exc}). Return only the JSON object."

    raise LLMError(f"no valid JSON after {MAX_ATTEMPTS} attempts: {last}")


async def chat_model(
    system: str,
    user: str,
    schema: type[T],
    *,
    model: str | None = None,
    temperature: float = 0.2,
    max_tokens: int = 2048,
) -> T:
    """JSON-mode completion validated into a pydantic model from shared.schemas.

    The model sees the real JSON schema, so field names always match the
    frozen contract. Retries feed validation errors back to the model.
    """
    contract = json.dumps(schema.model_json_schema(), indent=2)
    system = f"{system}\n\nMatch this JSON schema exactly:\n{contract}"
    last: Exception | None = None

    for attempt in range(MAX_ATTEMPTS):
        data = await chat_json(
            system, user, model=model, temperature=temperature, max_tokens=max_tokens
        )
        try:
            return schema.model_validate(data)
        except ValidationError as exc:
            last = exc
            user = f"{user}\n\nYour previous reply failed validation:\n{exc}\nFix those fields."

    raise LLMError(f"{schema.__name__} validation failed after {MAX_ATTEMPTS} attempts: {last}")


# --------------------------------------------------------------------------
# Compatibility shim
# --------------------------------------------------------------------------


async def complete_json(system: str, user: str, *, agent: str = "") -> dict[str, Any]:
    """Fixture-first JSON completion. Original signature, hardened internals.

    Behaviour matches the earlier implementation -- fixtures when USE_FIXTURES=1
    or GROQ_API_KEY is missing -- but live calls now route through `chat_json`,
    so they retry through Groq's 8k tokens/minute rate limit instead of raising.

    Falls back to the agent's fixture if the model is unreachable, so a rate
    limit can never take a service down mid-demo.
    """
    if use_fixtures() or not available():
        return fixture_json(agent, user)

    try:
        return await chat_json(system, user)
    except LLMError:
        return fixture_json(agent, user)


__all__ = [
    "USE_FIXTURES",
    "DEFAULT_MODEL",
    "FAST_MODEL",
    "LLMError",
    "available",
    "chat",
    "chat_json",
    "chat_model",
    "complete_json",
    "fixture_json",
    "seed_opportunities",
]
