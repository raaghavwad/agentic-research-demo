# Agentic Research Analyst Demo

A teaching-oriented demo that showcases a multi-agent research workflow with full observability. The application coordinates web-search and Oracle database agents, instruments spans with OpenTelemetry, and exports traces to Jaeger for visualization.

## Prerequisites
- Python 3.11+
- Docker Desktop (for Jaeger)
- Make (optional, for future scripts)

## Installation
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Environment Variables
Copy the template and update secrets:
```bash
cp .env.example .env
# Edit .env with your keys
```

## Running Jaeger
```bash
cd docker
docker compose up jaeger
# UI available at http://localhost:16686
```

## Running the Application

```bash
python src/app.py
```

The entrypoint spins up the LangGraph workflow which:

1. Starts a root span `root_agent.handle_request`.
2. Executes search node (`search_agent.run`) calling `web_search_and_summarize` and an Ollama model.
3. Executes database node (`db_agent.run`) calling `oracle.query_trends`.
4. Combines results and emits response length metrics.

To enable the experimental SQLcl subprocess path for Oracle queries:

```bash
USE_SQLCL_MCP=true python src/app.py
```

If SQLcl isn't installed or the subprocess fails, it gracefully falls back to the direct Python driver.

## Viewing Traces

1. Start Jaeger (see above) and run the app.
2. Open <http://localhost:16686>.
3. Filter by service name (default: the module name where spans were created).
4. Inspect span chain:
    - root_agent.handle_request
    - search_agent.run → web_search_and_summarize → ollama.summarize
    - db_agent.run → oracle.query_trends
5. Check attributes like `user.query`, `search.summary.length`, `db.rows_count`, `response.length`.

## Architecture (High-Level)

```mermaid
graph TD
    User((User Query)) --> RootAgent
    RootAgent --> SearchAgent
    RootAgent --> DBAgent
    SearchAgent --> WebSearchService
    SearchAgent -->|Spans| Jaeger
    DBAgent --> OracleDBClient
    OracleDBClient -->|Direct or SQLcl| OracleDB
    RootAgent -->|Parent Span| Jaeger
```
