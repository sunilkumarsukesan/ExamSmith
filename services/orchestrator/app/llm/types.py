from __future__ import annotations

from typing import Any, Literal, Optional

from pydantic import BaseModel, Field


class LLMMessage(BaseModel):
    role: Literal["system", "user", "assistant"]
    content: str


class LLMRequest(BaseModel):
    messages: list[LLMMessage]
    provider: str
    model: str

    temperature: float = 0.2
    top_p: float = 1.0
    max_output_tokens: int = 800

    # Optional extra knobs for specific providers
    metadata: dict[str, Any] = Field(default_factory=dict)


class LLMResponse(BaseModel):
    text: str
    raw: Optional[dict[str, Any]] = None

    # Optional usage info (provider-dependent)
    input_tokens: int | None = None
    output_tokens: int | None = None
    total_tokens: int | None = None
    cost_usd: float | None = None
