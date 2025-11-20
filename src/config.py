"""Configuration helpers for environment-driven settings."""

from __future__ import annotations

import os
from dataclasses import dataclass

from dotenv import load_dotenv

_DOTENV_LOADED = False


@dataclass(frozen=True)
class Settings:
    """Simple container for demo-friendly configuration values."""

    llm_api_key: str
    web_search_api_key: str
    sqlcl_mcp_endpoint: str
    ollama_model: str
    ollama_base_url: str
    oracle_user: str
    oracle_password: str
    oracle_dsn: str


def _load_environment() -> None:
    """Idempotently load `.env` values for local development."""
    global _DOTENV_LOADED
    if not _DOTENV_LOADED:
        load_dotenv()
        _DOTENV_LOADED = True


def get_settings() -> Settings:
    """Return strongly-typed settings sourced from environment variables.

    This helper is intentionally verbose so a blog reader can follow the flow
    from `.env` file → environment variables → dataclass instance.
    """

    _load_environment()

    # Pull secrets/URLs from the environment with defensive defaults for dev.
    llm_api_key = os.getenv("LLM_API_KEY", "")
    web_search_api_key = os.getenv("WEB_SEARCH_API_KEY", "")
    sqlcl_mcp_endpoint = os.getenv("SQLCL_MCP_ENDPOINT", "http://localhost:1234")
    ollama_model = os.getenv("OLLAMA_MODEL", "phi3.5:latest")
    ollama_base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    oracle_user = os.getenv("ORACLE_USER", "SYSTEM")
    oracle_password = os.getenv("ORACLE_PASSWORD", "OraclePassword123")
    oracle_dsn = os.getenv("ORACLE_DSN", "localhost:1521/FREEPDB1")

    # TODO: Add schema validation (e.g., pydantic) once inputs become stricter.
    return Settings(
        llm_api_key=llm_api_key,
        web_search_api_key=web_search_api_key,
        sqlcl_mcp_endpoint=sqlcl_mcp_endpoint,
        ollama_model=ollama_model,
        ollama_base_url=ollama_base_url,
        oracle_user=oracle_user,
        oracle_password=oracle_password,
        oracle_dsn=oracle_dsn,
    )
