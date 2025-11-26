"""Prometheus metrics helpers for the agentic research demo."""

from __future__ import annotations

import os

from prometheus_client import Counter, Histogram, start_http_server

# Basic KPIs
REQUEST_COUNTER = Counter(
    "agentic_requests_total",
    "Total number of agentic research requests processed",
    ["outcome"],  # "success" or "error"
)

REQUEST_LATENCY = Histogram(
    "agentic_request_latency_seconds",
    "Latency for processing a full agentic request",
)

# LLM latency histogram
LLM_REQUEST_LATENCY = Histogram(
    "agentic_llm_latency_seconds",
    "Latency for individual LLM calls",
)

# LLM token tracking
TOTAL_PROMPT_TOKENS = Counter(
    "agentic_llm_prompt_tokens_total",
    "Total prompt tokens used across all LLM calls",
)

TOTAL_COMPLETION_TOKENS = Counter(
    "agentic_llm_completion_tokens_total",
    "Total completion tokens produced across all LLM responses",
)

TOTAL_COST_USD = Counter(
    "agentic_llm_cost_usd_total",
    "Total cost spent in USD for LLM usage",
)

# Unanswerable query tracking
UNANSWERABLE_QUERY_COUNTER = Counter(
    "agentic_unanswerable_queries_total",
    "Number of queries where web and database provided no useful answer",
)

# Queries per session (session-level aggregator)
QUERIES_PER_SESSION = Counter(
    "agentic_queries_per_session_total",
    "Total number of queries made in user session",
)

# Revenue / productivity savings metric (manual input or compute later)
REVENUE_SAVINGS = Counter(
    "agentic_revenue_savings_usd_total",
    "Estimated USD revenue saved using agent automation",
)


def init_metrics_server() -> None:
    """
    Start a Prometheus metrics HTTP server on the configured port.

    Uses METRICS_PORT env var (default: 9464).
    The app should call this once at startup.
    """

    port_str = os.getenv("METRICS_PORT", "9464")
    try:
        port = int(port_str)
    except ValueError:
        port = 9464

    start_http_server(port)


"""
Example usage for instrumentation:

from observability.metrics import (
    REQUEST_COUNTER,
    REQUEST_LATENCY,
    LLM_REQUEST_LATENCY,
    TOTAL_PROMPT_TOKENS,
    TOTAL_COMPLETION_TOKENS,
    TOTAL_COST_USD,
    UNANSWERABLE_QUERY_COUNTER,
    QUERIES_PER_SESSION,
    REVENUE_SAVINGS,
)

with REQUEST_LATENCY.time():
    ...
REQUEST_COUNTER.labels(outcome="success").inc()

with LLM_REQUEST_LATENCY.time():
    ...
TOTAL_PROMPT_TOKENS.inc(prompt_tokens)
TOTAL_COMPLETION_TOKENS.inc(completion_tokens)
TOTAL_COST_USD.inc(cost_usd)

UNANSWERABLE_QUERY_COUNTER.inc()
QUERIES_PER_SESSION.inc()
REVENUE_SAVINGS.inc(estimated_savings_usd)
"""
