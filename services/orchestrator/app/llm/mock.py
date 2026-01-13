from __future__ import annotations

import json

from app.llm.client import LLMClient
from app.llm.types import LLMRequest, LLMResponse


class MockLLMClient(LLMClient):
    """Deterministic mock LLM for local development.

    Returns a JSON object in text form with question_text + answer_key.
    """

    async def generate(self, req: LLMRequest) -> LLMResponse:
        user = next((m.content for m in reversed(req.messages) if m.role == "user"), "")
        payload = {
            "question_text": f"(mock) {req.model}: {user[:120].strip()}",
            "answer_key": "(mock) Answer key based on provided context.",
        }
        return LLMResponse(text=json.dumps(payload, ensure_ascii=False), raw={"provider": "mock"})
