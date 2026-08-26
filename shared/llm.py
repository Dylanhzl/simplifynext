"""Groq LLM helper. One client for every named agent on the team.

Agents are async, so these are async. Three entry points:

    text   = await chat(system, user)
    data   = await chat_json(system, user)            # -> dict
    model  = await chat_model(System, user, Schema)   # -> validated pydantic

`available()` is False when GROQ_API_KEY is unset. Agents should check it and
fall back to fixtures rather than raising -- the demo must never hard-fail.
"""

from __future__ import annotations

import json
import os
from typing import Any, TypeVar

from dotenv import load_dotenv
from pydantic import BaseModel, ValidationError

load_dotenv()

T = TypeVar("T", bound=BaseModel)

DEFAULT_MODEL = os.getenv("GROQ_MODEL", "openai/gpt-oss-120b")
MAX_ATTEMPTS = 3


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


async def chat(
    system: str,
    user: str,
    *,
    model: str | None = None,
    temperature: float = 0.3,
    max_tokens: int = 2048,
) -> str:
    """Plain text completion."""
    resp = await _client().chat.completions.create(
        model=model or DEFAULT_MODEL,
        temperature=temperature,
        max_tokens=max_tokens,
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
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
        resp = await _client().chat.completions.create(
            model=model or DEFAULT_MODEL,
            temperature=temperature,
            max_tokens=max_tokens,
            response_format={"type": "json_object"},
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
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
