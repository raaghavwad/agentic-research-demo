"""Configuration helpers for environment-driven settings.

OpenAI is the default LLM provider, but settings remain provider-agnostic so
other vendors can be swapped in without touching the orchestration code.
"""

from __future__ import annotations

import os
from dataclasses import dataclass

from dotenv import load_dotenv

_DOTENV_LOADED = False


@dataclass(frozen=True)
class Settings:
    """Simple container for demo-friendly configuration values."""

    llm_api_key: str
    llm_model: str
    llm_provider: str
    web_search_api_key: str
    sqlcl_mcp_endpoint: str
    oracle_user: str
    oracle_password: str
    oracle_dsn: str
    use_sqlcl_mcp: bool


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

    The LLM configuration defaults to OpenAI Chat Completions but can be
    overridden via provider-agnostic env vars.
    """

    _load_environment()

    # Pull secrets/URLs from the environment with defensive defaults for dev.
    llm_api_key = os.getenv("LLM_API_KEY") or os.getenv("OPENAI_API_KEY") or ""
    llm_model = os.getenv("LLM_MODEL") or os.getenv("OPENAI_MODEL") or "gpt-4o-mini"
    llm_provider = os.getenv("LLM_PROVIDER") or "openai"
    web_search_api_key = os.getenv("WEB_SEARCH_API_KEY", "")
    sqlcl_mcp_endpoint = os.getenv("SQLCL_MCP_ENDPOINT", "http://localhost:1234")
    oracle_user = os.getenv("ORACLE_USER", "SYSTEM")
    oracle_password = os.getenv("ORACLE_PASSWORD", "OraclePassword123")
    oracle_dsn = os.getenv("ORACLE_DSN", "localhost:1521/FREEPDB1")
    use_sqlcl_mcp = os.getenv("USE_SQLCL_MCP", "false").lower() == "true"

    # TODO: Add schema validation (e.g., pydantic) once inputs become stricter.
    return Settings(
        llm_api_key=llm_api_key,
        llm_model=llm_model,
        llm_provider=llm_provider,
        web_search_api_key=web_search_api_key,
        sqlcl_mcp_endpoint=sqlcl_mcp_endpoint,
        oracle_user=oracle_user,
        oracle_password=oracle_password,
        oracle_dsn=oracle_dsn,
        use_sqlcl_mcp=use_sqlcl_mcp,
    )
