## Purpose

Agentic Research Analyst demo that:

- Runs a multi-agent workflow (Search + LLM summarization + Oracle DB trends)
- Instruments every step with OpenTelemetry for traces and KPIs
- Visualizes observability via Grafana using Tempo (traces) and Prometheus (metrics)

## 🚀 Docker Quick Start (Recommended)

1. **Configure Environment**:
   Copy the example environment file and fill in your API keys (especially `OPENAI_API_KEY`):

   ```bash
   cp .env.example .env
   # Edit .env with your actual keys
   ```

2. **Run the Stack**:
   Run the entire stack (App + UI + Observability) with a single command:

   ```bash
   docker compose up --build
   ```

Access the services:

- **Streamlit UI**: <http://localhost:8501>
- **Grafana**: <http://localhost:3000>
- **Jaeger/Tempo**: <http://localhost:3200>
- **Prometheus**: <http://localhost:9090>

## 🐍 Local Development Setup

```bash
git clone <your-fork-url>
cd agentic-research-demo
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env  # then fill in API keys / DB settings
```

## Observability Stack (Standalone)

If running the app locally (not in Docker), start the observability backend separately:

```bash
cd docker
docker compose up
```

This launches Tempo, Prometheus, and Grafana.

Access the observability services:

- **Grafana**: <http://localhost:3000>
- **Jaeger/Tempo**: <http://localhost:3200>
- **Prometheus**: <http://localhost:9090>

## Running the Application (Local)

```bash
# CLI mode
python src/app.py

# Streamlit UI
streamlit run ui/streamlit_app.py
```

## Environment Variables

```env
OPENAI_API_KEY=...
OPENAI_MODEL=gpt-4o-mini

# OpenTelemetry configuration for local Tempo instance
export OTEL_SERVICE_NAME=agentic-research-demo
export OTEL_TRACES_EXPORTER=otlp
export OTEL_EXPORTER_OTLP_ENDPOINT=http://localhost:4318
export OTEL_EXPORTER_OTLP_PROTOCOL=http/protobuf

# Optional: signal-specific config if preferred
export OTEL_EXPORTER_OTLP_TRACES_ENDPOINT=http://localhost:4318/v1/traces

GRAFANA_URL=http://localhost:3000

ORACLE_USER=SYSTEM
ORACLE_PASSWORD=OraclePassword123
ORACLE_DSN=localhost:1521/FREEPDB1
```

**Note**: Either the generic `OTEL_EXPORTER_OTLP_ENDPOINT` or the more specific `OTEL_EXPORTER_OTLP_TRACES_ENDPOINT` can be used, but the base URL should match the docker-exposed `localhost:4318`.

Oracle Database is optional. If it's unreachable, `DatabaseAgent` falls back to static sample rows so the demo still works.

## Observability UI

- Traces flow via OTLP to Tempo → view in Grafana (Explore → Trace view).
- KPIs come from Prometheus scraping `http://host.docker.internal:9464/metrics`.
- Streamlit sidebar links to Grafana; set `GRAFANA_TRACES_URL` / `GRAFANA_KPIS_URL` to deep-link dashboards.

## Key Concepts

- RootAgent orchestrates SearchAgent + DatabaseAgent
- Web search + LLM summary
- Oracle DB trends
- OpenTelemetry traces + metrics
- Grafana UI for observability

## Support / Troubleshooting

- No traces? Confirm `OTEL_EXPORTER_OTLP_ENDPOINT` and that `docker compose up` is running.
- Missing metrics? Ensure Prometheus scrapes `http://host.docker.internal:9464/metrics`.
- Oracle errors? The fallback mock data preserves the demo flow.
