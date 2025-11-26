## Purpose

Agentic Research Analyst demo that:

- Runs a multi-agent workflow (Search + LLM summarization + Oracle DB trends)
- Instruments every step with OpenTelemetry for traces and KPIs
- Visualizes observability via Grafana using Tempo (traces) and Prometheus (metrics)

## Quick Start

```bash
git clone <your-fork-url>
cd agentic-research-demo
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env  # then fill in API keys / DB settings
```

## Observability Stack

```bash
cd docker
docker compose up
```

This launches Tempo, Prometheus, and Grafana (http://localhost:3000).

## Running the Application

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

OTEL_SERVICE_NAME=agentic-research-demo
OTEL_EXPORTER_OTLP_ENDPOINT=http://localhost:4318/v1/traces
GRAFANA_URL=http://localhost:3000

ORACLE_USER=SYSTEM
ORACLE_PASSWORD=OraclePassword123
ORACLE_DSN=localhost:1521/FREEPDB1
```

Oracle Database is optional. If it’s unreachable, `DatabaseAgent` falls back to static sample rows so the demo still works.

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
