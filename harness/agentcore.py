"""AWS Bedrock AgentCore — runtime + memory for deploy / recorded demo.

Local default remains Groq. When AWS credentials exist, swap the LLM and
optionally host the CDR container on AgentCore Runtime.
"""

import os
from typing import Any


def use_agentcore() -> bool:
    return bool(os.getenv("BEDROCK_AGENTCORE_MEMORY_ID") or os.getenv("AWS_ACCESS_KEY_ID"))


def get_model_id() -> str:
    return os.getenv("BEDROCK_MODEL_ID", "anthropic.claude-3-5-sonnet-20241022-v2:0")


def get_memory_id() -> str | None:
    return os.getenv("BEDROCK_AGENTCORE_MEMORY_ID")


def runtime_payload() -> dict[str, Any]:
    return {
        "runtime": "bedrock-agentcore" if use_agentcore() else "local-groq",
        "model_id": get_model_id() if use_agentcore() else os.getenv("GROQ_MODEL"),
        "memory_id": get_memory_id(),
    }
