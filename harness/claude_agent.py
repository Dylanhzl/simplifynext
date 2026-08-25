"""Claude Agent SDK path (kick-off harness list).

Use for one specialist (FactCheckerAgent or Outreach) when ANTHROPIC_API_KEY is set.
Otherwise P2 implements the same agent in LangGraph/Groq so the demo never hard-depends on Anthropic.
"""

from typing import Any


async def run_claude_specialist(prompt: str) -> Any:
    raise NotImplementedError("pip install claude-agent-sdk — optional specialist")
