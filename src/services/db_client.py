"""Demo-friendly Oracle DB client that currently mocks SQLcl responses."""

from __future__ import annotations

from typing import List, Dict

from opentelemetry import trace

class OracleDBClient:
    """Wraps SQLcl MCP interactions for Oracle queries."""
    def __init__(self, sqlcl_endpoint: str) -> None:
        # Store the MCP endpoint so a future implementation can make HTTP/CLI calls.
        self.sqlcl_endpoint = sqlcl_endpoint

    def query_trends(self, topic: str) -> List[Dict]:
        """Return mocked rows describing Oracle tech trends for a given topic."""

        tracer = trace.get_tracer(__name__)
        with tracer.start_as_current_span("oracle.query_trends") as span:
            span.set_attribute("db.topic", topic)

            # TODO: Replace this mocked data with a real SQLcl MCP call.
            rows = [
                {"year": 2023, "trend": "vector databases"},
                {"year": 2024, "trend": "AI-native databases"},
            ]

            span.set_attribute("db.rows_count", len(rows))
            return rows
