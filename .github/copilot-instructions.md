## Quick context for AI coding assistants

This repo is a teaching/demo for an Agentic Research Analyst instrumented with OpenTelemetry and Jaeger. The primary goal of edits is to implement clear, minimal, and demonstrable code that follows the project's SPEC.md spans and observable behaviors.

What to read first (high signal):

- `SPEC.md` — canonical span names, attributes, and behavioral requirements (authoritative).
- `README.md` — run steps and high-level architecture diagram.
- `src/app.py` — bootstraps tracer + HTTP instrumentation and constructs agents.
- `src/agents/` — `root_agent.py`, `search_agent.py`, `db_agent.py` (span creation and orchestration patterns).
- `src/services/` — `db_client.py` (Oracle SQLcl MCP client) and `web_search.py` (HTTP search wrapper).
- `src/observability/otel_setup.py` — tracer / exporter setup and HTTP instrumentation helpers.

Project conventions you must follow (explicit and discoverable):

- Spans: always use `tracer = trace.get_tracer(__name__)` and `with tracer.start_as_current_span("<span.name>")`.
  - Expected span names (from SPEC): `root_agent.handle_request`, `search_agent.run`, `db_agent.run`, `oracle.query_trends`, `web_search_and_summarize`.
- Agents return newline-delimited human-readable strings; `RootAgent._combine_results()` concatenates them. Do not change the return shape without updating callers and README/SPEC.
- `OracleDBClient.query_trends(topic)` should return List[dict] rows like `[{"year": 2024, "trend": "..."}]`. `DatabaseAgent.run()` formats rows as `"{year}: {trend}"` lines.
- Configuration: `src/config.py` loads `.env` via `python-dotenv`. Use `SQLCL_MCP_ENDPOINT` default `http://localhost:1234` for local mocks.

Developer workflows & runnable checks (explicit commands):

- Create venv and install deps:

  ```bash
  python -m venv .venv
  source .venv/bin/activate
  pip install -r requirements.txt
  ```

- Start Jaeger for trace visualization:

  ```bash
  cd docker
  docker compose up jaeger
  # UI: http://localhost:16686
  ```

- Run the demo entrypoint (runs a sample query): `python src/app.py`.

Assignment-specific checklist (Developer Evangelist deliverables — keep these in repo docs):

- Blog post (Markdown/PDF): include architecture diagram, step-by-step guide, code excerpts tied to files above, and troubleshooting tips.
- Video demo (≤5 minutes): record running app + Jaeger UI showing traces for root -> search -> db calls.
- Ensure repo is runnable from a fresh clone: `requirements.txt`, `.env.example`, `data/init_db.sql`, and `docker/docker-compose.yml` must be present and documented.

Observability-focused guidance (concrete):

- Instrument these elements with spans/attributes: user query (`user.query`), search queries (`search.query`), db topic (`db.topic`), `result.length` or `result.lines`, and timings for external LLM/API calls.
- Use `RequestsInstrumentor` (initialized by `init_http_instrumentation()`) to capture HTTP calls made by `web_search.py`.
- Keep span names and attributes stable; they're referenced in the SPEC and README examples and are useful for demo visuals.

Small, low-risk additions you may implement proactively:

- Add a mocked `OracleDBClient` response in `services/db_client.py` with a clear TODO comment linking to SPEC.md.
- Add a tiny unit test for `DatabaseAgent.run()` that asserts formatting of `[{"year":...,"trend":...}]` → `"{year}: {trend}"` lines.

When in doubt:

- Prefer small, documented changes. If modifying behavior required by SPEC.md, open a PR summarizing the rationale and update SPEC.md/README.md accordingly.

Resources & evaluation hints (use these when preparing the blog/video):

- SPEC.md (tracing spans & attributes) — authoritative.
- README.md (run steps & architecture) — use exact commands from repo.
- Demonstration tip: show Jaeger traces with span names listed above so reviewers can tie visuals back to code lines.

---

If you want, I can expand this into a short checklist for adding a new agent (constructor signature, expected span name, example return format) or add a sample blog outline for the assignment deliverable.
