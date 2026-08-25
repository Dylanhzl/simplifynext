"""Domain RAG for research agents (kick-off: multi-agent RAG pipelines)."""

from pathlib import Path
from typing import Any

CORPUS = Path(__file__).resolve().parents[1] / "demo" / "maya" / "rag_corpus.json"


def retrieve(query: str, k: int = 4) -> list[dict[str, Any]]:
    """P3 indexes Maya posts + research briefs. P2 research agents call this via MCP retrieve_creator_memory."""
    import json

    if not CORPUS.exists():
        return []
    docs = json.loads(CORPUS.read_text())
    # scaffold: keyword overlap. Replace with embeddings.
    q = query.lower()
    scored = []
    for doc in docs:
        text = (doc.get("text") or "").lower()
        score = sum(1 for w in q.split() if w in text)
        scored.append((score, doc))
    scored.sort(key=lambda x: x[0], reverse=True)
    return [d for s, d in scored[:k] if s > 0] or [d for _, d in scored[:k]]
