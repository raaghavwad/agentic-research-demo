"""Demo-friendly helper that fakes a web search + summarization pipeline."""

from __future__ import annotations

import requests
from opentelemetry import trace


def web_search_and_summarize(query: str) -> str:
    """Perform a placeholder web search call and return a mocked summary."""

    tracer = trace.get_tracer(__name__)

    # Wrap the entire operation in a span so downstream calls nest nicely.
    with tracer.start_as_current_span("web_search_and_summarize") as span:
        span.set_attribute("search.query", query)

        # TODO: Replace with Tavily/SerpAPI/etc. and pass actual API keys.
        try:
            resp = requests.get("https://httpbin.org/json", timeout=10)
            resp.raise_for_status()
            mock_payload = resp.json()
        except requests.RequestException:
            mock_payload = {"results": []}

        results = mock_payload.get("slideshow", {}).get("slides", [])

        # Instead of an LLM, stitch together a simple description.
        summary = f"Found {len(results)} potential leads for '{query}'."
        span.set_attribute("summary.length", len(summary))

        return summary
