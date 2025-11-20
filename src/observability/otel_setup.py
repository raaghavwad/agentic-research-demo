"""Utilities to wire OpenTelemetry tracing for the demo app."""

from __future__ import annotations

from opentelemetry import trace
from opentelemetry.exporter.jaeger.thrift import JaegerExporter
from opentelemetry.instrumentation.requests import RequestsInstrumentor
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor


def init_tracer(service_name: str = "agentic-research-demo") -> trace.Tracer:
    """Return a tracer instance configured with a Jaeger exporter.

    This helper centralizes the boilerplate so that future blog readers can
    copy/paste the setup and focus on the fun multi-agent logic.
    """

    # Define resource attributes so Jaeger can label spans by logical service.
    resource = Resource(attributes={"service.name": service_name})

    # Use the batch span processor for lower overhead vs. synchronous emitting.
    tracer_provider = TracerProvider(resource=resource)
    span_processor = BatchSpanProcessor(
        JaegerExporter(
            agent_host_name="localhost",
            agent_port=6831,
        )
    )
    tracer_provider.add_span_processor(span_processor)

    # Register the provider globally so instrumentation picks it up automatically.
    trace.set_tracer_provider(tracer_provider)

    # TODO: Allow configurable service names + exporters via env vars / CLI flags.
    return trace.get_tracer(service_name)


def init_http_instrumentation() -> None:
    """Instrument the `requests` library so outbound HTTP calls emit spans."""

    # A single call instruments every future `requests` usage in the process.
    RequestsInstrumentor().instrument()

    # TODO: Add idempotency guards if this gets called multiple times in the future.
