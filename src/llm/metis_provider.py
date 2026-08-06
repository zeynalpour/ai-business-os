"""Metis LLM Provider for AI Business OS.

Metis (metisai.ir) provides access to multiple model families from Iran.
Each family uses a different SDK/endpoint:

- Gemini models  → Google GenerativeAI SDK with Metis endpoint
- OpenAI models  → OpenAI-compatible wrapper (gpt-4o, gpt-4o-mini, etc.)
- Grok models    → OpenAI-compatible wrapper (grok-beta, etc.)

The provider auto-detects which SDK to use based on the model name.
The Runtime never knows which path was taken — it just calls generate().
"""

from __future__ import annotations

import os
import time

from google import genai
from google.genai import types
from openai import AsyncOpenAI

from core.models import LLMResponse, LLMUsage, Message, Role

METIS_BASE_URLS = {
    "openai": "https://api.metisai.ir/api/v1/wrapper/openai",
    "grok": "https://api.metisai.ir/api/v1/wrapper/grok",
}

METIS_GEMINI_ENDPOINT = "https://api.metisai.ir"


def _get_base_url(model: str) -> str:
    if model.startswith("grok"):
        return METIS_BASE_URLS["grok"]
    return METIS_BASE_URLS["openai"]


class MetisProvider:
    name = "metis"

    def __init__(
        self,
        api_key: str,
        model: str = "gemini-2.5-flash-lite",
        proxy_url: str | None = None,
    ) -> None:
        self.model = model
        self._is_gemini = model.startswith("gemini")
        self._gemini_client: genai.Client | None = None
        self._openai_client: AsyncOpenAI | None = None

        if self._is_gemini:
            if proxy_url:
                os.environ["HTTPS_PROXY"] = proxy_url
                os.environ["HTTP_PROXY"] = proxy_url
            self._gemini_client = genai.Client(
                api_key=api_key,
                http_options=types.HttpOptions(
                    base_url=METIS_GEMINI_ENDPOINT,
                ),
            )
        else:
            self._openai_client = AsyncOpenAI(
                api_key=api_key,
                base_url=_get_base_url(model),
            )

    async def generate(
        self,
        messages: list[Message],
        system_prompt: str | None = None,
    ) -> LLMResponse:
        if self._is_gemini:
            return await self._generate_gemini(messages, system_prompt)
        return await self._generate_openai(messages, system_prompt)

    async def _generate_gemini(
        self,
        messages: list[Message],
        system_prompt: str | None = None,
    ) -> LLMResponse:
        contents = []
        for msg in messages:
            if msg.role == Role.USER:
                contents.append(
                    types.Content(
                        role="user",
                        parts=[types.Part(text=msg.content)],
                    )
                )
            elif msg.role == Role.ASSISTANT:
                contents.append(
                    types.Content(
                        role="model",
                        parts=[types.Part(text=msg.content)],
                    )
                )

        config = types.GenerateContentConfig(
            system_instruction=system_prompt or "",
        )

        start = time.perf_counter()
        response = await self._gemini_client.aio.models.generate_content(
            model=self.model,
            contents=contents,
            config=config,
        )
        latency_ms = (time.perf_counter() - start) * 1000

        usage_metadata = response.usage_metadata
        return LLMResponse(
            content=response.text or "",
            usage=LLMUsage(
                prompt_tokens=usage_metadata.prompt_token_count if usage_metadata else 0,
                completion_tokens=usage_metadata.candidates_token_count if usage_metadata else 0,
                latency_ms=latency_ms,
            ),
            provider=self.name,
            model=self.model,
        )

    async def _generate_openai(
        self,
        messages: list[Message],
        system_prompt: str | None = None,
    ) -> LLMResponse:
        assert self._openai_client is not None
        
        openai_messages : list[dict[str, str]] = []

        if system_prompt:
            openai_messages.append({"role": "system", "content": system_prompt})

        for msg in messages:
            if msg.role in (Role.USER, Role.ASSISTANT):
                openai_messages.append({
                    "role": msg.role.value,
                    "content": msg.content,
                })

        start = time.perf_counter()
        response = await self._openai_client.chat.completions.create(
            model=self.model,
            messages=openai_messages, # type: ignore[arg-type]
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