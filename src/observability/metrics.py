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

