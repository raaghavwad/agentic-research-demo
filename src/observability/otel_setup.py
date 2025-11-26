"""Utilities to wire OpenTelemetry tracing for the demo app (Tempo/Grafana)."""

from __future__ import annotations

import os

from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.instrumentation.requests import RequestsInstrumentor
try:  # optional httpx instrumentation; package may not be present in early setups
    from opentelemetry.instrumentation.httpx import HTTPXClientInstrumentor
except ImportError:  # pragma: no cover - graceful degradation
    HTTPXClientInstrumentor = None
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor


def init_tracer(service_name: str = "agentic-research-demo") -> trace.Tracer:
    """Configure OpenTelemetry OTLP exporting (Tempo/Grafana friendly).

    Args:
        service_name: Default logical service name when env var overrides are absent.

    Returns:
        trace.Tracer scoped to the resolved service name.
    """

    resolved_service_name = os.getenv("OTEL_SERVICE_NAME", service_name)
    otlp_endpoint = os.getenv(
        "OTEL_EXPORTER_OTLP_ENDPOINT",
        "http://localhost:4318/v1/traces",
    )
    otlp_headers_raw = os.getenv("OTEL_EXPORTER_OTLP_HEADERS", "")

    headers = {}
    if otlp_headers_raw:
        pairs = [h.strip() for h in otlp_headers_raw.split(",") if h.strip()]
        for pair in pairs:
            if "=" in pair:
                key, value = pair.split("=", 1)
                headers[key.strip()] = value.strip()

    resource = Resource(attributes={"service.name": resolved_service_name})
    tracer_provider = TracerProvider(resource=resource)
    span_processor = BatchSpanProcessor(
        OTLPSpanExporter(
            endpoint=otlp_endpoint,
            headers=headers,
        )
    )
    tracer_provider.add_span_processor(span_processor)

    trace.set_tracer_provider(tracer_provider)
    return trace.get_tracer(resolved_service_name)


_http_instrumented = False

def init_http_instrumentation() -> None:
    """Instrument HTTP client libraries (requests + httpx)."""
    global _http_instrumented
    if _http_instrumented:
        return
    RequestsInstrumentor().instrument()
    if HTTPXClientInstrumentor is not None:
        try:
            HTTPXClientInstrumentor().instrument()
        except Exception:  # pragma: no cover - non-critical failure
            # httpx instrumentation is optional; ignore if it fails.
            pass
    _http_instrumented = True
    # TODO: Add config-driven enable/disable flags.
