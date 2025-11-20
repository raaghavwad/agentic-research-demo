"""DatabaseAgent helps narrate Oracle-backed insights with tracing."""

from __future__ import annotations

from typing import List

from opentelemetry import trace

from services.db_client import OracleDBClient


class DatabaseAgent:
    """Translate database rows into friendly text snippets for downstream agents."""

    def __init__(self, db_client: OracleDBClient) -> None:
        """Store the Oracle client so we can delegate SQL work to it."""
        self._db_client = db_client

    def run(self, topic: str) -> str:
        """Fetch trend rows for a topic and format them as human-readable text."""
        tracer = trace.get_tracer(__name__)

        with tracer.start_as_current_span("db_agent.run") as span:
            span.set_attribute("topic", topic)

            rows = self._db_client.query_trends(topic)

            # Convert each dictionary into a line so presenters can read the output aloud.
            lines = [f"{row['year']}: {row['trend']}" for row in rows]

            span.set_attribute("result.lines", len(lines))

            # Returning a newline-delimited snippet keeps the CLI/console output clean.
            return "\n".join(lines)

