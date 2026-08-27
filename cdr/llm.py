"""CDR LLM helper — re-exports the shared Groq / fixture client."""

from shared.llm import USE_FIXTURES, complete_json, fixture_json

__all__ = ["USE_FIXTURES", "complete_json", "fixture_json"]
