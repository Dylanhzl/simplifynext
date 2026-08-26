"""Client for the MCP tool server on :8085.

Rule from STACK.md: agents call tools through MCP, never ad-hoc HTTP inside a
prompt. Import this instead of hand-rolling httpx.

    places = await call_tool("search_local_places", {"city": "Singapore"})
    hits   = await search_web("easy laksa recipe singapore")
"""

from __future__ import annotations

import os
from typing import Any

import httpx

MCP_URL = os.getenv("MCP_URL", "http://localhost:8085")


class MCPError(RuntimeError):
    """MCP server unreachable or returned an error."""


async def list_tools() -> list[dict[str, Any]]:
    async with httpx.AsyncClient(timeout=10.0) as c:
        r = await c.get(f"{MCP_URL}/mcp/tools")
        r.raise_for_status()
        return r.json().get("tools", [])


async def call_tool(
    name: str,
    arguments: dict[str, Any] | None = None,
    *,
    timeout: float = 30.0,
) -> Any:
    """Invoke one MCP tool and return its `result` payload.

    Raises MCPError on transport failure so callers can fall back to fixtures.
    """
    payload = {"name": name, "arguments": arguments or {}}
    try:
        async with httpx.AsyncClient(timeout=timeout) as c:
            r = await c.post(f"{MCP_URL}/mcp/call", json=payload)
            r.raise_for_status()
            body = r.json()
    except httpx.HTTPError as exc:
        raise MCPError(f"MCP call {name!r} failed: {exc}") from exc

    if body.get("error"):
        raise MCPError(f"MCP tool {name!r} returned an error: {body['error']}")
    return body.get("result")


# Convenience wrappers -- P1 tools.


async def search_web(query: str, limit: int = 5) -> Any:
    return await call_tool("search_web", {"query": query, "limit": limit})


async def search_local_places(city: str, category: str | None = None) -> Any:
    args: dict[str, Any] = {"city": city}
    if category:
        args["category"] = category
    return await call_tool("search_local_places", args)


async def fetch_url(url: str) -> Any:
    return await call_tool("fetch_url", {"url": url})


async def retrieve_creator_memory(query: str, k: int = 4) -> Any:
    return await call_tool("retrieve_creator_memory", {"query": query, "k": k})
