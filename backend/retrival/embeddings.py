"""
Mistral Embeddings Module

Provides real embedding generation using Mistral AI API.
No placeholder embeddings allowed - this is a MANDATORY component.
"""

import httpx
import logging
from typing import List, Optional
from config import settings

logger = logging.getLogger(__name__)


class MistralEmbeddings:
    """
    Mistral embedding provider for semantic search.
    
    Uses mistral-embed model with 1024 dimensions.
    REQUIRED for proper RAG functionality.
    """
    
    def __init__(self, api_key: str = None):
        self.api_key = api_key or settings.mistral_api_key
        self.model = settings.mistral_embed_model
        self.dimension = settings.mistral_embed_dimension
        self.base_url = "https://api.mistral.ai/v1/embeddings"
        
        if not self.api_key:
            logger.warning(
                "⚠️ MISTRAL_API_KEY not configured! "
                "Semantic search will NOT work properly. "
                "Set MISTRAL_API_KEY in your .env file."
            )
    
    async def embed_text(self, text: str) -> List[float]:
        """
        Generate embedding for a single text.
        
        Args:
            text: Text to embed (max ~8000 tokens)
        
        Returns:
            list[float]: 1024-dimensional embedding vector
        
        Raises:
            ValueError: If API key not configured
            httpx.HTTPError: If API request fails
        """
        if not self.api_key:
            raise ValueError(
                "MISTRAL_API_KEY not configured. "
                "Cannot generate embeddings. "
                "Please add MISTRAL_API_KEY to your .env file."
            )
        
        result = await self._call_api([text])
        return result[0]
    
    async def embed_texts(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings for multiple texts (batch).
        
        Args:
            texts: List of texts to embed (max 32 per batch)
        
        Returns:
            list[list[float]]: List of 1024-dimensional embedding vectors
        """
        if not self.api_key:
            raise ValueError(
                "MISTRAL_API_KEY not configured. "
                "Cannot generate embeddings."
            )
        
        # Batch in chunks of 32 (Mistral limit)
        batch_size = 32
        all_embeddings = []
        
        for i in range(0, len(texts), batch_size):
            batch = texts[i:i + batch_size]
            batch_embeddings = await self._call_api(batch)
            all_embeddings.extend(batch_embeddings)
        
        return all_embeddings
    
    async def _call_api(self, texts: List[str]) -> List[List[float]]:
        """
        Call Mistral embeddings API.
        
        Args:
            texts: List of texts (max 32)
        
        Returns:
            List of embedding vectors
        """
        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(
                    self.base_url,
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": self.model,
                        "input": texts
                    }
                )
                response.raise_for_status()
                
                data = response.json()
                
                # Extract embeddings in order
                embeddings = [
                    item["embedding"]
                    for item in sorted(data["data"], key=lambda x: x["index"])
                ]
                
                logger.debug(f"Generated {len(embeddings)} embeddings via Mistral API")
                return embeddings
                
        except httpx.HTTPStatusError as e:
            logger.error(f"Mistral API error: {e.response.status_code} - {e.response.text}")
            raise
        except httpx.RequestError as e:
            logger.error(f"Mistral API request failed: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Embedding generation failed: {str(e)}")
            raise


# Singleton instance for application-wide use
_embeddings_instance: Optional[MistralEmbeddings] = None


def get_embeddings() -> MistralEmbeddings:
    """Get singleton embeddings instance."""
    global _embeddings_instance
    if _embeddings_instance is None:
        _embeddings_instance = MistralEmbeddings()
    return _embeddings_instance


# Convenience function for quick embedding
async def embed_query(query: str) -> List[float]:
    """
    Generate embedding for a query string.
    
    This is the primary function for retrieval queries.
    
    Args:
        query: Search query text
    
    Returns:
        1024-dimensional embedding vector
    """
    embeddings = get_embeddings()
    return await embeddings.embed_text(query)
