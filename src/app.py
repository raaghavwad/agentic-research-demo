"""Main entrypoint for the agentic research + observability demo."""

from __future__ import annotations

from src.config import get_settings
from src.observability.otel_setup import init_tracer, init_http_instrumentation
from src.services.db_client import OracleDBClient
from src.agents.search_agent import SearchAgent
from src.agents.db_agent import DatabaseAgent
from src.agents.root_agent import RootAgent


def build_app() -> RootAgent:
    """Construct all dependencies and return a ready-to-run RootAgent."""
    settings = get_settings()

    init_tracer(service_name="agentic-research-demo")
    init_http_instrumentation()

    db_client = OracleDBClient(sqlcl_endpoint=settings.sqlcl_mcp_endpoint)
    search_agent = SearchAgent()
    db_agent = DatabaseAgent(db_client=db_client)
    root_agent = RootAgent(search_agent=search_agent, db_agent=db_agent)

    return root_agent


def main() -> None:
    """Bootstrap the agentic workflow (placeholder)."""
    user_query = "Latest trends in AI databases"

    root_agent = build_app()
    response = root_agent.handle_request(user_query)

    print("=== Agentic Research Demo ===")
    print(f"User query: {user_query}")
    print("\n=== Combined Answer ===")
    print(response)


if __name__ == "__main__":
    main()
