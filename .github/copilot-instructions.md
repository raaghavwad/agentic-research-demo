# AI Coding Agent Instructions

## 🔭 Project Overview & Architecture

This is an **Agentic Research Analyst** demo using Python, LangGraph, Oracle SQLcl, and OpenTelemetry.

- **Core Flow**: `RootAgent` orchestrates `SearchAgent` (web search + LLM) and `DatabaseAgent` (Oracle DB trends).
- **Observability**: Full OTel instrumentation (traces/metrics) exporting to Jaeger/Tempo/Prometheus.
- **Data Flow**: User Query -> RootAgent -> [SearchAgent, DatabaseAgent] -> Combined String Response.
- **Database**: `OracleDBClient` supports direct `oracledb` or `sql` (SQLcl) subprocess, with fallback mocks.

## 📖 Critical Context

- **`SPEC.md`**: Authoritative source for span names, attributes, and behavioral requirements. **Read this first.**
- **`src/app.py`**: Entry point, bootstraps tracing and agent graph.
- **`src/observability/otel_setup.py`**: Central OTel configuration.

## 🛠️ Developer Workflows

- **Setup**: `python -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt`
- **Run CLI**: `python src/app.py`
- **Run UI**: `streamlit run ui/streamlit_app.py`
- **Run Everything (Docker)**: `docker compose up --build` (Runs App + Jaeger/Tempo + Prometheus + Grafana)
- **Observability Stack (Standalone)**: `cd docker && docker compose up` (Jaeger UI: http://localhost:16686)
- **Env Vars**: Copy `.env.example` to `.env`.

## 📏 Code Conventions & Patterns

- **Tracing is Mandatory**: Every agent method must start a span.
  ```python
  tracer = trace.get_tracer(__name__)
  with tracer.start_as_current_span("span.name.from.spec") as span:
      span.set_attribute("custom.attr", value)
  ```
- **Span Names**: MUST match `SPEC.md` (e.g., `root_agent.handle_request`, `oracle.query_trends`).
- **Agent Output**: Agents return newline-delimited strings. `RootAgent` concatenates them. Do not change return types.
- **Database Access**: Use `OracleDBClient`. Do not use raw SQL in agents.
  - `DatabaseAgent` formats `List[dict]` from client into `"{year}: {trend}"` strings.

## 🧪 Integration & Testing

- **Oracle Fallback**: `OracleDBClient` has built-in fallbacks if DB is unreachable. Do not remove this resilience.
- **HTTP Instrumentation**: `RequestsInstrumentor` is auto-initialized. Use `requests` or `httpx` for external calls.

## ⚠️ Common Pitfalls

- **Missing Spans**: Failing to wrap agent logic in a span breaks the demo visualization.
- **Attribute Types**: Ensure span attributes are primitives (str, int, bool).
- **Return Formats**: Changing `DatabaseAgent` to return a dict instead of a string will break `RootAgent`.
