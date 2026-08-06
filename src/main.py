"""Entry point for AI Business OS.

This file wires everything together:
  Settings -> LLM Provider -> Agent Runtime -> Gateway -> Start

This is the only place in the codebase that knows about concrete
implementations. Everything else depends on interfaces only.
"""

from __future__ import annotations

import asyncio
import logging

import structlog

from core.config import get_settings, Settings
from gateways.telegram import TelegramGateway
from llm.avalai_provider import AvalAIProvider
from llm.metis_provider import MetisProvider
from core.interfaces import LLMProvider
from runtime.sales_runtime import SalesRuntime


def setup_logging(debug: bool = False) -> None:
    """Configure structured logging for the entire app."""
    level = logging.DEBUG if debug else logging.INFO

    structlog.configure(
        processors=[
            structlog.contextvars.merge_contextvars,
            structlog.processors.add_log_level,
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.dev.ConsoleRenderer(),
        ],
        wrapper_class=structlog.make_filtering_bound_logger(level),
        context_class=dict,
        logger_factory=structlog.PrintLoggerFactory(),
    )


def build_llm_provider(settings: Settings) -> LLMProvider:
    """Instantiate the correct LLM provider based on config."""
    if settings.llm_provider == "metis":
        return MetisProvider(
            api_key=settings.metis_api_key,
            model=settings.llm_model,
            proxy_url=settings.proxy_url,
        )
    return AvalAIProvider(
        api_key=settings.avalai_api_key,
        model=settings.llm_model,
        use_flex_tier=settings.llm_use_flex_tier,
    )


async def main() -> None:
    settings = get_settings()
    setup_logging(debug=settings.app_debug)

    log = structlog.get_logger()
    log.info(
        "starting ai-business-os",
        env=settings.app_env,
        provider=settings.llm_provider,
        model=settings.llm_model,
    )

    # Wire: Provider -> Runtime -> Gateway
    llm = build_llm_provider(settings)
    runtime = SalesRuntime(llm=llm)
    gateway = TelegramGateway(
        token=settings.telegram_bot_token,
        runtime=runtime,
        tenant_id=settings.default_tenant_id,
        proxy_url=settings.proxy_url,
    )


    await gateway.start()


if __name__ == "__main__":
    asyncio.run(main())