from __future__ import annotations

import os
from typing import Any

import httpx

from app.llm.client import LLMClient
from app.llm.types import LLMRequest, LLMResponse


class GroqClient(LLMClient):
    """Groq LLM client.

    Groq exposes an OpenAI-compatible API surface for chat completions.
    Default base URL: https://api.groq.com/openai/v1
    """

    def __init__(self, api_key: str | None = None, base_url: str | None = None) -> None:
        self.api_key = api_key or os.getenv("GROQ_API_KEY")
        self.base_url = base_url or os.getenv("GROQ_BASE_URL") or "https://api.groq.com/openai/v1"

    async def generate(self, req: LLMRequest) -> LLMResponse:
        if not self.api_key:
            raise RuntimeError("GROQ_API_KEY is not set")

        url = f"{self.base_url}/chat/completions"
        payload: dict[str, Any] = {
            "model": req.model,
            "messages": [{"role": m.role, "content": m.content} for m in req.messages],
            "temperature": req.temperature,
            "top_p": req.top_p,
            "max_tokens": req.max_output_tokens,
        }

        headers = {"Authorization": f"Bearer {self.api_key}"}
        async with httpx.AsyncClient(timeout=60.0) as client:
            r = await client.post(url, json=payload, headers=headers)
            r.raise_for_status()
            data = r.json()

        text = (
            (((data.get("choices") or [])[0] or {}).get("message") or {}).get("content")
            if (data.get("choices") or [])
            else ""
        )
        if not text:
            text = str(data)

        usage = data.get("usage") or {}
        input_tokens = usage.get("prompt_tokens")
        output_tokens = usage.get("completion_tokens")
        total_tokens = usage.get("total_tokens")

        return LLMResponse(
            text=text,
            raw=data,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            total_tokens=total_tokens,
        )
