"""SearchAgent orchestrates web search + summarization with tracing hooks."""

from __future__ import annotations

from typing import Callable

from opentelemetry import trace

from src.services.web_search import web_search_and_summarize


class SearchAgent:
    """Coordinate the web search workflow with simple dependency injection."""

    def __init__(self, search_fn: Callable[[str], str] = web_search_and_summarize):
        self._search_fn = search_fn

    def run(self, query: str) -> str:
        """Execute the search workflow with OpenTelemetry instrumentation."""
        tracer = trace.get_tracer(__name__)
        with tracer.start_as_current_span("search_agent.run") as span:
            span.set_attribute("query", query)

            result = self._search_fn(query)

            span.set_attribute("result.length", len(result))

            return result
