"""Domain RAG for research agents (kick-off: multi-agent RAG pipelines)."""

from pathlib import Path
from typing import Any

CORPUS = Path(__file__).resolve().parents[1] / "demo" / "maya" / "rag_corpus.json"


def retrieve(query: str, k: int = 4) -> list[dict[str, Any]]:
    """P3 indexes Maya posts + research briefs. P2 research agents call this via MCP retrieve_creator_memory."""
    import json

    if not CORPUS.exists():
        return []
    data = json.loads(CORPUS.read_text())
    # The corpus file is {corpus_id, description, documents[]}; iterating the
    # object itself yielded its keys (strings) and blew up on doc.get().
    docs = data.get("documents", []) if isinstance(data, dict) else data
    docs = [d for d in docs if isinstance(d, dict)]

    # scaffold: keyword overlap. Replace with embeddings.
    q = query.lower()
    scored = []
    for doc in docs:
        score = sum(1 for w in q.split() if w in _searchable(doc))
        scored.append((score, doc))
    scored.sort(key=lambda x: x[0], reverse=True)
    return [d for s, d in scored[:k] if s > 0] or [d for _, d in scored[:k]]


# Documents carry title/notes, not a single `text` blob - scoring against a
# field that does not exist scored every document zero.
_FIELDS = ("text", "title", "notes", "insight", "summary", "type", "platform")


def _searchable(doc: dict[str, Any]) -> str:
    return " ".join(str(doc.get(f, "")) for f in _FIELDS).lower()
