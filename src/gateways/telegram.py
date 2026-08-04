"""Telegram Gateway for AI Business OS.

Receives messages from Telegram via long-polling and converts them into
normalized IncomingEvents. Delivers OutgoingResponses back to users.

This gateway knows nothing about LLMs, prompts, or business logic —
its only job is translation between Telegram's format and the internal
event model. Swapping to webhook mode later is a change inside this
file only, nothing else in the system changes.

Uses aiogram v3 — the leading async Telegram bot framework for Python.
"""

from __future__ import annotations

import logging

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.client.session.aiohttp import AiohttpSession
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart
from aiogram.types import Message as TelegramMessage

from core.interfaces import AgentRuntime
from core.models import (
    ChannelType,
    IncomingEvent,
    Message,
    OutgoingResponse,
    Role,
)

logger = logging.getLogger(__name__)





class TelegramGateway:
    """Gateway implementation for Telegram.

    Satisfies the Gateway Protocol by shape — no inheritance needed.
    """

    name = "telegram"

    def __init__(
        self,
        token: str,
        runtime: AgentRuntime,
        tenant_id: str = "default",
        proxy_url: str | None = None,
    ) -> None:
        self._runtime = runtime
        self._tenant_id = tenant_id

        session = AiohttpSession(proxy=proxy_url) if proxy_url else None

        self._bot = Bot(
            token=token,
            session=session,
            default=DefaultBotProperties(parse_mode=ParseMode.HTML),
        )
        self._dp = Dispatcher()
        self._register_handlers()

    def _register_handlers(self) -> None:
        """Register all Telegram message handlers."""

        @self._dp.message(CommandStart())
        async def handle_start(message: TelegramMessage) -> None:
            await message.answer(
                "👋 Hello! I am your AI Sales Assistant.\n"
                "Ask me anything about our products."
            )

        @self._dp.message()
        async def handle_message(message: TelegramMessage) -> None:
            if not message.text:
                return

            event = await self.parse_incoming(message)
            response = await self._runtime.handle(event)
            await self.send(response)

    async def parse_incoming(self, raw: TelegramMessage) -> IncomingEvent:
        """Convert a Telegram message into a normalized IncomingEvent."""
        message = Message(
            role=Role.USER,
            content=raw.text or "",
            tenant_id=self._tenant_id,
            conversation_id=str(raw.chat.id),
            channel=ChannelType.TELEGRAM,
            external_user_id=str(raw.from_user.id if raw.from_user else raw.chat.id),
        )
        return IncomingEvent(
            message=message,
            raw_payload={"message_id": raw.message_id, "chat_id": raw.chat.id},
        )

    async def send(self, response: OutgoingResponse) -> None:
        """Deliver a response back to the user on Telegram."""
        await self._bot.send_message(
            chat_id=int(response.external_user_id),
            text=response.content,
        )

    async def start(self) -> None:
        """Start polling for incoming messages."""
        logger.info("Starting Telegram gateway (long-polling)")
        await self._dp.start_polling(self._bot)