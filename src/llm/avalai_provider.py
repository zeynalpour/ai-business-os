"""AvalAI LLM Provider for AI Business OS.

AvalAI (avalai.ir) is an OpenAI-compatible gateway providing access to
GPT, Gemini, Cohere and other models from Iran via a single base_url.

Default model: gemini-2.0-flash with flex service tier (50% cheaper).

Docs: https://docs.avalai.ir
"""

from __future__ import annotations

import time

from openai import AsyncOpenAI

from core.models import LLMResponse, LLMUsage, Message, Role

AVALAI_BASE_URL = "https://api.avalai.ir/v1"


class AvalAIProvider:
    """LLMProvider implementation backed by AvalAI.

    Satisfies the LLMProvider Protocol by shape — no inheritance needed.
    """

    name = "avalai"

    def __init__(
        self,
        api_key: str,
        model: str = "gemini-2.0-flash",
        use_flex_tier: bool = True,
    ) -> None:
        self.model = model
        self._use_flex_tier = use_flex_tier
        self._client = AsyncOpenAI(
            api_key=api_key,
            base_url=AVALAI_BASE_URL,
        )

    async def generate(
        self,
        messages: list[Message],
        system_prompt: str | None = None,
    ) -> LLMResponse:
        openai_messages = []

        if system_prompt:
            openai_messages.append({
                "role": "system",
                "content": system_prompt,
            })

        for msg in messages:
            if msg.role in (Role.USER, Role.ASSISTANT):
                openai_messages.append({
                    "role": msg.role.value,
                    "content": msg.content,
                })

        extra = {"service_tier": "flex"} if self._use_flex_tier else {}

        start = time.perf_counter()
        response = await self._client.chat.completions.create(
            model=self.model,
            messages=openai_messages,
            **extra,
        )
        latency_ms = (time.perf_counter() - start) * 1000

        choice = response.choices[0].message
        usage = response.usage

        return LLMResponse(
            content=choice.content or "",
            usage=LLMUsage(
                prompt_tokens=usage.prompt_tokens if usage else 0,
                completion_tokens=usage.completion_tokens if usage else 0,
                latency_ms=latency_ms,
            ),
            provider=self.name,
            model=self.model,
        )