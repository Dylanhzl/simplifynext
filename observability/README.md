# OpenTelemetry (all services)

Wrap every named agent `run()` with `agent_span(name, pattern, run_id)` from `otel.py`.

Local: console spans. Set `OTEL_EXPORTER_OTLP_ENDPOINT` to ship traces.

Kick-off stack: **OTEL — Traceability & Observability**.
