"""Application configuration for AI Business OS.

All settings are loaded from environment variables / .env file.
Never hardcode secrets or model names in code — everything that
changes between dev/test/prod lives here.

pydantic-settings automatically:
- reads from environment variables
- reads from .env file (lower priority than env vars)
- validates types and raises clear errors on missing required values
"""

from __future__ import annotations

from functools import lru_cache
from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    # ── LLM ───────────────────────────────────────────────
    llm_provider: Literal["avalai", "metis"] = Field(
        "avalai", description="Which LLM provider to use"
    )
    avalai_api_key: str = Field("", description="AvalAI API key")
    metis_api_key: str = Field("", description="Metis API key")
    llm_model: str = Field("gemini-2.0-flash", description="Model to use")
    llm_use_flex_tier: bool = Field(True, description="50% cheaper on AvalAI")

    # ── Telegram ──────────────────────────────────────────
    telegram_bot_token: str = Field(..., description="Telegram bot token")

    # ── App ───────────────────────────────────────────────
    app_env: str = Field("development", description="development | test | production")
    app_debug: bool = Field(False, description="Enable debug logging")
    default_tenant_id: str = Field("default", description="Tenant id")

    # ── Proxy ─────────────────────────────────────────────
    proxy_url: str | None = Field(None, description="Proxy URL for restricted networks")


@lru_cache
def get_settings() -> Settings:
    """Return cached settings instance.

    Use this everywhere instead of instantiating Settings() directly:
        from core.config import get_settings
        settings = get_settings()
    """
    return Settings() # type: ignore[call-arg]