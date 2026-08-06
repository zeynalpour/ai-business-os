"""Core protocol interfaces for AI Business OS.

Every concrete implementation (TelegramGateway, OpenAIProvider, ...) must
satisfy one of these Protocols. The runtime is written entirely against
these interfaces, never against a concrete class — this is what
"provider agnostic", "interface first", and "no vendor lock-in" mean in
practice, not just in the docs.

Using typing.Protocol instead of ABCs means:
- No forced inheritance — any class with the right shape satisfies the
  interface (structural typing), which lowers the bar for contributors
  adding a new gateway or provider.
- runtime_checkable lets us assert conformance in tests without the
  implementation needing to know about this module at all.
"""

from __future__ import annotations

from typing import Any, Protocol, runtime_checkable

from core.models import IncomingEvent, LLMResponse, Message, OutgoingResponse


@runtime_checkable
class Gateway(Protocol):
    """A channel adapter: Telegram, WhatsApp, Slack, REST, etc.

    A Gateway's only job is translation: raw channel payload <->
    IncomingEvent / OutgoingResponse. It must never contain business
    logic, prompting, or LLM calls — that belongs to the Runtime.
    """

    name: str

    async def start(self) -> None:
        """Begin listening for incoming messages (polling, webhook, etc.)."""
        ...

    async def send(self, response: OutgoingResponse) -> None:
        """Deliver a response back to the user on this channel."""
        ...

    async def parse_incoming(self, raw_payload: dict[str, Any]) -> IncomingEvent:
        """Convert a channel-native payload into a normalized IncomingEvent."""
        ...


@runtime_checkable
class LLMProvider(Protocol):
    """A text-generation backend: OpenAI, Ollama, Claude, Gemini, ...

    The Runtime only ever calls generate(). It never knows which vendor,
    API shape, or auth scheme sits behind a given provider — that's the
    whole point of the interface.
    """

    name: str
    model: str

    async def generate(
        self,
        messages: list[Message],
        system_prompt: str | None = None,
    ) -> LLMResponse:
        """Generate a completion given conversation history."""
        ...


@runtime_checkable
class AgentRuntime(Protocol):
    """The brain: takes an event, decides what to do, returns a response.

    v0.1 implementations do nothing but call an LLMProvider directly with
    a fixed system prompt. Later phases (Memory, Tools, Multi-Agent) can
    swap this for a planner-driven runtime without the Gateway or
    LLMProvider layers ever changing — that's the payoff of designing to
    this interface now instead of hardcoding the call chain.
    """

    async def handle(self, event: IncomingEvent) -> OutgoingResponse:
        """Process one incoming event and produce a response to send back."""
        ...