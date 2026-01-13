from __future__ import annotations

import os
from typing import Any

import httpx

from app.llm.client import LLMClient
from app.llm.types import LLMRequest, LLMResponse


class AnthropicClient(LLMClient):
    def __init__(self, api_key: str | None = None, base_url: str | None = None) -> None:
        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
        self.base_url = base_url or os.getenv("ANTHROPIC_BASE_URL") or "https://api.anthropic.com"

    async def generate(self, req: LLMRequest) -> LLMResponse:
        if not self.api_key:
            raise RuntimeError("ANTHROPIC_API_KEY is not set")

        url = f"{self.base_url}/v1/messages"

        # Convert to Anthropic Messages format
        system = "\n".join([m.content for m in req.messages if m.role == "system"]).strip()
        messages = [
            {"role": m.role, "content": m.content}
            for m in req.messages
            if m.role in ("user", "assistant")
        ]

        payload: dict[str, Any] = {
            "model": req.model,
            "max_tokens": req.max_output_tokens,
            "temperature": req.temperature,
            "top_p": req.top_p,
            "messages": messages,
        }
        if system:
            payload["system"] = system

        headers = {
            "x-api-key": self.api_key,
            "anthropic-version": os.getenv("ANTHROPIC_VERSION") or "2023-06-01",
        }

        async with httpx.AsyncClient(timeout=60.0) as client:
            r = await client.post(url, json=payload, headers=headers)
            r.raise_for_status()
            data = r.json()

        text = ""
        for c in data.get("content", []) or []:
            if c.get("type") == "text":
                text += c.get("text", "")
        if not text:
            text = str(data)

        usage = data.get("usage") or {}
        input_tokens = usage.get("input_tokens")
        output_tokens = usage.get("output_tokens")

        total_tokens = None
        if isinstance(input_tokens, int) and isinstance(output_tokens, int):
            total_tokens = input_tokens + output_tokens

        return LLMResponse(
            text=text,
            raw=data,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            total_tokens=total_tokens,
        )
