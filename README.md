# Agentic Research Analyst Demo

A teaching-oriented demo that showcases a multi-agent research workflow with full observability. The application coordinates web-search and Oracle database agents, instruments spans with OpenTelemetry, and exports traces to Jaeger for visualization.

## Prerequisites

- Python 3.11+
- Docker (for Jaeger + optional Oracle DB + Ollama runtime)
- curl (for Ollama install script)
- Make (optional, for future scripts)

## Installation

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Install & Pull Ollama Model

Install Ollama (Linux/macOS):

```bash
curl -fsSL https://ollama.com/install.sh | sh
```

Verify it is running and pull the model defined in `.env.example` (`phi3.5:latest` by default):

```bash
ollama list
ollama pull phi3.5:latest
```

If you change `OLLAMA_MODEL` (e.g. to a lighter model like `qwen2.5:0.5b`), pull that instead:

```bash
ollama pull qwen2.5:0.5b
```

## Optional: Run Oracle Database Free (Local)

If you want real Oracle results instead of fallback rows, run the Oracle Database Free image locally. (You may need to create a free account and accept terms at <https://container-registry.oracle.com>.)

Pull the image:

```bash
docker pull container-registry.oracle.com/database/free:latest
```

Start the container (password must match your `.env` or update `ORACLE_PASSWORD` there):

```bash
docker run -d --name oracle-free -p 1521:1521 \
    -e ORACLE_PASSWORD=OraclePassword123 \
    container-registry.oracle.com/database/free:latest
```

(Optional) Initialize sample data using SQLcl once the DB is healthy:

```bash
sqlcl SYSTEM/OraclePassword123@localhost:1521/FREEPDB1 @data/init_db.sql
```

Smoke test connectivity:

```bash
python test_oracle_connection.py
```

If you prefer NOT to run Oracle, the app will gracefully fall back to static sample rows.

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

Jaeger captures spans from the Python app; leave it running while you experiment.

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

### Quick Start (All Together)

```bash
# 1. Clone & enter repo
git clone <your-fork-url> && cd agentic-research-demo

# 2. Python deps
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# 3. Env setup
cp .env.example .env

# 4. Ollama install + model pull
curl -fsSL https://ollama.com/install.sh | sh
ollama pull phi3.5:latest

# 5. (Optional) Oracle Free DB
docker pull container-registry.oracle.com/database/free:latest
docker run -d --name oracle-free -p 1521:1521 -e ORACLE_PASSWORD=OraclePassword123 container-registry.oracle.com/database/free:latest
sqlcl SYSTEM/OraclePassword123@localhost:1521/FREEPDB1 @data/init_db.sql || echo "Skip if SQLcl not installed"

# 6. Jaeger tracing backend
cd docker && docker compose up jaeger &
cd ..

# 7. Run demo
python src/app.py
```

## Viewing Traces

1. Start Jaeger (see above) and run the app.
2. Open <http://localhost:16686>.
3. Filter by service name (default: the module name where spans were created).
4. Inspect span chain:
    - root_agent.handle_request
    - search_agent.run → web_search_and_summarize → ollama.summarize
    - db_agent.run → oracle.query_trends
5. Check attributes like `user.query`, `search.summary.length`, `db.rows_count`, `response.length`.

To test fallback vs. SQLcl path, toggle:

```bash
USE_SQLCL_MCP=true python src/app.py
```

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
