"""AI Sales Employee runtime for AI Business OS.

This is the brain for v0.1: receives an IncomingEvent, calls the LLM
with a sales-focused system prompt, returns an OutgoingResponse.

No memory, no RAG, no tools — intentionally minimal. This proves the
architecture works end-to-end. Later phases replace this class with a
planner-driven runtime without touching Gateway or LLMProvider at all.
"""

from __future__ import annotations

import logging

from core.interfaces import LLMProvider
from core.models import IncomingEvent, OutgoingResponse

logger = logging.getLogger(__name__)

SALES_SYSTEM_PROMPT = """You are a professional AI Sales Assistant.

Your responsibilities:
- Answer customer questions about products clearly and helpfully
- Recommend suitable products based on customer needs
- Qualify leads by understanding customer intent
- Collect relevant customer information naturally
- Escalate to a human agent when the question is too complex

Your tone:
- Friendly and professional
- Concise — no unnecessary filler
- Never make up product details you don't know

If you don't know something, say so honestly and offer to help find out.
"""


class SalesRuntime:
    """Minimal AgentRuntime for the AI Sales Employee.

    Satisfies the AgentRuntime Protocol by shape — no inheritance needed.
    """

    def __init__(self, llm: LLMProvider) -> None:
        self._llm = llm

    async def handle(self, event: IncomingEvent) -> OutgoingResponse:
        """Process one incoming event and return a response."""
        message = event.message

        logger.info(
            "handling event",
            extra={
                "event_id": str(event.id),
                "conversation_id": message.conversation_id,
                "tenant_id": message.tenant_id,
            },
        )

        llm_response = await self._llm.generate(
            messages=[message],
            system_prompt=SALES_SYSTEM_PROMPT,
        )

        logger.info(
            "llm response",
            extra={
                "provider": llm_response.provider,
                "model": llm_response.model,
                "prompt_tokens": llm_response.usage.prompt_tokens,
                "completion_tokens": llm_response.usage.completion_tokens,
                "latency_ms": round(llm_response.usage.latency_ms, 2),
            },
        )

        return OutgoingResponse(
            conversation_id=message.conversation_id,
            content=llm_response.content,
            channel=message.channel,
            external_user_id=message.external_user_id,
        )