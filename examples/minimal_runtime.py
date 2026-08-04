"""Minimal reference implementation of the v0.1 pipeline.

This shows how a concrete AgentRuntime and a fake LLMProvider satisfy the
Protocols in core/interfaces.py, with no inheritance required. Use this
as the starting point for Day 5 (wiring) and as a template for the first
unit tests: swap FakeLLMProvider for OpenAIProvider/OllamaProvider and
nothing else in this file needs to change.

Run directly for a smoke test:
    python examples/minimal_runtime.py
"""

from __future__ import annotations

import asyncio
import time

from core.interfaces import AgentRuntime, LLMProvider
from core.models import (
    ChannelType,
    IncomingEvent,
    LLMResponse,
    LLMUsage,
    Message,
    OutgoingResponse,
    Role,
)

SALES_SYSTEM_PROMPT = (
    "You are an AI Sales Employee for a small online store. Answer "
    "questions about products helpfully and concisely, and ask a "
    "qualifying question if the customer's intent is unclear."
)


class FakeLLMProvider:
    """Stand-in LLMProvider for tests and local smoke-testing.

    Satisfies the LLMProvider Protocol purely by shape - no base class,
    no import of core.interfaces required at runtime.
    """

    name = "fake"
    model = "fake-echo-1"

    async def generate(
        self, messages: list[Message], system_prompt: str | None = None
    ) -> LLMResponse:
        start = time.perf_counter()
        last_user_message = messages[-1].content if messages else ""
        reply = f"(fake reply) You said: {last_user_message!r}"
        latency_ms = (time.perf_counter() - start) * 1000
        return LLMResponse(
            content=reply,
            usage=LLMUsage(
                prompt_tokens=len(last_user_message.split()),
                completion_tokens=len(reply.split()),
                latency_ms=latency_ms,
            ),
            provider=self.name,
            model=self.model,
        )


class MinimalSalesRuntime:
    """v0.1 AgentRuntime: one LLM call, no memory, no tools.

    Later phases replace this class entirely (planner, retrieval, tools)
    without touching Gateway or LLMProvider implementations.
    """

    def __init__(self, llm: LLMProvider) -> None:
        self._llm = llm

    async def handle(self, event: IncomingEvent) -> OutgoingResponse:
        message = event.message
        llm_response = await self._llm.generate(
            messages=[message], system_prompt=SALES_SYSTEM_PROMPT
        )
        return OutgoingResponse(
            conversation_id=message.conversation_id,
            content=llm_response.content,
            channel=message.channel,
            external_user_id=message.external_user_id,
        )


async def _smoke_test() -> None:
    runtime: AgentRuntime = MinimalSalesRuntime(llm=FakeLLMProvider())

    event = IncomingEvent(
        message=Message(
            role=Role.USER,
            content="Do you have this product in blue?",
            tenant_id="demo-store",
            conversation_id="conv-1",
            channel=ChannelType.TELEGRAM,
            external_user_id="123456",
        )
    )

    response = await runtime.handle(event)
    print(response.model_dump_json(indent=2))


if __name__ == "__main__":
    asyncio.run(_smoke_test())