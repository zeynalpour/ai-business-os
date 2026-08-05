"""Core event/message models for AI Business OS.

These are the shared data contracts that flow through every layer of the
runtime (Gateway -> Orchestrator -> Agent Runtime -> LLM Provider). No
component should invent its own message shape — everything speaks in
terms of these models, which is what lets gateways, providers and tools
be swapped without touching core business logic.
"""

from __future__ import annotations

from datetime import datetime, UTC
from enum import StrEnum
from typing import Any
from uuid import UUID, uuid4

from pydantic import BaseModel, Field


class ChannelType(StrEnum):
    """Which gateway a message originated from / should be delivered to."""

    TELEGRAM = "telegram"
    WHATSAPP = "whatsapp"
    SLACK = "slack"
    DISCORD = "discord"
    REST = "rest"


class Role(StrEnum):
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"


class Message(BaseModel):
    """A single conversation turn, channel-agnostic."""

    id: UUID = Field(default_factory=uuid4)
    role: Role
    content: str
    tenant_id: str = Field(..., description="Business/tenant this message belongs to")
    conversation_id: str
    channel: ChannelType
    external_user_id: str = Field(
        ..., description="User id in the source channel, e.g. Telegram chat id"
    )
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    metadata: dict[str, Any] = Field(default_factory=dict)


class IncomingEvent(BaseModel):
    """Normalized event emitted by a Gateway when a new message arrives.

    This is the concrete instance of the 'everything is an event'
    principle: customer_message today, product_updated / order_created /
    payment_received etc. later, all following the same envelope shape.
    """

    id: UUID = Field(default_factory=uuid4)
    type: str = "customer_message"
    message: Message
    raw_payload: dict[str, Any] = Field(
        default_factory=dict,
        description="Original provider payload, kept for debugging and replay",
    )


class OutgoingResponse(BaseModel):
    """What the Runtime hands back to a Gateway for delivery to the user."""

    conversation_id: str
    content: str
    channel: ChannelType
    external_user_id: str
    metadata: dict[str, Any] = Field(default_factory=dict)


class LLMUsage(BaseModel):
    """Per-call usage stats — the seed of the Observability module."""

    prompt_tokens: int = 0
    completion_tokens: int = 0
    latency_ms: float = 0.0


class LLMResponse(BaseModel):
    content: str
    usage: LLMUsage = Field(default_factory=LLMUsage)
    provider: str
    model: str