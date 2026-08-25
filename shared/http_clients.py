import os

import httpx

OPPORTUNITY_FINDER_URL = os.getenv("OPPORTUNITY_FINDER_URL", "http://localhost:8081")
PIPELINE_MANAGER_URL = os.getenv("PIPELINE_MANAGER_URL", "http://localhost:8082")
ENGAGEMENT_LISTENER_URL = os.getenv("ENGAGEMENT_LISTENER_URL", "http://localhost:8083")
CDR_URL = os.getenv("CDR_URL", "http://localhost:8084")


def client(timeout: float = 30.0) -> httpx.AsyncClient:
    return httpx.AsyncClient(timeout=timeout)


async def find_opportunities(payload: dict) -> dict:
    async with client() as c:
        r = await c.post(f"{OPPORTUNITY_FINDER_URL}/tools/find_opportunities", json=payload)
        r.raise_for_status()
        return r.json()


async def persist_and_schedule(payload: dict) -> dict:
    async with client() as c:
        r = await c.post(f"{PIPELINE_MANAGER_URL}/tools/persist_and_schedule", json=payload)
        r.raise_for_status()
        return r.json()


async def get_memory() -> dict:
    async with client() as c:
        r = await c.get(f"{PIPELINE_MANAGER_URL}/pipeline/memory")
        r.raise_for_status()
        return r.json()
