"""LangGraph-based orchestration for the agentic research demo.

This module introduces a LangGraph StateGraph that coordinates the existing
SearchAgent and DatabaseAgent while preserving SPEC.md span naming:
  - root_agent.handle_request
  - search_agent.run
  - db_agent.run
The underlying service functions still emit spans: web_search_and_summarize,
oracle.query_trends.

We wrap the whole graph invocation in a root span so Jaeger shows a neat
parent/child hierarchy for demo clarity.
"""

from __future__ import annotations

from typing import TypedDict

from opentelemetry import trace
from langgraph.graph import StateGraph, END  # type: ignore

from agents.search_agent import SearchAgent
from agents.db_agent import DatabaseAgent
from observability.metrics import (
    REQUEST_COUNTER,
    REQUEST_LATENCY,
    QUERIES_PER_SESSION,
    REVENUE_SAVINGS,
)

# Business value placeholder for revenue savings calculation
ESTIMATED_SAVINGS_PER_SUCCESS_USD = 1.0


class GraphState(TypedDict, total=False):
    query: str
    search_summary: str
    db_lines: str
    combined: str


def build_graph(search_agent: SearchAgent, db_agent: DatabaseAgent):
    """Create and compile a LangGraph workflow coordinating both agents.

    Each node mutates a portion of the shared state. We keep it intentionally
    small for tutorial readability.
    """
    graph = StateGraph(GraphState)

    tracer = trace.get_tracer(__name__)

    def search_node(state: GraphState) -> GraphState:
        query = state.get("query", "")  # type: ignore[index]
        with tracer.start_as_current_span("search_agent.run") as span:
            summary = search_agent.run(query)
            span.set_attribute("search.summary.length", len(summary))
        return {"search_summary": summary}

    def db_node(state: GraphState) -> GraphState:
        query = state.get("query", "")  # type: ignore[index]
        with tracer.start_as_current_span("db_agent.run") as span:
            # For this demo we reuse the user query as a topic.
            lines = db_agent.run(query)
            span.set_attribute("db.lines.count", lines.count("\n") + (1 if lines else 0))
        return {"db_lines": lines}

    def combine_node(state: GraphState) -> GraphState:
        combined = (
            "=== Web Research Summary ===\n"
            f"{state.get('search_summary','')}\n\n"
            "=== Oracle Trends ===\n"
            f"{state.get('db_lines','')}"
        )
        return {"combined": combined}

    # Register nodes.
    graph.add_node("search", search_node)
    graph.add_node("db", db_node)
    graph.add_node("combine", combine_node)

    # Simple sequential flow: search -> db -> combine -> END
    graph.set_entry_point("search")
    graph.add_edge("search", "db")
    graph.add_edge("db", "combine")
    graph.add_edge("combine", END)

    return graph.compile()


def run_graph(workflow, user_query: str) -> str:
    """Execute the compiled workflow under the root span and return combined result."""
    QUERIES_PER_SESSION.inc()
    outcome = "success"
    
    with REQUEST_LATENCY.time():
        try:
            tracer = trace.get_tracer(__name__)
            with tracer.start_as_current_span("root_agent.handle_request") as span:
                span.set_attribute("user.query", user_query)
                final_state: GraphState = workflow.invoke({"query": user_query})
                combined = final_state.get("combined", "")
                span.set_attribute("response.length", len(combined))
                span.set_attribute("response.lines", combined.count("\n") + (1 if combined else 0))
            
            REVENUE_SAVINGS.inc(ESTIMATED_SAVINGS_PER_SUCCESS_USD)
            return combined
        except Exception:
            outcome = "error"
            raise
        finally:
            REQUEST_COUNTER.labels(outcome=outcome).inc()
