"""Root agent orchestrator for the agentic research demo."""

from __future__ import annotations

from opentelemetry import trace

from agents.search_agent import SearchAgent
from agents.db_agent import DatabaseAgent


class RootAgent:
    """Coordinates SearchAgent and DatabaseAgent execution."""

    def __init__(self, search_agent: SearchAgent, db_agent: DatabaseAgent) -> None:
        """Store agent references so we can orchestrate their outputs later."""
        self._search_agent = search_agent
        self._db_agent = db_agent

    def handle_request(self, user_query: str) -> str:
        """Handle the incoming user query (not yet implemented)."""
        tracer = trace.get_tracer(__name__)
        with tracer.start_as_current_span("root_agent.handle_request") as span:
            span.set_attribute("user.query", user_query)

            search_results = self._search_agent.run(user_query)
            db_results = self._db_agent.run(user_query)

            combined = self._combine_results(search_results, db_results)

            span.set_attribute("response.length", len(combined))
            return combined

    def _combine_results(self, search_payload: str, db_payload: str) -> str:
        """Combine agent outputs before returning to the caller."""
        return (
            "=== Web Research Summary ===\n"
            f"{search_payload}\n\n"
            "=== Oracle Trends ===\n"
            f"{db_payload}"
        )
