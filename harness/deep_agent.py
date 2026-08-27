"""DeepAgents job: long-horizon CDRRootAgent. Runtime is LangGraph in cdr.graph."""

from typing import Any


def create_cdr_deep_agent() -> Any:
    from cdr.graph import run_campaign

    return run_campaign
