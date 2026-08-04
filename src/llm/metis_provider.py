"""Metis LLM Provider for AI Business OS.

Metis (metisai.ir) is an OpenAI-compatible gateway giving access to
models like Gemini, GPT-4o, Grok etc. from Iran.

Default model: gemini-2.0-flash — best quality/cost ratio for dev.

Docs: https://docs.metisai.ir/api/wrapper/openai
"""

from __future__ import annotations

import time

from openai import AsyncOpenAI

from core.models import LLMResponse, LLMUsage, Message, Role

# base_url changes per model family on Metis
METIS_BASE_URLS = {
    "gemini": "https://api.metisai.ir/api/v1/wrapper/gemini",
    "openai": "https://api.metisai.ir/api/v1/wrapper/openai",
    "grok":   "https://api.metisai.ir/api/v1/wrapper/grok",
}

def _get_base_url(model: str) -> str:
    """Pick the correct Metis base_url based on model name."""
    if model.startswith("gemini"):
        return METIS_BASE_URLS["gemini"]
    if model.startswith("grok"):
        return METIS_BASE_URLS["grok"]
    return METIS_BASE_URLS["openai"]


class MetisProvider:
    """LLMProvider implementation backed by Metis API.

    Satisfies the LLMProvider Protocol by shape — no inheritance needed.
    """

    name = "metis"

    def __init__(
        self,
        api_key: str,
        model: str = "gemini-2.0-flash",
    ) -> None:
        self.model = model
        self._client = AsyncOpenAI(
            api_key=api_key,
            base_url=_get_base_url(model),
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

        start = time.perf_counter()
        response = await self._client.chat.completions.create(
            model=self.model,
            messages=openai_messages,
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