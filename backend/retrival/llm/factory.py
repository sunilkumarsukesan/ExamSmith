from typing import Literal
from .base import LLMProvider
from .groq_provider import GroqProvider
from config import settings

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

def get_llm(provider: Literal["groq"] = "groq", **kwargs) -> LLMProvider:
    """Get an LLM provider instance.

    This is lazy by design so the service can start even when secrets
    are not configured (e.g., GROQ_API_KEY is blank).
    """
    if provider == "groq" and not (kwargs.get("api_key") or settings.groq_api_key):
        raise ValueError("GROQ_API_KEY is not set. Add it to the root .env to enable LLM features.")
    return LLMFactory.create(provider, **kwargs)
