"""Oracle DB client supporting direct oracledb and optional SQLcl MCP path.

Span name stays `oracle.query_trends` per SPEC.md. When the environment variable
`USE_SQLCL_MCP=true` is set and a `sql` executable is found, the client will attempt
to run the query through SQLcl (as a lightweight stand‑in for a formal MCP server
integration). Otherwise it falls back to the direct Python driver. This keeps the
demo resilient while illustrating the optional path.

TODO (MCP full): Replace subprocess invocation with a proper MCP server session
once SQLcl MCP endpoint contract is finalized (see SPEC.md).
"""

from __future__ import annotations

from typing import List, Dict, Any
import os
import shutil
import subprocess
import oracledb
from config import get_settings

from opentelemetry import trace

class OracleDBClient:
    """Simple wrapper around direct oracledb connectivity for demo queries."""

    def __init__(self) -> None:
        settings = get_settings()
        self._user = settings.oracle_user
        self._password = settings.oracle_password
        self._dsn = settings.oracle_dsn

    def query_trends(self, topic: str) -> List[Dict[str, Any]]:
        """Query recent AI database trends (top 5 rows) from Oracle.

        Decision order:
        1. If USE_SQLCL_MCP=true and `sql` present -> attempt SQLcl subprocess path.
        2. Else use direct oracledb driver.
        3. On any failure -> emit fallback rows + span error attribute.
        """
        tracer = trace.get_tracer(__name__)
        with tracer.start_as_current_span("oracle.query_trends") as span:
            span.set_attribute("db.topic", topic)
            rows: List[Dict[str, Any]] = []
            use_sqlcl = os.getenv("USE_SQLCL_MCP", "false").lower() == "true"
            sql_exe = shutil.which("sql") if use_sqlcl else None
            span.set_attribute("db.mcp.mode", "sqlcl" if (use_sqlcl and sql_exe) else "direct")

            query = (
                "SELECT year, trend FROM ai_database_trends "
                "ORDER BY year DESC, trend FETCH FIRST 5 ROWS ONLY"
            )

            if use_sqlcl and sql_exe:
                # Attempt a lightweight SQLcl invocation. We request CSV output for easy parsing.
                # NOTE: Flags may vary by SQLcl version; this is illustrative.
                try:
                    cmd = [
                        sql_exe,
                        f"{self._user}/{self._password}@{self._dsn}",
                        "-n",  # non-interactive
                        "-S",  # silent banner
                        "-L",  # attempt login retries
                        f"SET SQLFORMAT CSV; {query};"
                    ]
                    proc = subprocess.run(cmd, capture_output=True, text=True, timeout=15)
                    if proc.returncode != 0:
                        raise RuntimeError(f"SQLcl exit {proc.returncode}: {proc.stderr.strip()}")
                    # Parse CSV lines: expect header year,trend then rows.
                    for line in proc.stdout.splitlines():
                        line = line.strip()
                        if not line or line.lower().startswith("year,"):
                            continue
                        parts = [p.strip() for p in line.split(",")]
                        if len(parts) >= 2 and parts[0].isdigit():
                            rows.append({"year": int(parts[0]), "trend": parts[1]})
                except Exception as exc:
                    span.set_attribute("db.error", f"sqlcl_failure: {exc}")
                    rows = []  # fallback to direct driver below if empty

            if not rows:
                # Either not using SQLcl path or it failed; use direct driver.
                try:
                    conn = oracledb.connect(user=self._user, password=self._password, dsn=self._dsn)
                    cur = conn.cursor()
                    cur.execute(query)
                    for year, trend in cur.fetchall():
                        rows.append({"year": int(year), "trend": trend})
                    cur.close()
                    conn.close()
                except Exception as exc:
                    # Final fallback rows.
                    if not rows:  # Only overwrite if still empty.
                        rows = [
                            {"year": 2024, "trend": "(fallback) AI-native databases"},
                            {"year": 2023, "trend": "(fallback) vector databases"},
                        ]
                    span.set_attribute("db.error", f"direct_failure: {exc}")

            span.set_attribute("db.rows_count", len(rows))
            return rows

