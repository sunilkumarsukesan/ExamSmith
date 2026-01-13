from __future__ import annotations

import os
from typing import Any

import httpx

from app.llm.client import LLMClient
from app.llm.types import LLMRequest, LLMResponse


class OpenAIClient(LLMClient):
    def __init__(self, api_key: str | None = None, base_url: str | None = None) -> None:
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.base_url = base_url or os.getenv("OPENAI_BASE_URL") or "https://api.openai.com/v1"

    async def generate(self, req: LLMRequest) -> LLMResponse:
        if not self.api_key:
            raise RuntimeError("OPENAI_API_KEY is not set")

        # Uses the Responses API (recommended) but remains a thin wrapper.
        url = f"{self.base_url}/responses"
        payload: dict[str, Any] = {
            "model": req.model,
            "input": [{"role": m.role, "content": m.content} for m in req.messages],
            "temperature": req.temperature,
            "top_p": req.top_p,
            "max_output_tokens": req.max_output_tokens,
        }

        headers = {"Authorization": f"Bearer {self.api_key}"}
        async with httpx.AsyncClient(timeout=60.0) as client:
            r = await client.post(url, json=payload, headers=headers)
            r.raise_for_status()
            data = r.json()

        # Best-effort extraction of text
        text = ""
        for item in data.get("output", []) or []:
            for content in item.get("content", []) or []:
                if content.get("type") in ("output_text", "text"):
                    text += content.get("text", "")
        if not text:
            text = str(data)

        usage = data.get("usage") or {}
        input_tokens = usage.get("input_tokens")
        output_tokens = usage.get("output_tokens")
        total_tokens = usage.get("total_tokens")

        return LLMResponse(
            text=text,
            raw=data,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            total_tokens=total_tokens,
        )
