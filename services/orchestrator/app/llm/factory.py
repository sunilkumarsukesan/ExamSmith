from __future__ import annotations

from app.llm.anthropic import AnthropicClient
from app.llm.client import LLMClient
from app.llm.groq import GroqClient
from app.llm.mock import MockLLMClient
from app.llm.openai import OpenAIClient


def get_llm_client(provider: str) -> LLMClient:
    p = (provider or "").strip().lower()
    if p in ("mock", "dev"):
        return MockLLMClient()
    if p in ("openai", "azure_openai"):
        # Azure OpenAI can be supported via OPENAI_BASE_URL + key; keep same client.
        return OpenAIClient()
    if p in ("anthropic",):
        return AnthropicClient()
    if p in ("groq",):
        return GroqClient()

    # Unknown providers fall back to mock to keep the system usable in dev.
    return MockLLMClient()
