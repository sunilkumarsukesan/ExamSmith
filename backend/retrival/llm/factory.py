from typing import Literal
from .base import LLMProvider
from .groq_provider import GroqProvider

class LLMFactory:
    """Factory for LLM provider selection."""
    
    _providers = {
        "groq": GroqProvider,
        # Future providers:
        # "openai": OpenAIProvider,
        # "gemini": GeminiProvider,
    }
    
    @staticmethod
    def create(provider: Literal["groq"] = "groq", **kwargs) -> LLMProvider:
        """Create LLM provider instance."""
        if provider not in LLMFactory._providers:
            raise ValueError(
                f"Unknown provider: {provider}. Available: {list(LLMFactory._providers.keys())}"
            )
        
        return LLMFactory._providers[provider](**kwargs)
    
    @staticmethod
    def register_provider(name: str, provider_class):
        """Register new LLM provider (for future scaling)."""
        LLMFactory._providers[name] = provider_class

# Global instance
llm = LLMFactory.create("groq")
