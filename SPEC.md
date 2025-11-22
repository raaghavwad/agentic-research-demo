# Technical Specification — Agentic AI Observability Demo
This document defines the full project specification for an interview assignment:  
**Observability for Agentic AI Applications**  
using Python, LangChain/LangGraph, Oracle SQLcl MCP server, OpenTelemetry, and Jaeger.

Cursor should use this file as the authoritative reference when generating files, code, and structure.

---

## 📌 Project Overview
We are building a **Research Analyst Agentic System** that demonstrates:

- Multi-agent orchestration  
- Web search + LLM summarization  
- Oracle database queries via SQLcl MCP  
- Full observability using OpenTelemetry  
- Distributed tracing visualization via Jaeger  

This project will be part of a technical demo and blog post for a Developer Evangelist position.

---

# 🧱 Architecture Requirements

## 1. Agents
The application must include:

### **Root Agent (Orchestrator)**
- Receives user query
- Calls two worker agents
- Combines results
- Returns a final summary
- Creates a root OpenTelemetry span

### **Worker Agent 1 — SearchAgent**
- Performs web search (placeholder API or Tavily/SerpAPI)
- Summarizes results using an LLM
- Uses HTTP calls instrumented via OpenTelemetry
- All logic wrapped in spans

### **Worker Agent 2 — DatabaseAgent**
- Connects to Oracle DB through **SQLcl MCP Server**
- Executes SQL queries (mocked at first, real call later)
- Returns structured results
- Fully instrumented with spans

---

# 🗄️ Database Requirements
We must include:

- Oracle Database 23ai (local Docker) **or** Autonomous DB (later)
- A sample table (example: `tech_trends`)
- A SQL script `init_db.sql` containing sample rows

DatabaseAgent should call a `OracleDBClient` abstraction that wraps the MCP call.

At first, this can return mocked results with TODO comments.

---

# 🧩 Observability Requirements

The project **must** include:

### **OpenTelemetry Tracing**
- OpenTelemetry SDK + API
- Jaeger exporter
- Parent/child spans for:
  - RootAgent
  - SearchAgent
  - DatabaseAgent
  - LLM calls
  - HTTP calls
  - Database queries

### **HTTP instrumentation**
Use:

```env
from opentelemetry.instrumentation.requests import RequestsInstrumentor
```

### **Jaeger**
- Docker compose file with Jaeger all-in-one service  
- Accessible at: http://localhost:16686

### **Span Naming Guidelines**
- `"root_agent.handle_request"`
- `"search_agent.run"`
- `"db_agent.run"`
- `"web_search_and_summarize"`
- `"oracle.query_trends"`

### **Span Attributes**

Include useful metadata such as:

- `user.query`
- `search.query`
- `db.topic`
- `result.length`
- `summary.length`
- `db.rows_count`

Additional attributes implemented (post initial spec) to enrich trace analysis:

- `search.summary.length` (length of LLM-produced search summary)
- `db.lines.count` (number of formatted lines returned by DatabaseAgent)
- `response.length` (total combined result length)
- `response.lines` (number of lines in final combined answer)
- `db.mcp.mode` ("sqlcl" when SQLcl subprocess path active, else "direct")
- `llm.response_length` (length of Ollama summarization output)
- `search.context_length` (length of gathered raw search context prior to summarization)

---

## Folder Structure (Must Match)

```text
src/
  app.py
  config.py

  agents/
    root_agent.py
    search_agent.py
    db_agent.py

  services/
    web_search.py
    db_client.py

  observability/
    otel_setup.py

data/
  init_db.sql

docker/
  docker-compose.yml

requirements.txt
README.md
.env.example
```

---

## Code Behavior Requirements

### RootAgent

- Coordinates SearchAgent + DatabaseAgent
- Creates root span
- Adds attributes for input + output length
- Sequential execution is fine
- Combines results in `_combine_results`

### SearchAgent

- Creates its own span
- Calls web_search_and_summarize
- Handles LLM summarization (placeholder is fine)

### DatabaseAgent

- Creates its own span
- Calls OracleDBClient.query_trends()
- Formats rows as text

### OracleDBClient

- Constructor reads connection settings from environment via `config.get_settings()`.
- `query_trends(topic: str)` wraps DB call in `oracle.query_trends` span.
- Selection logic:
  1. If env `USE_SQLCL_MCP=true` and `sql` executable found → attempt SQLcl subprocess (CSV output parsing).
  2. Else use direct Python `oracledb` driver.
  3. On failure fall back to static sample rows and set `db.error` span attribute.
- Emits `db.mcp.mode` indicating which path executed ("sqlcl" or "direct").

### Web Search Service

- Wrap logic in `"web_search_and_summarize"` span, sub-span `"ollama.summarize"` for LLM call.
- Uses DuckDuckGo Instant Answer API (`requests.get`, automatically instrumented) to gather context.
- Summarizes via local Ollama model defined by `OLLAMA_MODEL` env var.
- Attributes: `search.query`, `search.context_length`, `llm.model`, `llm.response_length`, `summary.length`.

---

## Environment Setup Requirements

Create `.env.example` with:

```
LLM_API_KEY=your_key_here
WEB_SEARCH_API_KEY=your_key_here
SQLCL_MCP_ENDPOINT=http://localhost:1234
OLLAMA_MODEL=phi3.5:latest
OLLAMA_BASE_URL=http://localhost:11434
ORACLE_USER=SYSTEM
ORACLE_PASSWORD=OraclePassword123
ORACLE_DSN=localhost:1521/FREEPDB1
USE_SQLCL_MCP=false
```

Use `python-dotenv` to load these values in `config.py`.

---

## Docker Requirements

`docker/docker-compose.yml` must include:

- Jaeger all-in-one
- Expose:
  - UDP 6831
  - UI 16686
- Add comments explaining usage

---

## README Requirements

README.md must include:

- Project description  
- Prerequisites (Python version, Docker)  
- Installation instructions  
- `.env` setup  
- How to run Jaeger  
- How to run `app.py`  
- How to view traces in Jaeger  
- High-level architecture diagram (can be Mermaid)

---

## Design Philosophy

- Code must be **readable**, **well-commented**, and **evangelist-friendly**  
- Avoid over-engineering — clarity matters more  
- Use TODO comments where Oracle specifics are not implemented yet  
- Compatible with blog/tutorial content  

---

## Deliverables

This SPEC.md describes the full scope needed for:

1. A working multi-agent demo  
2. Complete observability instrumentation  
3. A blog post  
4. A presentation-ready 5-minute demo  
5. A GitHub-ready project

Recommended additional verification steps for demo readiness:

- Run with Jaeger active and confirm span tree ordering.
- Toggle `USE_SQLCL_MCP=true` and verify `db.mcp.mode` changes.
- Inspect attributes `response.lines` and `search.summary.length` for sane values.

Cursor should follow this spec for:

- scaffolding
- code generation
- refinement

## 🖥️ UI Requirements (Streamlit Frontend)

In addition to the CLI entrypoint, provide a simple web UI using **Streamlit**.

Goals:
- Let a user enter a free-text research query.
- Run the same underlying agentic workflow used by the CLI:
  - Use the LangGraph workflow (root agent + SearchAgent + DatabaseAgent).
  - Preserve all existing observability behavior (OpenTelemetry spans, Jaeger traces).
- Display:
  - The combined final answer.
  - Optionally, the separate “Web Research Summary” and “Oracle Trends” sections.

Implementation details:
- Add a new module, for example: `ui/streamlit_app.py`.
- The UI should:
  - Initialize the workflow once (e.g., via `st.cache_resource`).
  - For each user query, call the orchestration function (e.g., `run_graph(workflow, user_query)`).
  - Provide clear instructions and a link or note about viewing traces in Jaeger.

Running the UI:
- It should be runnable from project root as:
  - `streamlit run ui/streamlit_app.py`
- The UI **must not** bypass observability:
  - It should always rely on the same `build_workflow` + `run_graph` functions that the CLI uses, so the traces remain consistent and visible in Jaeger under `service.name = agentic-research-demo`.

### LLM Configuration

The SearchAgent uses an LLM to summarize web search results into a concise answer.
The specific LLM provider is configurable and should not be hard-coded.

Environment variables (provider-agnostic):
- `LLM_PROVIDER` — e.g., `ollama`, `openai`, `oci`, or `azure`.
- `LLM_MODEL` — model name (provider-specific).
- `LLM_BASE_URL` — base URL or inference endpoint (optional).
- `LLM_API_KEY` — required only for external providers.

Requirements:
- All LLM calls must be wrapped in an OpenTelemetry span (`llm.summarize`).
- Spans must include attributes:
    - `llm.provider`
    - `llm.model`
    - `llm.response_length`
- Implementation should support swapping LLM providers without changing UI or agent logic.
