from abc import ABC, abstractmethod
from typing import Optional

class LLMProvider(ABC):
    """Abstract base for LLM providers."""
    
    @abstractmethod
    async def generate(
        self,
        prompt: str,
        max_tokens: int = 1024,
        temperature: float = 0.7,
    ) -> str:
        """Generate text from prompt."""
        pass

    @abstractmethod
    async def evaluate_answer(
        self,
        official_answer: str,
        student_answer: str,
        evidence_chunks: list[str],
    ) -> dict:
        """Evaluate student answer against official answer.
        
        Returns:
            {
                "match_percentage": float (0-100),
                "missing_points": list[str],
                "extra_points": list[str],
                "improvements": str
            }
        """
        pass
    
    @abstractmethod
    async def generate_paper(
        self,
        blueprint: dict,
        questions: list[dict],
    ) -> dict:
        """Generate paper structure with selected questions."""
        pass
