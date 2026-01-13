from __future__ import annotations

from abc import ABC, abstractmethod

from app.llm.types import LLMRequest, LLMResponse


class LLMClient(ABC):
    @abstractmethod
    async def generate(self, req: LLMRequest) -> LLMResponse:
        raise NotImplementedError
