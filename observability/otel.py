from __future__ import annotations

import os
from contextlib import contextmanager

from opentelemetry import trace
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor, ConsoleSpanExporter

_provider: TracerProvider | None = None


def setup_tracing(service_name: str) -> None:
    """OTEL from the kick-off stack. Console exporter locally; OTLP if endpoint set."""
    global _provider
    if _provider is not None:
        return
    resource = Resource.create({"service.name": service_name})
    provider = TracerProvider(resource=resource)
    provider.add_span_processor(BatchSpanProcessor(ConsoleSpanExporter()))
    endpoint = os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT")
    if endpoint:
        try:
            from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter

            provider.add_span_processor(BatchSpanProcessor(OTLPSpanExporter(endpoint=endpoint)))
        except Exception:
            pass
    trace.set_tracer_provider(provider)
    _provider = provider


def tracer():
    return trace.get_tracer("creatorloop")


@contextmanager
def agent_span(agent: str, pattern: str, run_id: str = ""):
    setup_tracing(os.getenv("OTEL_SERVICE_NAME", "creatorloop"))
    with tracer().start_as_current_span(agent) as span:
        span.set_attribute("agent.name", agent)
        span.set_attribute("agent.pattern", pattern)
        span.set_attribute("run.id", run_id)
        yield span
