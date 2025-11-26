"""Main entrypoint for the agentic research + observability demo."""

from __future__ import annotations

import warnings

# Suppress the pkg_resources deprecation warning from OpenTelemetry instrumentation
warnings.filterwarnings("ignore", category=UserWarning, module="opentelemetry.instrumentation.dependencies")

from config import get_settings
from observability.metrics import init_metrics_server
from observability.otel_setup import init_tracer, init_http_instrumentation
from services.db_client import OracleDBClient
from agents.search_agent import SearchAgent
from agents.db_agent import DatabaseAgent
from agents.agent_graph import build_graph, run_graph


def build_workflow():
    """Construct dependencies and compile LangGraph workflow."""
    _ = get_settings()  # Ensures env is loaded; settings used inside services.
    init_metrics_server()
    init_tracer(service_name="agentic-research-demo")
    init_http_instrumentation()

    db_client = OracleDBClient()
    search_agent = SearchAgent()
    db_agent = DatabaseAgent(db_client=db_client)
    workflow = build_graph(search_agent, db_agent)
    return workflow


def main() -> None:
    """Bootstrap the LangGraph-based agentic workflow."""
    user_query = "Latest trends in AI databases"
    workflow = build_workflow()
    response = run_graph(workflow, user_query)
    print("=== Agentic Research Demo (LangGraph) ===")
    print(f"User query: {user_query}")
    print("\n=== Combined Answer ===")
    print(response)


if __name__ == "__main__":
    main()
